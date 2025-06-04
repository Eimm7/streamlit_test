import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ------------- CONFIG -------------
st.set_page_config(page_title="FloodSight Malaysia 🌧", layout="wide")

WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ------------- DATA -------------
# Malaysian states with cities that are flood-prone (🌊) or possibly prone (⚠️)
state_city_coords = {
    "Selangor": {
        "Shah Alam 🌊": [3.0738, 101.5183],
        "Klang 🌊": [3.0333, 101.4500],
        "Petaling Jaya ⚠️": [3.1073, 101.6067],
        "Kajang 🌊": [2.9927, 101.7882],
        "Ampang 🌊": [3.1496, 101.7600],
        "Gombak ⚠️": [3.2960, 101.7255]
    },
    "Kuala Lumpur": {
        "Kuala Lumpur 🌊": [3.1390, 101.6869],
        "Setapak 🌊": [3.1979, 101.7146],
        "Cheras 🌊": [3.0723, 101.7405]
    },
    "Penang": {
        "George Town 🌊": [5.4164, 100.3327],
        "Bukit Mertajam ⚠️": [5.3510, 100.4409],
        "Butterworth ⚠️": [5.3997, 100.3638]
    },
    "Johor": {
        "Johor Bahru 🌊": [1.4927, 103.7414],
        "Muar ⚠️": [2.0500, 102.5667],
        "Batu Pahat 🌊": [1.8500, 102.9333],
        "Kluang 🌊": [2.0305, 103.3169],
        "Pontian ⚠️": [1.4856, 103.3895],
        "Segamat 🌊": [2.5143, 102.8105]
    },
    "Kelantan": {
        "Kota Bharu 🌊": [6.1256, 102.2513],
        "Pasir Mas 🌊": [6.0290, 102.2010],
        "Tanah Merah ⚠️": [5.9369, 102.1523]
    },
    "Perak": {
        "Ipoh 🌊": [4.5975, 101.0901],
        "Teluk Intan ⚠️": [4.0152, 100.9421],
        "Bagan Serai ⚠️": [5.0531, 100.7003]
    },
    "Pahang": {
        "Kuantan 🌊": [3.8073, 103.3260],
        "Temerloh ⚠️": [3.4399, 102.4188]
    },
    "Terengganu": {
        "Kuala Terengganu 🌊": [5.3300, 103.1400],
        "Dungun ⚠️": [4.8285, 103.4247]
    },
    "Perlis": {
        "Kangar ⚠️": [6.4445, 100.1999]
    },
    "Negeri Sembilan": {
        "Seremban ⚠️": [2.7261, 101.9384],
        "Port Dickson 🌊": [2.5196, 101.7942]
    },
    "Melaka": {
        "Melaka City ⚠️": [2.1896, 102.2501]
    },
    "Sabah": {
        "Kota Kinabalu 🌊": [5.9804, 116.0735],
        "Sandakan ⚠️": [5.8407, 118.1171]
    },
    "Sarawak": {
        "Kuching 🌊": [1.5533, 110.3593],
        "Sibu ⚠️": [2.2872, 111.8305]
    }
}

# Latest flood news for display
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

# Known historical flood events by city and date (used to highlight risk)
known_flood_events = {
    "Shah Alam 🌊": ["2025-06-01", "2025-04-15"],
    "Klang 🌊": ["2025-06-01"],
    "Johor Bahru 🌊": ["2025-05-28"],
    "George Town 🌊": ["2025-03-10"],
    # Add more as you get data
}

# ----------- UTILS -----------
def get_weather(city):
    """Fetch current weather data for a city using WeatherAPI."""
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
    """Fetch historical daily rainfall data for the specified month."""
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
    """Fetch 7-day rainfall forecast for a city."""
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params={"key": WEATHERAPI_KEY, "q": city, "days": 7}
        )
        if res.status_code == 200:
            data = res.json()
            forecast_list = []
            for day in data["forecast"]["forecastday"]:
                date_str = day["date"]
                rain_mm = day["day"].get("totalprecip_mm", 0)
                forecast_list.append((date_str, rain_mm))
            return forecast_list
    except Exception as e:
        st.error(f"Error fetching forecast: {e}")
    return []

def estimate_risk(rain, humidity):
    """Estimate flood risk level based on rainfall and humidity."""
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def get_risk_for_date(city, date_str, rain_mm):
    """Determine flood risk for a city on a specific date considering historical floods."""
    if city in known_flood_events and date_str in known_flood_events[city]:
        return "🔴 High (Actual Flood Recorded)"
    if rain_mm > 80:
        return "🔴 High"
    elif rain_mm > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def risk_color(risk_level):
    """Returns CSS styling for flood risk level badges."""
    if "High" in risk_level:
        return "background-color:#FF4B4B; color:white; font-weight:bold; padding:5px; border-radius:5px;"
    elif "Moderate" in risk_level:
        return "background-color:#FFA500; color:black; font-weight:bold; padding:5px; border-radius:5px;"
    else:
        return "background-color:#4CAF50; color:white; font-weight:bold; padding:5px; border-radius:5px;"

def flood_preparation_notes():
    """Helpful tips for flood preparedness shown in sidebar."""
    return """
- Secure important documents in waterproof bags.
- Prepare emergency kit (food, water, medicine).
- Know evacuation routes & nearest shelters.
- Keep devices charged.
- Monitor local news & alerts.
"""

