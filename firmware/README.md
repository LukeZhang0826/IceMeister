# firmware

Embedded code that runs on IceMeister's onboard chips.

**Status:** main microcontroller hardware not yet chosen. [`FingerBoards/`](FingerBoards/README.md) is the first peripheral board.

## Finger Controller Board

**Stack:** C++ on FreeRTOS.

- Real-time control loops

## Finger Board

**Stack:** C++ on Arduino, Register level I2C implementation

- Sensor I/O for ice surface detection
- Each chip stops its outputs if commands from the main microcontroller stop arriving
- Each chip is an I2C slave to the finger controller board, responding with raw sensor data. 

## Motor Controller Board and others to be developed

- Receives motion commands from `controller` and drives the peripheral chips
- Owns vehicle safety: if heartbeats from `controller` stop arriving, it brings the motors to a stop
- Motor drive,
- A physical e-stop cuts motor power through a relay, independent of all firmware.

## Building

Not part of the pnpm workspace. Projects here build with [PlatformIO](https://platformio.org/).

Install PlatformIO with `pipx install platformio`, or use the PlatformIO IDE extension for VS Code. The toolchain and board packages download on the first build.

Run `pio` commands from the project's folder, the one holding `platformio.ini`:

```bash
cd firmware/FingerBoards
pio run
```
