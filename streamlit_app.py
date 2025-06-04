import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import calendar
import pydeck as pdk

# ------------- CONFIG -------------
st.set_page_config(page_title="FloodSight Malaysia 🌧", layout="wide")

WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ------------- DATA -------------

# Extended flood-prone cities with 🌊 symbol
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
        "Kota Bharu 🌊": [6.1245, 102.2383],
        "Pasir Mas 🌊": [6.0676, 102.2505],
        "Tanah Merah 🌊": [5.8542, 102.1802]
    },
    "Perak": {
        "Ipoh 🌊": [4.5975, 101.0901],
        "Taiping 🌊": [4.8533, 100.7333]
    }
}

# Latest flood news (can be expanded or linked to real sources)
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

# Known flood events by city and date (expand as needed)
known_flood_events = {
    "Shah Alam 🌊": ["2025-06-01", "2025-04-15"],
    "Klang 🌊": ["2025-06-01"],
    "Johor Bahru 🌊": ["2025-05-28"],
    "George Town 🌊": ["2025-03-10"],
    "Kota Bharu 🌊": ["2025-06-01"],
    "Ipoh 🌊": ["2025-05-15"]
}

# ----------- UTILS -----------

def get_weather(city):
    """Fetch current weather from WeatherAPI"""
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
    """Get historical daily rainfall for a given month"""
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
    """Get 7-day rainfall forecast from WeatherAPI"""
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
    """Estimate risk level from current rain and humidity"""
    if rain > 80 and humidity > 85:
        return "🔴 High"
    elif rain > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

def flood_preparation_notes():
    """Safety tips"""
    return """
- Secure important documents in waterproof bags.
- Prepare emergency kit (food, water, medicine).
- Know evacuation routes & nearest shelters.
- Keep devices charged.
- Monitor local news & alerts.
"""

def risk_color(risk_level):
    """Style for risk level badge"""
    if "High" in risk_level:
        return "background-color:#FF4B4B; color:white; font-weight:bold; padding:5px; border-radius:5px;"
    elif "Moderate" in risk_level:
        return "background-color:#FFA500; color:black; font-weight:bold; padding:5px; border-radius:5px;"
    else:
        return "background-color:#4CAF50; color:white; font-weight:bold; padding:5px; border-radius:5px;"

def get_risk_for_date(city, date_str, rain_mm):
    """Flood risk based on date and rainfall"""
    # Check known flood events
    if city in known_flood_events and date_str in known_flood_events[city]:
        return "🔴 High (Actual Flood Recorded)"
    # Thresholds for risk
    if rain_mm > 80:
        return "🔴 High"
    elif rain_mm > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

# ----------- SIDEBAR -----------

st.sidebar.title("FloodSight Malaysia 🌧")
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
st.markdown(
    """
    #### Real-time Flood Risk Forecast & Rainfall History for Malaysian Cities
    *Stay safe and prepared with real-time data and forecasts.*
    """
)

# Location selection inputs
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
    # Defensive fallback for month names
    month_names = [calendar.month_name[i] for i in range(1, 13)]
    selected_month_name = st.selectbox("Select Month", month_names)
    selected_month = month_names.index(selected_month_name) + 1

