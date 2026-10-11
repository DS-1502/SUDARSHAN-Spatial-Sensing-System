# SUDARSHAN — Spatial Sensing System

**A Microcontroller-Based Multi-Sensor Spatial Sensing and Intelligent Navigation System**

SUDARSHAN is an embedded sensing project designed to combine GPS positioning, inertial measurements, infrared temperature sensing, and radio-frequency signal detection within a unified system. The project integrates hardware-level sensing with a Python-based dashboard for sensor visualization, monitoring, and spatial analysis.

The system is intended to explore applications in search-and-rescue operations, disaster response, autonomous robotics, and remote inspection.

## Live Dashboard

**Streamlit Application:** [SUDARSHAN Spatial Sensing System](https://sudarshan-spatial-sensing-system-syprfmbgttwbvfx3tfsnso.streamlit.app/)

## Key Features

- **GPS positioning:** Receives geographical coordinates from the NEO-6M GPS module.
- **RF signal detection:** Uses a 433 MHz digital RF receiver to detect incoming digital signals.
- **Inertial sensing:** Uses the MPU6050 to obtain accelerometer and gyroscope measurements.
- **Infrared temperature sensing:** Integrates the MLX90614 for non-contact infrared temperature measurements.
- **Dashboard visualization:** Presents sensor information through a Python-based Streamlit interface.
- **Sensor integration:** Brings together multiple sensing modalities for a consolidated monitoring workflow.

## System Architecture

The system is organized into two primary components:

1. **Hardware and firmware:** An Arduino Uno R3 interfaces with the GPS module, RF receiver, MPU6050, and MLX90614.
2. **Dashboard:** A Streamlit application provides the software interface for displaying and inspecting available sensor data.

The repository separates the dashboard, documentation, and firmware directory to make future development and integration easier to manage.

## Hardware Components

| Component | Purpose |
|---|---|
| Arduino Uno R3 | Main microcontroller |
| NEO-6M GPS module | Geographical positioning |
| 433 MHz digital RF receiver | Digital RF signal detection |
| MPU6050 | Accelerometer and gyroscope measurements |
| MLX90614 | Non-contact infrared temperature sensing |
| Jumper wires and supporting connections | Hardware interconnection |

## Hardware Connections

The following table summarizes the current Arduino Uno R3 pin assignments.

| Module | Module Pin | Arduino Uno R3 |
|---|---|---|
| 433 MHz RF receiver | DATA | D2 |
| 433 MHz RF receiver | ADD | GND |
| NEO-6M GPS | TX | D4 |
| NEO-6M GPS | RX | D3 |
| MPU6050 | SDA | A4 |
| MPU6050 | SCL | A5 |
| MLX90614 | SDA | A4 |
| MLX90614 | SCL | A5 |

**Connection notes:**
- The MPU6050 and MLX90614 share the I²C bus through A4 (SDA) and A5 (SCL).
- GPS TX and RX connections are crossed: module TX connects to Arduino RX, and module RX connects to Arduino TX.
- Confirm the supply-voltage requirements and logic-level compatibility of each module before powering the circuit.
- The RF receiver's ADD pin should be connected as specified in the module's configuration and wiring requirements.

## Repository Structure

```text
SUDARSHAN-Spatial-Sensing-System/
├── dashboard/
│   ├── dashboard.py
│   └── requirements.txt
├── docs/
│   └── abstract.pdf
├── firmware/
│   └── .keep
├── .gitignore
├── LICENSE
└── README.md
```

### Directory Overview

| Path | Description |
|---|---|
| `dashboard/dashboard.py` | Main Streamlit dashboard application |
| `dashboard/requirements.txt` | Python dependencies required by the dashboard |
| `docs/abstract.pdf` | Project abstract and supporting documentation |
| `firmware/` | Directory reserved for firmware source files |
| `.gitignore` | Specifies files excluded from version control |
| `LICENSE` | Project licensing information |
| `README.md` | Project overview, setup instructions, and documentation |

## Software Requirements

- Python 3.9 or a compatible version supported by the dependencies
- pip
- Git
- The Python packages listed in `dashboard/requirements.txt`

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/DS-1502/SUDARSHAN-Spatial-Sensing-System.git
cd SUDARSHAN-Spatial-Sensing-System
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install the dashboard dependencies

```bash
pip install -r dashboard/requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run dashboard/dashboard.py
```

Streamlit will provide a local URL in the terminal. Open that URL in a browser to access the dashboard.

## Development Status

The repository currently contains the dashboard application, its dependency list, project documentation, and a firmware directory reserved for embedded code.

The actual availability of live hardware data depends on the implemented data-acquisition and communication workflow. Dashboard visualizations should not be interpreted as live hardware measurements unless the relevant hardware or data source is connected and operating.

## Potential Applications

- Search-and-rescue support
- Disaster-response monitoring
- Autonomous robotics research
- Remote industrial inspection
- Embedded systems and multi-sensor integration experiments

These are intended application areas; operational deployment would require further validation, testing, and system-level integration.

## Future Scope

- Add and maintain the Arduino firmware within `firmware/`.
- Establish a documented data-transfer interface between the hardware and dashboard.
- Improve sensor calibration and validation.
- Add sensor-fusion and spatial-analysis capabilities where supported by measured data.
- Expand logging, error handling, and testing for reliable operation.

## Contributors
**Tannishtha Gupta .  Dhvan Shah**
**SUDARSHAN Spatial Sensing System**  

Developed as an embedded systems and multi-sensor integration project.

## License

Refer to the [`LICENSE`](LICENSE) file in this repository for the applicable licensing terms.
