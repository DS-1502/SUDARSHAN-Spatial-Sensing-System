# SUDARSHAN — Testing and Validation

## 1. Purpose

This document describes the testing and validation procedures for the SUDARSHAN Multi-Sensor Spatial Sensing & Navigation System.

The purpose of testing is to verify individual sensor interfaces, hardware communication, dashboard behaviour, data handling, and the reliability of the system's analytical outputs.

Testing is divided into:

- Hardware and electrical verification
- Individual sensor testing
- Arduino-to-dashboard communication
- Dashboard functionality testing
- Data validation and error handling
- Integrated system testing

**Testing status:** Pending verification. Update individual test statuses only after performing the corresponding tests.

## 2. System Under Test

The documented hardware configuration uses the following components:

| Component | Interface | Connection |
|---|---|---|
| Arduino Uno R3 | Microcontroller | USB/serial connection to host computer |
| NEO-6M GPS module | Serial | TX → D4, RX → D3 |
| MPU6050 6-axis IMU | I²C | SDA → A4, SCL → A5 |
| 433 MHz RF receiver | Digital output | DATA → D2, ADD → GND |
| MLX90614 IR temperature sensor | I²C | SDA → A4, SCL → A5 |
| SG90 servo | PWM/control signal | Optional; confirm actual wiring before testing |

The MPU6050 and MLX90614 share the Arduino Uno's I²C bus. Their supply voltages must be appropriate for the specific breakout boards being used.

The firmware source is to be tested once it has been added to the repository. Sensor testing must use the actual connected hardware rather than simulated dashboard values.

## 3. Test Status Convention

Use the following status values throughout this document:

| Status | Meaning |
|---|---|
| NOT RUN | The test has not been performed. |
| PASS | The test was performed and met its acceptance criteria. |
| FAIL | The test was performed but did not meet its acceptance criteria. |
| BLOCKED | The test could not be completed because a dependency or required component was unavailable. |
| NOT APPLICABLE | The test does not apply to the implemented configuration. |

A test must not be marked PASS based only on source-code inspection or the appearance of a dashboard visualization.

## 4. Hardware and Electrical Tests

### 4.1 Wiring Verification

**Objective:** Verify that the physical connections match the documented pin mapping.

**Procedure:**

1. Disconnect power before inspecting or modifying the wiring.
2. Verify the GPS TX/RX connections.
3. Verify the MPU6050 SDA/SCL connections.
4. Verify the RF receiver DATA connection and ADD-to-GND connection.
5. Check the power supply and ground connections.
6. Confirm that the sensor breakout boards support the applied supply voltages.
7. Inspect the circuit for loose wires and accidental shorts.

**Acceptance criteria:** All connections match the verified wiring documentation, and no incorrect supply connections or shorts are identified.

**Result:** NOT RUN

**Observations:** _Record the actual inspection results._

### 4.2 Power-Up Test

**Objective:** Confirm that the circuit powers up without abnormal behaviour.

**Procedure:**

1. Inspect the circuit with power disconnected.
2. Connect the Arduino to USB power.
3. Check for unexpected heating, resets, or unstable power.
4. Confirm that the Arduino can communicate with the host computer.

**Acceptance criteria:** The board powers up normally and remains operational during the test.

**Result:** NOT RUN

**Observations:** _Record any resets, power issues, or faults._

## 5. Individual Sensor Tests

### 5.1 GPS Test — NEO-6M

**Objective:** Verify GPS communication and position-fix handling.

**Procedure:**

1. Connect the GPS module according to the documented pin mapping.
2. Run the appropriate GPS parsing firmware.
3. Observe incoming serial data.
4. Test under suitable outdoor conditions with a reasonable view of the sky.
5. Record whether a valid GPS fix is obtained.
6. Check that invalid or unavailable fixes are not treated as valid coordinates.

**Acceptance criteria:**

- GPS data is received and parsed correctly.
- Valid coordinates are displayed when a valid fix is available.
- Missing or invalid fixes are reported accurately.
- Reference coordinates are not presented as live GPS measurements.

**Result:** NOT RUN

**Recorded observations:**

- Test environment:
- Time to obtain a fix:
- Reported coordinates:
- Fix validity:
- Notes:

### 5.2 MPU6050 Test

**Objective:** Verify I²C communication and inertial measurements.

**Procedure:**

1. Verify the power, ground, SDA, and SCL connections.
2. Run an I²C scanner or an appropriate sensor test sketch.
3. Confirm that the device responds at its detected I²C address.
4. Read acceleration and gyroscope measurements.
5. Keep the module stationary and record the measurements.
6. Rotate the module along different axes and observe the response.

**Acceptance criteria:**

- The sensor is detected over I²C.
- Measurements are received without communication errors.
- Readings respond consistently to movement.
- Stationary readings and gyroscope drift are recorded and interpreted appropriately.

