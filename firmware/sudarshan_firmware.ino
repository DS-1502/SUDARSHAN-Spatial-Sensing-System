#include <Wire.h>
#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>
#include <RCSwitch.h>

// ---------- Settings ----------
const int MPU_ADDR    = 0x68;   // use 0x69 if your scanner found 0x69
const int GPS_RX_PIN  = 4;      // Arduino receives here (GPS TX goes here)
const int GPS_TX_PIN  = 3;      // Arduino transmits here (GPS RX goes here)
const unsigned long PRINT_INTERVAL = 1000;   // ms between MPU and GPS prints

// ---------- Objects ----------
SoftwareSerial gpsSerial(GPS_RX_PIN, GPS_TX_PIN);
TinyGPSPlus gps;
RCSwitch rf = RCSwitch();

bool mpuOK = false;
unsigned long lastMpuPrint = 0;
unsigned long lastGpsPrint = 0;

// ---------- MPU-6050 helpers ----------
bool mpuInit() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0x80);                         // reset
  if (Wire.endTransmission(true) != 0) return false;
  delay(100);

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0x01);                         // wake up
  if (Wire.endTransmission(true) != 0) return false;
  delay(100);
  return true;
}

void readMPU() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  byte err = Wire.endTransmission(false);
  byte got = Wire.requestFrom(MPU_ADDR, 14);

  if (err != 0 || got != 14) {
    Serial.println("[MPU6050] READ FAILED - check wiring");
    return;
  }

  int16_t ax = (Wire.read() << 8) | Wire.read();
  int16_t ay = (Wire.read() << 8) | Wire.read();
  int16_t az = (Wire.read() << 8) | Wire.read();
  int16_t t  = (Wire.read() << 8) | Wire.read();
  int16_t gx = (Wire.read() << 8) | Wire.read();
  int16_t gy = (Wire.read() << 8) | Wire.read();
  int16_t gz = (Wire.read() << 8) | Wire.read();

  Serial.print("[MPU6050] Accel(g): ");
  Serial.print(ax / 16384.0, 2); Serial.print(", ");
  Serial.print(ay / 16384.0, 2); Serial.print(", ");
  Serial.print(az / 16384.0, 2);
  Serial.print(" | Gyro(deg/s): ");
  Serial.print(gx / 131.0, 1); Serial.print(", ");
  Serial.print(gy / 131.0, 1); Serial.print(", ");
  Serial.println(gz / 131.0, 1);

  Serial.print("[TEMP   ] MPU chip temperature: ");
  Serial.print(t / 340.0 + 36.53, 1);
  Serial.println(" C");
}

// ---------- Setup ----------
void setup() {
  Serial.begin(9600);
  Wire.begin();
  gpsSerial.begin(9600);
  rf.enableReceive(0);                      // interrupt 0 = pin D2

  Serial.println("=== Multi-sensor test starting ===");

  mpuOK = mpuInit();
  Serial.println(mpuOK ? "[MPU6050] Found and awake"
                       : "[MPU6050] NOT FOUND - check wiring/address");
  Serial.println("[GPS    ] Listening (needs open sky for a fix)");
  Serial.println("[RF433  ] Waiting for signals (press a remote button)");
  Serial.println("==================================");
}

// ---------- Main loop ----------
void loop() {
  // Keep feeding the GPS parser constantly
  while (gpsSerial.available()) {
    gps.encode(gpsSerial.read());
  }

  // 433 MHz receiver: print whenever a code arrives
  if (rf.available()) {
    Serial.print("[RF433  ] Value: ");
    Serial.print(rf.getReceivedValue());
    Serial.print(" | Bits: ");
    Serial.print(rf.getReceivedBitlength());
    Serial.print(" | Protocol: ");
    Serial.print(rf.getReceivedProtocol());
    Serial.print(" | Pulse: ");
    Serial.println(rf.getReceivedDelay());
    rf.resetAvailable();
  }

  // MPU-6050 and temperature: once per second
  if (millis() - lastMpuPrint >= PRINT_INTERVAL) {
    lastMpuPrint = millis();
    if (mpuOK) readMPU();
    else Serial.println("[MPU6050] Not available");
  }

  // GPS: once per second
  if (millis() - lastGpsPrint >= PRINT_INTERVAL) {
    lastGpsPrint = millis();

    if (gps.charsProcessed() < 10) {
      Serial.println("[GPS    ] FAULT - no data (check TX/RX wiring and power)");
    }
    else if (!gps.location.isValid()) {
      Serial.print("[GPS    ] Module OK, searching... Satellites: ");
      Serial.println(gps.satellites.isValid() ? gps.satellites.value() : 0);
    }
    else {
      Serial.print("[GPS    ] Lat: ");  Serial.print(gps.location.lat(), 6);
      Serial.print(" | Lng: ");         Serial.print(gps.location.lng(), 6);
      Serial.print(" | Alt: ");         Serial.print(gps.altitude.meters(), 1);
      Serial.print(" m | Speed: ");     Serial.print(gps.speed.kmph(), 1);
      Serial.print(" km/h | Sats: ");   Serial.println(gps.satellites.value());
    }
  }
}
