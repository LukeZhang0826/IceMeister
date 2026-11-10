"""Finger tester: pull the finger board along the rail with a Dynamixel XM430 and
record the finger's ADC (via the FingerBridge Uno) against carriage position.

Commands (run `python main.py <command> -h` for options):
    ports      list serial ports, to find the Dynamixel adapter and the Uno
    settings   show or save default ports, IDs and direction (settings.json)
    scan       search for the Dynamixel on every baud rate
    monitor    stream live ADC readings from the finger board (wiring check)
    jog        move the carriage a short distance (direction check)
    run        do a full test pull and plot the result
    analyze    re-plot a recorded run
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import config as C

HERE = Path(__file__).resolve().parent
SETTINGS_PATH = HERE / "settings.json"
RUNS_DIR = HERE / "runs"

SETTING_KEYS = {
    "dxl_port": str,
    "dxl_baud": int,
    "dxl_id": int,
    "bridge_port": str,
    "i2c_addr": lambda s: int(s, 0),
    "direction": int,
    "adc_vref": float,
}
SETTING_DEFAULTS = {
    "dxl_baud": C.DEFAULT_DXL_BAUD,
    "dxl_id": C.DEFAULT_DXL_ID,
    "direction": 1,
    "adc_vref": C.DEFAULT_ADC_VREF,
}


class Abort(RuntimeError):
    pass


# --- settings --------------------------------------------------------------

def load_settings() -> dict:
    s = dict(SETTING_DEFAULTS)
    if SETTINGS_PATH.exists():
        s.update(json.loads(SETTINGS_PATH.read_text()))
    return s


def resolve(args) -> dict:
    """Settings file values, overridden by any options given on the command line."""
    s = load_settings()
    for key in SETTING_KEYS:
        value = getattr(args, key, None)
        if value is not None:
            s[key] = value
    if s.get("direction") not in (1, -1):
        sys.exit("direction must be 1 or -1")
    return s


def require(s: dict, key: str, hint: str):
    if not s.get(key):
        sys.exit(f"No {key} set. {hint}")
    return s[key]


def add_common_options(p, dxl=False, bridge=False):
    if dxl:
        p.add_argument("--dxl-port", help="Dynamixel USB-RS485 adapter port, e.g. COM5")
        p.add_argument("--dxl-baud", type=int, help=f"Dynamixel baud (default {C.DEFAULT_DXL_BAUD})")
        p.add_argument("--dxl-id", type=int, help=f"Dynamixel ID (default {C.DEFAULT_DXL_ID})")
        p.add_argument("--direction", type=int, choices=[1, -1],
                       help="motor rotation sign that pulls the carriage away from the start")
    if bridge:
        p.add_argument("--bridge-port", help="FingerBridge Uno port, e.g. COM6")
        p.add_argument("--i2c-addr", type=lambda s: int(s, 0),
                       help="finger board I2C address (e.g. 0x08); auto-detected if omitted")


# --- helpers ---------------------------------------------------------------

def open_motor(s):
    from dxl import Motor

    port = require(s, "dxl_port", "Pass --dxl-port, or save one with `python main.py settings --dxl-port COM5`.")
    motor = Motor(port, s["dxl_baud"], s["dxl_id"])
    motor.open()
    try:
        model = motor.ping()
    except Exception as e:
        motor.close()
        raise Abort(f"{e}\nNo motor at ID {s['dxl_id']}, {s['dxl_baud']} baud on {port}. "
                    f"Run `python main.py scan` to find it.") from e
    if model != C.XM430_W210_MODEL_NUMBER:
        print(f"warning: motor model number is {model}, expected {C.XM430_W210_MODEL_NUMBER} (XM430-W210)")
    return motor


def open_bridge(s):
    from bridge import Bridge

    port = require(s, "bridge_port", "Pass --bridge-port, or save one with `python main.py settings --bridge-port COM6`.")
    print(f"Connecting to FingerBridge on {port} (the Uno resets on connect)...")
    br = Bridge(port).open()
    addr = s.get("i2c_addr")
    if not addr:
        found = br.scan_i2c()
        if len(found) != 1:
            br.close()
            listing = ", ".join(f"0x{a:02X}" for a in found) or "nothing"
            raise Abort(f"I2C scan found {listing}; expected exactly one finger board. "
                        f"Check wiring/pullups, or pass --i2c-addr.")
        addr = found[0]
    br.set_address(addr)
    print(f"Finger board at I2C address 0x{addr:02X}")
    return br, addr


def prepare_motor(motor, speed_mm_s, accel_mm_s2):
    if motor.ensure_extended_position_mode():
        print("Switched motor to extended position mode (multi-turn). This is saved in the motor.")
    motor.set_profile(C.speed_mm_s_to_velocity_units(speed_mm_s), C.accel_mm_s2_to_units(accel_mm_s2))


def check_speed(speed):
    if not 0 < speed <= C.MAX_SPEED_MM_S:
        sys.exit(f"speed must be between 0 and {C.MAX_SPEED_MM_S} mm/s")


# --- commands --------------------------------------------------------------

def cmd_ports(args):
    from serial.tools import list_ports

    ports = sorted(list_ports.comports(), key=lambda p: p.device)
    if not ports:
        print("No serial ports found.")
    for p in ports:
        print(f"{p.device:8} {p.description}  [{p.hwid}]")
    print("\nThe Dynamixel adapter is usually FTDI (U2D2 shows as 'USB Serial Port' / FT232H);"
          "\nthe Uno shows as 'Arduino Uno' or 'USB-SERIAL CH340' for clones.")


def cmd_settings(args):
    s = load_settings()
    changed = False
    for key, conv in SETTING_KEYS.items():
        value = getattr(args, key, None)
        if value is not None:
            s[key] = value
            changed = True
    if changed:
        SETTINGS_PATH.write_text(json.dumps(s, indent=2) + "\n")
        print(f"Saved {SETTINGS_PATH.name}")
    for key in SETTING_KEYS:
        value = s.get(key)
        if key == "i2c_addr" and value:
            value = f"0x{value:02X}"
        print(f"  {key:12} {value if value is not None else '(not set)'}")


def cmd_scan(args):
    from dxl import SCAN_BAUDS, scan

    s = resolve(args)
    port = require(s, "dxl_port", "Pass --dxl-port (see `python main.py ports`).")
    print(f"Broadcast-pinging Protocol 2.0 Dynamixels on {port}...")
    found = scan(port, SCAN_BAUDS)
    if not found:
        print("\nNothing found. Check 12 V motor power, the RS-485 A/B wiring, and the port.")
        return
    print()
    for baud, dxl_id, model in found:
        note = " (XM430-W210)" if model == C.XM430_W210_MODEL_NUMBER else ""
        print(f"Found ID {dxl_id} at {baud} baud, model {model}{note}")
    if len(found) == 1:
        baud, dxl_id, _ = found[0]
        print(f"\nSave it with: python main.py settings --dxl-port {port} --dxl-baud {baud} --dxl-id {dxl_id}")


def cmd_monitor(args):
    s = resolve(args)
    br, _ = open_bridge(s)
    try:
        br.set_rate(args.rate)
        br.start_stream()
        print("Streaming. Ctrl+C to stop.")
        last_n = 0
        last_t = time.perf_counter()
        while True:
            time.sleep(0.25)
            now = time.perf_counter()
            n = len(br.samples)
            rate = (n - last_n) / (now - last_t)
            last_n, last_t = n, now
            latest = br.samples[-1][2] if br.samples else None
            volts = f"{latest * s['adc_vref'] / C.ADC_MAX:5.3f} V" if latest is not None else "  -  "
            print(f"\rADC {latest if latest is not None else '----':>4}  {volts}  "
                  f"{rate:5.0f} Hz  errors {len(br.errors)}   ", end="", flush=True)
            if br.fatal:
                raise Abort(f"bridge connection lost: {br.fatal}")
    except KeyboardInterrupt:
        print()
    finally:
        br.close()


def cmd_jog(args):
    s = resolve(args)
    check_speed(args.speed)
    if not 0 < args.mm <= 50:
        sys.exit("jog distance must be between 0 and 50 mm")
    motor = open_motor(s)
    try:
        prepare_motor(motor, args.speed, C.DEFAULT_ACCEL_MM_S2)
        start = motor.read_state().position
        goal = start + s["direction"] * C.mm_to_ticks(args.mm)
        motor.set_goal(start)  # hold still when torque comes on, whatever the old goal was
        motor.torque(True)
        motor.set_goal(goal)
        deadline = time.monotonic() + args.mm / args.speed * 2 + 3
        while time.monotonic() < deadline:
            st = motor.read_state()
            if not st.moving and abs(st.position - goal) <= C.ARRIVAL_TOLERANCE_TICKS:
                break
            time.sleep(0.02)
        else:
            raise Abort("jog did not reach its goal in time")
        moved = (motor.read_state().position - start) * s["direction"] * C.MM_PER_TICK
        print(f"Moved {moved:.2f} mm (direction {s['direction']:+d}).")
        print("If the carriage moved TOWARD the start instead of away from it, save the other direction:\n"
              f"  python main.py settings --direction {-s['direction']}")
    finally:
        motor.torque_off_quietly()
        motor.close()


def cmd_run(args):
    import analysis

    s = resolve(args)
    check_speed(args.speed)
    if not 0 < args.travel <= C.TRAVEL_MM:
        sys.exit(f"travel must be between 0 and {C.TRAVEL_MM:g} mm (the rail's safe distance)")
    if not 1 <= args.rate <= C.MAX_SAMPLE_HZ:
        sys.exit(f"rate must be between 1 and {C.MAX_SAMPLE_HZ} Hz")

    direction = s["direction"]
    travel_ticks = C.mm_to_ticks(args.travel)

    print(f"Test pull: {args.travel:g} mm at {args.speed:g} mm/s, ADC at {args.rate} Hz"
          + (", then return to start" if args.return_ else ""))
    print("Make sure the carriage is at the START of the rail. Press Enter to go, Ctrl+C to cancel.")
    try:
        input()
    except KeyboardInterrupt:
        print("Cancelled.")
        return

    motor = open_motor(s)
    br = None
    completed = False
    try:
        br, addr = open_bridge(s)
        br.set_rate(args.rate)
        prepare_motor(motor, args.speed, args.accel)
        voltage, temperature = motor.read_supply()
        print(f"Motor supply {voltage:.1f} V, {temperature} C")

        start = motor.read_state().position
        goals = [start + direction * travel_ticks]
        if args.return_:
            goals.append(start)

        meta = {
            "started": datetime.now().isoformat(timespec="seconds"),
            "label": args.label,
            "travel_mm": args.travel,
            "speed_mm_s": args.speed,
            "accel_mm_s2": args.accel,
            "sample_hz": args.rate,
            "returned": args.return_,
            "direction": direction,
            "start_position": start,
            "mm_per_tick": C.MM_PER_TICK,
            "pulley_pitch_diameter_mm": C.PULLEY_PITCH_DIAMETER_MM,
            "adc_vref": s["adc_vref"],
            "i2c_addr": addr,
            "dxl_port": s["dxl_port"],
            "dxl_baud": s["dxl_baud"],
            "dxl_id": s["dxl_id"],
            "bridge_port": s["bridge_port"],
            "motor_supply_v": voltage,
            "motor_temperature_c": temperature,
        }

        motor_rows = []
        br.sync_burst(10)
        br.start_stream()
        motor.set_goal(start)  # hold still when torque comes on, whatever the old goal was
        motor.torque(True)

        def record(until=None, goal=None):
            """Read motor state continuously, pinging the bridge clock as we go.

            Returns when `until` (a perf_counter time) passes, or when the motor
            settles at `goal`.
            """
            next_ping = time.perf_counter()
            settled = 0
            while True:
                t0 = time.perf_counter()
                st = motor.read_state()
                t1 = time.perf_counter()
                motor_rows.append(((t0 + t1) / 2, st.position, st.velocity_raw, st.current_raw,
                                   int(st.moving), int(st.in_position)))

                if t1 >= next_ping:
                    br.ping_sync()
                    next_ping = t1 + 0.25

                carriage = (st.position - start) * direction * C.MM_PER_TICK
                if not -C.TRAVEL_OVERSHOOT_ABORT_MM <= carriage <= args.travel + C.TRAVEL_OVERSHOOT_ABORT_MM:
                    raise Abort(f"carriage reads {carriage:.1f} mm, outside the allowed travel")
                last = br.last_sample_time()
                if br.fatal:
                    raise Abort(f"bridge connection lost: {br.fatal}")
                if last is None or t1 - last > C.BRIDGE_STALL_ABORT_S:
                    if t1 - stream_started > C.BRIDGE_STALL_ABORT_S:
                        raise Abort("no ADC data from the bridge for over "
                                    f"{C.BRIDGE_STALL_ABORT_S:g} s (finger board unplugged?)")

                if until is not None and t1 >= until:
                    return
                if goal is not None:
                    arrived = not st.moving and abs(st.position - goal) <= C.ARRIVAL_TOLERANCE_TICKS
                    settled = settled + 1 if arrived else 0
                    if settled >= 3:
                        return
                    if t1 > deadline:
                        raise Abort("motor did not reach its goal in time (stalled or overloaded?)")

        stream_started = time.perf_counter()
        record(until=stream_started + C.PRE_ROLL_S)
        for i, goal in enumerate(goals):
            print("Pulling..." if i == 0 else "Returning...")
            motor.set_goal(goal)
            deadline = time.perf_counter() + args.travel / args.speed * 1.5 + 5
            record(goal=goal)
        record(until=time.perf_counter() + C.POST_ROLL_S)

        br.stop_stream()
        br.sync_burst(10)
        completed = True
    except KeyboardInterrupt:
        print("\nStopped by Ctrl+C. Torque off.")
    except Exception as e:
        print(f"\nABORTED: {e}\nTorque off.")
    finally:
        if not (completed and args.hold):
            motor.torque_off_quietly()
        motor.close()
        if br is not None:
            br.close()

    if not completed:
        sys.exit(1)

    run_name = datetime.now().strftime("%Y%m%d-%H%M%S") + (f"_{args.label}" if args.label else "")
    run_dir = RUNS_DIR / run_name
    run_dir.mkdir(parents=True)
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    analysis.write_csv(run_dir / "motor.csv",
                       ["host_t", "position", "velocity_raw", "current_raw", "moving", "in_position"], motor_rows)
    analysis.write_csv(run_dir / "adc.csv", ["host_rx", "bridge_us", "adc"], br.samples)
    analysis.write_csv(run_dir / "errors.csv", ["host_rx", "bridge_us", "code"], br.errors)
    analysis.write_csv(run_dir / "sync.csv", ["host_send", "host_recv", "bridge_us"], br.sync)
    print(f"Saved run to {run_dir}")
    if not args.hold:
        print("Torque is off; you can move the carriage back to the start.")
    analysis.analyze(run_dir, bin_mm=args.bin, show=not args.no_show)


def cmd_analyze(args):
    import analysis

    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        candidate = RUNS_DIR / args.run_dir
        if candidate.is_dir():
            run_dir = candidate
        elif args.run_dir == "latest" and RUNS_DIR.is_dir() and any(RUNS_DIR.iterdir()):
            run_dir = sorted(p for p in RUNS_DIR.iterdir() if p.is_dir())[-1]
        else:
            sys.exit(f"no run folder {args.run_dir!r}")
    analysis.analyze(run_dir, bin_mm=args.bin, show=not args.no_show)


# --- CLI -------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ports", help="list serial ports")
    p.set_defaults(func=cmd_ports)

    p = sub.add_parser("settings", help="show or save defaults to settings.json")
    add_common_options(p, dxl=True, bridge=True)
    p.add_argument("--adc-vref", type=float, help="finger board ADC reference voltage (its VDD)")
    p.set_defaults(func=cmd_settings)

    p = sub.add_parser("scan", help="find the Dynamixel's ID and baud rate")
    add_common_options(p, dxl=True)
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("monitor", help="live ADC readout from the finger board")
    add_common_options(p, bridge=True)
    p.add_argument("--rate", type=int, default=C.DEFAULT_SAMPLE_HZ, help="sample rate in Hz")
    p.set_defaults(func=cmd_monitor)

    p = sub.add_parser("jog", help="move a short distance to check direction")
    add_common_options(p, dxl=True)
    p.add_argument("--mm", type=float, default=10.0, help="distance to move (default 10, max 50)")
    p.add_argument("--speed", type=float, default=5.0, help="mm/s (default 5)")
    p.set_defaults(func=cmd_jog)

    p = sub.add_parser("run", help="full test pull, then plot")
    add_common_options(p, dxl=True, bridge=True)
    p.add_argument("--travel", type=float, default=C.TRAVEL_MM, help=f"mm to pull (default and max {C.TRAVEL_MM:g})")
    p.add_argument("--speed", type=float, default=C.DEFAULT_SPEED_MM_S, help=f"mm/s (default {C.DEFAULT_SPEED_MM_S:g})")
    p.add_argument("--accel", type=float, default=C.DEFAULT_ACCEL_MM_S2, help=f"mm/s^2 (default {C.DEFAULT_ACCEL_MM_S2:g})")
    p.add_argument("--rate", type=int, default=C.DEFAULT_SAMPLE_HZ, help=f"ADC sample rate in Hz (default {C.DEFAULT_SAMPLE_HZ})")
    p.add_argument("--label", help="short name appended to the run folder")
    p.add_argument("--return", dest="return_", action="store_true",
                   help="drive back to the start afterwards (records a reverse pass for hysteresis)")
    p.add_argument("--hold", action="store_true", help="leave torque on at the end")
    p.add_argument("--bin", type=float, default=1.0, help="position bin width for averaging, mm (default 1)")
    p.add_argument("--no-show", action="store_true", help="save plots without opening windows")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("analyze", help="re-plot a recorded run")
    p.add_argument("run_dir", help="run folder path, its name under runs/, or 'latest'")
    p.add_argument("--bin", type=float, default=1.0, help="position bin width for averaging, mm (default 1)")
    p.add_argument("--no-show", action="store_true", help="save plots without opening windows")
    p.set_defaults(func=cmd_analyze)

    return parser


def main():
    from serial import SerialException

    from bridge import BridgeError
    from dxl import DynamixelError

    args = build_parser().parse_args()
    try:
        args.func(args)
    except (Abort, BridgeError, DynamixelError, SerialException) as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
