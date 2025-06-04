import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import calendar
import time

# --- Config ---
st.set_page_config(page_title="🌧 FloodSight Malaysia", layout="wide", page_icon="🌊")

# API key for WeatherAPI (replace if needed)
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# --- Flood-prone cities with coords ---
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
    "Penang": {
        "George Town 🌊": [5.4164, 100.3327],
        "Bukit Mertajam": [5.3510, 100.4409],
        "Butterworth": [5.3997, 100.3638]
    },
    "Johor": {
        "Johor Bahru 🌊": [1.4927, 103.7414],
        "Muar": [2.0500, 102.5667],
        "Batu Pahat 🌊": [1.8500, 102.9333],
        "Kluang 🌊": [2.0305, 103.3169],
        "Pontian": [1.4856, 103.3895],
        "Segamat 🌊": [2.5143, 102.8105]
    },
    "Kelantan": {
        "Kota Bharu 🌊": [6.1254, 102.2381],
        "Pasir Mas 🌊": [6.0333, 102.1333],
        "Tumpat": [6.1978, 102.1715],
        "Tanah Merah": [5.8000, 102.1500]
    },
    "Terengganu": {
        "Kuala Terengganu 🌊": [5.3290, 103.1370],
        "Dungun": [4.7566, 103.4246],
        "Kemaman 🌊": [4.2333, 103.4167],
        "Besut": [5.7333, 102.5000]
    },
    "Pahang": {
        "Kuantan 🌊": [3.8077, 103.3260],
        "Temerloh 🌊": [3.4500, 102.4167],
        "Raub": [3.7921, 101.8578],
        "Bentong": [3.5215, 101.9081],
        "Jerantut": [3.9364, 102.3624]
    },
    "Perak": {
        "Ipoh": [4.5975, 101.0901],
        "Taiping 🌊": [4.8500, 100.7333],
        "Teluk Intan": [4.0252, 101.0166],
        "Sungai Siput": [4.8128, 101.0684]
    },
    "Negeri Sembilan": {
        "Seremban 🌊": [2.7297, 101.9381],
        "Port Dickson": [2.5372, 101.8057],
        "Rembau": [2.5844, 102.0784]
    },
    "Melaka": {
        "Melaka City 🌊": [2.2008, 102.2405],
        "Jasin": [2.3087, 102.4381],
        "Alor Gajah": [2.3800, 102.2100]
    },
    "Kedah": {
        "Alor Setar 🌊": [6.1184, 100.3685],
        "Sungai Petani": [5.6496, 100.4875],
        "Kulim": [5.3653, 100.5610],
        "Pendang": [5.9989, 100.4797]
    },
    "Sabah": {
        "Kota Kinabalu 🌊": [5.9804, 116.0735],
        "Sandakan": [5.8380, 118.1170],
        "Tawau": [4.2448, 117.8911],
        "Keningau": [5.3378, 116.1611]
    },
    "Sarawak": {
        "Kuching 🌊": [1.5535, 110.3593],
        "Sibu": [2.2878, 111.8300],
        "Bintulu": [3.1700, 113.0300],
        "Miri": [4.3993, 113.9915]
    },
    "Perlis": {
        "Kangar": [6.4333, 100.2000],
        "Arau": [6.4318, 100.2701]
    },
    "Putrajaya": {
        "Putrajaya": [2.9264, 101.6964]
    },
    "Labuan": {
        "Labuan": [5.2803, 115.2475]
    }
}

# --- Functions ---

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
        time.sleep(0.1)  # to avoid API rate limits
    progress_bar.empty()
    return rain_data

def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def get_latest_flood_news():
    # Static sample data - replace with API/web scraping if available
    return [
        {"date": "2025-05-28", "location": "Kuala Lumpur", "description": "Severe flooding in low-lying areas due to heavy rain."},
        {"date": "2025-05-20", "location": "Penang", "description": "Flash floods affected several districts causing road closures."},
        {"date": "2025-04-15", "location": "Johor Bahru", "description": "Floodwaters rose after days of continuous rain."}
    ]

# --- Main App ---

st.markdown(f"##### 📅 Today is {datetime.now().strftime('%A, %d %B %Y')}")

# Location selectors in sidebar
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

# Main page layout
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

            risk = estimate_risk(weather["rain"], weather["humidity"])
            st.markdown(f"## Flood Risk Level: {risk}")

            st.markdown("### Weather Summary")
            summary_df = pd.DataFrame({
                "Metric": ["Temperature (°C)", "Humidity (%)", "Rainfall (mm)"],
                "Value": [weather["temperature"], weather["humidity"], weather["rain"]]
            }).set_index("Metric")
            st.bar_chart(summary_df)

            # Show rainfall history with loading progress
            st.markdown(f"### Rainfall History for {calendar.month_name[selected_month]} {selected_year}")
            rain_data = get_monthly_rainfall(selected_city, selected_year, selected_month)
            dates, rains = zip(*rain_data)
            rain_df = pd.DataFrame({"Rainfall (mm)": rains}, index=pd.to_datetime(dates))
            st.line_chart(rain_df)
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

