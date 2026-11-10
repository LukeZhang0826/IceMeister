"""Load a recorded run, line up ADC samples with carriage position, and plot.

Run folder layout (written by main.py run):
    meta.json     settings and constants used for the run
    motor.csv     host_t, position, velocity_raw, current_raw, moving, in_position
    adc.csv       host_rx, bridge_us, adc
    errors.csv    host_rx, bridge_us, code
    sync.csv      host_send, host_recv, bridge_us
    merged.csv    written here: one row per ADC sample with its carriage position
"""

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from config import ADC_MAX, CURRENT_UNIT_MA, velocity_units_to_mm_s

MOVING_THRESHOLD_MM_S = 0.5


# --- file IO ---------------------------------------------------------------

def write_csv(path: Path, header: list[str], rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def read_csv(path: Path) -> np.ndarray:
    """Read a numeric CSV with a header row into a 2D float array (0 rows if empty)."""
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [[float(x) for x in row] for row in reader if row]
    return np.array(rows, dtype=float).reshape(-1, len(header))


# --- clock alignment -------------------------------------------------------

@dataclass
class ClockFit:
    slope: float       # host seconds per bridge second
    intercept: float   # host_s = intercept + slope * bridge_s
    pings_used: int
    pings_total: int
    rtt_median_ms: float

    def to_host(self, bridge_us: np.ndarray) -> np.ndarray:
        return self.intercept + self.slope * (bridge_us * 1e-6)

    @property
    def drift_ppm(self) -> float:
        """How fast the bridge clock runs relative to the PC clock (+ = bridge fast)."""
        return (1.0 / self.slope - 1.0) * 1e6


def fit_clock(sync: np.ndarray) -> ClockFit:
    """Map bridge micros() to host perf_counter() seconds from time-sync pings.

    Each ping gives: host send time, host receive time, bridge time at receipt.
    The bridge time corresponds to roughly the midpoint of send/receive. Pings
    with the shortest round trips have the least uncertainty, so keep the
    fastest half and fit a line (the Uno's resonator drifts by up to ~0.5%).
    """
    if len(sync) < 3:
        raise ValueError(f"only {len(sync)} time-sync replies recorded; cannot align clocks")
    send, recv, bridge_us = sync[:, 0], sync[:, 1], sync[:, 2]
    rtt = recv - send
    keep = rtt <= np.percentile(rtt, 50)
    if keep.sum() < 3:
        keep = np.argsort(rtt)[:3]
    mid = (send[keep] + recv[keep]) / 2
    b_s = bridge_us[keep] * 1e-6
    if b_s.max() - b_s.min() > 1.0:
        slope, intercept = np.polyfit(b_s, mid, 1)
    else:
        slope, intercept = 1.0, float(np.median(mid - b_s))
    return ClockFit(float(slope), float(intercept), int(np.size(mid)), len(sync), float(np.median(rtt) * 1e3))


# --- merge -----------------------------------------------------------------

@dataclass
class Run:
    path: Path
    meta: dict
    motor: np.ndarray
    adc: np.ndarray
    errors: np.ndarray
    sync: np.ndarray


def load_run(run_dir) -> Run:
    p = Path(run_dir)
    meta = json.loads((p / "meta.json").read_text())
    return Run(
        path=p,
        meta=meta,
        motor=read_csv(p / "motor.csv"),
        adc=read_csv(p / "adc.csv"),
        errors=read_csv(p / "errors.csv"),
        sync=read_csv(p / "sync.csv"),
    )


@dataclass
class Merged:
    t: np.ndarray            # s since first motor sample
    mm: np.ndarray           # carriage travel from start, mm
    adc: np.ndarray
    speed_mm_s: np.ndarray   # signed, + = away from start
    current_ma: np.ndarray
    motor_t: np.ndarray
    motor_mm: np.ndarray
    error_t: np.ndarray
    clock: ClockFit


def merge(run: Run) -> Merged:
    m = run.meta
    direction = m["direction"]
    mm_per_tick = m["mm_per_tick"]
    p0 = m["start_position"]

    motor_t = run.motor[:, 0]
    motor_mm = (run.motor[:, 1] - p0) * direction * mm_per_tick
    motor_speed = velocity_units_to_mm_s(run.motor[:, 2]) * direction
    motor_current = run.motor[:, 3] * CURRENT_UNIT_MA

    clock = fit_clock(run.sync)
    adc_t = clock.to_host(run.adc[:, 1])
    inside = (adc_t >= motor_t[0]) & (adc_t <= motor_t[-1])
    adc_t = adc_t[inside]

    err_t = clock.to_host(run.errors[:, 1]) - motor_t[0] if len(run.errors) else np.empty(0)

    return Merged(
        t=adc_t - motor_t[0],
        mm=np.interp(adc_t, motor_t, motor_mm),
        adc=run.adc[inside, 2],
        speed_mm_s=np.interp(adc_t, motor_t, motor_speed),
        current_ma=np.interp(adc_t, motor_t, motor_current),
        motor_t=motor_t - motor_t[0],
        motor_mm=motor_mm,
        error_t=err_t,
        clock=clock,
    )


def save_merged(run: Run, mg: Merged):
    write_csv(
        run.path / "merged.csv",
        ["t_s", "carriage_mm", "adc", "speed_mm_s", "current_ma"],
        zip(np.round(mg.t, 6), np.round(mg.mm, 4), mg.adc.astype(int), np.round(mg.speed_mm_s, 3), np.round(mg.current_ma, 1)),
    )


# --- analysis --------------------------------------------------------------

def binned(x: np.ndarray, y: np.ndarray, bin_mm: float):
    """Mean and std of y in fixed-width bins of x. Empty bins are dropped."""
    if len(x) == 0:
        return np.empty(0), np.empty(0), np.empty(0)
    edges = np.arange(np.floor(x.min()), np.ceil(x.max()) + bin_mm, bin_mm)
    idx = np.digitize(x, edges) - 1
    centers, means, stds = [], [], []
    for i in range(len(edges) - 1):
        sel = idx == i
        if sel.sum() >= 2:
            centers.append((edges[i] + edges[i + 1]) / 2)
            means.append(y[sel].mean())
            stds.append(y[sel].std())
    return np.array(centers), np.array(means), np.array(stds)


def summarize(run: Run, mg: Merged) -> list[str]:
    lines = []
    m = run.meta
    dur = max(mg.t[-1] - mg.t[0], 1e-9) if len(mg.t) > 1 else 1e-9
    lines.append(f"Run: {run.path.name}")
    lines.append(f"  samples: {len(mg.adc)} ADC over {dur:.1f} s ({len(mg.adc) / dur:.0f} Hz), "
                 f"{len(mg.motor_t)} motor reads ({len(mg.motor_t) / max(mg.motor_t[-1], 1e-9):.0f} Hz), "
                 f"{len(run.errors)} I2C read errors")
    lines.append(f"  clock: {mg.clock.pings_used}/{mg.clock.pings_total} sync pings used, "
                 f"median RTT {mg.clock.rtt_median_ms:.1f} ms, bridge drift {mg.clock.drift_ppm:+.0f} ppm")
    lines.append(f"  travel: {mg.motor_mm.min():.2f} to {mg.motor_mm.max():.2f} mm "
                 f"(commanded {m['travel_mm']:.1f} mm at {m['speed_mm_s']:.1f} mm/s)")

    still = np.abs(mg.speed_mm_s) < 0.05
    for where, sel in (("at start", still & (mg.mm < 1.0)), ("at end", still & (mg.mm > mg.motor_mm.max() - 1.0))):
        if sel.sum() > 10:
            lines.append(f"  stationary noise {where}: {mg.adc[sel].std():.2f} counts std "
                         f"(mean {mg.adc[sel].mean():.1f}, {sel.sum()} samples)")

    fwd = mg.speed_mm_s > MOVING_THRESHOLD_MM_S
    if fwd.sum() > 10:
        x, y = mg.mm[fwd], mg.adc[fwd]
        slope, intercept = np.polyfit(x, y, 1)
        resid = y - (slope * x + intercept)
        ss_tot = ((y - y.mean()) ** 2).sum()
        r2 = 1 - (resid ** 2).sum() / ss_tot if ss_tot > 0 else float("nan")
        lines.append(f"  ADC while moving out: {y.min():.0f} to {y.max():.0f} counts, "
                     f"linear fit {slope:+.3f} counts/mm, R^2 = {r2:.4f}")
        if abs(slope) > 1e-6:
            lines.append(f"  max deviation from linear fit: {np.abs(resid).max():.1f} counts "
                         f"(~{np.abs(resid).max() / abs(slope):.2f} mm)")
    return lines


# --- plotting --------------------------------------------------------------

def plot(run: Run, mg: Merged, bin_mm: float = 1.0, show: bool = True):
    import matplotlib.pyplot as plt

    vref = run.meta.get("adc_vref", 5.0)
    name = run.path.name
    fwd = mg.speed_mm_s > MOVING_THRESHOLD_MM_S
    rev = mg.speed_mm_s < -MOVING_THRESHOLD_MM_S
    passes = [("moving out", fwd, "tab:blue"), ("moving back", rev, "tab:orange")]
    passes = [p for p in passes if p[1].sum() > 0]

    # Figure 1: everything against carriage position, x axes linked for zooming.
    fig, (ax_adc, ax_sens, ax_cur) = plt.subplots(
        3, 1, sharex=True, figsize=(12, 9), height_ratios=[3, 1.3, 1.3], constrained_layout=True)
    fig.suptitle(f"{name}: finger ADC vs carriage position")

    for label, sel, color in passes:
        ax_adc.scatter(mg.mm[sel], mg.adc[sel], s=3, alpha=0.25, color=color, linewidths=0)
        c, mean, std = binned(mg.mm[sel], mg.adc[sel], bin_mm)
        ax_adc.plot(c, mean, color=color, lw=1.5, label=f"{label} ({bin_mm:g} mm bin mean)")
        ax_adc.fill_between(c, mean - std, mean + std, color=color, alpha=0.2, lw=0)
        if len(c) > 2:
            ax_sens.plot(c, np.gradient(mean, c), color=color, lw=1, label=label)
        ax_cur.plot(mg.mm[sel], mg.current_ma[sel], color=color, lw=0.8, label=label)

    ax_adc.set_ylabel("ADC (counts)")
    ax_adc.set_ylim(min(-5, mg.adc.min() - 10) if len(mg.adc) else -5, max(ADC_MAX + 5, mg.adc.max() + 10) if len(mg.adc) else ADC_MAX + 5)
    sec = ax_adc.secondary_yaxis("right", functions=(lambda a: a * vref / ADC_MAX, lambda v: v * ADC_MAX / vref))
    sec.set_ylabel(f"V (ref {vref:g} V)")
    ax_adc.grid(True, alpha=0.3)
    if passes:
        ax_adc.legend(loc="best")

    ax_sens.set_ylabel("dADC/dx\n(counts/mm)")
    ax_sens.axhline(0, color="k", lw=0.5)
    ax_sens.grid(True, alpha=0.3)

    ax_cur.set_ylabel("motor current\n(mA)")
    ax_cur.set_xlabel("carriage position from start (mm)")
    ax_cur.grid(True, alpha=0.3)

    fig.savefig(run.path / "adc_vs_position.png", dpi=150)

    # Figure 2: time domain, to check alignment, stalls and dropouts.
    fig2, (ax_t, ax_dt) = plt.subplots(2, 1, sharex=True, figsize=(12, 6), height_ratios=[3, 1], constrained_layout=True)
    fig2.suptitle(f"{name}: time domain")
    ax_t.plot(mg.t, mg.adc, color="tab:blue", lw=0.8, label="ADC")
    ax_t.set_ylabel("ADC (counts)", color="tab:blue")
    ax_pos = ax_t.twinx()
    ax_pos.plot(mg.motor_t, mg.motor_mm, color="tab:green", lw=1.2, label="carriage")
    ax_pos.set_ylabel("carriage (mm)", color="tab:green")
    for et in mg.error_t:
        ax_t.axvline(et, color="red", lw=0.5, alpha=0.6)
    ax_t.grid(True, alpha=0.3)

    if len(mg.t) > 1:
        ax_dt.plot(mg.t[1:], np.diff(mg.t) * 1e3, lw=0.6, color="gray")
    ax_dt.set_ylim(bottom=0)
    ax_dt.ticklabel_format(axis="y", useOffset=False)
    ax_dt.set_ylabel("ADC sample\ngap (ms)")
    ax_dt.set_xlabel("time (s)")
    ax_dt.grid(True, alpha=0.3)

    fig2.savefig(run.path / "time_domain.png", dpi=150)

    if show:
        plt.show()
    else:
        plt.close("all")


def analyze(run_dir, bin_mm: float = 1.0, show: bool = True):
    run = load_run(run_dir)
    mg = merge(run)
    save_merged(run, mg)
    for line in summarize(run, mg):
        print(line)
    plot(run, mg, bin_mm=bin_mm, show=show)
    print(f"  plots saved to {run.path}")
