import streamlit as st
import requests
import pandas as pd
from datetime import datetime
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
    # If date is known flood event for the city, mark High risk with note
    if city in known_flood_events and date_str in known_flood_events[city]:
        return "🔴 High (Actual Flood Recorded)"
    # Else use rainfall thresholds
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

# ----------- MAIN -----------
st.title("🌧 FloodSight Malaysia")
st.markdown("#### Real-time Flood Risk Forecast & Rainfall History for Malaysian Cities")

# Location selection
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

# Date selection for rainfall history
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Select Year", [2025, 2024, 2023])
with col2:
    selected_month = st.selectbox("Select Month", list(range(1, 13)), format_func=lambda m: calendar.month_name[m])

if selected_city:
    tab1, tab2, tab3 = st.tabs(["Overview 🌡", "Rainfall History 📅", "Latest Flood News 📰"])

    with tab1:
        if st.button("🔍 Check Flood Risk"):
            weather = get_weather(selected_city)
            if weather:
                st.success(f"Weather data for **{selected_city}** (as of {weather['time']})")
                # Show metrics in columns
                t1, t2, t3 = st.columns(3)
                t1.metric("🌡 Temperature (°C)", weather["temperature"])
                t2.metric("💧 Humidity (%)", weather["humidity"])
                t3.metric("🌧 Rainfall (mm)", weather["rain"])

                risk = estimate_risk(weather["rain"], weather["humidity"])
                st.markdown(f"### Flood Risk Level")
                st.markdown(f'<div style="{risk_color(risk)}">{risk}</div>', unsafe_allow_html=True)

                st.markdown("#### City Location")
                st.map(pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"]), zoom=10)

            else:
                st.error("Failed to retrieve weather data. Please try again later.")

    with tab2:
        if selected_city:
            st.markdown(f"### Daily Rainfall History for {selected_city} ({calendar.month_name[selected_month]} {selected_year})")
            with st.spinner("Fetching rainfall data..."):
                rainfall_data = get_monthly_rainfall(selected_city, selected_year, selected_month)

            if rainfall_data:
                df_rain = pd.DataFrame(rainfall_data, columns=["Date", "Rainfall (mm)"])
                df_rain["Date"] = pd.to_datetime(df_rain["Date"])
                st.line_chart(df_rain.set_index("Date")["Rainfall (mm)"])

                st.markdown("#### Flood Risk History")
                risk_list = []
                for date, rain_mm in rainfall_data:
                    risk_label = get_risk_for_date(selected_city, date, rain_mm)
                    risk_list.append({"Date": date, "Rainfall (mm)": rain_mm, "Flood Risk": risk_label})
                df_risk = pd.DataFrame(risk_list)
                df_risk["Date"] = pd.to_datetime(df_risk["Date"]).dt.strftime("%Y-%m-%d")

                def color_risk(val):
                    if "High" in val:
                        return 'background-color: #FF4B4B; color:white; font-weight:bold;'
                    elif "Moderate" in val:
                        return 'background-color: #FFA500; font-weight:bold;'
                    else:
                        return 'background-color: #4CAF50; color:white; font-weight:bold;'

                st.dataframe(df_risk.style.applymap(color_risk, subset=["Flood Risk"]), use_container_width=True)

            else:
                st.warning("No rainfall data available for this month.")

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
""", unsafe_allow_html=True
)

