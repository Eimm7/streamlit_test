# --------------------------------------------
# 🌧️ Malaysia Flood Risk Buddy (User-Friendly Edition)
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import numpy as np
from datetime import datetime
import requests_cache
from retry_requests import retry
import matplotlib.pyplot as plt
import time

# --------------------------------------------
# 🎨 Page Setup
# --------------------------------------------
st.set_page_config(
    page_title="🌧️ Flood Buddy - Interactive",
    page_icon="☔",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #eef3f9; }
    .stButton button { background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; }
    .stSelectbox label, .stDateInput label, .stTextInput label { font-weight: bold; }
    .stTabs [data-baseweb=\"tab\"] button { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------
# 🌐 Setup Open-Meteo Client
# --------------------------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

API_KEY = "1468e5c2a4b24ce7a64140429250306"

# --------------------------------------------
# 📍 City Coordinates (Flood-Prone Areas)
# --------------------------------------------
city_coords = {
    "Kuala Lumpur": (3.139, 101.6869),
    "Kuantan": (3.8148, 103.3381),
    "Kota Bharu": (6.1254, 102.2381),
    "George Town": (5.4164, 100.3327),
    "Johor Bahru": (1.4927, 103.7414)
}

# --------------------------------------------
# 🫲 Welcome Panel
# --------------------------------------------
st.title("🌧️ Malaysia Flood Risk Buddy")
st.subheader("🗺️ Select Location and Date Range")

selected_city = st.selectbox("Choose a City:", list(city_coords.keys()))
lat, lon = city_coords[selected_city]
selected_date = st.date_input("Start Date:", datetime.today())
confirmed = st.button("🚀 Get Forecast")

# --------------------------------------------
# 📡 Weather Fetch Logic
# --------------------------------------------
def risk_level(rain):
    if rain > 50:
        return "🔴 Extreme"
    elif rain > 30:
        return "🟠 High"
    elif rain > 10:
        return "🟡 Moderate"
    else:
        return "🟢 Low"

def preparedness_tips(level):
    if level == "🔴 Extreme":
        return "Evacuate if needed, keep emergency kit ready, avoid floodwaters."
    elif level == "🟠 High":
        return "Charge devices, prepare emergency contact list, avoid travel in low areas."
    elif level == "🟡 Moderate":
        return "Monitor local alerts, keep essentials ready, stay indoors during rain."
    else:
        return "Stay informed and maintain general awareness."

weather, om_rain, om_dates = None, None, None
if confirmed:
    try:
        url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=14"
        response = requests.get(url)
        if response.status_code == 200:
            weather = response.json()
    except Exception as e:
        st.error(f"❌ WeatherAPI Error: {e}")

    try:
        result = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto")
        if result.status_code == 200:
            om_json = result.json()
            om_rain = om_json["daily"]["precipitation_sum"]
            om_dates = om_json["daily"]["time"]
    except Exception as e:
        st.error(f"❌ Open-Meteo Error: {e}")

# --------------------------------------------
# ⚠️ Risk Alerts
# --------------------------------------------
def show_alert_box():
    if weather and om_rain is not None:
        rain_api = weather["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
        rain_om = om_rain[0]
        combined = max(rain_api, rain_om)
        level = risk_level(combined)
        if level == "🔴 Extreme":
            st.error("🚨 EXTREME RAINFALL! Take action immediately!")
        elif level == "🟠 High":
            st.warning("⚠️ Heavy rainfall expected. Be alert.")
        elif level == "🟡 Moderate":
            st.info("🔎 Moderate rain. Keep watch.")
        else:
            st.success("✅ Low rainfall. All clear.")

        st.markdown(f"### 🎓 Preparedness Tip: {preparedness_tips(level)}")

# --------------------------------------------
# 📊 Interactive Tabs
# --------------------------------------------
if confirmed and weather:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗕️ Forecast Calendar", "📽️ Live Map", "📈 Trend Charts", "🗕 Flood Risk Pie", "📈 Historical Comparison", "🌧️ Flood Animation"])

    with tab1:
        show_alert_box()
        st.write("### 🧾 14-Day Forecast Overview")
        forecast_df = pd.DataFrame({
            "Date": [f["date"] for f in weather["forecast"]["forecastday"]],
            "Rainfall (mm)": [f["day"]["totalprecip_mm"] for f in weather["forecast"]["forecastday"]],
            "Max Temp (°C)": [f["day"]["maxtemp_c"] for f in weather["forecast"]["forecastday"]],
            "Humidity (%)": [f["day"]["avghumidity"] for f in weather["forecast"]["forecastday"]],
            "Wind (kph)": [f["day"]["maxwind_kph"] for f in weather["forecast"]["forecastday"]]
        })
        st.dataframe(forecast_df, use_container_width=True, height=600)
        st.caption(f"Showing {len(forecast_df)} days of forecast")

    with tab6:
        st.subheader("🌧️ Simulated Flood Intensity Over Time")
        if om_rain and om_dates:
            progress = st.progress(0)
            flood_chart = st.empty()
            for i in range(1, len(om_rain)+1):
                current_data = pd.DataFrame({
                    "Date": om_dates[:i],
                    "Rainfall (mm)": om_rain[:i]
                })
                flood_chart.line_chart(current_data.set_index("Date"))
                progress.progress(i / len(om_rain))
                time.sleep(0.2)
            st.success("📅 Simulation Complete!")
