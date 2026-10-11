# SUDARSHAN

**Multi-Sensor Spatial Sensing & Navigation System**

**Live Dashboard:** [Launch SUDARSHAN](https://sudarshan-spatial-sensing-system-m2drfxaqtvh9wcb7qwddsy.streamlit.app/)

*Explore the dashboard interface and its sensor visualizations. Live hardware readings require a locally connected device.*

SUDARSHAN is an undergraduate engineering prototype exploring how different sensing technologies can be integrated into a common framework for spatial observation, angular response analysis and sensor-fusion-based processing. The project brings together GPS positioning, digital RF detection, infrared temperature sensing, inertial measurements and a dedicated engineering dashboard.

The central idea behind SUDARSHAN is to move beyond viewing sensor outputs as isolated readings and investigate how they can be recorded, compared and represented together. The current prototype is an initial implementation of this broader concept, developed within the practical constraints of an academic engineering project.

> **Project status:** Working academic prototype and platform for further development.

## What the system demonstrates

SUDARSHAN follows an acquisition-to-analysis workflow:

```text
Sensor acquisition
      ↓
Data validation
      ↓
Angular observations
      ↓
Sensor-specific response fields
      ↓
Vector representation
      ↓
Weighted directional analysis
      ↓
Resultant bearing estimate
      ↓
Spatial visualization
```

The dashboard brings sensor telemetry, recorded observations and analytical visualizations into one interface. It is designed to make the measurement process inspectable: live hardware readings, manually recorded observations and reference/demo inputs should be clearly distinguished.

The longer-term objective is to build on this foundation with better-calibrated directional measurements, improved localization methods and experimentally validated sensor-fusion algorithms.

## Dashboard workspaces

### 01 — Field

The main spatial overview workspace.

- Live GPS position when a valid fix is available
- Clearly labelled reference position when live GPS is unavailable
- Position history and configurable reference waypoint
- Working scan radius and directional result visualization
- Compact GPS / RF / thermal / IMU / scan status

The map represents the sensing unit's position when GPS is available. Any estimated source region is an analytical result and should not be interpreted as a verified target coordinate without suitable localization measurements.

### 02 — Sensor Field

An instrumentation-oriented view of angular observations.

**RF angular detection**

- Uses the receiver's digital `DATA` state
- Displays HIGH / LOW detection evidence associated with recorded scan angles
- Does **not** claim analog RSSI, dBm or direct source distance

**Thermal response**

- Uses MLX90614 object and ambient temperature when the sensor is connected and operating
- Derives `ΔT = object temperature − ambient temperature`
- Displays the measured thermal response associated with recorded scan angles

The observation-capture workflow supports manual scanning through known angles when automatic mechanical scanning is unavailable. The reliability of a directional interpretation depends on the sensing arrangement and experimental validation.

### 03 — Vector Fusion

The analytical workspace for examining directional observations.

- North-up directional frame
- RF observation vector
- Thermal response vector
- Resultant vector
- Angular separation and sensor contribution
- Angular coverage and observation quality
- Spatial estimate visualization

The vector framework provides a way to represent and compare observations. Its output depends on the validity, calibration and weighting of the underlying measurements. In particular, a digital RF HIGH/LOW state is not an analog signal-strength measurement, and temperature difference is not automatically a measure of distance or source direction.

### 04 — System

The engineering and diagnostics workspace.

- Serial acquisition state
- Packet count and packet age, where available
- Invalid-frame count
- Hardware topology and interface/pin map
- Current telemetry
- I²C commissioning references

This workspace supports testing and troubleshooting by making communication state and sensor availability visible.

## Hardware interface

The prototype is built around an Arduino Uno R3 and the following sensor interfaces:

| Device | Interface | Arduino interface |
|---|---|---|
| 433 MHz RF receiver | Digital DATA | D2 |
| NEO-6M GPS | Software serial | GPS TX → D4; GPS RX ← D3 |
| MPU6050 | I²C | A4 SDA / A5 SCL |
| MLX90614 | I²C | A4 SDA / A5 SCL |

The MPU6050 and MLX90614 share the I²C bus in parallel. Both use A4 (SDA) and A5 (SCL) on the Arduino Uno, while each device retains its own I²C address.

See [`hardware/README.md`](hardware/README.md) for wiring and power notes.

## RF data limitation

The installed 433 MHz receiver exposes a **digital DATA output**, not an analog RSSI output. The dashboard therefore represents the receiver's digital detection state:

```text
DATA = HIGH  → digital detection evidence
DATA = LOW   → no digital detection at that moment
```

A LOW state does not prove that no transmitter is present; detection depends on the signal, receiver and operating conditions. The software does not invent dBm, RSSI or analog signal-strength values.

## Thermal measurement

The MLX90614 provides object and ambient temperature readings. The dashboard can derive:

```text
ΔT = T_object − T_ambient
```

This is a temperature response, not a direct distance measurement. The MLX90614 is a non-contact temperature sensor rather than a thermal imaging camera, so it does not produce a spatial thermal image of the environment.

If the MLX90614 is unavailable during a test, any alternative value must be labelled clearly as a proxy or demonstration input rather than a live MLX90614 measurement.

## Position, direction and source estimation

GPS provides the geographical position of the sensing unit. It does not independently determine the coordinates of a separate object or radio source.

The current RF receiver detects compatible digital transmissions but does not, by itself, provide calibrated signal strength, range or reliable directional localization. The MPU6050 measures acceleration and angular velocity but does not provide absolute compass heading. Recorded scan angles can organize observations, but accurate geographical bearing requires a validated directional sensing arrangement and reliable heading reference.

For this reason, SUDARSHAN's current spatial and vector outputs should be understood as a framework for directional observation and analysis. Establishing the precise location of an external source is a further development objective requiring suitable measurements and validation.

## Manual/reference acquisition

The dashboard supports manual or reference acquisition for prototype testing, including cases such as:

- GPS fix unavailable during indoor testing
- Manual angular scanning
- Controlled reference-coordinate demonstrations
- Validation of visualization and processing workflows

Reference observations should remain explicitly labelled and separate from live hardware telemetry. This allows the dashboard to be demonstrated and tested without confusing reference inputs with measurements from connected sensors.

## Local setup

### Requirements

- Python 3.10 or later
- USB serial access for local live-hardware acquisition
- Arduino and sensor hardware connected as documented
- Serial data format compatible with the dashboard parser

### Install

From the project root:

```powershell
python -m pip install -r requirements.txt
```

### Run

```powershell
python -m streamlit run app.py
```

The terminal will provide a local URL such as:

```text
http://localhost:8501
```

Keep the terminal running while using the dashboard. Close Arduino Serial Monitor or Serial Plotter before connecting the dashboard to the same COM port, because a serial port generally cannot be used by both applications at the same time.

## Data handling and validation

The dashboard is intended to distinguish valid measurements from unavailable, malformed or reference data. Sensor readings should only be described as live when they originate from the connected hardware. GPS validity, sensor availability, packet age and parsing errors are important signals when evaluating the prototype.

For reproducible testing, future iterations should record timestamped sensor readings, scan angles, acquisition mode and processing outputs so the results can be compared across repeated trials.

## Demonstration workflow

For an academic or project demonstration:

1. Open **Field** and show the live GPS position or clearly labelled reference position.
2. Open **Sensor Field**.
3. Rotate the sensor assembly through known angles using the available manual scanning method.
4. Record the actual RF DATA state and thermal readings at each angle.
5. Show how the RF detection field and thermal response field build from the observations.
6. Open **Vector Fusion** and explain how recorded observations are represented and combined.
7. Return to **Field** to review the spatial visualization and any resulting bearing estimate.
8. Use **System** to discuss hardware connections, serial communication and diagnostics.

Explain clearly which values are live, which are manually recorded and which are reference/demo values.

## Cloud deployment and live dashboard

### Open the dashboard

**Live dashboard:** [Launch SUDARSHAN Dashboard](https://sudarshan-spatial-sensing-system-m2drfxaqtvh9wcb7qwddsy.streamlit.app/)


> Replace the placeholder above with the final public Streamlit deployment URL once deployment is complete.

A hosted dashboard provides an easy way for others to explore the interface and its supported reference/manual workflows. However, a cloud-hosted Streamlit application cannot directly access a USB COM port connected to a visitor's own computer.

- **Local deployment:** can communicate with hardware connected to the computer running the application, subject to the correct serial configuration.
- **Cloud deployment:** can display the dashboard and support available reference/manual workflows.
- **Remote live hardware:** requires a separate network-connected acquisition service or another secure method of forwarding telemetry to the hosted application.

Do not describe the public cloud page as directly reading sensors connected to a visitor's laptop unless that communication path has actually been implemented and tested.

## Project structure

```text
SUDARSHAN/
├── app.py
├── requirements.txt
├── README.md
├── VALIDATION.md
├── LICENSE
├── .gitignore
├── hardware/
│   └── README.md
└── SUDARSHAN REPORT/
    └── SUDARSHAN project report
```

## Design principles

- Engineering-first visual hierarchy
- Actual measurements over fabricated live telemetry
- Digital RF evidence instead of invented RSSI
- Explicit live, manual and reference states
- Clear handling of missing or stale sensor data
- Reproducible angular observations
- Consistent north-up bearing convention
- Estimated spatial region rather than unsupported exact coordinates
- Modular architecture intended for further validation and extension

## Future scope

SUDARSHAN is intended as a foundation that can be extended as additional hardware, time and experimental resources become available. Potential improvements include:

- Directional RF hardware and calibrated signal-strength measurements
- Thermal imaging for spatial temperature visualization
- Reliable absolute-heading measurements
- Appropriate ranging or localization methods for estimating an external source's position
- More consistent serial acquisition and lower-latency dashboard updates
- Automated scanning and repeatable measurement procedures
- Data logging, uncertainty estimation and systematic performance testing
- More compact hardware integration and improved power management

These improvements would allow the system to progress from a multi-sensor integration prototype toward a more thoroughly validated spatial sensing platform.

## Team

**Tannishtha Gupta · Dhvan Shah**

Student engineering prototype.

## License

MIT License. See [`LICENSE`](LICENSE).
