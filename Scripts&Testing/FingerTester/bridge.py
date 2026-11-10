"""PC side of the FingerBridge serial protocol (see FingerBridge/FingerBridge.ino).

The bridge timestamps every ADC sample with its own micros() clock. To line
those samples up with motor positions (timed by the PC), the PC sends time-sync
pings ("T,<seq>") and records when each was sent and when the reply carrying the
bridge's clock came back. analysis.fit_clock() turns those into a mapping from
bridge time to PC time.
"""

import queue
import threading
import time

import serial

from config import BRIDGE_BAUD


class BridgeError(RuntimeError):
    pass


class Bridge:
    def __init__(self, port_name: str, baud: int = BRIDGE_BAUD):
        self.port_name = port_name
        self.baud = baud
        self.ser = None

        # (host_rx_s, bridge_us, adc)
        self.samples: list[tuple[float, int, int]] = []
        # (host_rx_s, bridge_us, code)
        self.errors: list[tuple[float, int, int]] = []
        # (host_send_s, host_recv_s, bridge_us)
        self.sync: list[tuple[float, float, int]] = []

        self._replies: queue.Queue[str] = queue.Queue()
        self._pending: dict[int, float] = {}
        self._lock = threading.Lock()
        self._seq = 0
        self._wrap = 0
        self._last_raw = None
        self._stop = threading.Event()
        self._thread = None
        self.fatal: Exception | None = None

    # --- lifecycle ---

    def open(self, boot_timeout: float = 4.0):
        try:
            self.ser = serial.Serial(self.port_name, self.baud, timeout=0.05)
        except serial.SerialException as e:
            raise BridgeError(f"could not open {self.port_name}: {e}") from e
        self._thread = threading.Thread(target=self._reader, name="bridge-reader", daemon=True)
        self._thread.start()
        # Opening the port resets an Uno; it takes ~1.5 s to boot. Ping until it answers.
        deadline = time.monotonic() + boot_timeout
        while time.monotonic() < deadline:
            try:
                reply = self.command("?", "V,", timeout=0.5)
            except BridgeError:
                continue
            if not reply.startswith("V,FingerBridge"):
                raise BridgeError(f"unexpected device on {self.port_name}: {reply!r}")
            self.version = reply
            return self
        self.close()
        raise BridgeError(f"no FingerBridge answered on {self.port_name} (is the sketch flashed?)")

    def close(self):
        self._stop.set()
        if self.ser is not None:
            try:
                self.ser.write(b"X\n")
            except serial.SerialException:
                pass
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        if self.ser is not None:
            self.ser.close()

    def __enter__(self):
        return self.open()

    def __exit__(self, *exc):
        self.close()

    # --- reader thread ---

    def _unwrap(self, raw: int) -> int:
        # micros() on the Uno wraps every ~71.6 minutes.
        if self._last_raw is not None and raw < self._last_raw and self._last_raw - raw > 2**31:
            self._wrap += 2**32
        self._last_raw = raw
        return raw + self._wrap

    def _reader(self):
        buf = b""
        while not self._stop.is_set():
            try:
                chunk = self.ser.read(self.ser.in_waiting or 1)
            except serial.SerialException as e:
                self.fatal = e
                return
            if not chunk:
                continue
            now = time.perf_counter()
            buf += chunk
            while b"\n" in buf:
                raw_line, buf = buf.split(b"\n", 1)
                self._handle(raw_line.decode("ascii", "replace").strip(), now)

    def _handle(self, line: str, now: float):
        if not line:
            return
        parts = line.split(",")
        try:
            if parts[0] == "D" and len(parts) == 3:
                self.samples.append((now, self._unwrap(int(parts[1])), int(parts[2])))
                return
            if parts[0] == "E" and len(parts) == 3:
                self.errors.append((now, self._unwrap(int(parts[1])), int(parts[2])))
                return
            if parts[0] == "T" and len(parts) == 3:
                seq, bridge_us = int(parts[1]), self._unwrap(int(parts[2]))
                with self._lock:
                    sent = self._pending.pop(seq, None)
                if sent is not None:
                    self.sync.append((sent, now, bridge_us))
                return
        except ValueError:
            pass  # malformed line (e.g. partial line right after reset): fall through as text
        self._replies.put(line)

    # --- commands ---

    def _write(self, text: str):
        if self.fatal:
            raise BridgeError(f"bridge connection lost: {self.fatal}")
        self.ser.write((text + "\n").encode("ascii"))

    def command(self, text: str, expect_prefix: str, timeout: float = 2.0) -> str:
        while not self._replies.empty():
            self._replies.get_nowait()
        self._write(text)
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise BridgeError(f"no reply to {text!r}")
            try:
                line = self._replies.get(timeout=remaining)
            except queue.Empty:
                continue
            if line.startswith(expect_prefix):
                return line
            if line.startswith("ERR"):
                raise BridgeError(f"bridge rejected {text!r}: {line}")
            # anything else (e.g. "# ..." info lines) is ignored

    def scan_i2c(self) -> list[int]:
        while not self._replies.empty():
            self._replies.get_nowait()
        self._write("S")
        found = []
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            try:
                line = self._replies.get(timeout=0.2)
            except queue.Empty:
                continue
            if line == "F,END":
                return found
            if line.startswith("F,"):
                found.append(int(line[2:]))
        raise BridgeError("I2C scan did not finish")

    def set_address(self, addr: int):
        self.command(f"A,{addr}", "OK,A")

    def set_rate(self, hz: int):
        self.command(f"R,{hz}", "OK,R")

    def start_stream(self):
        self.command("G", "OK,G")

    def stop_stream(self):
        self.command("X", "OK,X")

    def ping_sync(self):
        """Send one time-sync ping; the reply is recorded by the reader thread."""
        self._seq += 1
        with self._lock:
            self._pending[self._seq] = time.perf_counter()
        self._write(f"T,{self._seq}")

    def sync_burst(self, count: int = 20, gap: float = 0.02):
        for _ in range(count):
            self.ping_sync()
            time.sleep(gap)
        time.sleep(0.1)  # let the last replies arrive

    def last_sample_time(self) -> float | None:
        return self.samples[-1][0] if self.samples else None
