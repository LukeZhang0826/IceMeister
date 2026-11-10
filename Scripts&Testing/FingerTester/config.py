"""Physical constants and defaults for the finger tester rig.

The rig: a Dynamixel XM430-W210-R drives a belt through a pulley, pulling the
finger board along a linear rail. An Arduino Uno (FingerBridge sketch) polls the
finger board over I2C and streams timestamped ADC readings to the PC.
"""

import math

# --- Mechanics -------------------------------------------------------------

PULLEY_PITCH_DIAMETER_MM = 27.0
MM_PER_REV = math.pi * PULLEY_PITCH_DIAMETER_MM  # 84.82 mm of belt per output revolution

# Carriage travel per run. The carriage is moved back to the start by hand before
# every run, and the rail is clear for this distance from there.
TRAVEL_MM = 300.0

# Abort if the carriage ends up this far outside [0, travel] (encoder sanity check).
TRAVEL_OVERSHOOT_ABORT_MM = 5.0

# --- Dynamixel XM430-W210-R, Protocol 2.0 ----------------------------------

TICKS_PER_REV = 4096
MM_PER_TICK = MM_PER_REV / TICKS_PER_REV  # ~0.0207 mm
VELOCITY_UNIT_RPM = 0.229
ACCEL_UNIT_REV_PER_MIN2 = 214.577
CURRENT_UNIT_MA = 2.69
XM430_W210_MODEL_NUMBER = 1030

DEFAULT_DXL_BAUD = 57600
DEFAULT_DXL_ID = 1

DEFAULT_SPEED_MM_S = 10.0
MAX_SPEED_MM_S = 50.0
DEFAULT_ACCEL_MM_S2 = 20.0

# Treat the move as finished once the motor reports in-position within this many ticks.
ARRIVAL_TOLERANCE_TICKS = 25  # ~0.5 mm

# --- FingerBridge (Arduino Uno over USB serial) ----------------------------

BRIDGE_BAUD = 115200
DEFAULT_SAMPLE_HZ = 200
MAX_SAMPLE_HZ = 1000

# Abort the run if no ADC sample arrives for this long while the motor is moving.
BRIDGE_STALL_ABORT_S = 1.0

# Seconds of stationary recording before and after the move (noise baseline).
PRE_ROLL_S = 0.5
POST_ROLL_S = 0.5

# --- Finger board ADC ------------------------------------------------------

ADC_MAX = 1023
DEFAULT_ADC_VREF = 5.0  # finger board ADC reference is VDD; boards run at 5 V for these tests


def mm_to_ticks(mm: float) -> int:
    return round(mm / MM_PER_TICK)


def speed_mm_s_to_velocity_units(speed_mm_s: float) -> int:
    rpm = speed_mm_s / MM_PER_REV * 60.0
    return max(1, round(rpm / VELOCITY_UNIT_RPM))


def accel_mm_s2_to_units(accel_mm_s2: float) -> int:
    rev_per_min2 = accel_mm_s2 / MM_PER_REV * 3600.0
    return max(1, round(rev_per_min2 / ACCEL_UNIT_REV_PER_MIN2))


def velocity_units_to_mm_s(units: float) -> float:
    return units * VELOCITY_UNIT_RPM / 60.0 * MM_PER_REV
