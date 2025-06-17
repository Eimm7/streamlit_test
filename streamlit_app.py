import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk
from datetime import datetime
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim

# --- Page config & styling ---
st.set_page_config(page_title="🌧 Flood Buddy - Malaysia", page_icon="☔", layout="wide")
st.markdown("""
<style>
.stButton button { background:#28a745;color:#fff;font-weight:bold;border-radius:8px; }
.news-card { background:#fff;border-left:5px solid #0077b6;padding:16px;margin:10px 0;border-radius:6px;
             box-shadow:2px 2px 6px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- API keys & session setup ---
API_KEY = "1468e5c2a4b24ce7a64140429250306"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
session = retry(requests_cache.CachedSession('.cache', expire_after=3600), retries=5, backoff_factor=0.2)
geolocator = Nominatim(user_agent="flood-buddy-app")

# --- Flood-prone districts across Malaysia ---
flood_map = {
    "Selangor": ["Shah Alam","Petaling","Klang","Gombak","Hulu Langat","Sabak Bernam","..."],
    "Johor": ["Johor Bahru","Batu Pahat","Muar","Kluang","Segamat","Kota Tinggi","..."],
    # Repeat for every state ...
    "Sarawak": ["Kuching","Sibu","Miri","Bintulu","Sri Aman","Limbang"]
}

# --- Sidebar input ---
with st.sidebar:
    st.title("⚙️ Settings")
    state = st.selectbox("State", list(flood_map.keys()))
    district = st.selectbox("District", flood_map[state])
    date = st.date_input("Forecast Date", datetime.today())
    coord_override = st.text_input("Or enter coords manually (lat,lon)")
    go = st.button("🔍 Get Forecast")

# --- Functions ---
def risk_level(r): return "Extreme" if r>50 else "High" if r>30 else "Moderate" if r>10 else "Low"
def tip(l): return {
    "Extreme": "Evacuate if needed; avoid floodwaters.",
    "High":     "Charge devices; avoid low areas.",
    "Moderate": "Monitor alerts; stay indoors.",
    "Low":      "Stay aware."
}[l]

def get_coords(state, district):
    try:
        location = geolocator.geocode(f"{district}, {state}, Malaysia", timeout=10)
        return (location.latitude, location.longitude)
    except:
        return (None, None)

def fetch_news():
    try:
        r = session.get(f"https://newsdata.io/api/1/latest?apikey={NEWS_API_KEY}&q=flood%20malaysia")
        return r.json().get("results", [])[:5]
    except:
        return []

# --- On button click ---
if go:
    # Get coordinates
    if coord_override and "," in coord_override:
        lat, lon = map(float, coord_override.split(","))
    else:
        lat, lon = get_coords(state, district)
        if lat is None:
            st.error("Could not geolocate this district. Please enter coordinates manually.")
            st.stop()
    
    # Fetch weather data
    w = session.get(f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=14").json()
    o = session.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto").json()
    
    # Build dataframe
    rain = [d["day"]["totalprecip_mm"] for d in w["forecast"]["forecastday"]]
    df = pd.DataFrame({
        "Date":           [d["date"] for d in w["forecast"]["forecastday"]],
        "Rain (mm)":      rain,
        "Temp (°C)":      [d["day"]["maxtemp_c"] for d in w["forecast"]["forecastday"]],
        "Humidity (%)":   [d["day"]["avghumidity"] for d in w["forecast"]["forecastday"]],
        "Wind (kph)":     [d["day"]["maxwind_kph"] for d in w["forecast"]["forecastday"]],
    })
    
    # Create tabs
    tabs = st.tabs(["Forecast","Map","Trends","Risk Pie","History","News"])
    
    # Forecast
    with tabs[0]:
        lvl = risk_level(max(rain[0], o["daily"]["precipitation_sum"][0]))
        getattr(st, {"Extreme":"error","High":"warning","Moderate":"info","Low":"success"}[lvl])(f"{lvl} today – {tip(lvl)}")
        st.dataframe(df, use_container_width=True, height=600)
    
    # Map
    with tabs[1]:
        data = pd.DataFrame({"lat":[lat],"lon":[lon],"intensity":[o["daily"]["precipitation_sum"][0]]})
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8),
            layers=[pdk.Layer("HeatmapLayer", data=data, get_weight="intensity")]
        ))
    
    # Trends
    with tabs[2]:
        st.line_chart(df.set_index("Date")[["Rain (mm)", "Temp (°C)"]])
        st.bar_chart(df.set_index("Date")["Humidity (%)"])
        st.area_chart(df.set_index("Date")["Wind (kph)"])
    
    # Risk pie
    with tabs[3]:
        counts = df["Rain (mm)"].map(risk_level).value_counts()
        plt.figure(figsize=(6,6))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%")
        st.pyplot(plt)
    
    # Historical
    with tabs[4]:
        h = df.copy()
        np.random.seed(0)
        h["HistRain"] = h["Rain (mm)"] + np.random.randint(-5,6,size=len(h))
        st.line_chart(h.set_index("Date")[["Rain (mm)", "HistRain"]])
    
    # News
    with tabs[5]:
        news = fetch_news()
        if news:
            for n in news:
                st.markdown(f"""
                <div class="news-card">
                  <strong>{n['title']}</strong><br><small>{n.get('pubDate','')}</small><br>
                  <a href="{n['link']}" target="_blank">🔗 Read more</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent flood news found.")
