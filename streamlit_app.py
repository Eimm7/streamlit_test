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
st.markdown("💡 **Note:** Cities marked with 🌊 are prone to floods.")

# ---------- FLOOD-PRONE CITIES BY STATE ----------
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

# ---------- USER INPUT ----------
st.markdown("#### 🏙 Select Location")

states = sorted(state_city_coords.keys())
selected_state = st.selectbox("State", states)

if selected_state in state_city_coords:
    cities = sorted(state_city_coords[selected_state].keys())
else:
    cities = []
    st.warning("Selected state not found. Please select a valid state.")

if cities:
    selected_city = st.selectbox("City", cities)
    latitude, longitude = state_city_coords[selected_state][selected_city]
else:
    selected_city = None
    latitude, longitude = None, None

# ---------- SHOW MAP ----------
if latitude and longitude:
    st.markdown("#### 🗺 City Location on Map")
    map_df = pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"])
    st.map(map_df, zoom=10)

# ---------- SELECT MONTH/YEAR ----------
st.markdown("#### 📅 Select Month for Rainfall History")
selected_year = st.selectbox("Year", [2025, 2024, 2023])
selected_month = st.selectbox("Month", range(1, 13), format_func=lambda m: calendar.month_name[m])

# ---------- FUNCTIONS ----------
def get_weather(city):
    try:
        res = requests.get("http://api.weatherapi.com/v1/current.json", params={"key": WEATHERAPI_KEY, "q": city})
        if res.status_code == 200:
            data = res.json()
            return {
                "temperature": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "rain": data["current"].get("precip_mm", 0),
                "time": data["location"]["localtime"]
            }
    except Exception as e:
        return None
    return None

def get_monthly_rainfall(city, year, month):
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
        except Exception as e:
            daily_rainfall.append((date_str, 0.0))
    return daily_rainfall

def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def flood_preparation_notes():
    return """
    **Before a flood, prepare by:**
    - Securing important documents in waterproof bags
    - Having an emergency kit ready (food, water, medicine)
    - Knowing evacuation routes and shelters
    - Keeping electronic devices charged
    - Staying informed via local news and alerts
    """

def fetch_latest_flood_news():
    # Using web tool to fetch latest Malaysia flood news (mock with static text here)
    # Replace with real web scraping or API if available
    news = [
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
    return news

# ---------- FLOOD RISK CHECK ----------
st.markdown("---")

if selected_city:
    if st.button("🔍 Check Flood Risk"):
        weather = get_weather(selected_city)
        if weather:
            st.success("✅ Weather data retrieved successfully.")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡 Temperature", f"{weather['temperature']} °C")
            col2.metric("💧 Humidity", f"{weather['humidity']}%")
            col3.metric("🌧 Rainfall", f"{weather['rain']} mm")
            st.caption(f"🕒 Data time: {weather['time']}")

            risk = estimate_risk(weather["rain"], weather["humidity"])
            st.sidebar.header("⚠ Flood Risk Level")
            st.sidebar.markdown(f"## {risk}")
            st.sidebar.markdown(flood_preparation_notes())

            df = pd.DataFrame([{
                "City": selected_city,
                "Rainfall (mm)": weather["rain"],
                "Humidity (%)": weather["humidity"],
                "Temperature (°C)": weather["temperature"],
                "Flood Risk": risk
            }])
            st.markdown("#### 📊 Weather Summary")
            st.dataframe(df, use_container_width=True)

            chart_df = pd.DataFrame({
                "Metric": ["Temperature", "Humidity", "Rainfall"],
                "Value": [weather["temperature"], weather["humidity"], weather["rain"]]
            }).set_index("Metric")
            st.bar_chart(chart_df)

            # Monthly Rainfall
            st.markdown("#### 🌧 Daily Rainfall in Selected Month")
            rain_data = get_monthly_rainfall(selected_city, selected_year, selected_month)
            if rain_data:
                dates, rains = zip(*rain_data)
                rain_df = pd.DataFrame({"Rainfall (mm)": rains}, index=pd.to_datetime(dates))
                st.line_chart(rain_df)

                # Estimate flood risk for each day in the month based on rainfall
                st.markdown("#### ⚠ Flood Risk History for Selected Month")
                risk_history = []
                for date, rain_mm in rain_data:
                    # Use only rain to estimate past risk (humidity data not available historically)
                    if rain_mm > 80:
                        risk_level = "🔴 High"
                    elif rain_mm > 40:
                        risk_level = "🟠 Moderate"
                    else:
                        risk_level = "🟢 Low"
                    risk_history.append({"Date": date, "Rainfall (mm)": rain_mm, "Flood Risk": risk_level})
                risk_df = pd.DataFrame(risk_history)
                risk_df["Date"] = pd.to_datetime(risk_df["Date"]).dt.strftime("%Y-%m-%d")
                st.dataframe(risk_df, use_container_width=True)

            else:
                st.warning("No rainfall data available.")

        else:
            st.error("Failed to retrieve weather data for the selected city.")

# ---------- LATEST FLOOD NEWS ----------
st.markdown("---")
st.markdown("### 📰 Latest Flood News in Malaysia")
news_list = fetch_latest_flood_news()
for news in news_list:
    st.markdown(f"**{news['date']}** - [{news['title']}]({news['link']})")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("Made with ❤️ by FloodSight Team | Data source: WeatherAPI.com")