if selected_city:
    tab1, tab2, tab3, tab4 = st.tabs(["Overview 🌡", "Rainfall History 📅", "7-Day Forecast 📈", "Latest Flood News 📰"])

    # Overview Tab
    with tab1:
        if st.button("🔍 Check Flood Risk"):
            weather = get_weather(selected_city)
            if weather:
                st.success(f"Weather data for **{selected_city}** (as of {weather['time']})")
                t1, t2, t3 = st.columns(3)
                t1.metric("🌡 Temperature (°C)", weather["temperature"])
                t2.metric("💧 Humidity (%)", weather["humidity"])
                t3.metric("🌧 Rainfall (mm)", weather["rain"])

                risk = estimate_risk(weather["rain"], weather["humidity"])
                st.markdown(f"### Flood Risk Level")
                st.markdown(f'<div style="{risk_color(risk)}">{risk}</div>', unsafe_allow_html=True)

                st.markdown("#### City Location")
                st.map(pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"]), zoom=10)

                # Highlight all high-risk cities on map
                st.markdown("#### High-Risk Flood Prone Cities Map")
                high_risk_cities = []
                for state, cities_dict in state_city_coords.items():
                    for city, (lat, lon) in cities_dict.items():
                        # Simple mock risk based on city name in known floods or random (could be improved)
                        if city in known_flood_events:
                            # If any flood event in recent days, mark high risk
                            if any((datetime.strptime(d, "%Y-%m-%d") >= datetime.now() - timedelta(days=30)) for d in known_flood_events[city]):
                                high_risk_cities.append({
                                    "City": city,
                                    "lat": lat,
                                    "lon": lon,
                                    "Risk": "🔴 High"
                                })
                if high_risk_cities:
                    df_map = pd.DataFrame(high_risk_cities)
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=df_map,
                        get_position='[lon, lat]',
                        get_radius=8000,
                        pickable=True,
                        get_fill_color='[255 * (Risk == "🔴 High"), 165 * (Risk == "🟠 Moderate"), 0 * (Risk == "🟢 Low"), 160]'
                    )
                    view_state = pdk.ViewState(
                        latitude=latitude,
                        longitude=longitude,
                        zoom=8,
                        pitch=0
                    )
                    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{City}\nRisk: {Risk}"})
                    st.pydeck_chart(r)
                else:
                    st.info("No current high-risk flood cities found nearby.")

    # Rainfall History Tab
    with tab2:
        st.markdown(f"### Daily Rainfall History - {selected_month_name} {selected_year}")
        with st.spinner("Fetching rainfall history..."):
            rainfall_history = get_monthly_rainfall(selected_city, selected_year, selected_month)
        if rainfall_history:
            df_rain = pd.DataFrame(rainfall_history, columns=["Date", "Rainfall (mm)"])
            df_rain["Date"] = pd.to_datetime(df_rain["Date"])
            # Calculate risk per day based on rainfall
            df_rain["Risk"] = df_rain.apply(lambda r: get_risk_for_date(selected_city, r["Date"].strftime("%Y-%m-%d"), r["Rainfall (mm)"]), axis=1)
            
            # Bar chart for daily rainfall with colored bars based on risk
            import altair as alt
            color_scale = alt.Scale(
                domain=["🔴 High", "🟠 Moderate", "🟢 Low"],
                range=["#FF4B4B", "#FFA500", "#4CAF50"]
            )
            bars = alt.Chart(df_rain).mark_bar().encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Rainfall (mm):Q', title='Rainfall (mm)'),
                color=alt.Color('Risk:N', scale=color_scale, legend=alt.Legend(title="Flood Risk")),
                tooltip=['Date:T', 'Rainfall (mm):Q', 'Risk:N']
            ).interactive()

            st.altair_chart(bars, use_container_width=True)

    # 7-Day Forecast Tab
    with tab3:
        st.markdown(f"### 7-Day Rainfall Forecast for {selected_city}")
        with st.spinner("Fetching 7-day forecast..."):
            forecast = get_7day_forecast(selected_city)
        if forecast:
            df_forecast = pd.DataFrame(forecast, columns=["Date", "Forecast Rainfall (mm)"])
            df_forecast["Date"] = pd.to_datetime(df_forecast["Date"])
            # Assign risk based on forecast rainfall
            df_forecast["Risk"] = df_forecast["Forecast Rainfall (mm)"].apply(lambda x: "🔴 High" if x > 80 else ("🟠 Moderate" if x > 40 else "🟢 Low"))

            # Line chart with points colored by risk
            line = alt.Chart(df_forecast).mark_line(point=True).encode(
                x='Date:T',
                y='Forecast Rainfall (mm):Q',
                tooltip=['Date:T', 'Forecast Rainfall (mm):Q', 'Risk:N']
            )

            points = alt.Chart(df_forecast).mark_point(filled=True, size=100).encode(
                x='Date:T',
                y='Forecast Rainfall (mm):Q',
                color=alt.Color('Risk:N', scale=color_scale, legend=alt.Legend(title="Flood Risk")),
                tooltip=['Date:T', 'Forecast Rainfall (mm):Q', 'Risk:N']
            )
            st.altair_chart(line + points, use_container_width=True)

    # Latest Flood News Tab
    with tab4:
        st.markdown("### Latest Flood News & Events")
        for news in latest_flood_news:
            st.markdown(f"**{news['date']}**: [{news['title']}]({news['link']})")

else:
    st.info("Select a valid state and city to view flood info.")

# ---------- Footer ----------
st.markdown("---")
st.markdown("© 2025 FloodSight Malaysia | Data Source: WeatherAPI.com")
