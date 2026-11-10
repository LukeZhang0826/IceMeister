# Finger Tester

Pulls a finger board along the linear rail with a Dynamixel XM430-W210-R and records the finger's ADC reading against carriage position, then plots ADC vs position, sensitivity (counts/mm), and motor current.

```
PC ──USB── RS-485 adapter ──── XM430-W210-R ── 27 mm pulley ── belt ── carriage
PC ──USB── Arduino Uno (FingerBridge) ──I2C── finger board (on the carriage)
```

The Uno polls the finger board over I2C, timestamps each reading with its own clock, and streams it to the PC. The PC timestamps the motor position reads and keeps pinging the Uno's clock during the run, so the two streams can be lined up afterwards. The Uno's resonator drift (up to ~0.5%) is corrected automatically.

## Hardware setup

- **Motor:** 12 V supply, RS-485 adapter (e.g. U2D2) to the PC.
- **Bridge:** Arduino Uno and finger board both on 5 V. Wire Uno A4 to finger PB1 (SDA), Uno A5 to finger PB0 (SCL), and share 5 V and GND. Add 4.7 kΩ pullups from SDA and SCL to 5 V.
- Flash [`FingerBridge/FingerBridge.ino`](FingerBridge/FingerBridge.ino) to the Uno with the Arduino IDE.

**Windows:** the FTDI driver's default 16 ms latency timer slows motor reads. Set it to 1 ms in Device Manager → the adapter's COM port → Port Settings → Advanced → Latency Timer.

## Software setup

Needs Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## First-time setup

```powershell
python main.py ports                                  # find the COM ports
python main.py scan --dxl-port COM5                   # find the motor's ID and baud rate
python main.py settings --dxl-port COM5 --dxl-baud 57600 --dxl-id 1 --bridge-port COM6
python main.py monitor                                # live ADC; move the finger to check wiring
python main.py jog                                    # moves 10 mm; check it goes AWAY from the start
```

If `jog` moves the carriage toward the start, run `python main.py settings --direction -1`.

The first time the motor is used, the script switches it to extended position (multi-turn) mode. 300 mm of travel is about 3.5 turns of the 27 mm pulley. The mode is saved in the motor's EEPROM.

## Running a test

1. Put the carriage at the start of the rail.
2. Run `python main.py run --label something` and press Enter when prompted.

The motor pulls the carriage 300 mm at 10 mm/s, then turns torque off so you can push it back. Useful options:

| Option | Effect |
| :--- | :--- |
| `--speed 20` | mm/s (max 50) |
| `--travel 150` | pull a shorter distance (max 300) |
| `--rate 500` | ADC samples per second (max 1000) |
| `--return` | drive back to the start afterwards, recording a reverse pass to show hysteresis |
| `--hold` | keep torque on at the end |
| `--bin 0.5` | position bin width (mm) for the averaged curve |

Press Ctrl+C at any time to turn torque off and stop. The run also aborts with torque off if:

- the Uno stops sending data for over 1 s
- the motor reports a hardware error
- the carriage reads outside the allowed travel
- the move takes much longer than expected

## Output

Each run is saved in `runs/<date-time>_<label>/`:

| File | Contents |
| :--- | :--- |
| `adc_vs_position.png` | ADC vs position (raw points, 1 mm bin mean ± std), dADC/dx, motor current |
| `time_domain.png` | ADC and position over time, plus sample gaps, to spot dropouts |
| `merged.csv` | one row per ADC sample: time, carriage mm, ADC, speed, motor current |
| `motor.csv`, `adc.csv`, `sync.csv`, `errors.csv`, `meta.json` | raw recordings |

A summary is printed too, covering sample rates, clock drift, stationary noise, and a linear fit with its maximum deviation.

The plot windows are interactive, and the position plots share an x axis, so zooming one zooms all three. To re-plot a run later:

```powershell
python main.py analyze latest
python main.py analyze 20261109-153000_something --bin 0.5
```

## Assumptions

Constants are in [`config.py`](config.py):

- **Pulley pitch diameter:** 27 mm, giving 84.82 mm of belt per revolution and about 0.0207 mm per encoder tick. If measured travel doesn't match 300 mm, correct `PULLEY_PITCH_DIAMETER_MM`.
- **ADC reference:** 5 V, because the finger board runs at 5 V for these tests. Change it with `settings --adc-vref`.
- **Finger board protocol:** a 2-byte I2C read, low byte first, value 0-1023. This matches `firmware/FingerBoards`.
