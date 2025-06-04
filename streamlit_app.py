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

def get_forecast(city):
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params={"key": WEATHERAPI_KEY, "q": city, "days": 7}
        )
        if res.status_code == 200:
            data = res.json()
            forecast_days = data["forecast"]["forecastday"]
            # List of (date, total_rain_mm)
            return [(fday["date"], fday["day"]["totalprecip_mm"]) for fday in forecast_days]
    except Exception as e:
        st.error(f"Error fetching forecast: {e}")
    return None

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

def is_recent_flood(city, date_str, days=30):
    """Check if city has known flood event within `days` days from date_str"""
    if city not in known_flood_events:
        return False
    date = datetime.strptime(date_str, "%Y-%m-%d")
    for flood_date_str in known_flood_events[city]:
        flood_date = datetime.strptime(flood_date_str, "%Y-%m-%d")
        delta = abs((date - flood_date).days)
        if delta <= days:
            return True
    return False

def get_risk_for_date(city, date_str, rain_mm):
    # If date is known flood event or recent flood within last 30 days, mark High risk
    if is_recent_flood(city, date_str):
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
    tab1, tab2, tab3, tab4 = st.tabs(["Overview 🌡", "Rainfall History 📅", "Latest Flood News 📰", "Flood Risk Map 🗺"])

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

                # Show 7-day forecast rainfall trend & risk
                forecast = get_forecast(selected_city)
                if forecast:
                    st.markdown("### 7-Day Rainfall Forecast & Risk")
                    df_forecast = pd.DataFrame(forecast, columns=["Date", "Rainfall (mm)"])
                    df_forecast["Risk"] = df_forecast.apply(lambda row: get_risk_for_date(selected_city, row["Date"], row["Rainfall (mm)"]), axis=1)
                    df_forecast["Date"] = pd.to_datetime(df_forecast["Date"])

                    st.bar_chart(df_forecast.set_index("Date")["Rainfall (mm)"])

                    # Show risk table with colors
                    def color_risk(val):
                        if "High" in val:
                            return 'background-color: #FF4B4B; color:white; font-weight:bold;'
                        elif "Moderate" in val:
                            return 'background-color: #FFA500; font-weight:bold;'
                        else:
                            return 'background-color: #4CAF50; color:white; font-weight:bold;'

                    st.dataframe(df_forecast[["Date", "Risk"]].style.applymap(color_risk, subset=["Risk"]))
                else:
                    st.warning("Forecast data unavailable.")

    with tab2:
        # Show monthly rainfall history bar chart + flood risk info
        daily_rainfall = get_monthly_rainfall(selected_city, selected_year, selected_month)
        if daily_rainfall:
            dates = [d for d, _ in daily_rainfall]
            rains = [r for _, r in daily_rainfall]
            df_daily = pd.DataFrame({
                "Date": pd.to_datetime(dates),
                "Rainfall (mm)": rains
            })
            # Calculate risk per day
            df_daily["Risk"] = df_daily.apply(lambda row: get_risk_for_date(selected_city, row["Date"].strftime("%Y-%m-%d"), row["Rainfall (mm)"]), axis=1)

            st.markdown(f"### Daily Rainfall History - {calendar.month_name[selected_month]} {selected_year}")

            # Bar chart of rainfall
            st.bar_chart(df_daily.set_index("Date")["Rainfall (mm)"])

            # Show table with color-coded risk
            def color_risk(val):
                if "High" in val:
                    return 'background-color: #FF4B4B; color:white; font-weight:bold;'
                elif "Moderate" in val:
                    return 'background-color: #FFA500; font-weight:bold;'
                else:
                    return 'background-color: #4CAF50; color:white; font-weight:bold;'

            st.dataframe(df_daily.style.applymap(color_risk, subset=["Risk"]))
        else:
            st.warning("No rainfall history data available.")

    with tab3:
        st.markdown("### Latest Flood News")
        for news in latest_flood_news:
            st.markdown(f"**{news['date']}** - [{news['title']}]({news['link']})")

    with tab4:
        st.markdown("### Flood Risk Map of Selected States and Cities")

        # Collect city info for map display
        all_cities = []
        for state, cities in state_city_coords.items():
            for city_name, coords in cities.items():
                lat, lon = coords
                risk = "🟢 Low"
                # Check if recent flood event today or last 30 days
                today_str = datetime.today().strftime("%Y-%m-%d")
                if is_recent_flood(city_name, today_str):
                    risk = "🔴 High"
                all_cities.append({
                    "City": city_name,
                    "State": state,
                    "lat": lat,
                    "lon": lon,
                    "Risk": risk
                })

        df_map = pd.DataFrame(all_cities)
        risk_colors = {"🟢 Low": "green", "🟠 Moderate": "orange", "🔴 High": "red"}

        # Display map with colored markers (using pydeck)
        import pydeck as pdk

        df_map["color"] = df_map["Risk"].map(risk_colors).fillna("green")

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position='[lon, lat]',
            get_fill_color="[255, 0, 0, 160]",  # Default red, will override in getFillColor
            get_radius=8000,
            pickable=True,
            get_fill_color='[255 * (Risk == "🔴 High"), 165 * (Risk == "🟠 Moderate"), 0 * (Risk == "🟢 Low"), 160]'
        )

        view_state = pdk.ViewState(
            latitude=df_map["lat"].mean(),
            longitude=df_map["lon"].mean(),
            zoom=7,
            pitch=0
        )

        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

        st.markdown("### Cities and Their Current Flood Risk Level")
        st.dataframe(df_map[["City", "State", "Risk"]].style.applymap(color_risk, subset=["Risk"]))

# ------------- END -------------

