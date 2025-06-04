import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ------------- CONFIG -------------
st.set_page_config(page_title="FloodSight Malaysia 🌧", layout="wide")

WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ------------- DATA -------------
state_city_coords = {
    "Selangor": {
        "Shah Alam 🌊": [3.0738, 101.5183],
        "Klang 🌊": [3.0333, 101.4500],
        "Petaling Jaya": [3.1073, 101.6067],
        "Kajang 🌊": [2.9927, 101.7882],
        "Ampang 🌊": [3.1496, 101.7600],
        "Gombak": [3.2960, 101.7255],
        "Hulu Langat 🌊": [3.1037, 101.7892],
        "Sungai Buloh 🌊": [3.1975, 101.5767]
    },
    "Kuala Lumpur": {
        "Kuala Lumpur 🌊": [3.1390, 101.6869],
        "Setapak 🌊": [3.1979, 101.7146],
        "Cheras 🌊": [3.0723, 101.7405],
        "Brickfields 🌊": [3.1283, 101.6848]
    },
    "Penang": {
        "George Town 🌊": [5.4164, 100.3327],
        "Bukit Mertajam": [5.3510, 100.4409],
        "Butterworth": [5.3997, 100.3638],
        "Balik Pulau 🌊": [5.3283, 100.2389]
    },
    "Johor": {
        "Johor Bahru 🌊": [1.4927, 103.7414],
        "Muar": [2.0500, 102.5667],
        "Batu Pahat 🌊": [1.8500, 102.9333],
        "Kluang 🌊": [2.0305, 103.3169],
        "Pontian": [1.4856, 103.3895],
        "Segamat 🌊": [2.5143, 102.8105],
        "Skudai 🌊": [1.5378, 103.6577]
    }
}

known_flood_events = {
    "Shah Alam 🌊": ["2025-06-01", "2025-04-15"],
    "Klang 🌊": ["2025-06-01"],
    "Johor Bahru 🌊": ["2025-05-28"],
    "George Town 🌊": ["2025-03-10"]
}

# ----------- UTILS -----------
def get_weather(city):
    try:
        res = requests.get("http://api.weatherapi.com/v1/current.json",
                           params={"key": WEATHERAPI_KEY, "q": city})
        if res.status_code == 200:
            data = res.json()
            return {
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "rain": data["current"].get("precip_mm", 0),
                "time": data["location"]["localtime"]
            }
    except:
        pass
    return None

def get_forecast(city):
    forecast_data = []
    today = datetime.today()
    try:
        res = requests.get("http://api.weatherapi.com/v1/forecast.json",
                           params={"key": WEATHERAPI_KEY, "q": city, "days": 7})
        if res.status_code == 200:
            data = res.json()
            for day in data["forecast"]["forecastday"]:
                date = day["date"]
                rain = sum(hour["precip_mm"] for hour in day["hour"])
                forecast_data.append((date, rain))
    except:
        pass
    return forecast_data

def get_monthly_rainfall(city, year, month):
    days = calendar.monthrange(year, month)[1]
    daily_rainfall = []
    for day in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        try:
            res = requests.get("http://api.weatherapi.com/v1/history.json",
                               params={"key": WEATHERAPI_KEY, "q": city, "dt": date_str})
            if res.status_code == 200:
                data = res.json()
                mm = sum(h.get("precip_mm", 0) for h in data["forecast"]["forecastday"][0]["hour"])
                daily_rainfall.append((date_str, mm))
            else:
                daily_rainfall.append((date_str, 0.0))
        except:
            daily_rainfall.append((date_str, 0.0))
    return daily_rainfall

def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def get_risk_for_date(city, date_str, rain_mm):
    if city in known_flood_events and date_str in known_flood_events[city]:
        return "🔴 High (Actual Flood Recorded)"
    if rain_mm > 80:
        return "🔴 High"
    elif rain_mm > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def flood_preparation_notes():
    return """
- 📁 Keep documents in waterproof bags
- 🎒 Prepare emergency kits (food, water, medicine)
- 📱 Charge devices & power banks
- 📡 Monitor local news and alerts
- 🏃‍♀️ Know your nearest shelters and routes
"""

