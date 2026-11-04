# FingerBoards

ATtiny404 peripheral board. Reads a potentiometer and serves the value to an I2C master.

**Status:** in development.

**Stack:** C++ with direct register access, on the Arduino framework (megaTinyCore). Runs at 10 MHz (20 MHz oscillator divided by 2), since 20 MHz is out of spec at 3.3 V.

Responsibilities:

- Sample the potentiometer continuously with the 10-bit ADC
- Respond as an I2C target at an address set by the board's strap pins
- Print debug output over serial at 9600 baud, which will be removed for prod

This board only reports a sensor value and drives no actuators, so it has no outputs to stop if commands stop arriving.

## Pins

| Pin | Use |
| :--- | :--- |
| PA0 | UPDI (flashing) |
| PA1 | Potentiometer input (AIN1) |
| PA2-PA7 | I2C address straps |
| PB0 | I2C SCL |
| PB1 | I2C SDA |
| PB2 | Serial TX / Red LED output|
| PB3 | Green LED output |

## I2C

The address is `0x08` plus the value of the straps, read once at startup. The straps use internal pullups, so tying a pin to ground sets its bit. PA7 is bit 0 and PA2 is bit 5, giving a range of `0x08` to `0x47`.

A read returns 2 bytes, low byte first, holding the latest ADC value (0-1023). Any further bytes read as `0xFF`. Writes are acknowledged and discarded.

The firmware does not enable pullups on SDA or SCL, so the bus needs external ones.

## Building

See [`firmware/README.md`](../README.md#building) for PlatformIO setup.

```bash
pio run                # build
pio run -t upload      # flash over SerialUPDI
pio device monitor     # serial output, 9600 baud
```

Flashing uses a USB-serial adapter wired for SerialUPDI to PA0. `upload_port` in `platformio.ini` is `/dev/ttyUSB1`. If your adapter is on a different port, override it:

```bash
pio run -t upload --upload-port /dev/ttyUSB0
```

Not part of the pnpm workspace.
