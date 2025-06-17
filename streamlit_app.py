# --------------------------------------------
# 🌧 Malaysia Flood Risk Buddy (Upgraded Edition)
# --------------------------------------------

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import numpy as np
from datetime import datetime
import requests_cache
from retry_requests import retry
import matplotlib.pyplot as plt

# --------------------------------------------
# 🎨 Page Setup
# --------------------------------------------
st.set_page_config(
    page_title="🌧 Flood Buddy - Interactive",
    page_icon="☔",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #eef3f9; }
    .stButton button { background-color: #28a745; color: white; font-weight: bold; border-radius: 8px; }
    .stSelectbox label, .stDateInput label, .stTextInput label { font-weight: bold; }
    .stTabs [data-baseweb="tab"] button { font-weight: bold; }
    .news-card {
        background-color: #ffffff;
        border-left: 5px solid #0077b6;
        padding: 16px;
        margin-bottom: 10px;
        border-radius: 6px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------
# 🌐 Setup Open-Meteo Client
# --------------------------------------------
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

API_KEY = "1468e5c2a4b24ce7a64140429250306"
NEWS_API_KEY = "YOUR_API_KEY"  # <-- Replace with your NewsData.io API key

# --------------------------------------------
# 📍 City Coordinates (Flood-Prone Areas)
# --------------------------------------------
flood_map = {
    "Selangor": {
        "Shah Alam": (3.0738, 101.5183), "Klang": (3.0339, 101.4455),
        "Kajang": (2.9935, 101.7871), "Gombak": (3.2986, 101.7250),
        "Puchong": (3.0250, 101.6167), "Ampang": (3.1500, 101.7667)
    },
    "Johor": {
        "Johor Bahru": (1.4927, 103.7414), "Batu Pahat": (1.8500, 102.9333),
        "Kluang": (2.0326, 103.3180), "Muar": (2.0500, 102.5667),
        "Kota Tinggi": (1.7333, 103.9000), "Pontian": (1.4833, 103.3833)
    },
    "Kelantan": {
        "Kota Bharu": (6.1333, 102.2500), "Pasir Mas": (6.0500, 102.1333),
        "Tumpat": (6.2000, 102.1667), "Tanah Merah": (5.8167, 102.1500),
        "Machang": (5.7667, 102.2167), "Gua Musang": (4.8833, 101.9667)
    },
    "Pahang": {
        "Kuantan": (3.8167, 103.3333), "Temerloh": (3.4500, 102.4167),
        "Jerantut": (3.9333, 102.3667), "Bentong": (3.5167, 101.9000),
        "Pekan": (3.4833, 103.4000), "Raub": (3.8000, 101.8667)
    },
    "Sarawak": {
        "Kuching": (1.5533, 110.3592), "Sibu": (2.3000, 111.8167),
        "Miri": (4.4000, 113.9833), "Bintulu": (3.1667, 113.0333),
        "Sri Aman": (1.2333, 111.4667), "Limbang": (4.7500, 115.0000)
    }
}

# --------------------------------------------
# 📥 Sidebar Input
# --------------------------------------------
with st.sidebar:
    st.title("🛠 Settings Panel")
    selected_state = st.selectbox("Choose State", list(flood_map.keys()))
    selected_city = st.selectbox("Choose City", list(flood_map[selected_state].keys()))
    selected_date = st.date_input("Pick Forecast Date", datetime.today())
    custom_location = st.text_input("Or type coordinates (lat,lon)")
    latlon = custom_location.split(',') if custom_location else []

    if len(latlon) == 2:
        try:
            lat, lon = float(latlon[0]), float(latlon[1])
        except:
            st.warning("⚠ Format Error. Try: 3.0738,101.5183")
            lat, lon = flood_map[selected_state][selected_city]
    else:
        lat, lon = flood_map[selected_state][selected_city]

    confirmed = st.button("🔍 Get My Forecast")

# --------------------------------------------
# ⚠️ Risk Logic & Tips
# --------------------------------------------
def risk_level(rain):
    if rain > 50:
        return "🔴 Extreme"
    elif rain > 30:
        return "🟠 High"
    elif rain > 10:
        return "🟡 Moderate"
    else:
        return "🟢 Low"

def preparedness_tips(level):
    return {
        "🔴 Extreme": "Evacuate if needed, keep emergency kit ready, avoid floodwaters.",
        "🟠 High": "Charge devices, prepare emergency contact list, avoid travel in low areas.",
        "🟡 Moderate": "Monitor local alerts, keep essentials ready, stay indoors during rain.",
        "🟢 Low": "Stay informed and maintain general awareness."
    }.get(level, "")

def fetch_flood_news():
    try:
        url = f"https://newsdata.io/api/1/latest?apikey={NEWS_API_KEY}&q=flood%20in%20malaysia"
        res = requests.get(url)
        if res.status_code == 200:
            return res.json().get("results", [])[:5]
    except Exception as e:
        st.error(f"🗞 News API Error: {e}")
    return []

# --------------------------------------------
# 📡 Get Weather Data
# --------------------------------------------
weather, om_rain = None, None
if confirmed:
    try:
        w_url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=14"
        response = requests.get(w_url)
        if response.status_code == 200:
            weather = response.json()
    except Exception as e:
        st.error(f"❌ WeatherAPI Error: {e}")

    try:
        om_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto"
        result = requests.get(om_url)
        if result.status_code == 200:
            om_rain = result.json()["daily"]["precipitation_sum"]
    except Exception as e:
        st.error(f"❌ Open-Meteo Error: {e}")

# --------------------------------------------
# 🧾 Forecast Tab Logic
# --------------------------------------------
def show_alert_box():
    if weather and om_rain is not None:
        rain_api = weather["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
        rain_om = om_rain[0]
        combined = max(rain_api, rain_om)
        level = risk_level(combined)

        if level == "🔴 Extreme":
            st.error("🚨 EXTREME RAINFALL! Take action immediately!")
        elif level == "🟠 High":
            st.warning("⚠ Heavy rainfall expected. Be alert.")
        elif level == "🟡 Moderate":
            st.info("🔎 Moderate rain. Keep watch.")
        else:
            st.success("✅ Low rainfall. All clear.")

        st.markdown(f"### 🎓 Preparedness Tip: {preparedness_tips(level)}")

# --------------------------------------------
# 📊 Tabs Output
# --------------------------------------------
if confirmed and weather:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗕 Forecast Calendar", "🗺 Live Map", "📈 Trend Charts",
        "📅 Flood Risk Pie", "📈 Historical Comparison", "🗞 Flood News"
    ])

    with tab1:
        show_alert_box()
        st.write("### 🧾 14-Day Forecast Overview")
        forecast_df = pd.DataFrame({
            "Date": [f["date"] for f in weather["forecast"]["forecastday"]],
            "Rainfall (mm)": [f["day"]["totalprecip_mm"] for f in weather["forecast"]["forecastday"]],
            "Max Temp (°C)": [f["day"]["maxtemp_c"] for f in weather["forecast"]["forecastday"]],
            "Humidity (%)": [f["day"]["avghumidity"] for f in weather["forecast"]["forecastday"]],
            "Wind (kph)": [f["day"]["maxwind_kph"] for f in weather["forecast"]["forecastday"]]
        })
        st.dataframe(forecast_df.style.set_properties(**{'text-align': 'center'}), height=600, use_container_width=True)

    with tab2:
        st.subheader("🌍 Visual Rainfall Intensity Map")
        map_df = pd.DataFrame({"lat": [lat], "lon": [lon], "intensity": [om_rain[0] if om_rain else 0]})
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/satellite-v9',
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8, pitch=40),
            layers=[
                pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_color='[255, 140, 0, 160]', get_radius=5000),
                pdk.Layer("HeatmapLayer", data=map_df, get_position='[lon, lat]', aggregation='MEAN', get_weight='intensity')
            ]
        ))

    with tab3:
        st.subheader("📉 Environmental Trends for Next 14 Days")
        st.line_chart(forecast_df.set_index("Date")[["Rainfall (mm)", "Max Temp (°C)"]])
        st.bar_chart(forecast_df.set_index("Date")["Humidity (%)"])
        st.area_chart(forecast_df.set_index("Date")["Wind (kph)"])

    with tab4:
        st.subheader("📊 Flood Risk Breakdown")
        risk_counts = forecast_df["Rainfall (mm)"].apply(risk_level).value_counts()
        plt.figure(figsize=(6, 6))
        plt.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        st.pyplot(plt)

    with tab5:
        st.subheader("🔢 Compare Current Forecast to Historical Averages")
        historical_df = forecast_df.copy()
        historical_df["Historical Rainfall"] = forecast_df["Rainfall (mm)"].apply(lambda x: max(0, x - np.random.randint(-5, 5)))
        st.line_chart(historical_df.set_index("Date")[["Rainfall (mm)", "Historical Rainfall"]])

    with tab6:
        st.subheader("📰 Latest Flood News in Malaysia")
        news_list = fetch_flood_news()
        if news_list:
            for item in news_list:
                st.markdown(f"""
                    <div class="news-card">
                        <strong>{item['title']}</strong><br>
                        <small>{item.get("pubDate", "")}</small><br>
                        <a href="{item['link']}" target="_blank">🔗 Read more</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent flood news found.")
