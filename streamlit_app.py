# --------------------------------------------
# 🇲🇾 Malaysia Flood Risk Forecast Dashboard
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --------------------------------------------
# 🎨 Page Setup
# --------------------------------------------
st.set_page_config(
    page_title="🇲🇾 Malaysia Flood Risk Forecast",
    page_icon="🌊",
    layout="wide"
)

# --------------------------------------------
# 📍 City Coordinates (Flood-Prone Areas)
# --------------------------------------------
flood_map = {
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
# 📅 User Selections + Confirmation
# --------------------------------------------
st.title("🌧 Malaysia Flood Risk Forecast Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    selected_state = st.selectbox("📍 Select State", list(flood_map.keys()))
with col2:
    selected_city = st.selectbox("🏙 Select City", list(flood_map[selected_state].keys()))
with col3:
    selected_date = st.date_input("📆 Select Date", datetime.today())

lat, lon = flood_map[selected_state][selected_city]

confirmed = st.button("✅ Confirm Selection")

# --------------------------------------------
# 🌦 Weather Forecast API
# --------------------------------------------
API_KEY = "1468e5c2a4b24ce7a64140429250306"
url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7&aqi=no&alerts=no"
response = requests.get(url)
weather = response.json() if response.status_code == 200 else None

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
# 🧭 Tabs Setup
# --------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "📆 Forecast Table", "🗺 National Risk Map", "📰 Flood News"])

# --------------------------------------------
# 📊 Tab 1: Charts for Weather Metrics
# --------------------------------------------
with tab1:
    st.header("📊 Rainfall, Temperature & Humidity Trends")
    if weather and confirmed:
        forecast = weather["forecast"]["forecastday"]
        data = []
        for day in forecast:
            data.append({
                "Date": day["date"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"],
                "Max Temp (°C)": day["day"]["maxtemp_c"],
                "Humidity (%)": day["day"]["avghumidity"]
            })
        df = pd.DataFrame(data).set_index("Date")

        st.subheader("🌧 Daily Rainfall")
        st.bar_chart(df["Rainfall (mm)"])

        st.subheader("🌡 Max Temperature")
        st.line_chart(df["Max Temp (°C)"])

        st.subheader("💧 Humidity Levels")
        st.area_chart(df["Humidity (%)"])
    elif not confirmed:
        st.info("👆 Please confirm your selection above to load charts.")

# --------------------------------------------
# 📆 Tab 2: Forecast Table + Risk Emoji
# --------------------------------------------
with tab2:
    st.header(f"📋 7-Day Weather Forecast for {selected_city}, {selected_state}")
    if weather and confirmed:
        df["Risk Level"] = df["Rainfall (mm)"].apply(risk_level)
        st.dataframe(df.reset_index())
    else:
        st.warning("⚠ Please confirm selection to view forecast table.")

# --------------------------------------------
# 🗺 Tab 3: National Map + Focused City Map
# --------------------------------------------
with tab3:
    st.header("🗺 National & State Flood Risk Maps")

    # 🔴 National overview map
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
            color = {
                "🟢 Low": [0, 255, 0],
                "🟡 Moderate": [255, 255, 0],
                "🟠 High": [255, 165, 0],
                "🔴 Extreme": [255, 0, 0]
            }[level]
            all_data.append({"lat": city_lat, "lon": city_lon, "color": color})

    df_map = pd.DataFrame(all_data)

    map1, map2 = st.columns(2)

    with map1:
        st.markdown("### 🌍 National Overview")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=4.5, longitude=109.5, zoom=5),
            layers=[
                pdk.Layer("ScatterplotLayer", data=df_map,
                          get_position='[lon, lat]', get_color="color", get_radius=6000)
            ]
        ))

    with map2:
        st.markdown(f"### 🔎 Focus on {selected_city}, {selected_state}")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=9),
            layers=[
                pdk.Layer("ScatterplotLayer",
                          data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                          get_position='[lon, lat]',
                          get_color='[255, 0, 0]',
                          get_radius=8000)
            ]
        ))

# --------------------------------------------
# 📰 Tab 4: Flood News
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