# ----------- SIDEBAR -----------
st.sidebar.title("FloodSight Malaysia")
st.sidebar.markdown("### How to use this app:")
st.sidebar.markdown(
    """
1. Select your **State** and **City**.
2. Pick the **Year** and **Month** for rainfall history.
3. Click **Check Flood Risk** for the latest weather and risk.
4. View daily rainfall history as bar chart.
5. View 7-day rainfall forecast trends.
6. See all high-risk cities highlighted on map.
7. Read latest flood news to stay informed.
"""
)
st.sidebar.markdown("### 💧 Flood Preparedness Tips")
st.sidebar.info(flood_preparation_notes())

# ----------- MAIN LAYOUT -----------
st.title("🌧 FloodSight Malaysia")
st.markdown("#### Real-time Flood Risk Forecast & Rainfall History for Malaysian Cities")

# --- Location Selection ---
states = sorted(state_city_coords.keys())
selected_state = st.selectbox("Select State", states)

cities = sorted(state_city_coords.get(selected_state, {}).keys())
selected_city = st.selectbox("Select City", cities)

# --- Date Selection ---
current_year = datetime.now().year
year = st.selectbox("Select Year", list(range(current_year - 5, current_year + 1)), index=5)
month_names = list(calendar.month_name)
month_names.pop(0)  # Remove empty string at index 0
selected_month_name = st.selectbox("Select Month", month_names, index=datetime.now().month - 1)

# Convert month name to month number safely
try:
    selected_month = month_names.index(selected_month_name) + 1
except ValueError:
    selected_month = datetime.now().month

# --- Fetch Current Weather ---
weather = get_weather(selected_city.split()[0])  # Use city name without flood symbol for API

if weather:
    st.subheader(f"Current Weather in {selected_city}")
    st.write(f"Temperature: {weather['temperature']} °C")
    st.write(f"Humidity: {weather['humidity']}%")
    st.write(f"Rainfall Now: {weather['rain']} mm")
    st.write(f"Local Time: {weather['time']}")

    # --- Estimate Current Flood Risk ---
    current_risk = estimate_risk(weather['rain'], weather['humidity'])
    st.markdown(f"<span style='{risk_color(current_risk)}'>Current Flood Risk: {current_risk}</span>", unsafe_allow_html=True)
else:
    st.warning("Unable to fetch current weather data.")

# --- Daily Rainfall History (Bar Chart) ---
st.subheader(f"Daily Rainfall History - {selected_month_name} {year}")
daily_rainfall = get_monthly_rainfall(selected_city.split()[0], year, selected_month)
df_daily = pd.DataFrame(daily_rainfall, columns=["Date", "Rainfall_mm"])
df_daily["Date"] = pd.to_datetime(df_daily["Date"])

# Bar chart for rainfall history
st.bar_chart(df_daily.set_index("Date")["Rainfall_mm"])

# --- 7-Day Rainfall Forecast (Line Chart) ---
st.subheader(f"7-Day Rainfall Forecast for {selected_city}")
forecast = get_7day_forecast(selected_city.split()[0])

if forecast:
    df_forecast = pd.DataFrame(forecast, columns=["Date", "Rainfall_mm"])
    df_forecast["Date"] = pd.to_datetime(df_forecast["Date"])
    st.line_chart(df_forecast.set_index("Date")["Rainfall_mm"])
else:
    st.warning("7-day forecast data unavailable.")

# --- Highlight All High Risk Cities ---
st.subheader("Flood Risk Map: High-Risk Cities Highlighted")

import pydeck as pdk

risk_markers = []
for state, cities_dict in state_city_coords.items():
    for city, coords in cities_dict.items():
        # For simplicity, use today's date and arbitrary rainfall to estimate risk for demo
        # You can enhance by fetching real daily rainfall for each city
        risk = "🟢 Low"
        # Mark as high risk if city is in known flood events today or recent
        today_str = datetime.now().strftime("%Y-%m-%d")
        if city in known_flood_events and today_str in known_flood_events[city]:
            risk = "🔴 High"
        risk_markers.append({
            "name": city,
            "lat": coords[0],
            "lon": coords[1],
            "risk": risk
        })

# Color mapping for pydeck
def risk_color_rgb(risk):
    if "High" in risk:
        return [255, 0, 0]
    elif "Moderate" in risk:
        return [255, 165, 0]
    else:
        return [0, 128, 0]

layer = pdk.Layer(
    "ScatterplotLayer",
    data=risk_markers,
    get_position='[lon, lat]',
    get_fill_color='[255 if risk=="🔴 High" else 255 if risk=="🟠 Moderate" else 0, 0 if risk=="🔴 High" else 165 if risk=="🟠 Moderate" else 128, 0]',
    get_radius=15000,
    pickable=True,
)

view_state = pdk.ViewState(latitude=4.5, longitude=102, zoom=6)

tooltip = {
    "html": "<b>{name}</b><br/>Risk: {risk}",
    "style": {"color": "white"}
}

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

# --- Latest Flood News ---
st.subheader("Latest Flood News")
for news in latest_flood_news:
    st.markdown(f"**{news['date']}**: [{news['title']}]({news['link']})")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 FloodSight Malaysia. Data courtesy of WeatherAPI.com.")

