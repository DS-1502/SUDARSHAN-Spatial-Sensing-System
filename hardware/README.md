# SUDARSHAN Hardware Interface

Current prototype interface for the SUDARSHAN dashboard.

## Pin map

| Module | Module pin | Arduino pin | Notes |
|---|---|---|---|
| 433 MHz RF receiver | DATA | D4 | Digital detection only |
| 433 MHz RF receiver | +5V | 5V | Supply |
| 433 MHz RF receiver | GND | GND | Common ground |
| 433 MHz RF receiver | ANT | — | Leave disconnected during current prototype stage if not required |
| SG90 | Signal | D5 | PWM control |
| SG90 | Red | 5V | Servo supply |
| SG90 | Brown/Black | GND | Common ground |
| NEO-6M | TX | D8 | GPS data into controller |
| NEO-6M | RX | — | Leave disconnected in current implementation |
| NEO-6M | VCC | 5V | Verify the specific breakout's regulator/input specification |
| NEO-6M | GND | GND | Common ground |
| MPU6050 | SDA | A4 | Shared I²C bus |
| MPU6050 | SCL | A5 | Shared I²C bus |
| MPU6050 | VCC | 3.3V | Current prototype connection |
| MPU6050 | GND | GND | Common ground |
| MLX90614 | SDA | A4 | Shared I²C bus |
| MLX90614 | SCL | A5 | Shared I²C bus |
| MLX90614 | VIN | 5V | Current breakout connection |
| MLX90614 | GND | GND | Common ground |

## Important electrical notes

- All modules must share a common ground.
- The SG90 can draw substantially more current than the controller I/O can provide. If servo movement causes resets, use a suitable regulated 5 V servo supply and connect its ground to the controller ground.
- Do not drive the servo from an I/O pin.
- Confirm the voltage requirements of the exact sensor breakout boards before changing their supply connections.
- The current RF receiver exposes digital DATA; it is **not** an analog RSSI receiver.

## I²C commissioning

Expected addresses for the current modules are commonly:

- MPU6050: `0x68`
- MLX90614: `0x5A`

Confirm the actual addresses with an I²C scanner during hardware commissioning rather than assuming them.

## Angular scanning

The MLX90614 is mechanically mounted on the SG90 horn. The intended workflow is:

```text
Known scan angle
      ↓
RF DATA observation
      ↓
MLX90614 object / ambient temperature
      ↓
ΔT calculation
      ↓
Record observation
```

If the servo cannot be powered adequately during a demonstration, manual rotation of the assembly can be used as a temporary mechanical actuation method while the dashboard records the known angle and measured sensor values.
