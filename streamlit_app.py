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
OPENWEATHER_API_KEY = "1468e5c2a4b24ce7a64140429250306"  # Replace with your actual API key

# ---------- HEADER ----------
st.title("🌧 FloodSight Malaysia")
st.markdown("### Realtime Flood Risk Forecast for Malaysian Cities")

# ---------- USER INPUT ----------
city = st.text_input("Enter your city (e.g., Kuala Lumpur):", "Kuala Lumpur")

# ---------- FETCH WEATHER DATA ----------
def get_weather(city):
    url = "https://www.weatherapi.com/"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "rain": data.get("rain", {}).get("1h", 0),
                "time": datetime.utcfromtimestamp(data["dt"]).strftime('%Y-%m-%d %H:%M UTC')
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
if st.button("🔍 Check Flood Risk"):
    weather = get_weather(city)

    if weather:
        st.success("Weather data retrieved successfully.")
        st.subheader("📊 Weather Info")
        st.write(f"🌡 Temperature: {weather['temperature']} °C")
        st.write(f"💧 Humidity: {weather['humidity']}%")
        st.write(f"🌧 Rainfall (1h): {weather['rain']} mm")
        st.caption(f"Data time: {weather['time']}")

        # Estimate risk
        risk = estimate_risk(weather['rain'], weather['humidity'])
        st.sidebar.header("⚠ Flood Risk Level")
        st.sidebar.markdown(f"## {risk}")

        # Show map if folium is available
        coords = {
            "Kuala Lumpur": [3.139, 101.6869],
            "Johor Bahru": [1.4927, 103.7414],
            "Penang": [5.4141, 100.3288],
            "Kota Bharu": [6.1254, 102.2381]
        }
        location = coords.get(city, [4.2105, 101.9758])

        if folium:
            map_obj = folium.Map(location=location, zoom_start=10)
            folium.Marker(location, tooltip=f"{city} - Risk: {risk}").add_to(map_obj)
            html(map_obj._repr_html_(), height=500)
        else:
            st.warning("📍 Map is not available because 'folium' is not installed.")

        # Summary Table
        st.subheader("📈 Summary Table")
        df = pd.DataFrame([{
            "City": city,
            "Rainfall (mm)": weather["rain"],
            "Humidity (%)": weather["humidity"],
            "Temperature (°C)": weather["temperature"],
            "Flood Risk": risk
        }])
        st.dataframe(df)

    else:
        st.error("❌ Could not retrieve weather data. Check the city name or API key.")