def risk_color(risk_level):
    if "High" in risk_level:
        return "background-color:#FF4B4B; color:white; font-weight:bold; padding:5px; border-radius:5px;"
    elif "Moderate" in risk_level:
        return "background-color:#FFA500; color:black; font-weight:bold; padding:5px; border-radius:5px;"
    else:
        return "background-color:#4CAF50; color:white; font-weight:bold; padding:5px; border-radius:5px;"

# ----------- SIDEBAR -----------
st.sidebar.title("📍 FloodSight Malaysia")
st.sidebar.markdown("### How to use:")
st.sidebar.markdown("1. Choose **State** and **City**\n2. View live data and flood risk\n3. Explore rainfall & 7-day trends")
st.sidebar.markdown("### 💧 Tips to Prepare")
st.sidebar.info(flood_preparation_notes())

# ----------- MAIN UI -----------
st.title("🌧️ FloodSight Malaysia")
st.markdown("### Real-time Rainfall and Flood Risk Forecasting")

# Location selection
states = sorted(state_city_coords.keys())
selected_state = st.selectbox("Select State", states)
cities = sorted(state_city_coords[selected_state].keys())
selected_city = st.selectbox("Select City", cities)
latitude, longitude = state_city_coords[selected_state][selected_city]

# Date selection with fixed month name index
month_names = list(calendar.month_name)[1:]
selected_month_name = st.selectbox("Select Month", month_names)
try:
    selected_month = month_names.index(selected_month_name) + 1
except ValueError:
    selected_month = datetime.now().month
selected_year = st.selectbox("Select Year", [2025, 2024, 2023])

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📅 History", "📈 7-Day Forecast", "🗺️ All High-Risk Cities"])

with tab1:
    if st.button("🔍 Check Flood Risk Now"):
        weather = get_weather(selected_city)
        if weather:
            st.success(f"**Weather for {selected_city}** (as of {weather['time']})")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡 Temp (°C)", weather["temperature"])
            col2.metric("💧 Humidity", f"{weather['humidity']}%")
            col3.metric("🌧 Rainfall", f"{weather['rain']} mm")

            risk = estimate_risk(weather["rain"], weather["humidity"])
            st.markdown("#### Flood Risk Level")
            st.markdown(f'<div style="{risk_color(risk)}">{risk}</div>', unsafe_allow_html=True)

            st.map(pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"]), zoom=10)
        else:
            st.warning("Unable to fetch weather data.")

with tab2:
    st.markdown(f"### Daily Rainfall History – {selected_month_name} {selected_year}")
    with st.spinner("Fetching rainfall data..."):
        rainfall_data = get_monthly_rainfall(selected_city, selected_year, selected_month)
    df_rain = pd.DataFrame(rainfall_data, columns=["Date", "Rainfall (mm)"])
    df_rain["Date"] = pd.to_datetime(df_rain["Date"])
    st.bar_chart(df_rain.set_index("Date")["Rainfall (mm)"])

    st.markdown("### Flood Risk by Date")
    risk_data = [{"Date": date, "Rainfall (mm)": rain, "Flood Risk": get_risk_for_date(selected_city, date, rain)}
                 for date, rain in rainfall_data]
    df_risk = pd.DataFrame(risk_data)
    df_risk["Date"] = pd.to_datetime(df_risk["Date"]).dt.strftime("%Y-%m-%d")
    st.dataframe(df_risk.style.applymap(risk_color, subset=["Flood Risk"]), use_container_width=True)

with tab3:
    st.markdown("### 7-Day Rainfall Forecast")
    forecast_data = get_forecast(selected_city)
    if forecast_data:
        df_forecast = pd.DataFrame(forecast_data, columns=["Date", "Forecast Rainfall (mm)"])
        df_forecast["Date"] = pd.to_datetime(df_forecast["Date"])
        st.line_chart(df_forecast.set_index("Date")["Forecast Rainfall (mm)"])
    else:
        st.warning("Unable to fetch forecast data.")

with tab4:
    st.markdown("### High-Risk Cities Map")
    high_risk_points = []
    for state, cities in state_city_coords.items():
        for city, coords in cities.items():
            if city in known_flood_events:
                high_risk_points.append({"City": city, "lat": coords[0], "lon": coords[1]})
    if high_risk_points:
        st.map(pd.DataFrame(high_risk_points))
    else:
        st.info("No high-risk cities to display.")

# ----------- FOOTER -----------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:12px;'>Made with ❤️ by FloodSight Team | Powered by WeatherAPI.com</div>",
    unsafe_allow_html=True
)
