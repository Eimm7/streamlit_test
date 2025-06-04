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
    }
}

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

known_flood_events = {
    "Shah Alam 🌊": ["2025-06-01", "2025-04-15"],
    "Klang 🌊": ["2025-06-01"],
    "Johor Bahru 🌊": ["2025-05-28"],
    "George Town 🌊": ["2025-03-10"],
}

# ----------- UTILS -----------
def get_weather(city):
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

def get_daily_rainfall(city, date_str):
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/history.json",
            params={"key": WEATHERAPI_KEY, "q": city, "dt": date_str}
        )
        if res.status_code == 200:
            data = res.json()
            mm = sum(h.get("precip_mm", 0) for h in data["forecast"]["forecastday"][0]["hour"])
            return mm
    except:
        pass
    return 0.0

def estimate_risk(rain, humidity):
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def flood_preparation_notes():
    return """
- Secure important documents in waterproof bags.
- Prepare emergency kit (food, water, medicine).
- Know evacuation routes & nearest shelters.
- Keep devices charged.
- Monitor local news & alerts.
"""

def risk_color(risk_level):
    if "High" in risk_level:
        return "background-color:#FF4B4B; color:white; font-weight:bold; padding:5px; border-radius:5px;"
    elif "Moderate" in risk_level:
        return "background-color:#FFA500; color:black; font-weight:bold; padding:5px; border-radius:5px;"
    else:
        return "background-color:#4CAF50; color:white; font-weight:bold; padding:5px; border-radius:5px;"

def get_risk_for_date(city, date_str, rain_mm):
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
2. Pick an exact **Date** to check rainfall & flood risk.
3. Click **Check Flood Risk** to get latest weather and flood risk.
4. View rainfall and flood risk for the selected date.
5. Read latest flood news to stay informed.
"""
)
st.sidebar.markdown("### 💧 Flood Preparedness Tips")
st.sidebar.info(flood_preparation_notes())

# ----------- MAIN -----------
st.title("🌧 FloodSight Malaysia")
st.markdown("#### Real-time Flood Risk & Rainfall History for Malaysian Cities")

states = sorted(state_city_coords.keys())
selected_state = st.selectbox("Select State", states)

cities = sorted(state_city_coords.get(selected_state, {}).keys())
if cities:
    selected_city = st.selectbox("Select City", cities)
    latitude, longitude = state_city_coords[selected_state][selected_city]
else:
    selected_city = None
    latitude = longitude = None
    st.warning("Please select a valid state and city.")

min_date = datetime.now() - timedelta(days=365)
max_date = datetime.now()

selected_date = st.date_input("Select Date", max_date, min_value=min_date, max_value=max_date)
selected_date_str = selected_date.strftime("%Y-%m-%d")

if selected_city:
    tab1, tab2, tab3 = st.tabs(["Overview 🌡", "Rainfall History 📅", "Latest Flood News 📰"])

    with tab1:
        if st.button("🔍 Check Flood Risk"):
            weather = get_weather(selected_city)
            rain_mm = get_daily_rainfall(selected_city, selected_date_str)
            if weather is not None:
                st.success(f"Weather data for **{selected_city}** (as of {weather['time']})")
                t1, t2, t3 = st.columns(3)
                t1.metric("🌡 Temperature (°C)", weather["temperature"])
                t2.metric("💧 Humidity (%)", weather["humidity"])
                t3.metric(f"🌧 Rainfall (mm) on {selected_date_str}", f"{rain_mm:.2f}")

                risk = get_risk_for_date(selected_city, selected_date_str, rain_mm)
                if selected_date == datetime.now().date():
                    risk = estimate_risk(rain_mm, weather["humidity"])

                st.markdown(f"### Flood Risk Level on {selected_date_str}")
                st.markdown(f'<div style="{risk_color(risk)}">{risk}</div>', unsafe_allow_html=True)

                st.markdown("#### City Location")
                st.map(pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"]), zoom=10)

            else:
                st.error("Failed to retrieve weather data. Please try again later.")

    with tab2:
        st.markdown(f"### Rainfall and Flood Risk History for {selected_city} 🌧️")
        days_to_show = 7
        dates_list = [(selected_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_to_show)][::-1]

        rain_data = []
        for dt_str in dates_list:
            mm = get_daily_rainfall(selected_city, dt_str)
            if mm is None or not isinstance(mm, (int, float)):
                mm = 0
            rain_data.append({"date": dt_str, "rainfall_mm": mm})

        df_rain = pd.DataFrame(rain_data)
        if not df_rain.empty and "rainfall_mm" in df_rain:
            st.markdown("#### 📊 Rainfall Trend (Past 7 Days)")
            st.line_chart(df_rain.rename(columns={"date": "index"}).set_index("index")["rainfall_mm"])

            st.markdown("#### 📋 Daily Rainfall Data (mm)")
            st.dataframe(df_rain.style.format({"rainfall_mm": "{:.1f}"}), use_container_width=True)
        else:
            st.warning("Rainfall data not available for selected city or date range.")

    with tab3:
        st.markdown("### Latest Flood News in Malaysia")
        for news in latest_flood_news:
            st.markdown(f"**{news['date']}** - [{news['title']}]({news['link']})")

else:
    st.info("Please select a city to start.")

# ----------- FOOTER -----------
st.markdown("---")
st.markdown(
    """
<div style="text-align:center; font-size:12px; color:gray;">
Made with ❤️ by FloodSight Team | Data source: WeatherAPI.com
</div>
""", unsafe_allow_html=True)
'''

# Save updated code to file so the user can download or use it
with open("/mnt/data/floodsight_updated.py", "w") as f:
    f.write(updated_code)

"/mnt/data/floodsight_updated.py"

