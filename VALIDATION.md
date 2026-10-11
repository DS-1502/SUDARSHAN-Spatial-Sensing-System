# SUDARSHAN Validation Record

## Static validation

- Python `py_compile`: **PASS**
- Undefined uppercase-name scan: **PASS**
- Required geometry function `destination_ring`: **PASS**
- Plotly polar `shape="hv"` compatibility issue: **removed**
- Unsupported `Scattermap.line.dash` property: **removed**
- `st.rerun()` full-page refresh loop: **absent**
- `time.sleep()` UI refresh loop: **absent**
- Legacy ESP32 references: **absent**
- Hard-coded COM7 fallback: **removed**

## Plotly figure smoke tests

The following paths were constructed successfully using Plotly 6.5.2:

- empty RF field
- empty thermal field
- populated RF field
- populated thermal field
- vector-fusion compass
- spatial map
- spatial map with waypoint
- spatial map with estimated source region
- spatial map with resultant bearing

## Workspace render-path tests

Using a controlled Streamlit API stub, all four application branches executed without exceptions:

- Overview: **PASS**
- Sensor Field: **PASS**
- Vector Fusion: **PASS**
- System: **PASS**

## Telemetry validation tests

The parser was checked for:

- valid GPS coordinates
- invalid GPS coordinates
- bounded servo angles
- bounded scan angles
- satellite-count limits
- digital RF state handling
- finite numeric conversion

## Runtime limitation

The build environment used for this validation did not provide the Streamlit package or a physical USB serial device, so a full Windows browser/COM-port demonstration could not be executed here.

The final acceptance test should therefore be performed locally with:

```powershell
python -m streamlit run app.py
```

followed by verification of all four workspaces and, when hardware is connected, the selected serial port.
