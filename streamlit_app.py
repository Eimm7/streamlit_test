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
    selected_city = st.selectbox("🏙 Select City", list(flood_map[selected_state].keys()))
with col3:
    selected_date = st.date_input("📆 Select Date", datetime.today())

# Get latitude and longitude from selected city
lat, lon = flood_map[selected_state][selected_city]
confirmed = st.button("✅ Confirm Selection")

# --------------------------------------------
# 🌦 Get WeatherAPI Forecast Data
# --------------------------------------------
API_KEY = "1468e5c2a4b24ce7a64140429250306"
url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7&aqi=no&alerts=no"
response = requests.get(url)
weather = response.json() if response.status_code == 200 else None

# --------------------------------------------
# 📡 Get Open-Meteo River Discharge
# --------------------------------------------
discharge_data = []
try:
    river_url = "https://flood-api.open-meteo.com/v1/flood"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "river_discharge"
    }
    responses = openmeteo.weather_api(river_url, params=params)
    response_river = responses[0]
    daily = response_river.Daily()
    discharge_data = daily.Variables(0).ValuesAsNumpy()
    discharge_dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )
except:
    discharge_data = [0] * 7
    discharge_dates = pd.date_range(datetime.today(), periods=7)

# --------------------------------------------
# 🚦 Risk Level Function
# --------------------------------------------
def risk_level(rain_mm):
    if rain_mm < 20:
        return "🟢 Low"
    elif rain_mm < 50:
        return "🟡 Moderate"
    elif rain_mm < 100:
        return "🟠 High"
    else:
        return "🔴 Extreme"

# --------------------------------------------
# 🧭 Tabs Interface
# --------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "📆 Forecast Table", "🗺 National Heatmap", "📰 Flood News"])

# --------------------------------------------
# 📊 Tab 1: Trend Charts
# --------------------------------------------
with tab1:
    st.header("📊 Rainfall, Temperature & River Discharge Trends")
    if weather and confirmed:
        forecast = weather["forecast"]["forecastday"]
        data = []
        for day, discharge in zip(forecast, discharge_data):
            data.append({
                "Date": day["date"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"],
                "Max Temp (°C)": day["day"]["maxtemp_c"],
                "River Discharge (m³/s)": discharge
            })
        df = pd.DataFrame(data).set_index("Date")

        # Rainfall chart
        st.subheader("🌧 Daily Rainfall")
        st.bar_chart(df["Rainfall (mm)"])

        # Temperature chart
        st.subheader("🌡 Max Temperature")
        st.line_chart(df["Max Temp (°C)"])

        # River discharge chart
        st.subheader("🌊 River Discharge")
        st.area_chart(df["River Discharge (m³/s)"])
    elif not confirmed:
        st.info("👆 Please confirm your selection above to load charts.")

# --------------------------------------------
# 📆 Tab 2: Forecast Table with Risk Coloring
# --------------------------------------------
with tab2:
    st.header(f"📋 7-Day Weather Forecast for {selected_city}, {selected_state}")
    if weather and confirmed:
        df["Risk Level"] = df["Rainfall (mm)"].apply(risk_level)
        st.dataframe(df.reset_index().style.applymap(
            lambda val: "background-color: #ffcccc" if "Extreme" in str(val) else
                        "background-color: #ffe599" if "High" in str(val) else
                        "background-color: #fff2cc" if "Moderate" in str(val) else
                        "background-color: #d9ead3" if "Low" in str(val) else "",
            subset=["Risk Level"]
        ))
    else:
        st.warning("⚠ Please confirm selection to view forecast table.")

# --------------------------------------------
# 🗺 Tab 3: National Heatmap with Points
# --------------------------------------------
with tab3:
    st.header("🗺 Malaysia National Flood Risk Map (Heat + Points)")
    all_data = []
    for state, cities in flood_map.items():
        for city, coords in cities.items():
            city_lat, city_lon = coords
            try:
                city_url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city_lat},{city_lon}&days=1"
                city_weather = requests.get(city_url).json()
                rain = city_weather["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
            except:
                rain = 0
            level = risk_level(rain)
            intensity = min(rain / 100, 1.0)
            all_data.append({"lat": city_lat, "lon": city_lon, "intensity": intensity})

    df_map = pd.DataFrame(all_data)

    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(latitude=4.5, longitude=109.5, zoom=5),
        layers=[
            # Heatmap Layer
            pdk.Layer("HeatmapLayer",
                      data=df_map,
                      get_position='[lon, lat]',
                      get_weight='intensity',
                      radiusPixels=60),
            # Point Layer
            pdk.Layer("ScatterplotLayer",
                      data=df_map,
                      get_position='[lon, lat]',
                      get_color='[255, 0, 0]',
                      get_radius=5000)
        ]
    ))

# --------------------------------------------
# 📰 Tab 4: Latest News
# --------------------------------------------
with tab4:
    st.header("📰 Latest Malaysian Flood News")
    st.markdown("- [🔗 Floods in Kelantan: Several Evacuated](https://www.thestar.com.my)")
    st.markdown("- [🔗 Johor Faces Torrential Rain](https://www.nst.com.my)")
    st.markdown("- [🔗 Klang Valley Monsoon Alert](https://www.malaymail.com)")
    st.markdown("- [🔗 Flood Mitigation Projects Ongoing](https://www.bernama.com)")

# --------------------------------------------
# 📌 Footer
# --------------------------------------------
st.markdown("---")
st.caption("🛠 Developed for BVI1234 | Group VC24001 · VC24009 · VC24011 · 2025")
