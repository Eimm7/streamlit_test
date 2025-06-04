import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ---------- CONFIG ----------
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ---------- HEADER ----------
st.title("🌧 FloodSight Malaysia")
st.markdown("### Realtime Flood Risk Forecast for Malaysian Cities")
st.markdown(
    "⚠️ Cities with 🌊 symbol are flood-prone areas. Stay alert and prepare accordingly!"
)

# ---------- FLOOD-PRONE CITIES BY STATE ----------
state_city_coords = {
    "Selangor": {
        "Shah Alam 🌊": [3.0738, 101.5183],
        "Klang 🌊": [3.0333, 101.4500],
        "Petaling Jaya": [3.1073, 101.6067],
        "Kajang 🌊": [2.9927, 101.7882],
        "Ampang 🌊": [3.1496, 101.7600],
        "Gombak": [3.2960, 101.7255],
    },
    "Kuala Lumpur": {
        "Kuala Lumpur 🌊": [3.1390, 101.6869],
        "Setapak 🌊": [3.1979, 101.7146],
        "Cheras 🌊": [3.0723, 101.7405],
    },
    "Penang": {
        "George Town 🌊": [5.4164, 100.3327],
        "Bukit Mertajam": [5.3510, 100.4409],
        "Butterworth": [5.3997, 100.3638],
    },
    "Johor": {
        "Johor Bahru 🌊": [1.4927, 103.7414],
        "Muar": [2.0500, 102.5667],
        "Batu Pahat 🌊": [1.8500, 102.9333],
        "Kluang 🌊": [2.0305, 103.3169],
        "Pontian": [1.4856, 103.3895],
        "Segamat 🌊": [2.5143, 102.8105],
    },
    "Kelantan": {
        "Kota Bharu 🌊": [6.1254, 102.2381],
        "Pasir Mas 🌊": [6.0333, 102.1333],
        "Tumpat": [6.1978, 102.1715],
        "Tanah Merah": [5.8000, 102.1500],
    },
    "Terengganu": {
        "Kuala Terengganu 🌊": [5.3290, 103.1370],
        "Dungun": [4.7566, 103.4246],
        "Kemaman 🌊": [4.2333, 103.4167],
        "Besut": [5.7333, 102.5000],
    },
    "Pahang": {
        "Kuantan 🌊": [3.8077, 103.3260],
        "Temerloh 🌊": [3.4500, 102.4167],
        "Raub": [3.7921, 101.8578],
        "Bentong": [3.5215, 101.9081],
        "Jerantut": [3.9364, 102.3624],
    },
    "Perak": {
        "Ipoh": [4.5975, 101.0901],
        "Taiping 🌊": [4.8500, 100.7333],
        "Teluk Intan": [4.0252, 101.0166],
        "Sungai Siput": [4.8128, 101.0684],
    },
    "Negeri Sembilan": {
        "Seremban 🌊": [2.7297, 101.9381],
        "Port Dickson": [2.5372, 101.8057],
        "Rembau": [2.5844, 102.0784],
    },
    "Melaka": {
        "Melaka City 🌊": [2.2008, 102.2405],
        "Jasin": [2.3087, 102.4381],
        "Alor Gajah": [2.3800, 102.2100],
    },
    "Kedah": {
        "Alor Setar 🌊": [6.1184, 100.3685],
        "Sungai Petani": [5.6496, 100.4875],
        "Kulim": [5.3653, 100.5610],
        "Pendang": [5.9989, 100.4797],
    },
    "Sabah": {
        "Kota Kinabalu 🌊": [5.9804, 116.0735],
        "Sandakan": [5.8380, 118.1170],
        "Tawau": [4.2448, 117.8911],
        "Keningau": [5.3378, 116.1611],
    },
    "Sarawak": {
        "Kuching 🌊": [1.5535, 110.3593],
        "Sibu": [2.2878, 111.8300],
        "Bintulu": [3.1700, 113.0300],
        "Miri": [4.3993, 113.9915],
    },
    "Perlis": {
        "Kangar": [6.4333, 100.2000],
        "Arau": [6.4318, 100.2701],
    },
    "Putrajaya": {
        "Putrajaya": [2.9264, 101.6964],
    },
    "Labuan": {
        "Labuan": [5.2803, 115.2475],
    },
}

# ---------- USER INPUT ----------
st.markdown("#### 🏙 Select Location")

selected_state = st.selectbox(
    "State",
    sorted(state_city_coords.keys()),
)

# Fix for empty city list: disable city selectbox until state chosen
cities_in_state = sorted(state_city_coords[selected_state].keys())
selected_city = st.selectbox(
    "City",
    cities_in_state,
)

