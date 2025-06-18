# --------------------------------------------
# 🌧 Malaysia Flood Risk Buddy 
# BVI1234 | Group VC24001 · VC24009 · VC24011
# --------------------------------------------

# --- 🧠 Import Libraries and Tools ---
import streamlit as st                  # Streamlit for building the web interface
import requests                         # For sending API requests
import pandas as pd                     # For working with tabular data
import numpy as np                      # For numerical operations
import matplotlib.pyplot as plt         # For plotting the pie chart
import pydeck as pdk                    # For rendering interactive maps
from datetime import datetime, timedelta  # To handle dates and time windows
import requests_cache                   # To cache API responses and reduce calls
from retry_requests import retry        # Adds retry mechanism to HTTP requests
from geopy.geocoders import Nominatim   # For geolocation lookup (lat/lon from address)

# --- 🖼 Page Configuration & CSS Styling ---
st.set_page_config(page_title="Flood Buddy - Malaysia", page_icon="☔", layout="wide")

# Injecting custom button style using HTML/CSS
st.markdown("""
<style>
.stButton button {
    background:#28a745;
    color:#fff;
    font-weight:bold;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# --- 🔐 API Keys and Caching Setup ---
API_KEY = "1468e5c2a4b24ce7a64140429250306"                       # WeatherAPI key for weather forecast
NEWS_API_KEY = "pub_6b426fe08efa4436a4cd58ec988c62e0"             # NewsData.io key for fetching news articles
session = retry(requests_cache.CachedSession('.cache', expire_after=3600), retries=5, backoff_factor=0.2)
geolocator = Nominatim(user_agent="flood-buddy-app")              # Geolocator for translating address to coordinates

# --- 📍 Define Flood-Prone Districts by State (Malaysia) ---
flood_map = {
    "Selangor": ["Shah Alam", "Petaling", "Klang", "Gombak", "Hulu Langat", "Sabak Bernam"],
    "Johor": ["Johor Bahru", "Batu Pahat", "Muar", "Kluang", "Segamat", "Kota Tinggi"],
    "Sarawak": ["Kuching", "Sibu", "Miri", "Bintulu", "Sri Aman", "Limbang"],
    "Sabah": ["Kota Kinabalu", "Sandakan", "Tawau", "Lahad Datu", "Beaufort", "Keningau"],
    "Kelantan": ["Kota Bharu", "Pasir Mas", "Tumpat", "Gua Musang", "Tanah Merah"],
    "Terengganu": ["Kuala Terengganu", "Dungun", "Kemaman", "Besut", "Setiu"],
    "Pahang": ["Kuantan", "Temerloh", "Jerantut", "Raub", "Bentong"],
    "Penang": ["George Town", "Seberang Perai", "Balik Pulau"],
    "Perak": ["Ipoh", "Taiping", "Teluk Intan", "Lumut"],
    "Negeri Sembilan": ["Seremban", "Port Dickson", "Jempol"],
    "Melaka": ["Melaka Tengah", "Alor Gajah", "Jasin"],
    "Kedah": ["Alor Setar", "Sungai Petani", "Kulim"],
    "Perlis": ["Kangar", "Arau"]
}

# --- 🧭 Sidebar User Input Form ---
with st.sidebar:
    st.markdown("## 🌧️ **Flood Risk Buddy**")
    st.caption("Malaysia Flood Risk Forecast & Updates")
    st.title("⚙️ Settings")
    state = st.selectbox("State", list(flood_map.keys()))                    # Select a state
    district = st.selectbox("District", flood_map[state])                   # Select a district within the state
    date = st.date_input("Forecast Date", datetime.today())                 # Choose forecast date
    coord_override = st.text_input("Or enter coords manually (lat,lon)")    # Optional manual coordinate entry
    go = st.button("🔍 Get Forecast")                                        # Action trigger

# --- 🧩 Helper Functions for Data Processing ---
def risk_level(rain):
    """Assign risk level based on rainfall in mm."""
    return "Extreme" if rain > 50 else "High" if rain > 30 else "Moderate" if rain > 10 else "Low"

def tip(level):
    """Return flood preparedness tip based on risk level."""
    return {
        "Extreme": "Evacuate if needed; avoid floodwaters.",
        "High":     "Charge devices; avoid low areas.",
        "Moderate": "Monitor alerts; stay indoors.",
        "Low":      "Stay aware."
    }[level]

def get_coords(state, district):
    """Retrieve latitude and longitude from a given district + state."""
    try:
        location = geolocator.geocode(f"{district}, {state}, Malaysia", timeout=10)
        return (location.latitude, location.longitude)
    except:
        return (None, None)

def fetch_news(search_term):
    """Fetch flood-related news using NewsData.io."""
    try:
        r = session.get(f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={search_term}%20flood%20malaysia")
        results = r.json().get("results", [])
        keywords = ["flood", "banjir", "evacuate", "rain", "landslide", "inundation"]
        filtered = [n for n in results if any(k in n["title"].lower() for k in keywords)]
        return filtered
    except:
        return []

# --- 🌧️ Forecast and Display Logic ---
if go:
    # 📍 Get coordinates from user input or auto-detection
    if coord_override and "," in coord_override:
        lat, lon = map(float, coord_override.split(","))
    else:
        lat, lon = get_coords(state, district)
        if lat is None:
            st.error("Could not geolocate this district. Please enter coordinates manually.")
            st.stop()

    # 📅 Define forecast time range (3-day window)
    today = datetime.today()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")

    # 🌐 Call WeatherAPI and Open-Meteo for forecast data
    w = session.get(f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=3").json()
    o = session.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum&timezone=auto").json()

    # 📊 Format forecast data into a dataframe
    rain = [d["day"]["totalprecip_mm"] for d in w["forecast"]["forecastday"]]
    df = pd.DataFrame({
        "Date": [d["date"] for d in w["forecast"]["forecastday"]],
        "Rain (mm)": rain,
        "Temp (°C)": [d["day"]["maxtemp_c"] for d in w["forecast"]["forecastday"]],
        "Humidity (%)": [d["day"]["avghumidity"] for d in w["forecast"]["forecastday"]],
        "Wind (kph)": [d["day"]["maxwind_kph"] for d in w["forecast"]["forecastday"]],
    })

    # --- 📊 Tabbed Interface for Output Display ---
    tabs = st.tabs(["🌧️ Forecast", "🗺️ Map View", "📈 Trends", "🧭 Risk Overview", "📰 News"])

    with tabs[0]:
        # 🌧️ Show today's flood risk level and recommendation
        lvl = risk_level(max(rain[0], o["daily"]["precipitation_sum"][0]))
        getattr(st, {"Extreme":"error","High":"warning","Moderate":"info","Low":"success"}[lvl])(f"{lvl} today – {tip(lvl)}")

        st.subheader("📅 3-Day Forecast")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

        # ✅ Real Past Rain Data (7 days) via Open-Meteo ERA5
        # --------------------------------------------------
        # This section retrieves accurate daily rainfall totals for the past 7 days.
        # Open-Meteo's historical ERA5 API is used for this purpose.
        # The resulting table displays real, location-based rainfall values.
        # --------------------------------------------------
        past_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        past_end = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        hist_url = (
            f"https://archive-api.open-meteo.com/v1/era5?"
            f"latitude={lat}&longitude={lon}&start_date={past_start}&end_date={past_end}"
            f"&daily=precipitation_sum&timezone=auto"
        )
        try:
            hist = session.get(hist_url).json()
            if "daily" in hist:
                df_past = pd.DataFrame({
                    "Date": hist["daily"]["time"],
                    "Rain (mm)": hist["daily"]["precipitation_sum"]
                })
                st.subheader("📊 Past Rain Data (7 days actual)")
                st.dataframe(df_past, use_container_width=True)
            else:
                st.warning("No historical data available.")
        except:
            st.error("Failed to retrieve historical rainfall.")

    with tabs[1]:
        # 🗺️ Map View using Pydeck
        data = pd.DataFrame({
            "lat": [lat],
            "lon": [lon],
            "intensity": [o["daily"]["precipitation_sum"][0]],
            "tooltip": [f"Location: {district}, {state}\nRainfall: {o['daily']['precipitation_sum'][0]} mm"]
        })
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8),
            layers=[pdk.Layer(
                "ScatterplotLayer",
                data=data,
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 100]',
                get_radius=10000,
                pickable=True,
                opacity=0.3
            )],
            tooltip={"text": "{tooltip}"}
        ))

    with tabs[2]:
        # 📈 Trend Charts for Rain, Humidity, Wind
        st.subheader("Rainfall Trend")
        st.line_chart(df.set_index("Date")["Rain (mm)"])
        st.subheader("Humidity Trend")
        st.bar_chart(df.set_index("Date")["Humidity (%)"])
        st.subheader("Wind Speed Trend")
        st.area_chart(df.set_index("Date")["Wind (kph)"])

    with tabs[3]:
        # 🧭 Risk Level Pie Chart (3-Day Forecast)
        counts = df["Rain (mm)"].map(risk_level).value_counts()
        plt.figure(figsize=(6,6))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%")
        st.pyplot(plt)

    with tabs[4]:
        # 📰 News Tab with filtered flood-related articles
        search_term = st.text_input("Search flood news for Malaysia:", "flood")
        if search_term:
            news = fetch_news(search_term)
            if news:
                for n in news:
                    st.markdown(f"- **{n['title']}**\n  _{n.get('pubDate','')}_\n  [🔗 Read more]({n['link']})")
            else:
                st.info("No relevant flood-related news articles found.")
