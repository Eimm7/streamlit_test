# FloodSight Lite 🌧 - Streamlit Flood Forecast Mini Project
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit.components.v1 import html

# Optional import with fallback message
try:
    import folium
except ImportError:
    folium = None

# ---------- CONFIG ----------
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ---------- HEADER ----------
st.title("🌧 FloodSight Malaysia")
st.markdown("### Realtime Flood Risk Forecast for Malaysian Cities")

# ---------- CITY OPTIONS ----------
city_coords = {
    "Kuala Lumpur": [3.139, 101.6869],
    "Shah Alam": [3.0738, 101.5183],
    "Petaling Jaya": [3.1073, 101.6067],
    "George Town (Penang)": [5.4164, 100.3327],
    "Johor Bahru": [1.4927, 103.7414],
    "Kota Bharu": [6.1254, 102.2381],
    "Kuantan": [3.8077, 103.3260],
    "Ipoh": [4.5975, 101.0901],
    "Seremban": [2.7258, 101.9381],
    "Alor Setar": [6.1194, 100.3679],
    "Kuala Terengganu": [5.3290, 103.1370]
}

# ---------- USER INPUT ----------
st.markdown("#### 🏙 Choose a city")
city = st.selectbox("Select city for flood forecast:", list(city_coords.keys()))

# ---------- FETCH WEATHER DATA ----------
def get_weather(city):
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": WEATHERAPI_KEY, "q": city}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            return {
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "rain": data["current"].get("precip_mm", 0),
                "time": data["location"]["localtime"]
            }
        else:
            return None
    except:
        return None

# ---------- FLOOD RISK LOGIC ----------
def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

# ---------- RENDER ----------
st.markdown("---")
if st.button("🔍 Check Flood Risk"):
    weather = get_weather(city)

    if weather:
        st.success("✅ Weather data retrieved successfully.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="🌡 Temperature", value=f"{weather['temperature']} °C")
        with col2:
            st.metric(label="💧 Humidity", value=f"{weather['humidity']}%")
        with col3:
            st.metric(label="🌧 Rainfall", value=f"{weather['rain']} mm")
        st.caption(f"🕒 Data time: {weather['time']}")

        # Estimate risk
        risk = estimate_risk(weather['rain'], weather['humidity'])
        st.sidebar.header("⚠ Flood Risk Level")
        st.sidebar.markdown(f"## {risk}")

        # Show map if folium is available
        location = city_coords.get(city, [4.2105, 101.9758])

        if folium:
            map_obj = folium.Map(location=location, zoom_start=10)
            folium.Marker(location, tooltip=f"{city} - Risk: {risk}").add_to(map_obj)
            html(map_obj._repr_html_(), height=500)
        else:
            st.warning("📍 Map is not available because 'folium' is not installed.")

        # Summary Table
        st.markdown("#### 📈 Summary Table")
        df = pd.DataFrame([{
            "City": city,
            "Rainfall (mm)": weather["rain"],
            "Humidity (%)": weather["humidity"],
            "Temperature (°C)": weather["temperature"],
            "Flood Risk": risk
        }])
        st.dataframe(df, use_container_width=True)

    else:
        st.error("❌ Could not retrieve weather data. Check the city name or API key.")
