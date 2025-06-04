# flood_app.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import calendar

# ---------- CONFIG ----------
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ---------- HEADER ----------
st.title("🌧 FloodSight Malaysia")
st.markdown("### Realtime Flood Risk Forecast for Malaysian Cities")
st.markdown("Note: Cities with 🌊 symbol are known to be flood-prone areas.")

# ---------- (same state_city_coords as before) ----------
# [use your existing state_city_coords dictionary here]

# ---------- Known Flood Events ----------
known_flood_events = {
    "2025-06-01": ["Kelantan 🌊", "Kota Bharu 🌊", "Pasir Mas 🌊"],
    "2025-05-28": ["Kuala Lumpur 🌊"],
    "2025-04-15": ["Kelantan 🌊"]
}

# ---------- User Input ----------
st.markdown("#### 🏙 Select Location")
selected_state = st.selectbox("State", sorted(state_city_coords.keys()))
cities = sorted(state_city_coords[selected_state].keys())
selected_city = st.selectbox("City", cities)
latitude, longitude = state_city_coords[selected_state][selected_city]

# ---------- Show Map ----------
st.markdown("#### 🗺 City Location on Map")
map_df = pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"])
st.map(map_df, zoom=10)

# ---------- Select Date ----------
st.markdown("#### 📅 Select Date for Rainfall History and Flood Risk")
selected_date = st.date_input(
    "Date",
    value=datetime.today(),
    min_value=datetime(2023, 1, 1),
    max_value=datetime.today(),
    format="DD/MM/YYYY"
)
selected_date_str = selected_date.strftime("%Y-%m-%d")
selected_date_display = selected_date.strftime("%d/%m/%Y")

# ---------- API + Utility Functions ----------

def get_weather(city):
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/current.json",
            params={"key": WEATHERAPI_KEY, "q": city},
            timeout=10,
        )
        if res.status_code == 200:
            data = res.json()
            return {
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "rain": data["current"].get("precip_mm", 0),
                "time": data["location"]["localtime"],
            }
    except:
        return None
    return None

def get_daily_rainfall(city, date_str):
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/history.json",
            params={"key": WEATHERAPI_KEY, "q": city, "dt": date_str},
            timeout=10,
        )
        if res.status_code == 200:
            data = res.json()
            mm = sum(h["precip_mm"] for h in data["forecast"]["forecastday"][0]["hour"])
            return mm
    except:
        return None
    return None

def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def flood_preparation_notes():
    return """
- Ensure you have an emergency kit ready with food, water, medications, and important documents.
- Keep your mobile devices charged and have backup power banks.
- Identify safe evacuation routes and shelters.
- Avoid driving or walking through floodwaters.
- Stay updated with local news and official flood warnings.
"""

def get_latest_flood_news():
    return [
        {"date": "2025-06-01", "location": "Kelantan", "details": "Flash floods disrupt local communities."},
        {"date": "2025-05-28", "location": "Kuala Lumpur", "details": "Heavy rainfall causes urban flooding in parts of the city."},
        {"date": "2025-04-15", "location": "Kelantan", "details": "Severe flooding damages infrastructure and homes."}
    ]

# ---------- Main ----------
st.markdown("---")
if st.button("🔍 Check Flood Risk"):
    weather = get_weather(selected_city)
    if weather is None:
        st.error("❌ Failed to retrieve current weather data.")
    else:
        st.success("✅ Current weather data retrieved.")

        col1, col2, col3 = st.columns(3)
        col1.metric("🌡 Temperature", f"{weather['temperature']} °C")
        col2.metric("💧 Humidity", f"{weather['humidity']}%")
        col3.metric("🌧 Rainfall (Today)", f"{weather['rain']} mm")
        st.caption(f"🕒 Data time: {weather['time']}")

        # Historical Rainfall
        daily_rain = get_daily_rainfall(selected_city, selected_date_str)
        if daily_rain is None:
            daily_rain = 0.0

        # Flood risk logic
        if selected_date_str in known_flood_events and selected_city in known_flood_events[selected_date_str]:
            risk = "🔴 High (Known Flood Date)"
        else:
            risk = estimate_risk(daily_rain, weather["humidity"])

        # Sidebar risk level and tips
        st.sidebar.header("⚠ Flood Risk Level")
        st.sidebar.markdown(f"## {risk}")
        st.sidebar.markdown(flood_preparation_notes())

        # Summary Table
        st.markdown("#### 📊 Weather Summary")
        df = pd.DataFrame([{
            "City": selected_city,
            "Date": selected_date_display,
            "Rainfall (mm)": daily_rain,
            "Humidity (%)": weather["humidity"],
            "Temperature (°C)": weather["temperature"],
            "Flood Risk": risk
        }])
        st.dataframe(df, use_container_width=True)

        # Bar chart
        st.bar_chart(
            pd.DataFrame(
                {"Metric": ["Temperature", "Humidity", "Rainfall"],
                 "Value": [weather["temperature"], weather["humidity"], daily_rain]}
            ).set_index("Metric")
        )

        # Flood News
        st.markdown("#### 📰 Latest Flood News in Malaysia")
        for news in get_latest_flood_news():
            st.markdown(f"**{datetime.strptime(news['date'], '%Y-%m-%d').strftime('%d/%m/%Y')}** - **{news['location']}**: {news['details']}")

# ---------- Footer ----------
st.markdown("---")
st.caption("© 2025 FloodSight Malaysia | Data sourced from WeatherAPI and local flood reports")
