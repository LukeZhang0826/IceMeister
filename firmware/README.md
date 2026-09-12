# firmware

Embedded code that runs on IceMeister's onboard chips.

**Status:** placeholder. Target hardware not yet chosen.

## Main microcontroller

**Stack:** C++ on FreeRTOS.

- Real-time control loops
- Receives motion commands from `controller` and drives the peripheral chips
- Owns vehicle safety: if heartbeats from `controller` stop arriving, it brings the motors to a stop

## Peripheral chips

**Stack:** bare-metal C.

- Motor drive, sensor I/O, and other low-level hardware tasks
- Each chip stops its outputs if commands from the main microcontroller stop arriving

A physical e-stop cuts motor power through a relay, independent of all firmware.

Not part of the pnpm workspace. Will build with its own toolchain.
