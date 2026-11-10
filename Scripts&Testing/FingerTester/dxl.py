"""Minimal Dynamixel XM430 (Protocol 2.0) driver for the finger tester."""

from dataclasses import dataclass

from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler

# Control table addresses (XM430-W210, Protocol 2.0)
ADDR_OPERATING_MODE = 11
ADDR_TORQUE_ENABLE = 64
ADDR_HARDWARE_ERROR_STATUS = 70
ADDR_PROFILE_ACCELERATION = 108
ADDR_PROFILE_VELOCITY = 112
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_INPUT_VOLTAGE = 144
ADDR_PRESENT_TEMPERATURE = 146

# One read from 122 covers: Moving(122) Moving Status(123) PWM(124,2)
# Current(126,2) Velocity(128,4) Position(132,4).
ADDR_STATE_BLOCK = 122
STATE_BLOCK_LEN = 14

EXTENDED_POSITION_MODE = 4
ERRBIT_ALERT = 0x80

SCAN_BAUDS = [57600, 1_000_000, 115200, 9600, 2_000_000, 3_000_000, 4_000_000, 4_500_000]

HARDWARE_ERROR_BITS = {
    0: "input voltage error",
    2: "overheating",
    3: "motor encoder error",
    4: "electrical shock",
    5: "overload",
}


class DynamixelError(RuntimeError):
    pass


@dataclass
class MotorState:
    moving: bool
    in_position: bool
    current_raw: int
    velocity_raw: int
    position: int


def _signed(value: int, bits: int) -> int:
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def _le(data, start: int, length: int) -> int:
    return int.from_bytes(bytes(data[start:start + length]), "little")


class Motor:
    def __init__(self, port_name: str, baud: int, dxl_id: int):
        self.port_name = port_name
        self.baud = baud
        self.id = dxl_id
        self.port = PortHandler(port_name)
        self.packet = PacketHandler(2.0)

    def open(self):
        try:
            opened = self.port.openPort()
        except Exception as e:  # pyserial raises SerialException for a missing/busy port
            raise DynamixelError(f"could not open {self.port_name}: {e}") from e
        if not opened:
            raise DynamixelError(f"could not open {self.port_name}")
        if not self.port.setBaudRate(self.baud):
            self.port.closePort()
            raise DynamixelError(f"could not set {self.port_name} to {self.baud} baud")

    def close(self):
        self.port.closePort()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()

    # --- low level ---

    def _check(self, result, error, what: str):
        if result != COMM_SUCCESS:
            raise DynamixelError(f"{what}: {self.packet.getTxRxResult(result)}")
        if error & ~ERRBIT_ALERT:
            raise DynamixelError(f"{what}: {self.packet.getRxPacketError(error)}")
        if error & ERRBIT_ALERT:
            raise DynamixelError(f"{what}: motor reports a hardware error ({self.hardware_error_text()})")

    def _read1(self, addr: int, what: str) -> int:
        value, result, error = self.packet.read1ByteTxRx(self.port, self.id, addr)
        self._check(result, error, what)
        return value

    def _write1(self, addr: int, value: int, what: str):
        result, error = self.packet.write1ByteTxRx(self.port, self.id, addr, value)
        self._check(result, error, what)

    def _write4(self, addr: int, value: int, what: str):
        result, error = self.packet.write4ByteTxRx(self.port, self.id, addr, value & 0xFFFFFFFF)
        self._check(result, error, what)

    # --- operations ---

    def ping(self) -> int:
        model, result, error = self.packet.ping(self.port, self.id)
        self._check(result, error, f"ping ID {self.id}")
        return model

    def hardware_error_text(self) -> str:
        """Read Hardware Error Status without raising on the alert bit."""
        value, result, _ = self.packet.read1ByteTxRx(self.port, self.id, ADDR_HARDWARE_ERROR_STATUS)
        if result != COMM_SUCCESS:
            return "could not read hardware error status"
        names = [name for bit, name in HARDWARE_ERROR_BITS.items() if value & (1 << bit)]
        return ", ".join(names) if names else "none"

    def torque(self, enable: bool):
        self._write1(ADDR_TORQUE_ENABLE, 1 if enable else 0, "set torque")

    def torque_off_quietly(self):
        """Best-effort torque off for abort paths; never raises."""
        try:
            self.packet.write1ByteTxRx(self.port, self.id, ADDR_TORQUE_ENABLE, 0)
        except Exception:
            pass

    def ensure_extended_position_mode(self) -> bool:
        """Switch to extended (multi-turn) position mode. Returns True if it changed.

        Operating Mode lives in EEPROM, so it is only written when it differs.
        """
        mode = self._read1(ADDR_OPERATING_MODE, "read operating mode")
        if mode == EXTENDED_POSITION_MODE:
            return False
        self.torque(False)
        self._write1(ADDR_OPERATING_MODE, EXTENDED_POSITION_MODE, "set operating mode")
        return True

    def set_profile(self, velocity_units: int, accel_units: int):
        self._write4(ADDR_PROFILE_ACCELERATION, accel_units, "set profile acceleration")
        self._write4(ADDR_PROFILE_VELOCITY, velocity_units, "set profile velocity")

    def set_goal(self, position: int):
        self._write4(ADDR_GOAL_POSITION, position, "set goal position")

    def read_state(self) -> MotorState:
        data, result, error = self.packet.readTxRx(self.port, self.id, ADDR_STATE_BLOCK, STATE_BLOCK_LEN)
        self._check(result, error, "read state")
        return MotorState(
            moving=bool(data[0]),
            in_position=bool(data[1] & 0x01),
            current_raw=_signed(_le(data, 4, 2), 16),
            velocity_raw=_signed(_le(data, 6, 4), 32),
            position=_signed(_le(data, 10, 4), 32),
        )

    def read_supply(self) -> tuple[float, int]:
        """Return (input voltage in V, temperature in C)."""
        value, result, error = self.packet.read2ByteTxRx(self.port, self.id, ADDR_PRESENT_INPUT_VOLTAGE)
        self._check(result, error, "read input voltage")
        temp = self._read1(ADDR_PRESENT_TEMPERATURE, "read temperature")
        return value / 10.0, temp


def scan(port_name: str, bauds=SCAN_BAUDS, progress=print) -> list[tuple[int, int, int]]:
    """Broadcast-ping at each baud rate. Returns [(baud, id, model_number)]."""
    port = PortHandler(port_name)
    packet = PacketHandler(2.0)
    try:
        opened = port.openPort()
    except Exception as e:
        raise DynamixelError(f"could not open {port_name}: {e}") from e
    if not opened:
        raise DynamixelError(f"could not open {port_name}")
    found = []
    try:
        for baud in bauds:
            if not port.setBaudRate(baud):
                progress(f"  {baud:>9} baud: not supported by this adapter, skipped")
                continue
            port.clearPort()
            data, _ = packet.broadcastPing(port)
            ids = sorted(data.items())
            progress(f"  {baud:>9} baud: " + (", ".join(f"ID {i} (model {m[0]})" for i, m in ids) or "nothing"))
            found.extend((baud, i, m[0]) for i, m in ids)
    finally:
        port.closePort()
    return found
