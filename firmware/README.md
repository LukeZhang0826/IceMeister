# firmware

Embedded code that runs on the zamboni's onboard microcontroller —
motor drive, sensor I/O, low-level safety interlocks.

**Status:** placeholder. Target hardware and language not yet chosen.

**Likely candidates:**
- ESP32 / RP2040 / STM32 / Teensy
- C or C++ (PlatformIO, esp-idf)
- Rust embedded (`embassy`, `cargo-embed`)

Not part of the pnpm workspace. Will build with its own toolchain.