**Result:** NOT RUN

**Recorded observations:**

- Detected I²C address:
- Stationary measurements:
- Movement response:
- Communication errors:
- Notes:

The MPU6050 does not independently provide an absolute compass heading. Any heading calculation must account for sensor orientation, drift, and the limitations of inertial measurements.

### 5.3 RF Receiver Test — 433 MHz

**Objective:** Verify the digital output of the RF receiver.

**Procedure:**

1. Connect receiver DATA to Arduino D2 and ADD to GND.
2. Run firmware that reads the digital input.
3. Record the receiver output under the test conditions.
4. Compare observations with and without a known compatible transmitting source, where available.
5. Repeat observations to identify inconsistent detection.

**Acceptance criteria:**

- The digital DATA input is read correctly.
- The observed HIGH/LOW states are recorded accurately.
- Detection behaviour is evaluated under documented test conditions.
- Digital output is not reported as calibrated RSSI, dBm, or direct distance.

**Result:** NOT RUN

**Recorded observations:**

- Test environment:
- Transmitter used, if applicable:
- Receiver output without the test transmitter:
- Receiver output with the test transmitter:
- Repeatability:
- Notes:

A LOW output does not conclusively establish that no transmitter is present. Receiver sensitivity, interference, signal conditions, and transmitter compatibility can affect detection.

### 5.4 MLX90614 Temperature Sensor Test

**Objective:** Verify object and ambient temperature measurements.

**Procedure:**

1. Verify the sensor's power and I²C connections.
2. Run the appropriate sensor library or test sketch.
3. Confirm that the sensor is detected on the I²C bus.
4. Read object and ambient temperatures.
5. Repeat measurements under stable environmental conditions.
6. Compare readings with a suitable reference thermometer when available.

**Acceptance criteria:**

- The sensor communicates correctly.
- Object and ambient temperature values are available and numerically valid.
- Repeated readings are recorded.
- Any comparison with a reference instrument is documented.
- Missing or simulated values are not presented as live measurements.

**Result:** NOT RUN

**Recorded observations:**

- Detected I²C address:
- Object temperature:
- Ambient temperature:
- Reference instrument reading, if available:
- Difference from reference:
- Notes:

The MLX90614 is a non-contact temperature sensor, not a thermal imaging camera. Temperature difference alone does not establish the distance or direction of a heat source.

### 5.5 Optional SG90 Servo Test

Perform this test only if the servo is installed and connected.

**Objective:** Verify controlled mechanical movement for angular observation.

**Procedure:**

1. Verify the actual signal, power, and ground connections.
2. Confirm that the servo has an appropriate power supply.
3. Command a limited sequence of known angles.
4. Observe movement, repeatability, and mechanical interference.
5. Record the actual orientation at each commanded angle.

**Acceptance criteria:**

- The servo responds to commands within the tested operating range.
- Movement does not cause unintended resets or power instability.
- Commanded angles are not assumed to equal measured physical orientation without verification.

**Result:** NOT RUN

**Recorded observations:**

- Actual wiring:
- Tested angular range:
- Movement repeatability:
- Power stability:
- Notes:

## 6. Firmware and Serial Communication Tests

Perform these tests after the Arduino firmware has been added.

### 6.1 Firmware Upload

**Objective:** Confirm that the firmware can be compiled and uploaded.

**Acceptance criteria:**

- The firmware compiles using the documented board configuration and required libraries.
- The sketch uploads successfully to the Arduino Uno R3.
- The device starts without repeated resets or unexpected errors.

**Result:** NOT RUN

**Firmware version/commit:** _Record after implementation._

### 6.2 Serial Data Test

**Objective:** Verify that the Arduino transmits data in the format expected by the dashboard.

**Procedure:**

1. Record the configured serial port and baud rate.
2. Open the serial output using a compatible serial monitor.
3. Verify the message structure and line termination.
4. Check that sensor values are represented correctly.
5. Test unavailable sensor readings and malformed or incomplete data handling.
6. Close the serial monitor before opening a dashboard connection to the same port.

**Acceptance criteria:**

- The transmitted messages follow the documented protocol.
- Sensor fields correspond to the correct hardware inputs.
- Invalid measurements are identified rather than silently treated as valid.
- The dashboard parser can process the transmitted data consistently.

**Result:** NOT RUN

**Recorded observations:**

- Serial port:
- Baud rate:
- Message format:
- Transmission errors:
- Notes:

The serial protocol must be documented in `firmware/PROTOCOL.md` once the actual firmware format has been established.

## 7. Dashboard Tests

### 7.1 Local Startup

**Objective:** Verify that the dashboard starts on the local computer.

**Procedure:**

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**Acceptance criteria:**

