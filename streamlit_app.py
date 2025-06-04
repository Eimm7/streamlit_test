import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

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
    """Fetch current weather for city using WeatherAPI."""
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
    """Get total rainfall (mm) for a city on a given date from WeatherAPI history endpoint."""
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/history.json",
            params={"key": WEATHERAPI_KEY, "q": city, "dt": date_str}
        )
        if res.status_code == 200:
            data = res.json()
            # Sum rainfall for every hour of the day
            mm = sum(h.get("precip_mm", 0) for h in data["forecast"]["forecastday"][0]["hour"])
            return mm
    except:
        pass
    return 0.0

def estimate_risk(rain, humidity):
    """Estimate flood risk based on rainfall and humidity."""
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def flood_preparation_notes():
    """Text with flood preparedness tips."""
    return """
- Secure important documents in waterproof bags.
- Prepare emergency kit (food, water, medicine).
- Know evacuation routes & nearest shelters.
- Keep devices charged.
- Monitor local news & alerts.
"""

def risk_color(risk_level):
    """Return CSS style string based on risk level for colored display."""
    if "High" in risk_level:
        return "background-color:#FF4B4B; color:white; font-weight:bold; padding:5px; border-radius:5px;"
    elif "Moderate" in risk_level:
        return "background-color:#FFA500; color:black; font-weight:bold; padding:5px; border-radius:5px;"
    else:
        return "background-color:#4CAF50; color:white; font-weight:bold; padding:5px; border-radius:5px;"

def city_has_recent_flood_news(city, selected_date):
    """Check if the city has flood news within past 7 days of selected_date."""
    recent_threshold = datetime.strptime(selected_date, "%Y-%m-%d") - timedelta(days=7)
    for news in latest_flood_news:
        news_date = datetime.strptime(news["date"], "%Y-%m-%d")
        # Check if city name appears in news title and date is recent enough
        if city.split(" ")[0] in news["title"] and news_date >= recent_threshold:
            return True
    return False

def get_risk_for_date(city, date_str, rain_mm):
    """Determine risk level based on known flood events, recent news, and rainfall."""
    if city in known_flood_events and date_str in known_flood_events[city]:
        return "🔴 High (Actual Flood Recorded)"
    if city_has_recent_flood_news(city, date_str):
        return "🔴 High (Recent Flood News)"
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

# Select State
states = sorted(state_city_coords.keys())
selected_state = st.selectbox("Select State", states)

# Select City based on State
cities = sorted(state_city_coords.get(selected_state, {}).keys())

if cities:
    selected_city = st.selectbox("Select City", cities)
    latitude, longitude = state_city_coords[selected_state][selected_city]
else:
    selected_city = None
    latitude = longitude = None
    st.warning("Please select a valid state and city.")

# Date Picker (limit to past 1 year)
min_date = datetime.now() - timedelta(days=365)
max_date = datetime.now()

selected_date = st.date_input(
    "Select Date",
    max_date,
    min_value=min_date,
    max_value=max_date
)
selected_date_str = selected_date.strftime("%Y-%m-%d")

if selected_city:
    # Create 4 tabs including the new flood events map tab
    tab1, tab2, tab3, tab4 = st.tabs(["Overview 🌡", "Rainfall History 📅", "Latest Flood News 📰", "Flood Events Map 🗺"])

    with tab1:
        if st.button("🔍 Check Flood Risk"):
            weather = get_weather(selected_city)
            rain_mm = get_daily_rainfall(selected_city, selected_date_str)
            if weather is not None:
                st.success(f"Weather data for **{selected_city}** (as of {weather['time']})")

                # Show temperature, humidity, rainfall in columns
                t1, t2, t3 = st.columns(3)
                t1.metric("🌡 Temperature (°C)", weather["temperature"])
                t2.metric("💧 Humidity (%)", weather["humidity"])
                t3.metric(f"🌧 Rainfall (mm) on {selected_date_str}", f"{rain_mm:.2f}")

                # Calculate flood risk level
                risk = get_risk_for_date(selected_city, selected_date_str, rain_mm)

                # If selected date is today, optionally use humidity for better estimate
                if selected_date == datetime.now().date():
                    risk = estimate_risk(rain_mm, weather["humidity"])

                st.markdown(f"### Flood Risk Level on {selected_date_str}")
                st.markdown(f'<div style="{risk_color(risk)}">{risk}</div>', unsafe_allow_html=True)

                # Show city location on map
                st.map(pd.DataFrame({"lat": [latitude], "lon": [longitude]}))

            else:
                st.error("Failed to get weather data.")

        # Embed Real-time Radar iframe (no install needed)
        st.markdown("#### Real-time Rain Radar for Malaysia")
        radar_url = "https://www.rainviewer.com/weather-radar.html?loc=3.1390,101.6869&zoom=6&opacity=90&noclutter=1"
        st.markdown(
            f'<iframe src="{radar_url}" width="100%" height="400" frameborder="0" scrolling="no"></iframe>',
            unsafe_allow_html=True
        )

    with tab2:
        st.markdown(f"### Rainfall History for {selected_city}")
        # Show last 7 days rainfall from selected_date backwards
        days_to_show = 7
        dates_list = [(selected_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_to_show)][::-1]

        rain_data = []
        for dt_str in dates_list:
            mm = get_daily_rainfall(selected_city, dt_str)
            rain_data.append({"date": dt_str, "rainfall_mm": mm})

        df_rain = pd.DataFrame(rain_data)
        st.line_chart(df_rain.rename(columns={"date": "index"}).set_index("date")["rainfall_mm"])

        st.table(df_rain)

    with tab3:
        st.markdown("### Latest Flood News")
        if latest_flood_news:
            for news in latest_flood_news:
                st.write(f"**{news['date']}** - [{news['title']}]({news['link']})")
        else:
            st.info("No latest flood news available.")

    with tab4:
        st.markdown("### Historical Flood Events Across Malaysia")
        flood_points = []
        for city_name, dates in known_flood_events.items():
            coord_found = False
            for state in state_city_coords.values():
                if city_name in state:
                    lat, lon = state[city_name]
                    coord_found = True
                    break
            if not coord_found:
                continue
            for date in dates:
                flood_points.append({
                    "city": city_name,
                    "date": date,
                    "lat": lat,
                    "lon": lon
                })

        if flood_points:
            df_flood = pd.DataFrame(flood_points)
            # Simple map with flood points (no tooltips)
            st.map(df_flood[["lat", "lon"]])

            # List flood events details below map
            st.markdown("**Flood event details:**")
            for idx, row in df_flood.iterrows():
                st.write(f"- {row['city']} on {row['date']}")
        else:
            st.info("No flood event data available.")
