import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ---------- CONFIG ----------
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
WEATHERAPI_KEY = "1468e5c2a4b24ce7a64140429250306"  # Replace with your own key if needed

# ---------- HEADER ----------
st.title("🌧 FloodSight Malaysia")
st.markdown("### Realtime Flood Risk Forecast for Malaysian Cities")
st.markdown("Note: Cities with 🌊 symbol are known to be flood-prone areas.")

# ---------- CITY COORDINATES ----------
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

# ---------- FUNCTIONS ----------
def get_forecast_rain(city, days=7):
    try:
        res = requests.get(
            "http://api.weatherapi.com/v1/forecast.json",
            params={"key": WEATHERAPI_KEY, "q": city, "days": days},
            timeout=10,
        )
        if res.status_code == 200:
            data = res.json()
            result = []
            for day in data["forecast"]["forecastday"]:
                result.append({
                    "date": day["date"],
                    "rain": day["day"]["totalprecip_mm"],
                    "humidity": day["day"]["avghumidity"]
                })
            return result
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

# ---------- SIDEBAR: HIGH RISK DETECTION ----------
st.sidebar.markdown("## 🔍 High-Risk Cities (Next 7 Days)")
high_risk_cities = []
for state, cities in state_city_coords.items():
    for city in cities:
        forecast = get_forecast_rain(city, days=1)
        if forecast and forecast[0]["rain"] > 80 and forecast[0]["humidity"] > 85:
            high_risk_cities.append(f"{city} ({state})")

if high_risk_cities:
    for item in high_risk_cities:
        st.sidebar.warning(f"⚠ {item}")
else:
    st.sidebar.success("No high-risk cities today!")

# ---------- MAIN UI ----------
st.markdown("#### 🏙 Select Location")
selected_state = st.selectbox("State", sorted(state_city_coords.keys()))
cities = sorted(state_city_coords[selected_state].keys())
selected_city = st.selectbox("City", cities)

# ---------- FORECAST DISPLAY ----------
forecast_data = get_forecast_rain(selected_city, days=7)
if forecast_data:
    df = pd.DataFrame(forecast_data)
    df["Risk Level"] = df.apply(lambda row: estimate_risk(row["rain"], row["humidity"]), axis=1)
    st.markdown("#### 📈 7-Day Rainfall & Risk Forecast")
    st.dataframe(df)
    st.bar_chart(df.set_index("date")[["rain", "humidity"]])
else:
    st.error("⚠ Unable to retrieve forecast. Please try again.")
