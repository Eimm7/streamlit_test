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

# --------------------------------------------
# 🎨 Page Setup
# --------------------------------------------
st.set_page_config(
    page_title="🇲🇾 Malaysia Flood Risk Forecast",
    page_icon="🌊",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton button { background-color: #007BFF; color: white; font-weight: bold; }
    .stSelectbox label, .stDateInput label { font-weight: bold; }
    .stTabs [data-baseweb="tab"] button { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

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
# 📅 User Interface
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
# 📡 Fetch Data from WeatherAPI + Open-Meteo
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

weather, om_rain = None, None
if confirmed:
    try:
        url = f"https://api.weatherapi.com/v1/forecast.json?key=YOUR_API_KEY&q={lat},{lon}&days=7"
        response = requests.get(url)
        if response.status_code == 200:
            weather = response.json()
    except Exception as e:
        st.error(f"❌ WeatherAPI Error: {e}")

    try:
        result = openmeteo.weather_forecast(latitude=lat, longitude=lon, daily=["precipitation_sum"], timezone="auto")
        om_rain = result.Daily().Variables(0).ValuesAsNumpy()
    except Exception as e:
        st.error(f"❌ Open-Meteo Error: {e}")

# --------------------------------------------
# ⚠️ Real-Time Alert Function
# --------------------------------------------
def show_alert_box():
    if weather and om_rain is not None:
        rain_api = weather["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
        rain_om = om_rain[0]
        combined = max(rain_api, rain_om)
        level = risk_level(combined)
        if level == "🔴 Extreme":
            st.error("🚨 EXTREME RAINFALL! Immediate flood risk!")
        elif level == "🟠 High":
            st.warning("⚠️ High rainfall. Be alert.")
        elif level == "🟡 Moderate":
            st.info("🔎 Moderate rain. Monitor updates.")
        else:
            st.success("✅ Low rainfall today.")

# --------------------------------------------
# 📊 Tabbed Display
# --------------------------------------------
if confirmed and weather:
    tab1, tab2, tab3 = st.tabs(["📅 Forecast", "🗺️ Map", "📊 Monitoring"])

    with tab1:
        show_alert_box()
        st.write("### 7-Day Forecast Summary")
        forecast_df = pd.DataFrame({
            "Date": [f["date"] for f in weather["forecast"]["forecastday"]],
            "Rainfall (mm)": [f["day"]["totalprecip_mm"] for f in weather["forecast"]["forecastday"]],
            "Max Temp (°C)": [f["day"]["maxtemp_c"] for f in weather["forecast"]["forecastday"]]
        })
        st.dataframe(forecast_df)

    with tab2:
        st.subheader("🗺️ Rainfall Risk Map")
        map_df = pd.DataFrame({"lat": [lat], "lon": [lon], "intensity": [om_rain[0] if om_rain is not None else 0]})
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8, pitch=40),
            layers=[
                pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_color='[200, 30, 0, 160]', get_radius=3000),
                pdk.Layer("HeatmapLayer", data=map_df, get_position='[lon, lat]', aggregation='MEAN', get_weight='intensity')
            ]
        ))

    with tab3:
        st.subheader("📈 7-Day Monitoring Charts")
        df = pd.DataFrame({
            "Date": [d["date"] for d in weather["forecast"]["forecastday"]],
            "Rain (mm)": [d["day"]["totalprecip_mm"] for d in weather["forecast"]["forecastday"]],
            "Humidity (%)": [d["day"]["avghumidity"] for d in weather["forecast"]["forecastday"]],
            "Wind (kph)": [d["day"]["maxwind_kph"] for d in weather["forecast"]["forecastday"]]
        })
        st.line_chart(df.set_index("Date")["Rain (mm)"])
        st.bar_chart(df.set_index("Date")["Humidity (%)"])
        st.area_chart(df.set_index("Date")["Wind (kph)"])

# End of Dashboard
