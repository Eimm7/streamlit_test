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
    "Johor": {
        "Johor Bahru 🌊": [1.4927, 103.7414],
        "Muar 🌊": [2.0500, 102.5667],
        "Batu Pahat 🌊": [1.8500, 102.9333],
        "Kluang 🌊": [2.0305, 103.3169],
        "Pontian 🌊": [1.4856, 103.3895],
        "Segamat 🌊": [2.5143, 102.8105]
    },
    "Kedah": {
        "Alor Setar 🌊": [6.1203, 100.3672],
        "Sungai Petani 🌊": [5.6426, 100.4885],
        "Kulim 🌊": [5.3603, 100.5383]
    },
    "Kelantan": {
        "Kota Bharu 🌊": [6.1247, 102.2546],
        "Pasir Mas 🌊": [6.0599, 102.1833],
        "Tanah Merah 🌊": [5.8981, 102.2670]
    },
    "Melaka": {
        "Melaka City 🌊": [2.1896, 102.2501],
        "Alor Gajah 🌊": [2.3887, 102.2337]
    },
    "Negeri Sembilan": {
        "Seremban 🌊": [2.7296, 101.9381],
        "Port Dickson 🌊": [2.5183, 101.7960]
    },
    "Pahang": {
        "Kuantan 🌊": [3.8074, 103.3260],
        "Temerloh 🌊": [3.4402, 102.3434]
    },
    "Perak": {
        "Ipoh 🌊": [4.5975, 101.0901],
        "Teluk Intan 🌊": [4.0132, 100.9612],
        "Bidor 🌊": [4.0000, 101.3333]
    },
    "Perlis": {
        "Kangar 🌊": [6.4420, 100.1994]
    },
    "Penang": {
        "George Town 🌊": [5.4164, 100.3327],
        "Bukit Mertajam 🌊": [5.3510, 100.4409],
        "Butterworth 🌊": [5.3997, 100.3638]
    },
    "Sabah": {
        "Kota Kinabalu 🌊": [5.9804, 116.0735],
        "Sandakan 🌊": [5.8400, 118.1176]
    },
    "Sarawak": {
        "Kuching 🌊": [1.5533, 110.3593],
        "Sibu 🌊": [2.2870, 111.8331]
    },
    "Selangor": {
        "Shah Alam 🌊": [3.0738, 101.5183],
        "Klang 🌊": [3.0333, 101.4500],
        "Petaling Jaya 🌊": [3.1073, 101.6067],
        "Kajang 🌊": [2.9927, 101.7882],
        "Ampang 🌊": [3.1496, 101.7600],
        "Gombak 🌊": [3.2960, 101.7255]
    },
    "Terengganu": {
        "Kuala Terengganu 🌊": [5.3304, 103.1400],
        "Dungun 🌊": [4.8192, 103.4394]
    },
    "Federal Territories": {
        "Kuala Lumpur 🌊": [3.1390, 101.6869],
        "Putrajaya": [2.9264, 101.6964],
        "Labuan": [5.2940, 115.2420]
    }
}

# Latest flood news (could be linked to actual sources)
latest_flood_news = [
    {
        "date": "2025-06-01",
        "title": "Flash floods in Kelantan disrupt local communities",
        "link": "https://example.com/news/kelantan-flood-2025"
    },
    {
        "date": "2025-05-28",
        "title": "Heavy rains cause flooding in Johor Bahru",
        "link": "https://example.com/news/johor-flood-2025"
    }
]

# Known flood events by city and date (example, expand as needed)
known_flood_events = {
    "Shah Alam 🌊": ["2025-06-01", "2025-04-15"],
    "Klang 🌊": ["2025-06-01"],
    "Johor Bahru 🌊": ["2025-05-28"],
    "George Town 🌊": ["2025-03-10"],
    # Add more based on real historical flood data
}

# ----------- UTILS -----------
def get_weather(city):
    """Get current weather data for a city."""
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/current.json",
            params={"key": WEATHERAPI_KEY, "q": city}
        )
        if res.status_code == 200:
            data = res.json()
            return {
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "rain": data["current"].get("precip_mm", 0),
                "time": data["location"]["localtime"]
            }
    except Exception as e:
        st.error(f"Error fetching weather: {e}")
    return None

def get_monthly_rainfall(city, year, month):
    """Fetch historical rainfall data for each day of a specified month."""
    days = calendar.monthrange(year, month)[1]
    daily_rainfall = []

    for day in range(1, days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        try:
            res = requests.get(
                "http://api.weatherapi.com/v1/history.json",
                params={"key": WEATHERAPI_KEY, "q": city, "dt": date_str}
            )
            if res.status_code == 200:
                data = res.json()
                mm = sum(h.get("precip_mm", 0) for h in data["forecast"]["forecastday"][0]["hour"])
                daily_rainfall.append((date_str, mm))
            else:
                daily_rainfall.append((date_str, 0.0))
        except:
            daily_rainfall.append((date_str, 0.0))
    return daily_rainfall

def get_7day_forecast(city):
    """Get 7-day rainfall forecast for the selected city."""
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params={"key": WEATHERAPI_KEY, "q": city, "days": 7}
        )
        if res.status_code == 200:
            data = res.json()
            forecast_days = data["forecast"]["forecastday"]
            forecast_list = []
            for day in forecast_days:
                date = day["date"]
                rain = day["day"].get("totalprecip_mm", 0)
                forecast_list.append((date, rain))
            return forecast_list
    except Exception as e:
        st.error(f"Error fetching forecast data: {e}")
    return []

