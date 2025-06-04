import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import calendar

# ---------- CONFIG ----------
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ---------- DATA ----------
state_city_coords = {
    "Selangor": {
        "Shah Alam 🌊": [3.0738, 101.5183],
        "Klang 🌊": [3.0333, 101.4500],
        "Petaling Jaya": [3.1073, 101.6067],
        "Kajang 🌊": [2.9927, 101.7882],
        "Ampang 🌊": [3.1496, 101.7600],
        "Gombak": [3.2960, 101.7255]
    },
    "Kuala Lumpur": {
        "Kuala Lumpur 🌊": [3.1390, 101.6869],
        "Setapak 🌊": [3.1979, 101.7146],
        "Cheras 🌊": [3.0723, 101.7405]
    },
    # ... same as before (include all states and cities) ...
}

known_flood_events = {
    "2025-06-01": ["Kelantan 🌊", "Kota Bharu 🌊", "Pasir Mas 🌊"],
    "2025-05-28": ["Kuala Lumpur 🌊"],
    "2025-04-15": ["Kelantan 🌊"],
}

# ---------- FUNCTIONS ----------
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
    except Exception:
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
    except Exception:
        return None
    return None

def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def get_7_day_forecast(city):
    forecast_data = []
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params={"key": WEATHERAPI_KEY, "q": city, "days": 7},
            timeout=10,
        )
        if res.status_code == 200:
            data = res.json()
            for day in data["forecast"]["forecastday"]:
                date = day["date"]
                day_data = day["day"]
                forecast_data.append({
                    "Date": datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y"),
                    "Rainfall (mm)": day_data["totalprecip_mm"],
                    "Humidity (%)": round(day_data["avghumidity"], 1),
                    "Temp (°C)": round(day_data["avgtemp_c"], 1),
                    "Risk": estimate_risk(day_data["totalprecip_mm"], day_data["avghumidity"])
                })
    except Exception:
        pass
    return forecast_data

def highlight_high_risk_cities(date_str):
    high_risk_cities = []
    for state, cities in state_city_coords.items():
        for city in cities:
            if date_str in known_flood_events and city in known_flood_events[date_str]:
                high_risk_cities.append(city)
                continue
            rain = get_daily_rainfall(city, date_str)
            weather = get_weather(city)
            humidity = weather["humidity"] if weather else 0
            if rain is not None and humidity is not None:
                risk = estimate_risk(rain, humidity)
                if "High" in risk:
                    high_risk_cities.append(city)
    return high_risk_cities

# ---------- APP ----------
st.title("🌧 FloodSight Malaysia")
st.markdown(
    "Realtime Flood Risk Forecast for Malaysian Cities — "
    "Cities marked with 🌊 are flood-prone."
)

# Sidebar controls and info
with st.sidebar:
    st.header("🌍 Select Location & Date")
    selected_state = st.selectbox("State", sorted(state_city_coords.keys()))
    cities = sorted(state_city_coords.get(selected_state, {}).keys())
    selected_city = st.selectbox("City", cities) if cities else None
    selected_date = st.date_input(
        "Date",
        value=datetime.today(),
        min_value=datetime(2023, 1, 1),
        max_value=datetime.today()
    )
    selected_date_str = selected_date.strftime("%Y-%m-%d")

    st.markdown("---")
    with st.expander("🛈 User Manual"):
        st.write(
            """
            1. Select a state and city from the dropdown menus.  
            2. Pick a date to check the flood risk for that day.  
            3. Click 'Check Flood Risk' button below.  
            4. View weather details, flood risk, 7-day forecast, and alerts.  
            Stay safe and prepare accordingly!
            """
        )

    st.markdown("---")
    with st.expander("⚠️ Flood Precaution & Preparation"):
        st.write(
            """
            - Prepare emergency kit: food, water, medicines.  
            - Keep phones charged and have backup power banks.  
            - Know evacuation routes and shelters.  
            - Avoid flooded areas and driving through water.  
            - Stay tuned to local news and alerts.
            """
        )

    if st.button("Check Flood Risk"):

        if not selected_city:
            st.error("Please select a city.")
        else:
            with st.spinner("Fetching data..."):
                weather = get_weather(selected_city)
                daily_rain = get_daily_rainfall(selected_city, selected_date_str) or 0.0
                if weather is None:
                    st.error("Could not fetch weather data. Try again later.")
                else:
                    # Override for known flood events:
                    if (selected_date_str in known_flood_events and
                        selected_city in known_flood_events[selected_date_str]):
                        risk = "🔴 High (Known Flood Event)"
                    else:
                        risk = estimate_risk(daily_rain, weather["humidity"])

                    st.session_state["result_ready"] = True
                    st.session_state["weather"] = weather
                    st.session_state["daily_rain"] = daily_rain
                    st.session_state["risk"] = risk
                    st.session_state["city"] = selected_city
                    st.session_state["date"] = selected_date
                    st.session_state["date_str"] = selected_date_str

# Main page: display results if ready
if st.session_state.get("result_ready"):

    city = st.session_state["city"]
    date = st.session_state["date"]
    date_str = st.session_state["date_str"]
    weather = st.session_state["weather"]
    daily_rain = st.session_state["daily_rain"]
    risk = st.session_state["risk"]
    latitude, longitude = state_city_coords[selected_state][city]

    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"### 📍 {city} Location")
        map_df = pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"])
        st.map(map_df, zoom=11)

    with col2:
        st.markdown(f"### ☁️ Weather & Flood Risk on {date.strftime('%d %b %Y')}")
        st.write(f"**Temperature:** {weather['temperature']} °C")
        st.write(f"**Humidity:** {weather['humidity']} %")
        st.write(f"**Rainfall:** {daily_rain} mm")
        st.markdown(f"### ⚠️ Flood Risk Level: {risk}")

    st.markdown("---")
    st.markdown(f"### 📅 7-Day Rainfall Forecast for {city}")
    forecast = get_7_day_forecast(city)
    if forecast:
        df_forecast = pd.DataFrame(forecast)
        # Color code risk column:
        def highlight_risk(val):
            color = ""
            if "High" in val:
                color = "background-color: #ff9999"  # light red
            elif "Moderate" in val:
                color = "background-color: #ffcc99"  # light orange
            elif "Low" in val:
                color = "background-color: #ccffcc"  # light green
            return color

        st.dataframe(df_forecast.style.applymap(highlight_risk, subset=["Risk"]), height=300)
    else:
        st.info("7-day forecast data not available.")

    st.markdown("---")
    st.markdown(f"### ⚠️ Cities at High Flood Risk on {date.strftime('%d %b %Y')}")
    high_risk_cities = highlight_high_risk_cities(date_str)
    if high_risk_cities:
        for c in high_risk_cities:
            st.markdown(f"- **{c}**")
    else:
        st.info("No high-risk cities detected for this date.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by FloodSight Malaysia Team. Data sourced from WeatherAPI.com")
