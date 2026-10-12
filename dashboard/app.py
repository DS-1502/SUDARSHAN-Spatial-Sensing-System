
import json
import re
import math
import threading
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    import serial
    import serial.tools.list_ports
except Exception:
    serial = None


# ============================================================
# SUDARSHAN
# Multi-Sensor Spatial Sensing & Navigation System
# ============================================================
APP_VERSION = "1.0.0"

st.set_page_config(
    page_title="SUDARSHAN | Spatial Sensing",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
BG = "#0b0f12"
SURFACE = "#11171c"
SURFACE_2 = "#151d23"
SURFACE_3 = "#192229"
BORDER = "#2a353d"
BORDER_SOFT = "#202c34"
TEXT = "#f1eee7"
MUTED = "#8d9aa3"
DIM = "#687780"
RF = "#d84a4a"
THERMAL = "#e6b84b"
GPS = "#6e9bbd"
RESULTANT = "#f0eee8"
GOOD = "#78a98b"
WARN = "#c89b4b"
BAD = "#a95757"

SIT_LAT = 18.541361
SIT_LON = 73.728286

DEFAULTS = {
    "lat": SIT_LAT,
    "lon": SIT_LON,
    "way_lat": SIT_LAT,
    "way_lon": SIT_LON,
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: "DM Sans", sans-serif;
}}
.stApp {{
    background:
      radial-gradient(circle at 82% 6%, rgba(92,125,145,.10), transparent 26%),
      radial-gradient(circle at 18% 88%, rgba(120,90,55,.07), transparent 30%),
      {BG};
    color: {TEXT};
}}
.block-container {{
    max-width: 1500px;
    padding-top: 1.25rem;
    padding-bottom: 1.5rem;
}}
section[data-testid="stSidebar"] {{
    background: #0d1216;
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 1.15rem;
}}
div[data-testid="stMetric"] {{
    background: transparent;
}}
div[data-testid="stMetricLabel"] {{
    color: {MUTED};
}}
div[data-testid="stMetricValue"] {{
    color: {TEXT};
}}
.stButton > button {{
    border: 1px solid {BORDER};
    background: {SURFACE_2};
    color: {TEXT};
    border-radius: 7px;
    min-height: 2.25rem;
}}
.stButton > button:hover {{
    border-color: #56636c;
    color: white;
}}
div[data-baseweb="select"] > div {{
    background: {SURFACE_2};
    border-color: {BORDER};
}}
textarea, input {{
    background: {SURFACE_2} !important;
    color: {TEXT} !important;
}}
.sdr-brand {{
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: .11em;
    color: {TEXT};
}}
.sdr-subbrand {{
    color: {MUTED};
    font-size: .74rem;
    letter-spacing: .09em;
    text-transform: uppercase;
    margin-top: .15rem;
}}
.sdr-rule {{
    height: 1px;
    background: {BORDER};
    margin: 1rem 0 1.05rem 0;
}}
.sdr-kicker {{
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: .69rem;
    font-weight: 600;
}}
.sdr-title {{
    font-size: 1.55rem;
    font-weight: 600;
    letter-spacing: -.025em;
    margin-top: .2rem;
}}
.sdr-caption {{
    color: {MUTED};
    font-size: .82rem;
}}
.panel {{
    background: linear-gradient(180deg, rgba(24,32,38,.96), rgba(15,21,26,.96));
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 15px 16px;
}}
.panel-tight {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 11px 13px;
}}
.panel-title {{
    font-size: .73rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: {MUTED};
    font-weight: 600;
    margin-bottom: .55rem;
}}
.big-number {{
    font-size: 1.42rem;
    font-weight: 600;
    letter-spacing: -.02em;
}}
.mono {{
    font-family: "IBM Plex Mono", monospace;
}}
.status-dot {{
    display:inline-block;
    width:7px;height:7px;border-radius:50%;
    margin-right:7px;
    background:{GOOD};
    box-shadow:0 0 0 3px rgba(120,169,139,.10);
}}
.status-dot.warn {{
    background:{WARN};
    box-shadow:0 0 0 3px rgba(200,155,75,.10);
}}
.status-dot.bad {{
    background:{BAD};
    box-shadow:0 0 0 3px rgba(169,87,87,.10);
}}
.sidebar-note {{
    color:{MUTED};
    font-size:.72rem;
    line-height:1.45;
}}
.small-table {{
    font-size:.78rem;
}}
footer {{visibility:hidden;}}