def estimate_risk(rain, humidity):
    """Estimate flood risk level based on rainfall and humidity."""
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def flood_preparation_notes():
    """Display helpful flood preparedness tips."""
    return """
- Secure important documents in waterproof bags.
- Prepare emergency kit (food, water, medicine).
- Know evacuation routes & nearest shelters.
- Keep devices charged.
- Monitor local news & alerts.
"""

def risk_color(risk_level):
    """Return background style color based on risk level."""
    if "High" in risk_level:
        return "background-color:#FF4B4B; color:white; font-weight:bold; padding:5px; border-radius:5px;"
    elif "Moderate" in risk_level:
        return "background-color:#FFA500; color:black; font-weight:bold; padding:5px; border-radius:5px;"
    else:
        return "background-color:#4CAF50; color:white; font-weight:bold; padding:5px; border-radius:5px;"

def get_risk_for_date(city, date_str, rain_mm):
    """Determine risk for a specific date and city based on rainfall and known flood events."""
    if city in known_flood_events and date_str in known_flood_events[city]:
        return "🔴 High (Actual Flood Recorded)"
    if rain_mm > 80:
        return "🔴 High"
    elif rain_mm > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

# ----------- SIDEBAR -----------
st.sidebar.title("FloodSight Malaysia")
st.sidebar.markdown("### How to use this app:")
st.sidebar.markdown(
    """
1. Select your **State** and **City**.
2. Pick the **Year** and **Month** for rainfall history.
3. Click **Check Flood Risk** to get the latest weather and flood risk.
4. View daily rainfall and flood risk history.
5. Read latest flood news to stay informed.
"""
)
st.sidebar.markdown("### 💧 Flood Preparedness Tips")
st.sidebar.info(flood_preparation_notes())

# ----------- MAIN PAGE -----------
st.title("🌧 FloodSight Malaysia - Flood Forecasting & Rainfall History")

# Select State and City
state = st.selectbox("Select State:", sorted(state_city_coords.keys()))
city = st.selectbox("Select Flood-Prone City:", sorted(state_city_coords[state].keys()))

# Select year and month for historical rainfall
today = datetime.today()
year = st.selectbox("Select Year:", [2025, 2024, 2023], index=0)
month = st.selectbox("Select Month:", list(calendar.month_name)[1:], index=today.month-1)

# Fetch data button
if st.button("Check Flood Risk & Rainfall"):
    # Display city coordinates
    lat, lon = state_city_coords[state][city]

    st.markdown(f"### Weather & Flood Risk for **{city}**, {state}")
    weather = get_weather(city)
    if weather:
        st.write(f"**Temperature:** {weather['temperature']} °C")
        st.write(f"**Humidity:** {weather['humidity']}%")
        st.write(f"**Rainfall (Current):** {weather['rain']} mm")
        st.write(f"**Local Time:** {weather['time']}")

        risk = estimate_risk(weather['rain'], weather['humidity'])
        st.markdown(f"<div style='{risk_color(risk)}'>**Flood Risk Level:** {risk}</div>", unsafe_allow_html=True)
    else:
        st.error("Could not fetch current weather data.")

    # Daily Rainfall History as Bar Chart
    st.markdown(f"### Daily Rainfall History - {calendar.month_name[month]} {year}")
    rainfall_data = get_monthly_rainfall(city, year, month)
    df_rain = pd.DataFrame(rainfall_data, columns=["Date", "Rainfall (mm)"])
    df_rain["Date"] = pd.to_datetime(df_rain["Date"])
    
    # Calculate flood risk for each day and show it as a color indicator in a table
    df_rain["Flood Risk"] = df_rain.apply(lambda row: get_risk_for_date(city, row["Date"].strftime("%Y-%m-%d"), row["Rainfall (mm)"]), axis=1)
    
    # Bar chart of daily rainfall
    st.bar_chart(data=df_rain.set_index("Date")["Rainfall (mm)"])

    # Show a table with date, rainfall, and flood risk
    st.markdown("#### Daily Rainfall and Flood Risk Details")
    def color_risk(val):
        if "High" in val:
            color = 'background-color: #FF4B4B; color:white; font-weight:bold'
        elif "Moderate" in val:
            color = 'background-color: #FFA500; color:black; font-weight:bold'
        else:
            color = 'background-color: #4CAF50; color:white; font-weight:bold'
        return color

    st.dataframe(df_rain.style.applymap(color_risk, subset=["Flood Risk"]))

    # 7-day Rainfall Forecast
    st.markdown("### 7-Day Rainfall Forecast")
    forecast = get_7day_forecast(city)
    if forecast:
        df_forecast = pd.DataFrame(forecast, columns=["Date", "Rainfall (mm)"])
        df_forecast["Date"] = pd.to_datetime(df_forecast["Date"])
        st.line_chart(df_forecast.set_index("Date")["Rainfall (mm)"])
    else:
        st.info("No forecast data available.")

    # Highlight cities with high risk (for current day, demo)
    st.markdown("### Flood Risk High-Risk Cities Today")
    high_risk_cities = []
    for st_name, cities in state_city_coords.items():
        for c, coord in cities.items():
            w = get_weather(c)
            if w:
                r = estimate_risk(w['rain'], w['humidity'])
                if "High" in r:
                    high_risk_cities.append(c)
    if high_risk_cities:
        st.markdown(", ".join(high_risk_cities))
    else:
        st.markdown("No cities with high flood risk currently.")

# ----------- Footer -----------
st.markdown("---")
st.markdown("### Latest Flood News")
for news in latest_flood_news:
    st.markdown(f"- {news['date']}: [{news['title']}]({news['link']})")

st.markdown("**Developed by FloodSight Team**")
