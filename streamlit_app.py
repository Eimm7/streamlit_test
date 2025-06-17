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
st.set_page_config(page_title="\ud83c\udf27 Flood Buddy - Malaysia", page_icon="\u2614", layout="wide")
st.markdown("""
<style>
.stButton button { background:#28a745;color:#fff;font-weight:bold;border-radius:8px; }
.news-card { background:#e3f2fd;border-left:5px solid #0077b6;padding:16px;margin:10px 0;border-radius:6px;
             box-shadow:2px 2px 6px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- API keys & session setup ---
API_KEY = "1468e5c2a4b24ce7a64140429250306"  # WeatherAPI key
NEWS_API_KEY = "pub_6b426fe08efa4436a4cd58ec988c62e0"  # NewsData API key
session = retry(requests_cache.CachedSession('.cache', expire_after=3600), retries=5, backoff_factor=0.2)
geolocator = Nominatim(user_agent="flood-buddy-app")

# --- Flood-prone districts ---
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

# --- Sidebar inputs ---
with st.sidebar:
    st.title("\u2699\ufe0f Settings")
    state = st.selectbox("State", list(flood_map.keys()))
    district = st.selectbox("District", flood_map[state])
    date = st.date_input("Forecast Date", datetime.today())
    coord_override = st.text_input("Or enter coords manually (lat,lon)")
    go = st.button("\ud83d\udd0d Get Forecast")

# --- Risk level logic ---
def risk_level(r):
    return "Extreme" if r > 50 else "High" if r > 30 else "Moderate" if r > 10 else "Low"

def tip(l):
    return {
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

# --- Main app logic ---
if go:
    if coord_override and "," in coord_override:
        lat, lon = map(float, coord_override.split(","))
    else:
        lat, lon = get_coords(state, district)
        if lat is None:
            st.error("Could not geolocate this district. Please enter coordinates manually.")
            st.stop()

    w = session.get(f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=14").json()
    o = session.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto").json()

    rain = [d["day"]["totalprecip_mm"] for d in w["forecast"]["forecastday"]]
    df = pd.DataFrame({
        "Date": [d["date"] for d in w["forecast"]["forecastday"]],
        "Rain (mm)": rain,
        "Temp (\u00b0C)": [d["day"]["maxtemp_c"] for d in w["forecast"]["forecastday"]],
        "Humidity (%)": [d["day"]["avghumidity"] for d in w["forecast"]["forecastday"]],
        "Wind (kph)": [d["day"]["maxwind_kph"] for d in w["forecast"]["forecastday"]],
    })

    tabs = st.tabs(["Forecast","Map","Trends","Risk Pie","History","News"])

    with tabs[0]:
        today_rain = df.iloc[0]["Rain (mm)"]
        open_meteo_today_rain = o["daily"]["precipitation_sum"][0]
        lvl = risk_level(max(today_rain, open_meteo_today_rain))
        getattr(st, {"Extreme": "error", "High": "warning", "Moderate": "info", "Low": "success"}[lvl])(f"{lvl} today – {tip(lvl)}")

        st.subheader("\ud83d\uddd3\ufe0f 14-Day Forecast")
        st.dataframe(df.style.format({
            "Rain (mm)": "{:.1f}",
            "Temp (°C)": "{:.1f}",
            "Humidity (%)": "{:.0f}",
            "Wind (kph)": "{:.1f}"
        }), use_container_width=True, height=600)

    with tabs[1]:
        st.subheader("\ud83d\udccd Map View")
        map_df = pd.DataFrame({"lat": [lat], "lon": [lon], "intensity": [open_meteo_today_rain]})
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=8),
            layers=[
                pdk.Layer("ScatterplotLayer", data=map_df, get_position='[lon, lat]', get_color='[200, 30, 0, 160]', get_radius=8000),
                pdk.Layer("HeatmapLayer", data=map_df, get_position='[lon, lat]', get_weight='intensity')
            ]
        ))

    with tabs[2]:
        st.subheader("\ud83d\udcca Trends")
        st.line_chart(df.set_index("Date")[["Rain (mm)", "Temp (°C)"]])
        st.bar_chart(df.set_index("Date")["Humidity (%)"])
        st.area_chart(df.set_index("Date")["Wind (kph)"])

    with tabs[3]:
        st.subheader("\ud83c\udf10 Risk Distribution")
        counts = df["Rain (mm)"].map(risk_level).value_counts()
        plt.figure(figsize=(6,6))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%")
        st.pyplot(plt)

    with tabs[4]:
        st.subheader("\u23f2\ufe0f Historical Comparison")
        h = df.copy()
        np.random.seed(0)
        h["HistRain"] = h["Rain (mm)"] + np.random.randint(-5,6,size=len(h))
        st.line_chart(h.set_index("Date")[["Rain (mm)", "HistRain"]])

    with tabs[5]:
        st.subheader("\ud83d\udd24 Latest Flood News")
        news = fetch_news()
        if news:
            for n in news:
                st.markdown(f"""
                <div class="news-card">
                  <strong>{n['title']}</strong><br><small>{n.get('pubDate','')}</small><br>
                  <a href="{n['link']}" target="_blank">\ud83d\udd17 Read more</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent flood news found.")