/* SUDARSHAN presentation layer — no nested bordered Streamlit wrappers. */
.sdr-pagehead {{ display:flex; justify-content:space-between; align-items:flex-end; gap:24px; margin-bottom:1.05rem; }}
.sdr-pagecode {{ color:{DIM}; font-family:"IBM Plex Mono",monospace; font-size:.61rem; letter-spacing:.12em; text-transform:uppercase; padding-bottom:.22rem; }}
.sdr-commandbar {{ display:flex; gap:0; border-top:1px solid {BORDER}; border-bottom:1px solid {BORDER}; background:rgba(17,23,28,.68); margin-bottom:1rem; }}
.sdr-commandbar span {{ flex:1; padding:.58rem .72rem; border-right:1px solid {BORDER}; color:{MUTED}; font-family:"IBM Plex Mono",monospace; font-size:.61rem; letter-spacing:.06em; }}
.sdr-commandbar span:last-child {{ border-right:0; }}
.sdr-commandbar b {{ color:{DIM}; font-weight:500; margin-right:.35rem; }}
.sdr-commandbar em {{ font-style:normal; }}
.sdr-section-head {{ display:flex; justify-content:space-between; align-items:end; border-bottom:1px solid {BORDER}; padding:.25rem 0 .55rem; margin:.2rem 0 .8rem; }}
.sdr-section-kicker {{ color:{GPS}; font-size:.61rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }}
.sdr-section-title {{ color:{TEXT}; font-size:1.02rem; font-weight:600; margin-top:.12rem; }}
.sdr-section-meta {{ color:{DIM}; font-family:"IBM Plex Mono"; font-size:.59rem; letter-spacing:.05em; }}
.tile-grid {{ display:grid; gap:8px; margin:.85rem 0 1rem; }}
.tile-grid.five {{ grid-template-columns:repeat(5,1fr); }}
.tile-grid.four {{ grid-template-columns:repeat(4,1fr); }}
.sdr-tile {{ min-height:76px; background:linear-gradient(180deg,#151d23,#10171c); border:1px solid {BORDER}; border-radius:8px; padding:.7rem .78rem; position:relative; overflow:hidden; }}
.sdr-tile:before {{ content:""; position:absolute; left:0; top:0; width:3px; height:100%; background:{BORDER}; }}
.sdr-tile-label {{ color:{MUTED}; font-size:.59rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }}
.sdr-tile-value {{ font-family:"IBM Plex Mono"; font-size:1.22rem; line-height:1.15; margin-top:.32rem; }}
.sdr-tile-sub {{ color:{DIM}; font-size:.61rem; margin-top:.25rem; }}
.chart-shell {{ border:1px solid {BORDER}; border-radius:9px; background:linear-gradient(180deg,#11181e,#0d1317); overflow:hidden; }}
.chart-shell-head {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid {BORDER_SOFT}; padding:.66rem .78rem; }}
.chart-shell-head b {{ color:#aeb9c0; font-size:.62rem; letter-spacing:.12em; }}
.chart-shell-head span {{ color:{DIM}; font-family:"IBM Plex Mono"; font-size:.56rem; letter-spacing:.04em; }}
.chart-foot {{ padding:.46rem .72rem .62rem; border-top:1px solid {BORDER_SOFT}; color:{DIM}; font-size:.63rem; }}
.readout-panel {{ background:linear-gradient(180deg,#141c22,#10161a); border:1px solid {BORDER}; border-radius:9px; padding:.85rem .9rem; margin-bottom:.75rem; }}
.readout-panel.tall {{ min-height:430px; }}
.readout-head, .micro-title {{ color:#9daab2; font-size:.61rem; font-weight:700; letter-spacing:.13em; text-transform:uppercase; margin-bottom:.65rem; }}
.coord {{ font-family:"IBM Plex Mono"; font-size:1.32rem; color:{TEXT}; letter-spacing:-.03em; }}
.coord span {{ color:{GPS}; font-size:.68rem; }}
.coord.sub {{ font-size:.88rem; color:{MUTED}; margin-top:.18rem; }}
.sdr-row {{ display:flex; justify-content:space-between; gap:16px; padding:.5rem 0; border-bottom:1px solid {BORDER_SOFT}; color:{MUTED}; font-size:.69rem; }}
.sdr-row:last-child {{ border-bottom:0; }}
.sdr-row strong {{ font-family:"IBM Plex Mono"; font-weight:500; text-align:right; }}
.micro-panel {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:8px; padding:.78rem .85rem; min-height:115px; }}
.sweep-wrap {{ margin:.7rem 0 1rem; }}
.sweep-axis {{ display:flex; justify-content:space-between; color:{DIM}; font-family:"IBM Plex Mono"; font-size:.56rem; margin-bottom:.28rem; }}
.sweep-track {{ height:8px; background:#1c272e; border:1px solid #27343c; border-radius:99px; position:relative; }}
.sweep-track:after {{ content:""; position:absolute; left:50%; top:-4px; bottom:-4px; width:1px; background:#46545c; opacity:.7; }}
.sweep-track i {{ position:absolute; top:1px; width:5px; height:5px; border-radius:50%; transform:translateX(-50%); box-shadow:0 0 0 2px rgba(0,0,0,.25); }}
.sweep-label {{ color:{DIM}; font-size:.56rem; letter-spacing:.1em; margin-top:.35rem; }}
.control-strip {{ border:1px solid {BORDER}; border-radius:9px; background:#10171c; padding:.75rem .82rem .8rem; margin:1rem 0; }}
.control-note {{ color:{MUTED}; font-size:.68rem; line-height:1.5; padding:.55rem 0; }}
.control-note b {{ color:{THERMAL}; font-family:"IBM Plex Mono"; }}
.table-head {{ display:flex; justify-content:space-between; color:#9daab2; font-size:.61rem; letter-spacing:.12em; font-weight:700; padding:.5rem 0 .55rem; border-bottom:1px solid {BORDER}; }}
.table-head span:last-child {{ color:{DIM}; font-family:"IBM Plex Mono"; font-size:.55rem; }}
.empty-state {{ border:1px dashed #34434c; border-radius:9px; padding:1.25rem; text-align:center; color:{MUTED}; background:rgba(17,23,28,.45); font-size:.72rem; line-height:1.55; }}
.empty-state b {{ color:{GPS}; font-size:.62rem; letter-spacing:.14em; }}
.legend-dot {{ display:inline-block; width:7px; height:7px; border-radius:50%; vertical-align:middle; }}
.legend-dot.rf {{ background:{RF}; }}
.legend-dot.thermal {{ background:{THERMAL}; }}
.legend-ring {{ display:inline-block; width:8px; height:8px; border:1px solid #66737b; border-radius:50%; vertical-align:middle; }}
.weight-row {{ display:flex; justify-content:space-between; color:{MUTED}; font-size:.68rem; margin:.55rem 0 .25rem; }}
.weight-row b {{ color:{TEXT}; font-family:"IBM Plex Mono"; font-weight:500; }}
.weight-track, .quality-bar {{ height:5px; background:#202b31; border-radius:99px; overflow:hidden; }}
.weight-track i, .quality-bar i {{ display:block; height:100%; border-radius:99px; }}
.quality-bar {{ margin-top:.85rem; }}
.quality-bar i {{ background:linear-gradient(90deg,{GPS},{RESULTANT}); }}
.quality-caption {{ color:{DIM}; font-size:.57rem; letter-spacing:.09em; margin-top:.32rem; }}
.quality-caption b {{ color:{TEXT}; float:right; font-family:"IBM Plex Mono"; }}
.method-chain {{ display:flex; flex-wrap:wrap; align-items:center; gap:.35rem; margin:.6rem 0 .8rem; }}
.method-chain span {{ border:1px solid #33424a; background:#121a20; border-radius:4px; padding:.32rem .4rem; color:#a9b4ba; font-family:"IBM Plex Mono"; font-size:.54rem; }}
.method-chain i {{ color:{DIM}; font-style:normal; }}
.readout-callout {{ border-left:2px solid {GPS}; margin-top:.75rem; padding:.55rem .65rem; background:rgba(110,155,189,.05); color:{MUTED}; font-size:.64rem; line-height:1.45; }}
.solution-band {{ display:flex; align-items:center; justify-content:space-between; gap:20px; margin-top:1rem; border:1px solid #3a4042; border-radius:9px; background:linear-gradient(90deg,#171c1d,#12171a); padding:.9rem 1rem; }}
.solution-bearing {{ color:{RESULTANT}; font-family:"IBM Plex Mono"; font-size:1.8rem; }}
.solution-bearing.muted {{ color:{DIM}; }}
.solution-meta {{ color:{DIM}; font-family:"IBM Plex Mono"; font-size:.58rem; }}
.solution-coords {{ display:flex; gap:1rem; color:{DIM}; font-family:"IBM Plex Mono"; font-size:.6rem; padding:.55rem .2rem .1rem; }}
.solution-coords b {{ color:{TEXT}; font-weight:500; }}
.system-panel {{ border:1px solid {BORDER}; border-radius:9px; background:linear-gradient(180deg,#121a20,#0e1418); padding:.8rem .9rem; margin-bottom:.9rem; }}
.system-head {{ display:flex; justify-content:space-between; border-bottom:1px solid {BORDER_SOFT}; padding-bottom:.55rem; margin-bottom:.35rem; }}
.system-head b {{ color:#9daab2; font-size:.61rem; letter-spacing:.12em; }}
.system-head span {{ color:{DIM}; font-family:"IBM Plex Mono"; font-size:.55rem; }}
.topology-row {{ display:grid; grid-template-columns:10px 78px 1fr 100px 1fr; gap:10px; align-items:center; padding:.55rem 0; border-bottom:1px solid {BORDER_SOFT}; font-size:.66rem; }}
.topology-row:last-child {{ border-bottom:0; }}
.topology-row b {{ color:{TEXT}; font-size:.65rem; }}
.topology-row span {{ color:{MUTED}; }}
.topology-row code {{ color:{GPS}; background:#111a20; border:1px solid #26353e; padding:.2rem .3rem; border-radius:3px; font-family:"IBM Plex Mono"; font-size:.55rem; }}
.topology-row em {{ color:{DIM}; font-style:normal; text-align:right; }}
.topo-dot {{ width:7px; height:7px; border-radius:50%; display:block; }}
@media (max-width:1100px) {{ .tile-grid.five,.tile-grid.four {{ grid-template-columns:repeat(2,1fr); }} .sdr-commandbar {{ flex-wrap:wrap; }} .sdr-commandbar span {{ flex:1 1 45%; }} .sdr-pagecode {{ display:none; }} }}
@media (max-width:700px) {{ .sdr-pagehead {{ align-items:flex-start; }} .tile-grid.five,.tile-grid.four {{ grid-template-columns:1fr 1fr; }} .sdr-section-meta {{ display:none; }} .topology-row {{ grid-template-columns:10px 70px 1fr; }} .topology-row code,.topology-row em {{ display:none; }} }}
.sdr-border-wrap {{ background:linear-gradient(180deg,#11181e,#0d1317); border:1px solid {BORDER}; border-radius:9px; padding:.05rem .05rem .1rem; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ background:linear-gradient(180deg,#11181e,#0d1317); border-color:{BORDER} !important; border-radius:9px !important; }}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{ background:transparent; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Data model ----------
@dataclass
class Telemetry:
    timestamp: float = field(default_factory=time.time)
    gps_valid: bool = False
    lat: float = SIT_LAT
    lon: float = SIT_LON
    satellites: int = 0
    altitude: float = 0.0
    scan_angle: float = 90.0
    rf_data: int = 0
    rf_angle: float = 90.0
    temp_available: bool = False
    object_c: float = 0.0
    ambient_c: float = 0.0
    delta_c: float = 0.0
    imu_available: bool = False
    roll: float = 0.0
    pitch: float = 0.0
    accel_x: float = 0.0
    accel_y: float = 0.0
    accel_z: float = 0.0
    gyro_x: float = 0.0
    gyro_y: float = 0.0
    gyro_z: float = 0.0
    source: str = "Waiting"
    rf_value: int = 0
    rf_bits: int = 0
    rf_protocol: int = 0
    rf_pulse_us: int = 0
    rf_event_time: float = 0.0


def safe_float(x, default=0.0):
    try:
        v = float(x)
        return v if math.isfinite(v) else default
    except Exception:
        return default


def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def clamp(value, low, high):
    return max(low, min(high, value))


def valid_lat_lon(lat, lon):
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0 and math.isfinite(lat) and math.isfinite(lon)


def parse_packet(obj: dict[str, Any]) -> Telemetry:
    """Compatibility parser for the older JSON packet format.

    The current Uno firmware does not use JSON; SerialManager uses
    parse_serial_line() below. This function is retained so the dashboard can
    still consume the earlier packet format during development/testing.
    """
    gps = obj.get("gps", {}) or {}
    servo = obj.get("servo", {}) or {}
    rf = obj.get("rf", {}) or {}
    mlx = obj.get("mlx90614", {}) or obj.get("mlx", {}) or {}
    imu = obj.get("imu", {}) or {}

    lat = safe_float(gps.get("lat"), SIT_LAT)
    lon = safe_float(gps.get("lon"), SIT_LON)
    gps_valid = bool(gps.get("valid", False)) and valid_lat_lon(lat, lon)
    scan_angle = clamp(safe_float(rf.get("angle_deg", servo.get("angle_deg", 90.0))), 0.0, 180.0)
    object_c = safe_float(mlx.get("object_c"))
    ambient_c = safe_float(mlx.get("ambient_c"))
    delta_c = safe_float(mlx.get("delta_c"), object_c - ambient_c)

    return Telemetry(
        timestamp=time.time(), gps_valid=gps_valid,
        lat=lat if valid_lat_lon(lat, lon) else SIT_LAT,
        lon=lon if valid_lat_lon(lat, lon) else SIT_LON,
        satellites=clamp(safe_int(gps.get("satellites", gps.get("sats", 0)), 0), 0, 99),
        altitude=safe_float(gps.get("altitude_m", gps.get("alt_m", 0.0)), 0.0),
        scan_angle=scan_angle,
        rf_data=1 if safe_int(rf.get("data"), 0) else 0,
        rf_angle=scan_angle,
        temp_available=bool(mlx.get("available", False)),
        object_c=clamp(object_c, -40.0, 200.0),
        ambient_c=clamp(ambient_c, -40.0, 125.0),
        delta_c=clamp(delta_c, -165.0, 240.0),
        imu_available=bool(imu.get("available", False)),
        roll=safe_float(imu.get("roll_deg")), pitch=safe_float(imu.get("pitch_deg")),
        accel_x=safe_float(imu.get("accel_x")), accel_y=safe_float(imu.get("accel_y")),
        accel_z=safe_float(imu.get("accel_z")), gyro_x=safe_float(imu.get("gyro_x_dps")),
        gyro_y=safe_float(imu.get("gyro_y_dps")), gyro_z=safe_float(imu.get("gyro_z_dps")),
        source="Live hardware",
        rf_value=safe_int(rf.get("value"), 0), rf_bits=safe_int(rf.get("bits"), 0),
        rf_protocol=safe_int(rf.get("protocol"), 0), rf_pulse_us=safe_int(rf.get("pulse"), 0),
        rf_event_time=time.time() if safe_int(rf.get("data"), 0) else 0.0,
    )


def _parse_num(pattern: str, text: str, default=None, flags=re.I):
    m = re.search(pattern, text, flags)
    if not m:
        return default
    try:
        return float(m.group(1))
    except (TypeError, ValueError):
        return default


def parse_serial_line(text: str, current: Telemetry, scan_angle: float, temp_baseline: float):
    """Parse one line emitted by the CURRENT Arduino Uno sketch.

    Recognized lines are intentionally narrow and match the user's firmware:
      [MPU6050] Accel(g): ax, ay, az | Gyro(deg/s): gx, gy, gz
      [TEMP   ] MPU chip temperature: T C
      [GPS    ] Lat: ... | Lng: ... | Alt: ... m | Speed: ... | Sats: ...
      [GPS    ] Module OK, searching... Satellites: N
      [GPS    ] FAULT - no data ...
      [RF433  ] Value: ... | Bits: ... | Protocol: ... | Pulse: ...

    Returns (updated Telemetry, recognized). No invented RSSI or compass
    heading is created. The MPU temperature is a clearly-labelled proxy
    channel; temp_baseline is only used to calculate a display ΔT PROXY proxy.
    """
    text = text.strip()
    now = time.time()
    a = clamp(float(scan_angle), 0.0, 180.0)

    # RF event
    if text.startswith("[RF433"):
        value = _parse_num(r"Value:\s*([-+]?\d+(?:\.\d+)?)", text, 0)
        bits = _parse_num(r"Bits:\s*(\d+)", text, 0)
        protocol = _parse_num(r"Protocol:\s*(\d+)", text, 0)
        pulse = _parse_num(r"Pulse:\s*(\d+)", text, 0)
        return replace(current, timestamp=now, rf_data=1, rf_angle=a,
                       rf_value=int(value or 0), rf_bits=int(bits or 0),
                       rf_protocol=int(protocol or 0), rf_pulse_us=int(pulse or 0),
                       rf_event_time=now, scan_angle=a, source="Live hardware"), True

    # MPU accelerometer + gyro
    if text.startswith("[MPU6050]") and "Accel(g):" in text:
        m = re.search(
            r"Accel\(g\):\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*\|\s*Gyro\(deg/s\):\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+)",
            text, re.I)
        if m:
            ax, ay, az, gx, gy, gz = [float(x) for x in m.groups()]
            # Tilt estimate from acceleration only. There is deliberately no
            # absolute compass heading because the MPU6050 has no magnetometer.
            roll = math.degrees(math.atan2(ay, az))
            pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
            return replace(current, timestamp=now, imu_available=True,
                           roll=roll, pitch=pitch, accel_x=ax, accel_y=ay, accel_z=az,
                           gyro_x=gx, gyro_y=gy, gyro_z=gz, scan_angle=a,
                           rf_angle=a, source="Live hardware"), True

    # MPU internal temperature proxy
    if text.startswith("[TEMP") and "MPU chip temperature" in text:
        t = _parse_num(r"temperature:\s*([-+]?\d*\.?\d+)\s*C", text, None)
        if t is not None:
            delta = float(t) - float(temp_baseline)
            return replace(current, timestamp=now, temp_available=True,
                           object_c=clamp(float(t), -40.0, 125.0),
                           ambient_c=clamp(float(temp_baseline), -40.0, 125.0),
                           delta_c=clamp(delta, -165.0, 165.0), scan_angle=a,
                           rf_angle=a, source="Live hardware"), True

    # GPS fix
    if text.startswith("[GPS") and "Lat:" in text and "Lng:" in text:
        lat = _parse_num(r"Lat:\s*([-+]?\d*\.?\d+)", text, None)
        lon = _parse_num(r"Lng:\s*([-+]?\d*\.?\d+)", text, None)
        alt = _parse_num(r"Alt:\s*([-+]?\d*\.?\d+)\s*m", text, current.altitude)
        sats = _parse_num(r"Sats:\s*(\d+)", text, current.satellites)
        if lat is not None and lon is not None and valid_lat_lon(lat, lon):
            return replace(current, timestamp=now, gps_valid=True, lat=lat, lon=lon,
                           altitude=float(alt or 0.0), satellites=int(sats or 0),
                           scan_angle=a, rf_angle=a, source="Live hardware"), True

    # GPS searching/fault lines are valid link information even without a fix.
    if text.startswith("[GPS") and "searching" in text.lower():
        sats = _parse_num(r"Satellites:\s*(\d+)", text, current.satellites)
        return replace(current, timestamp=now, gps_valid=False, satellites=int(sats or 0),
                       scan_angle=a, rf_angle=a, source="Live hardware"), True
    if text.startswith("[GPS") and "FAULT" in text.upper():
        return replace(current, timestamp=now, gps_valid=False, scan_angle=a,
                       rf_angle=a, source="Live hardware"), True

    # Expected diagnostic/status lines are intentionally ignored, not counted
    # as invalid packets. This prevents normal human-readable Arduino output
    # from filling the dashboard's INVALID counter.
    if text.startswith("===") or text.startswith("[MPU6050] Found") or text.startswith("[MPU6050] NOT") or text.startswith("[RF433"):
        return current, False
    return current, False


# ---------- Serial manager ----------
class SerialManager:
    """Non-blocking USB-serial reader for the Arduino Uno.

    The dashboard uses the exact current firmware link: USB -> COM7 -> 9600.
    A background thread owns the serial port so Plotly/Streamlit rendering never
    blocks on readline(). A generation token prevents an old reader thread from
    closing or overwriting a newer connection.
    """
    RF_ACTIVE_S = 1.5

    def __init__(self):
        self.lock = threading.Lock()
        self.ser = None
        self.thread = None
        self.stop_flag = True
        self.latest: Optional[Telemetry] = None
        self.last_packet_time = 0.0
        self.packet_count = 0
        self.invalid_count = 0
        self.port = ""
        self.baud = 9600
        self._generation = 0
        self.scan_angle = 90.0
        self.temp_baseline = 28.0

    def set_inputs(self, scan_angle: float, temp_baseline: float):
        with self.lock:
            self.scan_angle = clamp(float(scan_angle), 0.0, 180.0)
            self.temp_baseline = clamp(float(temp_baseline), -40.0, 125.0)

    def connect(self, port: str, baud: int = 9600):
        self.close()
        if serial is None:
            raise RuntimeError("pyserial is not installed. Run: python -m pip install pyserial")
        ser = serial.Serial(port, baudrate=int(baud), timeout=0.20)
        with self.lock:
            self.ser = ser
            self.port = port
            self.baud = int(baud)
            self.stop_flag = False
            self._generation += 1
            generation = self._generation
            self.packet_count = 0
            self.invalid_count = 0
            self.latest = None
            self.last_packet_time = 0.0
        self.thread = threading.Thread(target=self._reader, args=(ser, generation), daemon=True)
        self.thread.start()

    def _reader(self, ser, generation):
        while True:
            with self.lock:
                should_stop = self.stop_flag or generation != self._generation
                scan_angle = self.scan_angle
                temp_baseline = self.temp_baseline
                current = self.latest or Telemetry(source="Live hardware", scan_angle=scan_angle, rf_angle=scan_angle)
            if should_stop:
                break
            try:
                line = ser.readline()
                if not line:
                    continue
                text = line.decode("utf-8", errors="ignore").strip()
                if not text:
                    continue
                updated, recognized = parse_serial_line(text, current, scan_angle, temp_baseline)
                if not recognized:
                    # Normal Arduino banners/status lines are not errors.
                    continue
                with self.lock:
                    if generation != self._generation or self.stop_flag:
                        break
                    self.latest = updated
                    self.last_packet_time = time.time()
                    self.packet_count += 1
            except Exception:
                with self.lock:
                    if generation != self._generation:
                        break
                    self.invalid_count += 1

    def close(self):
        with self.lock:
            self.stop_flag = True
            self._generation += 1
            ser = self.ser
            self.ser = None
            self.port = ""
            self.thread = None
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass

    def snapshot(self):
        with self.lock:
            latest = self.latest
            # Digital RF is an event, not a latched analog signal. Clear HIGH
            # after a short display window if no new RF event arrives.
            if latest is not None and latest.rf_data and latest.rf_event_time:
                if time.time() - latest.rf_event_time > self.RF_ACTIVE_S:
                    latest = replace(latest, rf_data=0)
            return latest, self.last_packet_time, self.packet_count, self.invalid_count


# ---------- State ----------
if "serial_manager" not in st.session_state:
    st.session_state.serial_manager = SerialManager()
if "telemetry" not in st.session_state:
    st.session_state.telemetry = Telemetry()
if "position_history" not in st.session_state:
    st.session_state.position_history = []
if "observations" not in st.session_state:
    st.session_state.observations = []
if "reference_profiles" not in st.session_state:
    st.session_state.reference_profiles = {
        "thermal": [],
        "rf": [],
    }
if "manual_angle" not in st.session_state:
    st.session_state.manual_angle = 90.0
if "temp_baseline" not in st.session_state:
    st.session_state.temp_baseline = 28.0
if "override_rf" not in st.session_state:
    st.session_state.override_rf = False
if "override_temp" not in st.session_state:
    st.session_state.override_temp = False
if "override_gps" not in st.session_state:
    st.session_state.override_gps = False
if "override_angle" not in st.session_state:
    st.session_state.override_angle = False
if "auto_capture" not in st.session_state:
    st.session_state.auto_capture = False
if "last_auto_signature" not in st.session_state:
    st.session_state.last_auto_signature = None
if "manual_temp" not in st.session_state:
    st.session_state.manual_temp = 36.0
if "manual_ambient" not in st.session_state:
    st.session_state.manual_ambient = 28.0
if "manual_rf" not in st.session_state:
    st.session_state.manual_rf = 0
if "manual_lat" not in st.session_state:
    st.session_state.manual_lat = SIT_LAT
if "manual_lon" not in st.session_state:
    st.session_state.manual_lon = SIT_LON
if "way_lat" not in st.session_state:
    st.session_state.way_lat = SIT_LAT
if "way_lon" not in st.session_state:
    st.session_state.way_lon = SIT_LON


def get_live():
    sm = st.session_state.serial_manager
    latest, last_t, count, invalid = sm.snapshot()
    if latest is not None:
        st.session_state.telemetry = latest
    return st.session_state.telemetry, last_t, count, invalid


telemetry, last_packet, packet_count, invalid_packets = get_live()


# ---------- Derived analysis ----------
def unit_vector_from_angle(angle_deg: float):
    # Navigation convention: 0° = North, 90° = East, clockwise positive.
    # X is East and Y is North so the vector frame matches GPS bearing.
    a = math.radians(angle_deg)
    return math.sin(a), math.cos(a)


def vector_from_observations(obs):
    if not obs:
        return {"rf": (0, 0), "thermal": (0, 0), "resultant": (0, 0),
                "rf_mag": 0, "thermal_mag": 0, "resultant_mag": 0,
                "rf_dir": None, "thermal_dir": None, "resultant_dir": None,
                "rf_weight": 0, "thermal_weight": 0, "agreement": None,
                "coverage": 0.0, "observation_depth": 0.0,
                "agreement_score": 0.0, "quality": 0.0}

    rf_rows = [x for x in obs if x["rf"] == 1]
    thermal_rows = [x for x in obs if x["delta"] > 0]
    rf_dir = None
    thermal_dir = None
    rf_mag = 0.0
    thermal_mag = 0.0

    if rf_rows:
        # Digital RF has no amplitude; use angular concentration/detection density,
        # not fabricated RSSI.
        xs = sum(unit_vector_from_angle(x["angle"])[0] for x in rf_rows)
        ys = sum(unit_vector_from_angle(x["angle"])[1] for x in rf_rows)
        rf_mag = min(1.0, math.hypot(xs, ys) / max(1, len(rf_rows)))
        rf_dir = math.degrees(math.atan2(xs, ys)) % 360

    if thermal_rows:
        # Thermal response uses non-negative ΔT PROXY as the observation weight.
        weights = [max(0.0, x["delta"]) for x in thermal_rows]
        sx = sy = 0.0
        for x, w in zip(thermal_rows, weights):
            ux, uy = unit_vector_from_angle(x["angle"])
            sx += ux * w
            sy += uy * w
        thermal_mag = min(1.0, math.hypot(sx, sy) / max(1.0, sum(weights)))
        if math.hypot(sx, sy) > 0:
            thermal_dir = math.degrees(math.atan2(sx, sy)) % 360

    # Conservative weighting: thermal gets weight proportional to normalized
    # positive contrast; RF is evidence-only and receives a lower weight because
    # the installed receiver is digital rather than analog RSSI.
    if rf_dir is not None and thermal_dir is not None:
        rf_weight = 0.40
        thermal_weight = 0.60
    elif thermal_dir is not None:
        rf_weight, thermal_weight = 0.0, 1.0
    elif rf_dir is not None:
        rf_weight, thermal_weight = 1.0, 0.0
    else:
        rf_weight = thermal_weight = 0.0

    sx = sy = 0.0
    if rf_dir is not None:
        ux, uy = unit_vector_from_angle(rf_dir)
        sx += rf_weight * ux
        sy += rf_weight * uy
    if thermal_dir is not None:
        ux, uy = unit_vector_from_angle(thermal_dir)
        sx += thermal_weight * ux
        sy += thermal_weight * uy

    result_mag = math.hypot(sx, sy)
    result_dir = math.degrees(math.atan2(sx, sy)) % 360 if result_mag else None

    agreement = None
    if rf_dir is not None and thermal_dir is not None:
        d = abs(rf_dir - thermal_dir) % 360
        agreement = min(d, 360 - d)

    unique_angles = sorted({max(0, min(180, int(round(float(x.get("angle", 0))))) ) for x in obs})
    coverage = min(1.0, len(unique_angles) / 13.0)
    observation_depth = min(1.0, len(obs) / 10.0)
    agreement_score = (1.0 if agreement is None and (rf_dir is None or thermal_dir is None) else
                       max(0.0, 1.0 - agreement / 90.0)) if agreement is not None else 0.0
    coherence = result_mag
    # Evidence quality is deliberately conservative: depth, angular coverage,
    # directional coherence and cross-sensor agreement all matter.
    quality = min(1.0, (0.30 * observation_depth) + (0.25 * coverage) +
                  (0.25 * coherence) + (0.20 * agreement_score)) if obs else 0.0

    return {
        "rf": unit_vector_from_angle(rf_dir) if rf_dir is not None else (0, 0),
        "thermal": unit_vector_from_angle(thermal_dir) if thermal_dir is not None else (0, 0),
        "resultant": (sx, sy),
        "rf_mag": rf_mag,
        "thermal_mag": thermal_mag,
        "resultant_mag": result_mag,
        "rf_dir": rf_dir,
        "thermal_dir": thermal_dir,
        "resultant_dir": result_dir,
        "rf_weight": rf_weight,
        "thermal_weight": thermal_weight,
        "agreement": agreement,
        "coverage": coverage,
        "observation_depth": observation_depth,
        "agreement_score": agreement_score,
        "quality": quality,
    }


def destination_ring(lat, lon, radius_m, points=96):
    """Return latitude/longitude points for a geodesic circle around a center."""
    radius_m = max(0.0, float(radius_m))
    points = max(12, int(points))
    if radius_m == 0:
        return [float(lat)], [float(lon)]
    earth_radius = 6371000.0
    lat0 = math.radians(float(lat))
    lon0 = math.radians(float(lon))
    angular = radius_m / earth_radius
    lats, lons = [], []
    for bearing in np.linspace(0.0, 360.0, points + 1):
        br = math.radians(float(bearing))
        lat2 = math.asin(
            math.sin(lat0) * math.cos(angular)
            + math.cos(lat0) * math.sin(angular) * math.cos(br)
        )
        lon2 = lon0 + math.atan2(
            math.sin(br) * math.sin(angular) * math.cos(lat0),
            math.cos(angular) - math.sin(lat0) * math.sin(lat2),
        )
        lats.append(math.degrees(lat2))
        lons.append((math.degrees(lon2) + 540.0) % 360.0 - 180.0)
    return lats, lons


def source_estimate(lat, lon, bearing_deg, distance_m):
    if bearing_deg is None:
        return lat, lon
    R = 6371000.0
    br = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    d = distance_m / R
    lat2 = math.asin(math.sin(lat1) * math.cos(d) +
                     math.cos(lat1) * math.sin(d) * math.cos(br))
    lon2 = lon1 + math.atan2(
        math.sin(br) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)


# ---------- Plot helpers ----------
def base_fig(height=360):
    fig = go.Figure()
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="DM Sans"),
        margin=dict(l=12, r=12, t=18, b=12),
        hoverlabel=dict(bgcolor=SURFACE_3, font_color=TEXT),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
    )
    return fig


def angular_sensor_fig(obs, sensor="thermal", current_angle=90.0, current_rf=0, current_delta=0.0):
    rows = sorted(obs, key=lambda x: float(x.get("angle", 0)))
    fig = go.Figure()
    common = dict(
        height=410,
        paper_bgcolor="#11181e", plot_bgcolor="#11181e",
        font=dict(color=TEXT, family="DM Sans"),
        margin=dict(l=12, r=12, t=18, b=18), showlegend=False,
        hoverlabel=dict(bgcolor=SURFACE_3, font_color=TEXT),
        polar=dict(
            bgcolor="#0e151a",
            radialaxis=dict(showticklabels=False, showline=False, gridcolor="#27343b", range=[0, 1.18]),
            angularaxis=dict(direction="clockwise", rotation=90, dtick=30, gridcolor="#27343b", color=MUTED),
        ),
    )
    fig.update_layout(**common)
    ring_theta = np.linspace(0, 360, 181)
    for rr, dash in [(0.38, "dot"), (0.72, "dot"), (1.0, "solid")]:
        fig.add_trace(go.Scatterpolar(r=[rr] * len(ring_theta), theta=ring_theta, mode="lines",
                                      line=dict(color="#26343b", width=1, dash=dash), hoverinfo="skip", showlegend=False))
    current_angle = clamp(float(current_angle), 0.0, 180.0)

    if sensor == "rf":
        # Digital receiver: encode only state and angular occurrence, never amplitude.
        for state, radius, color, symbol in [(1, 1.0, RF, "circle"), (0, .62, "#53616a", "circle-open")]:
            subset = [r for r in rows if int(r.get("rf", 0)) == state]
            if subset:
                fig.add_trace(go.Scatterpolar(
                    r=[radius] * len(subset), theta=[float(r["angle"]) for r in subset],
                    mode="markers", marker=dict(size=12 if state else 9, color=color, symbol=symbol,
                                                 line=dict(color=BG, width=1.5)),
                    name="HIGH" if state else "LOW",
                    hovertemplate=("<b>RF HIGH</b><br>Scan angle %{theta:.0f}°<extra></extra>" if state else
                                   "RF LOW<br>Scan angle %{theta:.0f}°<extra></extra>"),
                    showlegend=False,
                ))
        # Connect the sampled states in angular order as a stepped detection envelope.
        fig.add_trace(go.Scatterpolar(
            r=[1.0 if int(r.get("rf", 0)) else .62 for r in rows],
            theta=[float(r["angle"]) for r in rows], mode="lines",
            line=dict(color=RF, width=2, shape="linear"), opacity=.75,
            hovertemplate="Angle %{theta:.0f}°<br>DATA %{r:.0f}<extra></extra>", showlegend=False,
        ))
        # Always show the current live scan state, even when no observations
        # have been recorded yet. LOW means the receiver is alive but no RF
        # event is detected at the current manual scan angle.
        live_radius = 1.0 if int(current_rf) else 0.62
        live_symbol = "circle" if int(current_rf) else "circle-open"
        live_color = RF if int(current_rf) else "#66737b"
        fig.add_trace(go.Scatterpolar(
            r=[live_radius], theta=[current_angle], mode="markers+text",
            marker=dict(size=15 if int(current_rf) else 11, color=live_color, symbol=live_symbol,
                        line=dict(color=BG, width=1.5)),
            text=["LIVE HIGH" if int(current_rf) else "LIVE LOW"],
            textposition="top center",
            textfont=dict(color=RF if int(current_rf) else "#8b979e", size=8, family="IBM Plex Mono"),
            hovertemplate=(f"<b>RF {'HIGH' if int(current_rf) else 'LOW'}</b><br>Live scan angle {current_angle:.0f}°<br>"
                           + ("Digital event detected<extra></extra>" if int(current_rf) else "No RF event detected<extra></extra>")),
            showlegend=False,
        ))
        fig.add_annotation(text="LIVE HIGH" if int(current_rf) else "LIVE LOW · NO EVENT",
                           x=.5, y=.51, xref="paper", yref="paper", showarrow=False,
                           font=dict(color=RF if int(current_rf) else "#6d7981", size=8, family="IBM Plex Mono"))
    else:
        vals = [max(0.0, float(r.get("delta", 0))) for r in rows]
        peak = max(vals) if vals else 0
        scale = peak if peak > 0 else 1.0
        # Filled-looking thermal envelope using a faint baseline plus observed line.
        rr = [.08 + .88 * min(1.0, v / scale) for v in vals]
        fig.add_trace(go.Scatterpolar(
            r=rr, theta=[float(r["angle"]) for r in rows], mode="lines+markers",
            line=dict(color=THERMAL, width=3, shape="spline"),
            marker=dict(size=8, color=THERMAL, line=dict(color=BG, width=1.3)),
            fill="toself", fillcolor="rgba(230,184,75,.055)",
            hovertemplate="<b>Thermal response</b><br>Angle %{theta:.0f}°<br>ΔT PROXY %{customdata:+.2f} °C<extra></extra>",
            customdata=vals, showlegend=False,
        ))
        if peak > 0:
            i = int(np.argmax(vals))
            fig.add_trace(go.Scatterpolar(
                r=[rr[i]], theta=[float(rows[i]["angle"])], mode="markers+text",
                marker=dict(size=13, color=TEXT, symbol="diamond", line=dict(color=THERMAL, width=2)),
                text=["PEAK"], textposition="top center", textfont=dict(color=THERMAL, size=9),
                hovertemplate=f"<b>Thermal peak</b><br>{float(rows[i]['angle']):.0f}° · {peak:+.2f} °C<extra></extra>",
                showlegend=False,
            ))
        # Always show the current temperature-proxy sample. This keeps the
        # field visibly live even before the user records an observation.
        live_delta = float(current_delta)
        thermal_scale = max(peak, abs(live_delta), 1.0)
        live_rr = .08 + .88 * min(1.0, max(0.0, live_delta) / thermal_scale)
        fig.add_trace(go.Scatterpolar(
            r=[live_rr], theta=[current_angle], mode="markers+text",
            marker=dict(size=14, color=THERMAL, symbol="diamond-open", line=dict(color=THERMAL, width=2)),
            text=["LIVE"], textposition="top center",
            textfont=dict(color=THERMAL, size=8, family="IBM Plex Mono"),
            hovertemplate=f"<b>Live temperature proxy</b><br>Scan angle {current_angle:.0f}°<br>ΔT PROXY {live_delta:+.2f} °C<extra></extra>",
            showlegend=False,
        ))
        fig.add_annotation(text="LIVE ΔT PROXY", x=.5, y=.51, xref="paper", yref="paper", showarrow=False,
                           font=dict(color="#6d7981", size=8, family="IBM Plex Mono"))
    fig.add_annotation(text="N", x=.5, y=1.035, xref="paper", yref="paper", showarrow=False,
                       font=dict(color=TEXT, size=10, family="IBM Plex Mono"))
    return fig


def vector_fig(v):
    fig = go.Figure()
    fig.update_layout(
        height=500, paper_bgcolor="#11181e", plot_bgcolor="#11181e", font=dict(color=TEXT, family="DM Sans"),
        margin=dict(l=18, r=18, t=20, b=18), showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=9), orientation="h", x=.02, y=1.05),
        polar=dict(bgcolor="#0e151a",
                   radialaxis=dict(range=[0,1.12], showticklabels=False, gridcolor="#26343b", showline=False),
                   angularaxis=dict(direction="clockwise", rotation=90, dtick=30, gridcolor="#26343b", color=MUTED)),
        hoverlabel=dict(bgcolor=SURFACE_3, font_color=TEXT),
    )
    theta = np.linspace(0, 360, 181)
    for r, dash in [(0.33, "dot"), (0.66, "dot"), (1.0, "solid")]:
        fig.add_trace(go.Scatterpolar(r=[r]*len(theta), theta=theta, mode="lines",
                                      line=dict(color="#25323a", width=1, dash=dash), hoverinfo="skip", showlegend=False))
    # Four cardinal axes for an unmistakable north/east frame.
    fig.add_trace(go.Scatterpolar(r=[0,1.05], theta=[0,0], mode="lines", line=dict(color="#34424a", width=1), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatterpolar(r=[0,1.05], theta=[90,90], mode="lines", line=dict(color="#34424a", width=1), showlegend=False, hoverinfo="skip"))
    rows = sorted(st.session_state.observations, key=lambda x: float(x.get("angle",0)))
    rf_rows = [r for r in rows if int(r.get("rf",0)) == 1]
    if rf_rows:
        fig.add_trace(go.Scatterpolar(r=[.96]*len(rf_rows), theta=[float(r["angle"]) for r in rf_rows], mode="markers",
                                      marker=dict(size=8, color=RF, line=dict(color=BG, width=1)), name="RF evidence",
                                      hovertemplate="RF evidence · %{theta:.0f}°<extra></extra>"))
    thermal_rows = [r for r in rows if float(r.get("delta",0)) > 0]
    if thermal_rows:
        mx = max(float(r.get("delta",0)) for r in thermal_rows) or 1.0
        fig.add_trace(go.Scatterpolar(r=[.30+.58*min(1,float(r.get("delta",0))/mx) for r in thermal_rows],
                                      theta=[float(r["angle"]) for r in thermal_rows], mode="markers",
                                      marker=dict(size=8, color=THERMAL, line=dict(color=BG, width=1)), name="Thermal evidence",
                                      customdata=[float(r.get("delta",0)) for r in thermal_rows],
                                      hovertemplate="Thermal evidence · %{theta:.0f}°<br>ΔT PROXY %{customdata:+.1f} °C<extra></extra>"))
    vectors = [("RF", v["rf_dir"], v["rf_mag"], RF, 2.8), ("THERMAL", v["thermal_dir"], v["thermal_mag"], THERMAL, 2.8),
               ("RESULTANT", v["resultant_dir"], min(1.0, v["resultant_mag"]), RESULTANT, 5.2)]
    for name, direction, mag, color, width in vectors:
        if direction is None or mag <= 0: continue
        end = max(.15, mag)
        fig.add_trace(go.Scatterpolar(r=[0,end], theta=[direction,direction], mode="lines+markers",
                                      line=dict(color=color, width=width), marker=dict(size=[4,11], color=color),
                                      name=name, hovertemplate=f"{name} · %{{theta:.1f}}°<br>Magnitude %{{r:.2f}}<extra></extra>"))
    if v["rf_dir"] is not None and v["thermal_dir"] is not None:
        # Short arc showing the actual separation between sensor bearings.
        d = v["agreement"] or 0
        start = v["rf_dir"]
        step = d / max(8, int(d/4)+1) if d else 1
        arc = [((start + i*step) % 360) for i in range(max(2, int(d/step)+1))]
        fig.add_trace(go.Scatterpolar(r=[.18]*len(arc), theta=arc, mode="lines", line=dict(color="#9ba7ad", width=2),
                                      name="Angular separation", hovertemplate="Separation %{customdata:.1f}°<extra></extra>",
                                      customdata=[d]*len(arc), showlegend=False))
        fig.add_annotation(text=f"Δ {d:.1f}°", x=.5, y=.08, xref="paper", yref="paper", showarrow=False,
                           font=dict(color=MUTED, size=9, family="IBM Plex Mono"))
    fig.add_annotation(text="N", x=.5, y=1.035, xref="paper", yref="paper", showarrow=False,
                       font=dict(color=TEXT, size=10, family="IBM Plex Mono"))
    fig.add_annotation(text="E", x=.95, y=.5, xref="paper", yref="paper", showarrow=False,
                       font=dict(color=GPS, size=9, family="IBM Plex Mono"))
    if v["resultant_dir"] is None:
        fig.add_annotation(text="AWAITING MULTI-SENSOR EVIDENCE", x=.5, y=.5, xref="paper", yref="paper", showarrow=False,
                           font=dict(color=DIM, size=11, family="IBM Plex Mono"))
    return fig


def map_fig(lat, lon, source_lat=None, source_lon=None, trail=None, bearing=None, radius_m=25, waypoint_lat=None, waypoint_lon=None):
    # Keep the original field-map presentation: familiar OSM geography, with
    # restrained engineering overlays layered on top.
    fig = go.Figure()
    if trail:
        fig.add_trace(go.Scattermap(lat=[p[0] for p in trail], lon=[p[1] for p in trail], mode="lines+markers",
                                    line=dict(color=GPS, width=3), marker=dict(size=5), name="Position history",
                                    hovertemplate="%{lat:.6f}, %{lon:.6f}<extra></extra>"))
    ring_lat, ring_lon = destination_ring(lat, lon, radius_m)
    fig.add_trace(go.Scattermap(lat=ring_lat, lon=ring_lon, mode="lines",
                                line=dict(color="rgba(110,155,189,.55)", width=1.5), name=f"Scan radius · {radius_m:.0f} m", hoverinfo="skip"))
    fig.add_trace(go.Scattermap(lat=[lat], lon=[lon], mode="markers+text", marker=dict(size=13, color=GPS),
                                text=["REFERENCE"], textposition="top right", textfont=dict(color=TEXT, size=9),
                                name="Reference position", hovertemplate="Reference<br>%{lat:.6f}, %{lon:.6f}<extra></extra>"))
    if waypoint_lat is not None and waypoint_lon is not None and (abs(waypoint_lat-lat)>1e-7 or abs(waypoint_lon-lon)>1e-7):
        fig.add_trace(go.Scattermap(lat=[waypoint_lat], lon=[waypoint_lon], mode="markers+text",
                                    marker=dict(size=11, color="#aeb9c0", symbol="diamond"), text=["WAYPOINT"], textposition="top right",
                                    textfont=dict(color=TEXT, size=9), name="Reference waypoint",
                                    hovertemplate="Waypoint<br>%{lat:.6f}, %{lon:.6f}<extra></extra>"))
        fig.add_trace(go.Scattermap(lat=[lat, waypoint_lat], lon=[lon, waypoint_lon], mode="lines",
                                    line=dict(color="rgba(174,185,192,.55)", width=2), name="Waypoint leg", hoverinfo="skip"))
    if source_lat is not None and source_lon is not None:
        u_lat, u_lon = destination_ring(source_lat, source_lon, 8, points=48)
        fig.add_trace(go.Scattermap(lat=u_lat, lon=u_lon, mode="lines", line=dict(color="rgba(230,184,75,.62)", width=1.5),
                                    name="Estimated source region", hoverinfo="skip"))
        fig.add_trace(go.Scattermap(lat=[source_lat], lon=[source_lon], mode="markers",
                                    marker=dict(size=10, color=THERMAL, symbol="diamond"), name="Estimated source region",
                                    hovertemplate="Estimated source region<br>%{lat:.6f}, %{lon:.6f}<extra></extra>"))
    if bearing is not None:
        end_lat, end_lon = source_estimate(lat, lon, bearing, radius_m)
        fig.add_trace(go.Scattermap(lat=[lat, end_lat], lon=[lon, end_lon], mode="lines",
                                    line=dict(color=RESULTANT, width=4), name="Resultant direction", hoverinfo="skip"))
    fig.update_layout(height=540, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)",
                      map=dict(style="open-street-map", center=dict(lat=lat, lon=lon), zoom=17),
                      legend=dict(bgcolor="rgba(11,15,18,.88)", bordercolor=BORDER, borderwidth=1,
                                  font=dict(color=TEXT, size=9), orientation="h", y=.02, x=.02))
    return fig


def _run_integrity_checks():
    """Exercise geometry, analysis and every Plotly figure path before UI rendering."""
    empty = vector_from_observations([])
    assert empty["resultant_dir"] is None
    assert empty["quality"] == 0.0

    sample = [
        {"time": "00:00:01", "angle": 0.0, "rf": 1, "object": 36.0, "ambient": 28.0, "delta": 8.0},
        {"time": "00:00:02", "angle": 30.0, "rf": 1, "object": 35.0, "ambient": 28.0, "delta": 7.0},
        {"time": "00:00:03", "angle": 60.0, "rf": 0, "object": 33.0, "ambient": 28.0, "delta": 5.0},
    ]
    analysis = vector_from_observations(sample)
    assert analysis["resultant_dir"] is not None
    assert 0.0 <= analysis["quality"] <= 1.0
    assert 0.0 <= analysis["coverage"] <= 1.0

    ring_lat, ring_lon = destination_ring(SIT_LAT, SIT_LON, 25)
    assert len(ring_lat) == len(ring_lon) and len(ring_lat) > 12
    source_estimate(SIT_LAT, SIT_LON, 90.0, 25.0)

    angular_sensor_fig([], "rf", current_angle=90.0, current_rf=0, current_delta=0.0)
    angular_sensor_fig([], "thermal", current_angle=90.0, current_rf=0, current_delta=8.0)
    angular_sensor_fig(sample, "rf")
    angular_sensor_fig(sample, "thermal")

    previous = st.session_state.get("observations", [])
    st.session_state.observations = sample
    vector_fig(analysis)
    map_fig(
        SIT_LAT, SIT_LON,
        source_lat=SIT_LAT, source_lon=SIT_LON,
        trail=[(SIT_LAT, SIT_LON)],
        bearing=analysis["resultant_dir"],
        radius_m=25,
        waypoint_lat=SIT_LAT + 0.001, waypoint_lon=SIT_LON + 0.001,
    )
    st.session_state.observations = previous


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="sdr-brand">SUDARSHAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-subbrand">Multi-sensor spatial sensing & navigation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-kicker">Workspace</div>', unsafe_allow_html=True)
    page = st.radio("Workspace", ["Overview", "Sensor Field", "Vector Fusion", "System"], label_visibility="collapsed")
    st.markdown('<div class="sdr-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-kicker">Acquisition</div>', unsafe_allow_html=True)
    mode = st.selectbox("Input mode", ["Live hardware", "Manual / reference"], label_visibility="collapsed")
    if mode == "Live hardware":
        ports = [p.device for p in serial.tools.list_ports.comports()] if serial is not None else []
        if not ports:
            ports = ["No serial ports detected"]
        port = st.selectbox("Serial port", ports, index=0)
        baud = st.selectbox("Baud", [9600, 115200], index=0)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Connect", use_container_width=True, disabled=port == "No serial ports detected"):
                try:
                    st.session_state.serial_manager.connect(port, baud)
                    st.toast("Serial acquisition connected")
                except Exception as e:
                    st.error(f"Unable to connect: {e}")
        with c2:
            if st.button("Disconnect", use_container_width=True):
                st.session_state.serial_manager.close()
    else:
        st.markdown('<div class="sidebar-note">Reference values are explicit inputs, not disguised live telemetry.</div>', unsafe_allow_html=True)
        st.session_state.manual_lat = st.number_input("Reference latitude", value=float(st.session_state.manual_lat), format="%.6f")
        st.session_state.manual_lon = st.number_input("Reference longitude", value=float(st.session_state.manual_lon), format="%.6f")
    st.markdown('<div class="sdr-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-kicker">Reference waypoint</div>', unsafe_allow_html=True)
    st.session_state.way_lat = st.number_input("Waypoint latitude", value=float(st.session_state.way_lat), format="%.6f")
    st.session_state.way_lon = st.number_input("Waypoint longitude", value=float(st.session_state.way_lon), format="%.6f")
    st.markdown('<div class="sdr-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-kicker">Live / Demo Controls</div>', unsafe_allow_html=True)
    st.session_state.manual_angle = st.number_input("Manual scan angle (°)", 0.0, 180.0, float(st.session_state.manual_angle), 1.0, key="sidebar_scan_angle")
    st.session_state.temp_baseline = st.number_input("Temperature proxy baseline (°C)", -20.0, 80.0, float(st.session_state.temp_baseline), 0.5, key="sidebar_temp_baseline")
    st.session_state.override_angle = st.checkbox("DEMO override: angle", value=st.session_state.override_angle, key="ov_angle")
    st.session_state.override_rf = st.checkbox("DEMO override: RF", value=st.session_state.override_rf, key="ov_rf")
    st.session_state.override_temp = st.checkbox("DEMO override: temperature", value=st.session_state.override_temp, key="ov_temp")
    st.session_state.override_gps = st.checkbox("DEMO override: GPS", value=st.session_state.override_gps, key="ov_gps")
    if st.session_state.override_rf:
        st.session_state.manual_rf = st.selectbox("DEMO RF DATA", [0, 1], index=int(st.session_state.manual_rf), format_func=lambda x: "HIGH" if x else "LOW", key="demo_rf")
    if st.session_state.override_temp:
        st.session_state.manual_temp = st.number_input("DEMO temperature (°C)", -40.0, 125.0, float(st.session_state.manual_temp), 0.1, key="demo_temp")
    if st.session_state.override_gps:
        st.session_state.manual_lat = st.number_input("DEMO latitude", -90.0, 90.0, float(st.session_state.manual_lat), format="%.6f", key="demo_lat")
        st.session_state.manual_lon = st.number_input("DEMO longitude", -180.0, 180.0, float(st.session_state.manual_lon), format="%.6f", key="demo_lon")
    st.session_state.auto_capture = st.checkbox("Auto-record changed live readings", value=st.session_state.auto_capture, key="auto_capture_box")
    st.markdown('<div class="sidebar-note">DEMO controls are explicit overrides. LIVE hardware values remain visible when overrides are off.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sdr-kicker">Project</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-note">Spatial observation, angular response analysis and weighted vector fusion for robotics, search-and-rescue, environmental and industrial sensing use cases.</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-note"><b style="color:#f1eee7">Tannishtha Gupta · Dhvan Shah</b><br>Student engineering prototype · v{APP_VERSION}</div>', unsafe_allow_html=True)


# ---------- Input selection ----------
if mode == "Manual / reference":
    st.session_state.telemetry = Telemetry(
        gps_valid=True,
        lat=float(st.session_state.manual_lat),
        lon=float(st.session_state.manual_lon),
        satellites=0,
        scan_angle=float(st.session_state.manual_angle),
        rf_data=int(st.session_state.manual_rf),
        rf_angle=float(st.session_state.manual_angle),
        temp_available=True,
        object_c=float(st.session_state.manual_temp),
        ambient_c=float(st.session_state.manual_ambient),
        delta_c=float(st.session_state.manual_temp - st.session_state.manual_ambient),
        imu_available=False,
        source="Manual / reference",
    )
    telemetry = st.session_state.telemetry

def apply_demo_overrides(t: Telemetry) -> Telemetry:
    """Apply only explicitly enabled, independently-labelled demo overrides."""
    out = t
    if st.session_state.override_angle:
        a = float(st.session_state.manual_angle)
        out = replace(out, scan_angle=a, rf_angle=a)
    if st.session_state.override_rf:
        out = replace(out, rf_data=int(st.session_state.manual_rf), rf_angle=float(st.session_state.manual_angle))
    if st.session_state.override_temp:
        temp = float(st.session_state.manual_temp)
        base = float(st.session_state.temp_baseline)
        out = replace(out, temp_available=True, object_c=temp, ambient_c=base, delta_c=temp-base)
    if st.session_state.override_gps:
        out = replace(out, gps_valid=True, lat=float(st.session_state.manual_lat), lon=float(st.session_state.manual_lon))
    if any((st.session_state.override_angle, st.session_state.override_rf, st.session_state.override_temp, st.session_state.override_gps)):
        out = replace(out, source="LIVE HARDWARE + DEMO OVERRIDE")
    return out

# The fragment below owns the live display refresh. Pull a fresh thread-safe
# snapshot inside the fragment so the UI does not freeze on the telemetry object
# captured during the initial Streamlit run.
# ---------- Live application workspace ----------
# The acquisition thread runs independently; the visual workspace refreshes at a
# controlled cadence so the map/charts remain responsive during demonstration.
def tile(label, value, sub="", accent=GPS):
    return (
        f'<div class="sdr-tile">'
        f'<div class="sdr-tile-label">{label}</div>'
        f'<div class="sdr-tile-value" style="color:{accent}">{value}</div>'
        f'<div class="sdr-tile-sub">{sub}</div></div>'
    )


def section_head(kicker, title, meta=""):
    st.markdown(
        f'<div class="sdr-section-head"><div><div class="sdr-section-kicker">{kicker}</div>'
        f'<div class="sdr-section-title">{title}</div></div>'
        f'<div class="sdr-section-meta">{meta}</div></div>',
        unsafe_allow_html=True,
    )


def html_rows(rows):
    bits = []
    for label, value, accent in rows:
        bits.append(
            f'<div class="sdr-row"><span>{label}</span>'
            f'<strong style="color:{accent or TEXT}">{value}</strong></div>'
        )
    return "".join(bits)


def sweep_strip(obs):
    angles = sorted({max(0, min(180, int(round(float(x.get("angle", 0))))) ) for x in obs})
    marks = []
    for a in angles:
        rows = [x for x in obs if int(round(float(x.get("angle", 0)))) == a]
        rf_hit = any(int(x.get("rf", 0)) == 1 for x in rows)
        therm = max([float(x.get("delta", 0)) for x in rows] + [0])
        pct = a / 180 * 100
        color = RF if rf_hit else (THERMAL if therm > 0 else DIM)
        marks.append(f'<i style="left:{pct:.2f}%;background:{color}" title="{a}°"></i>')
    return (
        '<div class="sweep-wrap"><div class="sweep-axis"><span>0° N</span>'
        '<span>90° E</span><span>180° S</span></div>'
        '<div class="sweep-track">' + "".join(marks) + '</div>'
        '<div class="sweep-label">ANGULAR COVERAGE · ' + f'{len(angles)} UNIQUE POSITIONS' + '</div></div>'
    )


def compact_quality(v):
    q = float(v.get("quality", 0.0))
    return max(0, min(100, round(q * 100)))


@st.fragment(run_every=1.0)
def render_workspace():
    global telemetry, last_packet, packet_count, invalid_packets
    sm = st.session_state.serial_manager
    sm.set_inputs(st.session_state.manual_angle, st.session_state.temp_baseline)
    latest, last_packet, packet_count, invalid_packets = sm.snapshot()
    if latest is not None:
        st.session_state.telemetry = latest
    telemetry = apply_demo_overrides(st.session_state.telemetry)

    # Keep the live GPS trail inside the fragment so it updates with the
    # background serial reader without requiring a full-page rerun.
    if telemetry.gps_valid:
        p = (telemetry.lat, telemetry.lon)
        if not st.session_state.position_history or (
            abs(p[0] - st.session_state.position_history[-1][0]) > 1e-7
            or abs(p[1] - st.session_state.position_history[-1][1]) > 1e-7
        ):
            st.session_state.position_history.append(p)
            st.session_state.position_history = st.session_state.position_history[-200:]

    header_titles = {
        "Overview": ("01 / FIELD", "Spatial field", "Live position, reference geometry and estimated source region"),
        "Sensor Field": ("02 / SENSOR FIELD", "Angular instrumentation", "RF detection and thermal response across the scan arc"),
        "Vector Fusion": ("03 / VECTOR FUSION", "Directional synthesis", "Independent sensor evidence resolved into a common bearing frame"),
        "System": ("04 / SYSTEM", "Engineering console", "Acquisition link, hardware topology and current telemetry"),
    }
    kicker, title, subtitle = header_titles[page]
    st.markdown(
        f'<div class="sdr-pagehead"><div><div class="sdr-kicker">{kicker}</div>'
        f'<div class="sdr-title">{title}</div><div class="sdr-caption">{subtitle}</div></div>'
        f'<div class="sdr-pagecode">SUDARSHAN / SPATIAL SENSING · v{APP_VERSION}</div></div>',
        unsafe_allow_html=True,
    )

    obs = st.session_state.observations
    v = vector_from_observations(obs)
    base_lat = telemetry.lat if telemetry.gps_valid else st.session_state.manual_lat
    base_lon = telemetry.lon if telemetry.gps_valid else st.session_state.manual_lon
    bearing = v["resultant_dir"]
    src_lat, src_lon = source_estimate(base_lat, base_lon, bearing, 25) if bearing is not None else (None, None)
    quality = compact_quality(v)
    coverage = round(v.get("coverage", 0) * 100)

    # ---------- Overview ----------
    if page == "Overview":
        position_source = "GPS FIX" if telemetry.gps_valid else "MANUAL REFERENCE"
        position_color = GOOD if telemetry.gps_valid else WARN
        st.markdown(
            '<div class="sdr-commandbar">'
            f'<span><b>POSITION SOURCE</b> <em style="color:{position_color}">● {position_source}</em></span>'
            f'<span><b>SCAN RADIUS</b> 25 m</span>'
            f'<span><b>OBSERVATIONS</b> {len(obs):02d}</span>'
            f'<span><b>EVIDENCE</b> {quality:02d}%</span>'
            '</div>', unsafe_allow_html=True)

        left, right = st.columns([2.15, 1], gap="large")
        with left:
            with st.container(border=True):
                st.markdown('<div class="chart-shell-head"><b>LIVE SPATIAL FIELD</b><span>REFERENCE · SCAN RADIUS · RESULTANT</span></div>', unsafe_allow_html=True)
                st.plotly_chart(
                    map_fig(base_lat, base_lon, src_lat, src_lon, st.session_state.position_history, bearing, 25,
                            st.session_state.way_lat, st.session_state.way_lon),
                    use_container_width=True, config={"displayModeBar": False}, key="overview_map",
                )
                st.markdown('<div class="chart-foot">Reference position, working radius, waypoint geometry and estimated source region.</div>', unsafe_allow_html=True)
        with right:
            with st.container(border=True):
                st.markdown('<div class="readout-head">POSITION FIX</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="coord">{base_lat:.6f}° <span>N</span></div><div class="coord sub">{base_lon:.6f}° <span>E</span></div>', unsafe_allow_html=True)
                st.markdown(html_rows([
                    ("Satellites", str(telemetry.satellites) if telemetry.gps_valid else "—", GPS),
                    ("Altitude", f"{telemetry.altitude:.1f} m" if telemetry.gps_valid else "—", TEXT),
                    ("Acquisition", position_source, position_color),
                ]), unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<div class="readout-head">SPATIAL SOLUTION</div>', unsafe_allow_html=True)
                st.markdown(html_rows([
                    ("Resultant bearing", f"{bearing:.1f}°" if bearing is not None else "Awaiting scan", RESULTANT),
                    ("Working distance", "25.0 m", GPS),
                    ("Estimated region", "Available" if bearing is not None else "Awaiting evidence", THERMAL if bearing is not None else MUTED),
                    ("Evidence quality", f"{quality}%" if obs else "—", GOOD if quality >= 70 else WARN),
                ]), unsafe_allow_html=True)

        st.markdown('<div class="tile-grid five">' +
                    tile("GPS", "FIX" if telemetry.gps_valid else "REF", "position source", GOOD if telemetry.gps_valid else WARN) +
                    tile("RF", "HIGH" if telemetry.rf_data else "LOW", "digital DATA", RF if telemetry.rf_data else MUTED) +
                    tile("TEMP PROXY", f"{telemetry.object_c:.1f} °C" if telemetry.temp_available else "—", "MPU6050 internal temperature", THERMAL) +
                    tile("IMU", "READY" if telemetry.imu_available else "—", "orientation", GPS) +
                    tile("SCAN", f"{coverage}%", "angular coverage", RESULTANT) + '</div>', unsafe_allow_html=True)

        a, b, c = st.columns([1.2, 1.2, 1], gap="large")
        with a:
            with st.container(border=True):
                st.markdown('<div class="micro-title">REFERENCE / WAYPOINT</div>', unsafe_allow_html=True)
                st.markdown(html_rows([
                    ("Reference", f"{base_lat:.5f}, {base_lon:.5f}", GPS),
                    ("Waypoint", f"{st.session_state.way_lat:.5f}, {st.session_state.way_lon:.5f}", TEXT),
                ]), unsafe_allow_html=True)
        with b:
            with st.container(border=True):
                st.markdown('<div class="micro-title">ANALYTICAL STATE</div>', unsafe_allow_html=True)
                st.markdown(html_rows([
                    ("RF direction", f"{v['rf_dir']:.1f}°" if v['rf_dir'] is not None else "—", RF),
                    ("Thermal direction", f"{v['thermal_dir']:.1f}°" if v['thermal_dir'] is not None else "—", THERMAL),
                    ("Resultant", f"{bearing:.1f}°" if bearing is not None else "—", RESULTANT),
                ]), unsafe_allow_html=True)
        with c:
            with st.container(border=True):
                st.markdown('<div class="micro-title">FIELD NOTE</div><div class="sdr-caption">The map presents a working spatial estimate. It does not claim an exact source coordinate.</div>', unsafe_allow_html=True)

    # ---------- Sensor Field ----------
    elif page == "Sensor Field":
        high_count = sum(1 for x in obs if int(x.get("rf", 0)) == 1)
        thermal_vals = [float(x.get("delta", 0)) for x in obs]
        positive_thermal = [v0 for v0 in thermal_vals if v0 > 0]
        peak = max(positive_thermal) if positive_thermal else 0.0
        peak_angle = None
        if positive_thermal:
            peak_row = max((x for x in obs if float(x.get("delta", 0)) > 0), key=lambda x: float(x.get("delta", 0)))
            peak_angle = float(peak_row.get("angle", 0))

        st.markdown('<div class="tile-grid four">' +
                    tile("SCAN COVERAGE", f"{coverage}%", "unique angular positions", GPS) +
                    tile("RF EVENTS", str(high_count), "digital HIGH observations", RF) +
                    tile("THERMAL PEAK", f"{peak:+.1f} °C", f"at {peak_angle:.0f}°" if peak_angle is not None else "awaiting scan", THERMAL) +
                    tile("SAMPLES", str(len(obs)), "recorded observations", RESULTANT) + '</div>', unsafe_allow_html=True)

        st.markdown(sweep_strip(obs), unsafe_allow_html=True)
        a, b = st.columns(2, gap="large")
        with a:
            with st.container(border=True):
                st.markdown('<div class="chart-shell-head"><b>RF ANGULAR DETECTION FIELD</b><span>DIGITAL DATA · NO RSSI</span></div>', unsafe_allow_html=True)
                st.plotly_chart(angular_sensor_fig(obs, "rf", current_angle=st.session_state.manual_angle, current_rf=telemetry.rf_data, current_delta=telemetry.delta_c), use_container_width=True, config={"displayModeBar": False}, key="rf_polar")
                st.markdown('<div class="chart-foot"><span class="legend-dot rf"></span> HIGH detection&nbsp;&nbsp;&nbsp; <span class="legend-ring"></span> LOW / no detection</div>', unsafe_allow_html=True)
        with b:
            with st.container(border=True):
                st.markdown('<div class="chart-shell-head"><b>THERMAL RESPONSE FIELD</b><span>MPU6050 · INTERNAL TEMPERATURE PROXY</span></div>', unsafe_allow_html=True)
                st.plotly_chart(angular_sensor_fig(obs, "thermal", current_angle=st.session_state.manual_angle, current_rf=telemetry.rf_data, current_delta=telemetry.delta_c), use_container_width=True, config={"displayModeBar": False}, key="thermal_polar")
                st.markdown('<div class="chart-foot"><span class="legend-dot thermal"></span> observed temperature-proxy response&nbsp;&nbsp;&nbsp; diamond = peak</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="micro-title">ANGULAR OBSERVATION CAPTURE</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1.35], gap="medium")
            with c1:
                angle = st.number_input("SCAN ANGLE", 0.0, 180.0, float(st.session_state.manual_angle), 1.0, key="scan_angle")
                st.session_state.manual_angle = float(angle)
            with c2:
                rf_state = st.selectbox("RF DATA", [0, 1], index=int(telemetry.rf_data), format_func=lambda x: "HIGH" if x else "LOW", key="scan_rf")
            with c3:
                obj = st.number_input("MPU TEMP °C", -40.0, 200.0, float(telemetry.object_c or 36.0), .1, key="scan_obj")
            with c4:
                amb = st.number_input("PROXY BASELINE °C", -40.0, 100.0, float(telemetry.ambient_c or 28.0), .1, key="scan_amb")
            delta = obj - amb
            if st.session_state.auto_capture:
                sig = (round(float(angle), 1), int(rf_state), round(float(obj), 1), round(float(amb), 1))
                if sig != st.session_state.last_auto_signature:
                    st.session_state.observations.append({"time": time.strftime("%H:%M:%S"), "angle": float(angle), "rf": int(rf_state), "object": float(obj), "ambient": float(amb), "delta": float(delta)})
                    st.session_state.observations = st.session_state.observations[-180:]
                    st.session_state.last_auto_signature = sig
            d1, d2, d3 = st.columns([1.1, 1.1, 2.2], gap="medium")
            with d1:
                if st.button("RECORD OBSERVATION", use_container_width=True, key="record_obs"):
                    st.session_state.observations.append({"time": time.strftime("%H:%M:%S"), "angle": float(angle), "rf": int(rf_state), "object": float(obj), "ambient": float(amb), "delta": float(delta)})
                    st.session_state.observations = st.session_state.observations[-180:]
            with d2:
                if st.button("CLEAR SCAN", use_container_width=True, key="clear_obs"):
                    st.session_state.observations = []
            with d3:
                st.markdown(f'<div class="control-note"><b>ΔT PROXY {delta:+.1f} °C</b> · Record the live reading at the known manual scan angle. Manual actuation is a temporary mechanical scanning method during prototype validation.</div>', unsafe_allow_html=True)

        if obs:
            st.markdown('<div class="table-head"><span>OBSERVATION LOG</span><span>LAST 12 · ACTUAL RECORDED VALUES</span></div>', unsafe_allow_html=True)
            df = pd.DataFrame(obs).tail(12)
            st.dataframe(df, use_container_width=True, hide_index=True, column_config={
                "time": st.column_config.TextColumn("Time"),
                "angle": st.column_config.NumberColumn("Angle", format="%.0f°"),
                "rf": st.column_config.NumberColumn("RF", format="%d"),
                "object": st.column_config.NumberColumn("MPU Temp", format="%.1f °C"),
                "ambient": st.column_config.NumberColumn("Proxy Baseline", format="%.1f °C"),
                "delta": st.column_config.NumberColumn("ΔT PROXY", format="%+.1f °C"),
            })
        else:
            st.markdown('<div class="empty-state"><b>SCAN READY</b><br>Set the manual scan angle and record the live RF event plus MPU6050 temperature-proxy reading. The analytical fields will build from those observations.</div>', unsafe_allow_html=True)

    # ---------- Vector Fusion ----------
    elif page == "Vector Fusion":
        st.markdown('<div class="tile-grid four">' +
                    tile("RF BEARING", f"{v['rf_dir']:.1f}°" if v['rf_dir'] is not None else "—", "digital evidence", RF) +
                    tile("THERMAL BEARING", f"{v['thermal_dir']:.1f}°" if v['thermal_dir'] is not None else "—", "ΔT PROXY weighted", THERMAL) +
                    tile("RESULTANT", f"{bearing:.1f}°" if bearing is not None else "—", "north-up bearing", RESULTANT) +
                    tile("EVIDENCE", f"{quality}%" if obs else "—", f"{len(obs)} observations", GOOD if quality >= 70 else WARN) + '</div>', unsafe_allow_html=True)

        left, right = st.columns([1.7, 1], gap="large")
        with left:
            with st.container(border=True):
                st.markdown('<div class="chart-shell-head"><b>FUSION COMPASS</b><span>0° NORTH · 90° EAST · CLOCKWISE</span></div>', unsafe_allow_html=True)
                st.plotly_chart(vector_fig(v), use_container_width=True, config={"displayModeBar": False}, key="fusion_compass")
                st.markdown('<div class="chart-foot">Evidence points remain separate from vectors. The resultant is a weighted directional combination of available sensor evidence.</div>', unsafe_allow_html=True)
        with right:
            with st.container(border=True):
                st.markdown('<div class="readout-head">NUMERICAL FUSION READOUT</div>', unsafe_allow_html=True)
                def val(x): return "—" if x is None else f"{x:.1f}°"
                st.markdown(html_rows([
                    ("RF direction", val(v["rf_dir"]), RF),
                    ("RF coherence", f'{v["rf_mag"]:.2f}', RF),
                    ("Thermal direction", val(v["thermal_dir"]), THERMAL),
                    ("Thermal coherence", f'{v["thermal_mag"]:.2f}', THERMAL),
                    ("Angular separation", val(v["agreement"]), TEXT),
                    ("Resultant direction", val(v["resultant_dir"]), RESULTANT),
                    ("Resultant magnitude", f'{v["resultant_mag"]:.2f}', RESULTANT),
                ]), unsafe_allow_html=True)
                st.markdown('<div class="readout-callout">' +
                            ('Directional agreement is available.' if v['agreement'] is not None else 'Record both sensor responses to establish directional agreement.') +
                            '</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1.05, 1.15, 1.35], gap="large")
        with c1:
            with st.container(border=True):
                rw = int(round(v["rf_weight"] * 100)); tw = int(round(v["thermal_weight"] * 100))
                st.markdown('<div class="micro-title">SENSOR CONTRIBUTION</div>'
                            f'<div class="weight-row"><span>RF</span><b>{rw}%</b></div><div class="weight-track"><i style="width:{rw}%;background:{RF}"></i></div>'
                            f'<div class="weight-row"><span>THERMAL</span><b>{tw}%</b></div><div class="weight-track"><i style="width:{tw}%;background:{THERMAL}"></i></div>'
                            '<div class="sdr-caption">Weights are the current fusion rule, not RF signal strength.</div>', unsafe_allow_html=True)
        with c2:
            with st.container(border=True):
                agreement_score = 0 if v["agreement"] is None else max(0, 1 - v["agreement"] / 90)
                st.markdown('<div class="micro-title">EVIDENCE DEPTH</div>' +
                            html_rows([("Observations", str(len(obs)), TEXT), ("Angular coverage", f"{coverage}%", GPS), ("Directional agreement", f"{agreement_score*100:.0f}%" if v["agreement"] is not None else "—", GOOD)]) +
                            '<div class="quality-bar"><i style="width:' + str(quality) + '%"></i></div>'
                            f'<div class="quality-caption">EVIDENCE QUALITY <b>{quality}%</b></div>', unsafe_allow_html=True)
        with c3:
            with st.container(border=True):
                st.markdown('<div class="micro-title">ANALYTICAL CHAIN</div>'
                            '<div class="method-chain"><span>OBSERVATIONS</span><i>→</i><span>UNIT VECTORS</span><i>→</i><span>WEIGHTING</span><i>→</i><span>VECTOR SUM</span><i>→</i><span>RESULTANT</span></div>'
                            '<div class="sdr-caption">RF remains digital detection evidence because the installed 433 MHz receiver has no analog RSSI output.</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="solution-band"><div><div class="micro-title">ESTIMATED SOURCE REGION</div><div class="sdr-caption">Bearing + selected working radius · not an exact source coordinate</div></div>' +
                        (f'<div class="solution-bearing">{bearing:.1f}°</div><div class="solution-meta">25 m working radius</div>' if bearing is not None else
                         '<div class="solution-bearing muted">—</div><div class="solution-meta">awaiting scan evidence</div>') +
                        '</div>', unsafe_allow_html=True)
            if bearing is not None:
                st.markdown(f'<div class="solution-coords"><span>LAT <b>{src_lat:.6f}°</b></span><span>LON <b>{src_lon:.6f}°</b></span><span>QUALITY <b>{quality}%</b></span></div>', unsafe_allow_html=True)

    # ---------- System ----------
    else:
        sm = st.session_state.serial_manager
        _, last_t, count, invalid = sm.snapshot()
        age = time.time() - last_t if last_t else None
        connected = bool(sm.ser is not None)
        stale = age is not None and age > 3
        st.markdown('<div class="tile-grid four">' +
                    tile("ACQUISITION", "ONLINE" if connected else "IDLE", sm.port or "USB serial", GOOD if connected else WARN) +
                    tile("PACKETS", str(count), "valid frames", GOOD if count else MUTED) +
                    tile("PACKET AGE", f"{age:.1f}s" if age is not None else "—", "latest frame", WARN if stale else GOOD) +
                    tile("INVALID", str(invalid), "discarded frames", BAD if invalid else GOOD) + '</div>', unsafe_allow_html=True)

        a, b = st.columns([1.15, 1], gap="large")
        with a:
            with st.container(border=True):
                st.markdown('<div class="system-head"><b>HARDWARE TOPOLOGY</b><span>IMPLEMENTATION VIEW</span></div>', unsafe_allow_html=True)
                topology = [
                    ("GPS", "NEO-6M", "TX→D4 / RX→D3", telemetry.gps_valid, "position"),
                    ("RF", "433 MHz receiver", "DATA→D2", True, "digital detection"),
                    ("TEMP", "MPU6050 internal", "A4/A5 I²C", telemetry.temp_available, "temperature proxy"),
                    ("IMU", "MPU6050", "A4/A5 I²C", telemetry.imu_available, "accel / gyro"),
                ]
                for name, dev, pin, ok, role in topology:
                    dot = GOOD if ok else WARN
                    st.markdown(f'<div class="topology-row"><span class="topo-dot" style="background:{dot}"></span><b>{name}</b><span>{dev}</span><code>{pin}</code><em>{role}</em></div>', unsafe_allow_html=True)
        with b:
            with st.container(border=True):
                st.markdown('<div class="system-head"><b>INTERFACE MAP</b><span>IMPLEMENTATION VIEW</span></div>', unsafe_allow_html=True)
                pins = pd.DataFrame([
                    ("RF DATA", "D2", "Digital input / interrupt 0"),
                    ("NEO-6M TX", "D4", "SoftwareSerial RX"),
                    ("NEO-6M RX", "D3", "SoftwareSerial TX"),
                    ("I²C SDA", "A4", "Shared bus"),
                    ("I²C SCL", "A5", "Shared bus"),
                ], columns=["Interface", "Pin", "Role"])
                st.dataframe(pins, use_container_width=True, hide_index=True)
                st.markdown('<div class="sdr-caption">The controller is an implementation detail; this page is the service/commissioning view.</div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="system-head"><b>CURRENT TELEMETRY</b><span>LATEST VALID FRAME</span></div>', unsafe_allow_html=True)
            telemetry_table = pd.DataFrame([
                ("GPS", "Position", f"{telemetry.lat:.6f}, {telemetry.lon:.6f}"),
                ("GPS", "Fix / satellites", f"{telemetry.gps_valid} / {telemetry.satellites}"),
                ("RF", "DATA", "HIGH" if telemetry.rf_data else "LOW"),
                ("RF", "Manual scan angle", f"{telemetry.rf_angle:.1f}°"),
                ("RF", "Last event", f"{telemetry.rf_value} / {telemetry.rf_bits} bits / P{telemetry.rf_protocol}" if telemetry.rf_value else "—"),
                ("MPU6050", "Internal temperature", f"{telemetry.object_c:.1f} °C" if telemetry.temp_available else "—"),
                ("MPU6050", "Temperature proxy ΔT", f"{telemetry.delta_c:+.1f} °C" if telemetry.temp_available else "—"),
                ("IMU", "Roll / pitch", f"{telemetry.roll:.1f}° / {telemetry.pitch:.1f}°"),
                ("Scan", "Manual angle", f"{telemetry.scan_angle:.1f}°"),
            ], columns=["Subsystem", "Field", "Value"])
            st.dataframe(telemetry_table, use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.markdown('<div class="system-head"><b>I²C / COMMISSIONING CHECK</b><span>EXPECTED DEVICE ADDRESSES</span></div>', unsafe_allow_html=True)
            st.markdown(html_rows([
                ("MPU6050", "0x68 expected", GPS),
                ("RF receiver", "D2 digital DATA", RF),
                ("GPS", "TX→D4 / RX→D3", GPS),
                ("MPU6050 temperature", "internal proxy channel", THERMAL),
            ]), unsafe_allow_html=True)
            st.markdown('<div class="sdr-caption">Confirm actual I²C presence with the controller-side scanner during commissioning. A missing sensor does not invalidate the rest of the workspace.</div>', unsafe_allow_html=True)

render_workspace()

