import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ---------- CONFIG ----------
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"

# ---------- DATA ----------
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

known_flood_events = {
    "2025-06-01": ["Kelantan 🌊", "Kota Bharu 🌊", "Pasir Mas 🌊"],
    "2025-05-28": ["Kuala Lumpur 🌊"],
    "2025-04-15": ["Kelantan 🌊"],
}

# ---------- HELPERS ----------
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
    except Exception:
        return None
    return None

def get_daily_rainfall(city, date_str):
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/history.json",
            params={"key": WEATHERAPI_KEY, "q": city, "dt": date_str},
            timeout=10,
        )
        if res.status_code == 200:
            data = res.json()
            mm = sum(h["precip_mm"] for h in data["forecast"]["forecastday"][0]["hour"])
            return mm
    except Exception:
        return None
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
- Ensure you have an emergency kit ready with food, water, medications, and important documents.
- Keep your mobile devices charged and have backup power banks.
- Identify safe evacuation routes and shelters.
- Avoid driving or walking through floodwaters.
- Stay updated with local news and official flood warnings.
"""

def get_latest_flood_news():
    return [
        {
            "date": "2025-06-01",
            "location": "Kelantan",
            "details": "Flash floods disrupt local communities."
        },
        {
            "date": "2025-05-28",
            "location": "Kuala Lumpur",
            "details": "Heavy rainfall causes urban flooding in parts of the city."
        },
        {
            "date": "2025-04-15",
            "location": "Kelantan",
            "details": "Severe flooding damages infrastructure and homes."
        }
    ]

def get_7_day_forecast(city):
    """Return a list of dicts with date, rainfall_mm, humidity, temperature for next 7 days"""
    forecast_data = []
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params={"key": WEATHERAPI_KEY, "q": city, "days": 7},
            timeout=10,
        )
        if res.status_code == 200:
            data = res.json()
            for day in data["forecast"]["forecastday"]:
                date = day["date"]
                day_data = day["day"]
                forecast_data.append({
                    "Date": datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y"),
                    "Rainfall (mm)": day_data["totalprecip_mm"],
                    "Humidity (%)": round(day_data["avghumidity"], 1),
                    "Temperature (°C)": round(day_data["avgtemp_c"], 1),
                    "Risk": estimate_risk(day_data["totalprecip_mm"], day_data["avghumidity"])
                })
    except Exception:
        pass
    return forecast_data

def highlight_high_risk_cities(date_str):
    """Return list of all cities that are high risk or known flood events on date_str"""
    high_risk_cities = []
    for state, cities in state_city_coords.items():
        for city in cities:
            # Check known flood events
            if date_str in known_flood_events and city in known_flood_events[date_str]:
                high_risk_cities.append(city)
                continue
            # Otherwise check weather history
            rain = get_daily_rainfall(city, date_str)
            weather = get_weather(city)
            humidity = weather["humidity"] if weather else 0
            if rain is not None and humidity is not None:
                risk = estimate_risk(rain, humidity)
                if "High" in risk:
                    high_risk_cities.append(city)
    return high_risk_cities

# ---------- APP LAYOUT ----------

st.title("🌧 FloodSight Malaysia")
st.markdown("### Realtime Flood Risk Forecast for Malaysian Cities")
st.markdown("Note: Cities with 🌊 symbol are known to be flood-prone areas.")

# Sidebar for controls
st.sidebar.header("🔍 Select Location & Date")
selected_state = st.sidebar.selectbox("State", sorted(state_city_coords.keys()))
cities = sorted(state_city_coords.get(selected_state, {}).keys())
selected_city = st.sidebar.selectbox("City", cities) if cities else None
selected_date = st.sidebar.date_input(
    "Date",
    value=datetime.today(),
    min_value=datetime(2023, 1, 1),
    max_value=datetime.today()
)
selected_date_str = selected_date.strftime("%Y-%m-%d")

if not selected_city:
    st.error(f"No cities found for state {selected_state}")
    st.stop()

latitude, longitude = state_city_coords[selected_state][selected_city]

st.markdown("#### 🗺 City Location on Map")
map_df = pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"])
st.map(map_df, zoom=10)

if st.sidebar.button("🔎 Check Flood Risk"):

    with st.spinner("Fetching current weather and historical data..."):
        weather = get_weather(selected_city)
        if weather is None:
            st.error("❌ Failed to retrieve current weather data.")
        else:
            daily_rain = get_daily_rainfall(selected_city, selected_date_str)
            if daily_rain is None:
                daily_rain = 0.0

            # Flood risk override for known flood events:
            if (selected_date_str in known_flood_events and selected_city in known_flood_events[selected_date_str]):
                risk = "🔴 High (Known Flood Event)"
            else:
                risk = estimate_risk(daily_rain, weather["humidity"])

            st.markdown(f"### Weather in {selected_city} on {selected_date.strftime('%d %b %Y')}")
            st.write(f"- Temperature: {weather['temperature']} °C")
            st.write(f"- Humidity: {weather['humidity']} %")
            st.write(f"- Rainfall: {daily_rain} mm")
            st.markdown(f"**Flood Risk Level:** {risk}")

            st.markdown("---")
            st.markdown("### 7-Day Rainfall Forecast & Flood Risk")
            forecast = get_7_day_forecast(selected_city)
            if forecast:
                df_forecast = pd.DataFrame(forecast)
                st.dataframe(df_forecast.style.applymap(
                    lambda v: 'background-color: #FFCCCC' if ("High" in str(v)) else '',
                    subset=["Risk"]
                ))
            else:
                st.info("Forecast data not available.")

            st.markdown("---")
            st.markdown("### Flood Risk Alert Across All Cities for Selected Date")
            high_risk_cities = highlight_high_risk_cities(selected_date_str)
            if high_risk_cities:
                st.warning(f"Cities at high flood risk on {selected_date.strftime('%d %b %Y')}:")
                for c in high_risk_cities:
                    st.write(f"- {c}")
            else:
                st.info(f"No high risk cities detected on {selected_date.strftime('%d %b %Y')}.")

# User manual in expander
with st.expander("🛈 How to Use FloodSight Malaysia - User Manual"):
    st.markdown("""
    Welcome to **FloodSight Malaysia**! Here's how to use this app:

    1. **Select a State and City:**  
       Use the sidebar dropdowns to pick a Malaysian state and city. Cities with a 🌊 symbol are known flood-prone areas.

    2. **Select a Date:**  
       Choose a date (default is today). You can check flood risk for any day from 1 Jan 2023 to today.

    3. **Check Flood Risk:**  
       Click the "Check Flood Risk" button to fetch current weather and historical rainfall data for your city and date.

    4. **Interpret the Results:**  
       - The app shows temperature, humidity, and rainfall for the selected city and date.  
       - Flood risk levels are estimated as Low (🟢), Moderate (🟠), or High (🔴).  
       - High risk means heavy rain and high humidity, indicating potential flooding.

    5. **7-Day Forecast:**  
       See the upcoming 7-day rainfall, temperature, humidity, and flood risk forecast for your selected city.

    6. **Flood Risk Alert:**  
       Check a list of all Malaysian cities currently predicted to be at high flood risk on the chosen date.

    7. **City Location Map:**  
       View your selected city on the map for quick geographic context.

    8. **Safety Tips:**  
       - Prepare emergency supplies and know evacuation routes.  
       - Avoid traveling during flood warnings.  
       - Stay tuned to official news for updates.

    **Note:**  
    Data comes from WeatherAPI and known flood event records. Accuracy depends on weather data availability and API response.

    Thank you for using FloodSight Malaysia — stay safe and prepared!
    """)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by FloodSight Malaysia Team. Data from WeatherAPI.com")