- Dependencies install successfully.
- The dashboard starts without fatal errors.
- The local page loads and the available workspaces can be accessed.

**Result:** NOT RUN

### 7.2 Field Workspace

**Objective:** Verify the position and spatial overview interface.

**Acceptance criteria:**

- Valid live GPS coordinates are displayed when available.
- Reference positions are clearly distinguished from live positions.
- Missing GPS data is handled without displaying fabricated live coordinates.
- Directional estimates are labelled according to their actual measurement basis.

**Result:** NOT RUN

### 7.3 Sensor Field Workspace

**Objective:** Verify the presentation of angular RF and thermal observations.

**Acceptance criteria:**

- Recorded RF observations correspond to the actual digital receiver state.
- Thermal observations correspond to actual MLX90614 readings when live hardware is used.
- Observation angles are associated with the correct measurements.
- Reference or demonstration inputs are clearly labelled.

**Result:** NOT RUN

### 7.4 Vector Fusion Workspace

**Objective:** Verify the processing and visualization of recorded observations.

**Acceptance criteria:**

- The displayed vectors correspond to the observations supplied to the processing pipeline.
- Angular conventions are consistent.
- Invalid or unavailable inputs are handled explicitly.
- Resultant bearing estimates are not presented as verified source locations without supporting measurements.

**Result:** NOT RUN

### 7.5 System Workspace

**Objective:** Verify the engineering and diagnostic information.

**Acceptance criteria:**

- The displayed connection information matches the documented hardware.
- Serial connection status is reported correctly when implemented.
- Packet counts, packet age, and invalid-frame counts correspond to actual application state when those metrics are available.
- Missing sensors and communication errors are identifiable.

**Result:** NOT RUN

## 8. Integrated System Tests

### 8.1 Multi-Sensor Operation

**Objective:** Verify that the available sensors operate together without communication or processing conflicts.

**Procedure:**

1. Connect all implemented sensors.
2. Start the Arduino firmware.
3. Start the local dashboard.
4. Confirm that each implemented sensor produces the expected data.
5. Observe system behaviour while changing the sensor orientation or environmental conditions.
6. Check for missing packets, invalid measurements, resets, and dashboard errors.

**Acceptance criteria:** The implemented sensors operate together, available measurements are processed correctly, and failures are reported without being mistaken for valid measurements.

**Result:** NOT RUN

### 8.2 Live, Reference, and Simulated Data Separation

**Objective:** Verify that the system does not confuse test inputs with live sensor measurements.

**Acceptance criteria:**

- Live readings originate from the connected hardware.
- Manual observations are identified as manually recorded.
- Reference coordinates are labelled as reference values.
- Simulated or demonstration values are identified explicitly.
- Missing sensor readings do not silently become fabricated live values.

**Result:** NOT RUN

### 8.3 Hosted Dashboard Limitations

**Objective:** Verify the distinction between local hardware access and cloud-hosted visualization.

**Acceptance criteria:**

- The public dashboard loads when the deployment is available.
- Supported reference/demo workflows are identified correctly.
- The documentation does not claim that the hosted dashboard directly accesses USB hardware attached to a visitor's computer.
- Any remote live-data workflow is tested separately before being claimed as operational.

**Result:** NOT RUN

## 9. Test Summary

Complete this table as tests are performed.

| Test Category | Total Tests | Passed | Failed | Blocked | Not Run |
|---|---:|---:|---:|---:|---:|
| Hardware and wiring | — | — | — | — | — |
| Individual sensors | — | — | — | — | — |
| Firmware and serial communication | — | — | — | — | — |
| Dashboard workspaces | — | — | — | — | — |
| Integrated system | — | — | — | — | — |

Replace the placeholders with actual counts after testing. Do not report a test as passed unless its acceptance criteria have been checked.

## 10. Limitations and Further Validation

The following limitations must be considered when interpreting test results:

- GPS measures the position of the sensing unit, not an external RF source.
- The RF receiver provides digital detection evidence rather than calibrated signal-strength measurements.
- The MPU6050 does not independently provide absolute compass heading.
- The MLX90614 provides temperature measurements rather than a thermal image.
- Directional estimates depend on the quality of angular observations, sensor calibration, orientation references, and the processing method.
- Source localization requires an appropriate and experimentally validated measurement approach.

Future validation should include repeatability measurements, reference-instrument comparisons, uncertainty analysis, documented test conditions, and end-to-end trials with the actual hardware.

## 11. Test Record

For each completed test, record:

- Test ID and date
- Hardware and firmware configuration
- Software version or Git commit
- Test environment and procedure
- Expected result
- Actual result
- Pass/fail status
- Relevant photographs, logs, or measurements
- Known limitations and corrective actions

These records provide evidence for the project's technical claims and make future development and debugging more reproducible.

