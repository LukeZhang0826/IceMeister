// FingerBridge: Arduino Uno sketch that polls one FingerBoard over I2C and
// streams timestamped ADC readings to the PC over USB serial (115200 baud).
//
// Wiring (Uno and FingerBoard both on 5 V for testing):
//   Uno A4 (SDA) -> FingerBoard PB1 (SDA)
//   Uno A5 (SCL) -> FingerBoard PB0 (SCL)
//   Uno 5V / GND -> FingerBoard VDD / GND
//   4.7k pullups from SDA and SCL to 5 V (the Uno's internal pullups are weak).
//
// Protocol: ASCII lines terminated by '\n'.
//   PC -> bridge                bridge -> PC
//   ?                           V,FingerBridge,1
//   S   (scan I2C bus)          F,<addr> per device found, then F,END
//   A,<addr>  (decimal)         OK,A,<addr>       | ERR,NOACK,<addr>
//   R,<hz>    (1..1000)         OK,R,<hz>         | ERR,RATE
//   G   (start streaming)       OK,G              | ERR,NOADDR
//   X   (stop streaming)        OK,X
//   T,<seq>   (time sync)       T,<seq>,<micros at receipt>
// While streaming:
//   D,<micros>,<adc>            one sample; micros taken just before the I2C read
//   E,<micros>,<code>           failed read: 1 = short read/NACK, 2 = value > 1023, 3 = bus timeout
//
// micros() wraps every ~71.6 minutes; the PC side unwraps it.

#include <Wire.h>

const unsigned long SERIAL_BAUD = 115200;
const uint32_t I2C_CLOCK_HZ = 100000;
const uint16_t DEFAULT_RATE_HZ = 200;
const uint16_t MAX_RATE_HZ = 1000;

static uint8_t targetAddr = 0;  // 0 = not set
static bool streaming = false;
static uint32_t periodUs = 1000000UL / DEFAULT_RATE_HZ;
static uint32_t nextSampleUs = 0;

static char cmdBuf[24];
static uint8_t cmdLen = 0;
static bool cmdOverflow = false;

static bool probe(uint8_t addr) {
  Wire.beginTransmission(addr);
  return Wire.endTransmission() == 0;
}

// Returns 0..1023 on success, or -(error code).
static int16_t readAdc(uint8_t addr) {
#if defined(WIRE_HAS_TIMEOUT)
  Wire.clearWireTimeoutFlag();
#endif
  uint8_t n = Wire.requestFrom(addr, (uint8_t)2);
#if defined(WIRE_HAS_TIMEOUT)
  if (Wire.getWireTimeoutFlag()) {
    while (Wire.available()) Wire.read();
    return -3;
  }
#endif
  if (n != 2) {
    while (Wire.available()) Wire.read();
    return -1;
  }
  uint8_t lo = Wire.read();
  uint8_t hi = Wire.read();
  uint16_t value = (uint16_t)lo | ((uint16_t)hi << 8);
  if (value > 1023) return -2;
  return (int16_t)value;
}

static void sample() {
  uint32_t t = micros();
  int16_t v = readAdc(targetAddr);
  Serial.print(v >= 0 ? F("D,") : F("E,"));
  Serial.print(t);
  Serial.print(',');
  Serial.println(v >= 0 ? v : -v);
}

static void handleCommand(char *cmd, uint32_t rxMicros) {
  char op = cmd[0];
  const char *arg = (cmd[1] == ',') ? cmd + 2 : "";

  switch (op) {
    case '?':
      Serial.println(F("V,FingerBridge,1"));
      break;

    case 'T':
      Serial.print(F("T,"));
      Serial.print(arg);
      Serial.print(',');
      Serial.println(rxMicros);
      break;

    case 'S': {
      bool wasStreaming = streaming;
      streaming = false;
      for (uint8_t addr = 0x08; addr < 0x78; addr++) {
        if (probe(addr)) {
          Serial.print(F("F,"));
          Serial.println(addr);
        }
      }
      Serial.println(F("F,END"));
      streaming = wasStreaming;
      nextSampleUs = micros();
      break;
    }

    case 'A': {
      long addr = atol(arg);
      if (addr < 0x08 || addr > 0x77 || !probe((uint8_t)addr)) {
        Serial.print(F("ERR,NOACK,"));
        Serial.println(addr);
      } else {
        targetAddr = (uint8_t)addr;
        Serial.print(F("OK,A,"));
        Serial.println(addr);
      }
      break;
    }

    case 'R': {
      long hz = atol(arg);
      if (hz < 1 || hz > MAX_RATE_HZ) {
        Serial.println(F("ERR,RATE"));
      } else {
        periodUs = 1000000UL / (uint32_t)hz;
        Serial.print(F("OK,R,"));
        Serial.println(hz);
      }
      break;
    }

    case 'G':
      if (targetAddr == 0) {
        Serial.println(F("ERR,NOADDR"));
      } else {
        streaming = true;
        nextSampleUs = micros();
        Serial.println(F("OK,G"));
      }
      break;

    case 'X':
      streaming = false;
      Serial.println(F("OK,X"));
      break;

    default:
      Serial.println(F("ERR,UNKNOWN"));
      break;
  }
}

static void pollSerial() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      uint32_t rxMicros = micros();
      cmdBuf[cmdLen] = '\0';
      if (cmdLen > 0 && !cmdOverflow) handleCommand(cmdBuf, rxMicros);
      if (cmdOverflow) Serial.println(F("ERR,LONG"));
      cmdLen = 0;
      cmdOverflow = false;
    } else if (cmdLen < sizeof(cmdBuf) - 1) {
      cmdBuf[cmdLen++] = c;
    } else {
      cmdOverflow = true;
    }
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  Wire.begin();
  Wire.setClock(I2C_CLOCK_HZ);
#if defined(WIRE_HAS_TIMEOUT)
  Wire.setWireTimeout(3000 /* us */, true /* reset bus on timeout */);
#endif
  Serial.println(F("# FingerBridge ready"));
}

void loop() {
  pollSerial();

  if (streaming) {
    uint32_t now = micros();
    if ((int32_t)(now - nextSampleUs) >= 0) {
      nextSampleUs += periodUs;
      // If we fell far behind (e.g. a slow scan), resynchronise instead of bursting.
      if ((int32_t)(now - nextSampleUs) > (int32_t)(4 * periodUs)) nextSampleUs = now + periodUs;
      sample();
    }
  }
}
