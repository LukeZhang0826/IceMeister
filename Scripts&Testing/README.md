# Scripts & Testing

Scripts for exercising and testing IceMeister hardware: bench tests, sensor and actuator checks, and other one-off or repeatable procedures run against real boards and the vehicle.

> These scripts can drive hardware. Run them only with the motors disconnected or the vehicle safely restrained, and keep the physical e-stop within reach.

## Contents

Add scripts here as they are written, and list them below so the folder is easy to scan.

| Script | Target | Purpose |
| :--- | :--- | :--- |
| _none yet_ | | |

## Conventions

- One script per test or procedure. Name files for what they test, for example `finger_board_serial_loopback.py`.
- Put a short header comment at the top of each script: what it tests, which hardware it expects, and how to run it.
- Scripts should exit with a non-zero status on failure so results can be checked by hand or in CI later.
- Do not commit credentials, serial port paths for a specific machine, or captured data files. Use arguments or environment variables for those.