latitude, longitude = state_city_coords[selected_state][selected_city]

# ---------- SHOW MAP ----------
st.markdown("#### 🗺 City Location on Map")
map_df = pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"])
st.map(map_df, zoom=10)

# ---------- SELECT DATE ----------
st.markdown("#### 📅 Select Date for Flood Risk & Rainfall History")
min_date = datetime.now() - timedelta(days=365)
max_date = datetime.now()

selected_date = st.date_input(
    "Select Date",
    max_date,
    min_value=min_date,
    max_value=max_date,
)
selected_date_str = selected_date.strftime("%Y-%m-%d")  # for API calls

st.write(f"Selected Date (dd/mm/yyyy): {selected_date.strftime('%d/%m/%Y')}")

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
    except Exception as e:
        st.warning(f"Weather API error: {e}")
        return None
    return None


def get_daily_rainfall(city, date_str):
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/history.json",
            params={"key": WEATHERAPI_KEY, "q": city, "dt": date_str},
            timeout=15,
        )
        if res.status_code == 200:
            data = res.json()
            # Sum hourly precip mm to get daily total
            daily_mm = sum(h["precip_mm"] for h in data["forecast"]["forecastday"][0]["hour"])
            return daily_mm
    except Exception as e:
        st.warning(f"History API error: {e}")
        return None
    return None


def estimate_risk(rain, humidity):
    # Risk based on rain & humidity thresholds
    if rain >= 80 and humidity >= 85:
        return "🔴 High"
    elif rain >= 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"


def flood_preparation_notes():
    return """
    **Before a flood:**
    - Prepare emergency kits (water, food, meds)
    - Charge mobile devices and keep power banks
    - Secure important documents in waterproof bags
    - Avoid driving or walking through floodwaters
    - Follow official updates and evacuation orders
    """


def get_latest_flood_news():
    # Simple static example (replace with live API or RSS feed if available)
    news = [
        {
            "date": "2025-05-28",
            "location": "Kuala Lumpur",
            "details": "Heavy floods affected several areas after intense rain. Residents urged to stay alert.",
        },
        {
            "date": "2025-04-15",
            "location": "Kelantan",
            "details": "Flash floods caused temporary road closures and evacuations in low-lying zones.",
        },
    ]
    return news


# ---------- FLOOD RISK CHECK ----------
st.markdown("---")
if st.button("🔍 Check Flood Risk"):

    weather = get_weather(selected_city)
    if weather is None:
        st.error("❌ Failed to retrieve current weather data.")
    else:
        st.success("✅ Current weather data retrieved successfully.")

        col1, col2, col3 = st.columns(3)
        col1.metric("🌡 Temperature", f"{weather['temperature']} °C")
        col2.metric("💧 Humidity", f"{weather['humidity']}%")
        col3.metric("🌧 Rainfall (Today)", f"{weather['rain']} mm")
        st.caption(f"🕒 Data time: {weather['time']}")

        # Get rainfall for selected date (history)
        daily_rain = get_daily_rainfall(selected_city, selected_date_str)
        if daily_rain is None:
            daily_rain = 0.0

        # Flood risk based on selected date rain + humidity from current weather (approximation)
        risk = estimate_risk(daily_rain, weather["humidity"])

        # Sidebar flood risk and notes
        st.sidebar.header("⚠ Flood Risk Level")
        st.sidebar.markdown(f"## {risk}")
        st.sidebar.markdown(flood_preparation_notes())

        # Weather summary table
        df = pd.DataFrame(
            [
                {
                    "City": selected_city,
                    "Date": selected_date.strftime("%d/%m/%Y"),
                    "Rainfall (mm)": daily_rain,
                    "Humidity (%)": weather["humidity"],
                    "Temperature (°C)": weather["temperature"],
                    "Flood Risk": risk,
                }
            ]
        )
        st.markdown("#### 📊 Weather Summary")
        st.dataframe(df, use_container_width=True)

        # Bar chart of metrics for selected date
        chart_df = pd.DataFrame(
            {
                "Metric": ["Temperature", "Humidity", "Rainfall"],
                "Value": [weather["temperature"], weather["humidity"], daily_rain],
            }
        ).set_index("Metric")
        st.bar_chart(chart_df)

        # Show latest flood news below
        st.markdown("#### 📰 Latest Flood News in Malaysia")
        news = get_latest_flood_news()
        for item in news:
            st.markdown(
                f"**{datetime.strptime(item['date'], '%Y-%m-%d').strftime('%d/%m/%Y')}** - "
                f"**{item['location']}**: {item['details']}"
            )
