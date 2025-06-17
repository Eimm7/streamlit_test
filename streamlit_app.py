# --------------------------------------------
# 🇲🇾 Malaysia Flood Risk Forecast Dashboard
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import numpy as np
from datetime import datetime
import openmeteo_requests
import requests_cache
from retry_requests import retry
import time
import streamlit.components.v1 as components

# --------------------------------------------
# 🎨 Page Setup
# --------------------------------------------
st.set_page_config(
    page_title="🇲🇾 Malaysia Flood Risk Forecast",
    page_icon="🌊",
    layout="wide"
)

# --------------------------------------------
# 🌐 Setup Open-Meteo Client
# --------------------------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# --------------------------------------------
# 📍 City Coordinates (Flood-Prone Areas)
# --------------------------------------------
flood_map = {
    # Coordinates for 5 Malaysian states with multiple cities
    "Selangor": {
        "Shah Alam": (3.0738, 101.5183),
        "Klang": (3.0339, 101.4455),
        "Kajang": (2.9935, 101.7871),
        "Gombak": (3.2986, 101.7250),
        "Puchong": (3.0250, 101.6167),
        "Ampang": (3.1500, 101.7667)
    },
    "Johor": {
        "Johor Bahru": (1.4927, 103.7414),
        "Batu Pahat": (1.8500, 102.9333),
        "Kluang": (2.0326, 103.3180),
        "Muar": (2.0500, 102.5667),
        "Kota Tinggi": (1.7333, 103.9000),
        "Pontian": (1.4833, 103.3833)
    },
    "Kelantan": {
        "Kota Bharu": (6.1333, 102.2500),
        "Pasir Mas": (6.0500, 102.1333),
        "Tumpat": (6.2000, 102.1667),
        "Tanah Merah": (5.8167, 102.1500),
        "Machang": (5.7667, 102.2167),
        "Gua Musang": (4.8833, 101.9667)
    },
    "Pahang": {
        "Kuantan": (3.8167, 103.3333),
        "Temerloh": (3.4500, 102.4167),
        "Jerantut": (3.9333, 102.3667),
        "Bentong": (3.5167, 101.9000),
        "Pekan": (3.4833, 103.4000),
        "Raub": (3.8000, 101.8667)
    },
    "Sarawak": {
        "Kuching": (1.5533, 110.3592),
        "Sibu": (2.3000, 111.8167),
        "Miri": (4.4000, 113.9833),
        "Bintulu": (3.1667, 113.0333),
        "Sri Aman": (1.2333, 111.4667),
        "Limbang": (4.7500, 115.0000)
    }
}

# --------------------------------------------
# 📅 User Selections Interface
# --------------------------------------------
st.title("🌧 Malaysia Flood Risk Forecast Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    selected_state = st.selectbox("📍 Select State", list(flood_map.keys()))
with col2:
    selected_city = st.selectbox("🌇 Select City", list(flood_map[selected_state].keys()))
with col3:
    selected_date = st.date_input("📆 Select Date", datetime.today())

lat, lon = flood_map[selected_state][selected_city]
confirmed = st.button("✅ Confirm Selection")

# --------------------------------------------
# ⚠️ Real-Time Alert Banner
# --------------------------------------------
def show_alert_box():
    if weather:
        today_rain = weather["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
        level = risk_level(today_rain)
        if level == "🔴 Extreme":
            st.error("🚨 REAL-TIME ALERT: Extreme rainfall detected today. Immediate flood risk in selected area!")
        elif level == "🟠 High":
            st.warning("⚠️ ALERT: High rainfall recorded today. Stay alert for possible flooding.")
        elif level == "🟡 Moderate":
            st.info("🔎 Moderate rainfall today. Monitor updates from local authorities.")
        else:
            st.success("😄 No major rainfall today. Flood risk is currently low.")

# Trigger the alert after data is fetched and confirmed
if confirmed:
    show_alert_box()

# Continue with weather, discharge, tabs, map, and news...
