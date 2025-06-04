import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import calendar
import time

# --- Config ---
st.set_page_config(page_title="🌧 FloodSight Malaysia", layout="wide", page_icon="🌊")

WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

state_city_coords = {
    # ... [same as before] ...
}

def get_weather(city):
    try:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {"key": WEATHERAPI_KEY, "q": city}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        current = data["current"]
        location = data["location"]
        return {
            "temperature": current["temp_c"],
            "humidity": current["humidity"],
            "rain": current.get("precip_mm", 0),
            "time": location["localtime"]
        }
    except Exception as e:
        st.error(f"Error fetching weather: {e}")
        return None

def get_monthly_rainfall(city, year, month):
    days = calendar.monthrange(year, month)[1]
    rain_data = []
    progress_bar = st.progress(0)
    for day in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        try:
            url = "http://api.weatherapi.com/v1/history.json"
            params = {"key": WEATHERAPI_KEY, "q": city, "dt": date_str}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            day_data = data["forecast"]["forecastday"][0]
            daily_rain = sum(hour["precip_mm"] for hour in day_data["hour"])
            rain_data.append((date_str, daily_rain))
        except Exception:
            rain_data.append((date_str, 0))
        progress_bar.progress(day / days)
        time.sleep(0.1)
    progress_bar.empty()
    return rain_data

def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def estimate_historical_risk(rain_list):
    """Estimate flood risk for historical rainfall data."""
    avg_rain = sum(r for _, r in rain_list) / len(rain_list)
    if avg_rain > 80:
        return "🔴 High (Past Month)"
    elif avg_rain > 40:
        return "🟠 Moderate (Past Month)"
    else:
        return "🟢 Low (Past Month)"

def get_latest_flood_news():
    return [
        {"date": "2025-05-28", "location": "Kuala Lumpur", "description": "Severe flooding in low-lying areas due to heavy rain."},
        {"date": "2025-05-20", "location": "Penang", "description": "Flash floods affected several districts causing road closures."},
        {"date": "2025-04-15", "location": "Johor Bahru", "description": "Floodwaters rose after days of continuous rain."}
    ]

# --- Main App ---

st.markdown(f"##### 📅 Today is {datetime.now().strftime('%A, %d %B %Y')}")

with st.sidebar:
    st.header("🌊 Select Location")
    selected_state = st.selectbox("State", sorted(state_city_coords.keys()))
    selected_city = st.selectbox("City", sorted(state_city_coords[selected_state].keys()))
    lat, lon = state_city_coords[selected_state][selected_city]

    st.markdown("---")
    st.header("⚠ Flood Risk Info & Preparation")
    st.markdown("""
    - 🔴 **High Risk**: Heavy rainfall & high humidity — prepare to evacuate.
    - 🟠 **Moderate Risk**: Moderate rainfall — stay alert.
    - 🟢 **Low Risk**: Low rainfall — normal conditions.

    ### Before a Flood:
    - Prepare emergency supplies (food, water, medicine)
    - Keep important documents safe and dry
    - Charge all devices & keep power banks ready
    - Plan evacuation routes
    - Stay updated with official announcements
    """)

    st.markdown("---")
    st.header("📅 Rainfall History")
    selected_year = st.selectbox("Year", [2025, 2024, 2023], index=0)
    selected_month = st.selectbox("Month", list(range(1, 13)), index=datetime.now().month - 1, format_func=lambda x: calendar.month_name[x])

col1, col2 = st.columns([3,1])

with col1:
    st.markdown(f"### Location Map for **{selected_city}**")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=11)

    if st.button("🔍 Check Flood Risk"):
        with st.spinner("Fetching weather data..."):
            weather = get_weather(selected_city)
        if weather:
            st.success(f"Weather data as of {weather['time']}")
            st.metric("🌡 Temperature", f"{weather['temperature']} °C")
            st.metric("💧 Humidity", f"{weather['humidity']} %")
            st.metric("🌧 Rainfall (last 1h)", f"{weather['rain']} mm")

            current_risk = estimate_risk(weather["rain"], weather["humidity"])
            st.markdown(f"## Flood Risk Level: {current_risk}")

            st.markdown("### Weather Summary")
            summary_df = pd.DataFrame({
                "Metric": ["Temperature (°C)", "Humidity (%)", "Rainfall (mm)"],
                "Value": [weather["temperature"], weather["humidity"], weather["rain"]]
            }).set_index("Metric")
            st.bar_chart(summary_df)

            st.markdown(f"### Rainfall History for {calendar.month_name[selected_month]} {selected_year}")
            rain_data = get_monthly_rainfall(selected_city, selected_year, selected_month)

            # Show dates + rainfall as DataFrame for clarity
            rain_df = pd.DataFrame(rain_data, columns=["Date", "Rainfall (mm)"])
            rain_df["Date"] = pd.to_datetime(rain_df["Date"])
            rain_df = rain_df.set_index("Date")

            st.dataframe(rain_df.style.format("{:.1f}"))

            st.line_chart(rain_df)

            hist_risk = estimate_historical_risk(rain_data)
            st.markdown(f"### Historical Flood Risk: {hist_risk}")

        else:
            st.error("Could not retrieve weather data. Please try again later.")

with col2:
    st.markdown("### 📰 Latest Flood Incidents in Malaysia")
    latest_floods = get_latest_flood_news()
    for flood in latest_floods:
        st.markdown(f"**{flood['date']} - {flood['location']}**")
        st.caption(flood["description"])

    st.markdown("---")
    st.markdown("ℹ️ Cities marked with 🌊 symbol are flood-prone areas.")
