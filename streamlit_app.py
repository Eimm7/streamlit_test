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

# --------------------------------------------
# 📍 City Coordinates (Flood-Prone Areas)
# --------------------------------------------
flood_map = {
    "Selangor": {
        "Shah Alam": (3.0738, 101.5183), "Klang": (3.0339, 101.4455),
        "Kajang": (2.9935, 101.7871), "Gombak": (3.2986, 101.7250),
        "Puchong": (3.0250, 101.6167), "Ampang": (3.1500, 101.7667)
    },
    "Johor": {
        "Johor Bahru": (1.4927, 103.7414), "Batu Pahat": (1.8500, 102.9333),
        "Kluang": (2.0326, 103.3180), "Muar": (2.0500, 102.5667),
        "Kota Tinggi": (1.7333, 103.9000), "Pontian": (1.4833, 103.3833)
    },
    "Kelantan": {
        "Kota Bharu": (6.1333, 102.2500), "Pasir Mas": (6.0500, 102.1333),
        "Tumpat": (6.2000, 102.1667), "Tanah Merah": (5.8167, 102.1500),
        "Machang": (5.7667, 102.2167), "Gua Musang": (4.8833, 101.9667)
    },
    "Pahang": {
        "Kuantan": (3.8167, 103.3333), "Temerloh": (3.4500, 102.4167),
        "Jerantut": (3.9333, 102.3667), "Bentong": (3.5167, 101.9000),
        "Pekan": (3.4833, 103.4000), "Raub": (3.8000, 101.8667)
    },
    "Sarawak": {
        "Kuching": (1.5533, 110.3592), "Sibu": (2.3000, 111.8167),
        "Miri": (4.4000, 113.9833), "Bintulu": (3.1667, 113.0333),
        "Sri Aman": (1.2333, 111.4667), "Limbang": (4.7500, 115.0000)
    }
}

# --------------------------------------------
# 🪯 Welcome Panel
# --------------------------------------------
st.title("🌊 Your Personal Flood Buddy Risk-Check")
st.markdown("Get real-time info, forecast, and visualize flood-prone conditions in Malaysia. Easy to use, fun to explore!")

st.markdown("---")

st.subheader("📍 Location & Date Settings")
col1, col2, col3 = st.columns(3)
with col1:
    selected_state = st.selectbox("🗺️ Choose State", list(flood_map.keys()))
with col2:
    selected_city = st.selectbox("🏠 Choose City", list(flood_map[selected_state].keys()))
with col3:
    selected_date = st.date_input("🪖️ Pick a Date to Check Forecast", datetime.today())

custom_location = st.text_input("type your own location (latitude,longitude) for more control")
latlon = custom_location.split(',') if custom_location else []

if len(latlon) == 2:
    try:
        lat, lon = float(latlon[0]), float(latlon[1])
    except:
        st.warning("⚠️ Format Error. Try: 3.0738,101.5183")
        lat, lon = flood_map[selected_state][selected_city]
else:
    lat, lon = flood_map[selected_state][selected_city]

confirmed = st.button("🔍 Get My Forecast")

# --------------------------------------------
# ⚠️ Risk Alerts
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

# --------------------------------------------
# 📊 Interactive Tabs
# --------------------------------------------
if confirmed:
    try:
        # Set the 14-day forecast window
        start_date = selected_date.strftime('%Y-%m-%d')
        end_date = (selected_date + pd.Timedelta(days=13)).strftime('%Y-%m-%d')

        # Simplified forecast query for testing reliability
        om_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&start_date={start_date}&end_date={end_date}"
            f"&daily=precipitation_sum"
            f"&timezone=auto"
        )

        st.caption(f"🔁 Open-Meteo URL: {om_url}")
        om_response = retry_session.get(om_url)

        if om_response.status_code == 200:
            om_data = om_response.json().get("daily", {})
            if not om_data or "precipitation_sum" not in om_data:
                st.error("❌ No daily precipitation data returned. Open-Meteo might be down or missing data for that range.")
                st.stop()

            forecast_df = pd.DataFrame({
                "Date": om_data["time"],
                "Rainfall (mm)": om_data["precipitation_sum"]
            })
        else:
            st.warning(f"🔁 Open-Meteo response status: {om_response.status_code}")
            st.error("❌ Failed to fetch data from Open-Meteo.")
            st.stop()

    except Exception as e:
        st.error(f"❌ Error fetching forecast: {e}")
        st.stop()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗕️ Forecast Calendar", "🗺️ Live Map", "📈 Trend Charts", "🗕 Flood Risk Pie", "📈 Historical Comparison"])

    with tab1:
        rain_today = forecast_df["Rainfall (mm)"].iloc[0]
        level = risk_level(rain_today)

        if level == "🔴 Extreme":
            st.error("🚨 EXTREME RAINFALL! Take action immediately!")
        elif level == "🟠 High":
            st.warning("⚠️ Heavy rainfall expected. Be alert.")
        elif level == "🟡 Moderate":
            st.info("🔎 Moderate rain. Keep watch.")
        else:
            st.success("✅ Low rainfall. All clear.")

        st.markdown(f"### 🎓 Preparedness Tip: {preparedness_tips(level)}")
        st.write("### 📟 14-Day Forecast Overview")
        st.dataframe(forecast_df, use_container_width=True, height=600)
        st.caption(f"Showing {len(forecast_df)} days of forecast from Open-Meteo")
