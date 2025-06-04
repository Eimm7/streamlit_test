# Malaysia Flood Risk Forecast Dashboard
# Developed for BVI1234 - Technology System Programming II
# Author: [Your Name Here]
# Date: June 2025

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- App Configuration --- #
st.set_page_config(page_title="Malaysia Flood Dashboard", page_icon="🌧️", layout="wide")

# --- Sidebar --- #
st.sidebar.title("🌧️ Flood Risk & Safety Dashboard")
st.sidebar.markdown("""
### 📅 Instructions:
1. Select your state and city below.
2. Review rainfall forecast and flood risk areas.

### ⚠️ Emergency Tips:
- Prepare a Go-Bag.
- Monitor flood alerts.
- Avoid flood-prone roads.
- Stay in contact with authorities.
""")

# --- Flood-prone locations by state --- #
flood_map = {
    "Selangor": {"Klang": (3.03, 101.45), "Shah Alam": (3.07, 101.52), "Kajang": (2.99, 101.78), "Hulu Langat": (3.1, 101.8), "Ampang": (3.15, 101.76)},
    "Johor": {"Johor Bahru": (1.49, 103.74), "Batu Pahat": (1.85, 102.93), "Muar": (2.05, 102.57), "Kulai": (1.66, 103.6), "Segamat": (2.51, 102.81)},
    "Kedah": {"Alor Setar": (6.12, 100.37), "Sungai Petani": (5.65, 100.49), "Baling": (5.67, 100.92), "Langkawi": (6.33, 99.84), "Pendang": (5.98, 100.47)},
    "Kelantan": {"Kota Bharu": (6.13, 102.24), "Pasir Mas": (6.04, 102.14), "Machang": (5.76, 102.23), "Tanah Merah": (5.8, 102.15), "Tumpat": (6.2, 102.17)},
    "Melaka": {"Melaka City": (2.19, 102.25), "Alor Gajah": (2.38, 102.2), "Jasin": (2.3, 102.43), "Merlimau": (2.16, 102.43), "Masjid Tanah": (2.35, 102.1)},
    "Negeri Sembilan": {"Seremban": (2.73, 101.94), "Port Dickson": (2.52, 101.8), "Jempol": (2.73, 102.4), "Rembau": (2.6, 102.08), "Tampin": (2.47, 102.23)},
    "Pahang": {"Kuantan": (3.82, 103.33), "Bentong": (3.52, 101.9), "Raub": (3.79, 101.85), "Temerloh": (3.45, 102.42), "Jerantut": (3.93, 102.37)},
    "Penang": {"George Town": (5.41, 100.33), "Bukit Mertajam": (5.36, 100.47), "Balik Pulau": (5.32, 100.23), "Butterworth": (5.4, 100.38), "Bayan Lepas": (5.29, 100.28)},
    "Perak": {"Ipoh": (4.6, 101.07), "Taiping": (4.85, 100.74), "Teluk Intan": (4.03, 101.02), "Lumut": (4.23, 100.63), "Manjung": (4.17, 100.68)},
    "Perlis": {"Kangar": (6.44, 100.2), "Arau": (6.43, 100.28), "Padang Besar": (6.65, 100.3), "Kaki Bukit": (6.6, 100.2), "Simpang Empat": (6.4, 100.15)},
    "Sabah": {"Kota Kinabalu": (5.98, 116.07), "Tawau": (4.26, 117.88), "Sandakan": (5.84, 118.11), "Keningau": (5.33, 116.16), "Lahad Datu": (5.02, 118.33)},
    "Sarawak": {"Kuching": (1.55, 110.33), "Sibu": (2.3, 111.83), "Bintulu": (3.17, 113.03), "Miri": (4.4, 113.98), "Sri Aman": (1.24, 111.45)},
    "Terengganu": {"Kuala Terengganu": (5.33, 103.14), "Dungun": (4.77, 103.42), "Kemaman": (4.23, 103.45), "Marang": (5.2, 103.22), "Besut": (5.73, 102.56)},
    "Putrajaya": {"Precinct 5": (2.89, 101.68), "Precinct 8": (2.91, 101.68), "Precinct 14": (2.95, 101.69), "Precinct 18": (2.94, 101.72), "Putrajaya": (2.93, 101.7)},
    "Kuala Lumpur": {"Kuala Lumpur": (3.14, 101.69), "Cheras": (3.08, 101.74), "Setapak": (3.2, 101.72), "Wangsa Maju": (3.2, 101.73), "Sentul": (3.19, 101.7)},
    "Labuan": {"Labuan": (5.28, 115.25), "Victoria": (5.28, 115.24), "Bebuloh": (5.26, 115.23), "Patau-Patau": (5.29, 115.25), "Sungai Miri": (5.3, 115.26)}
}

# --- Location Selection --- #
st.title("Malaysia 🇲🇾 Flood Forecast Dashboard")
st.markdown("Stay informed on rainfall and flood risk areas across Malaysia.")

selected_state = st.selectbox("Select a state", list(flood_map.keys()))
selected_city = st.selectbox("Select a city", list(flood_map[selected_state].keys()))
lat, lon = flood_map[selected_state][selected_city]

# --- Fetch weather data --- #
API_KEY = "1468e5c2a4b24ce7a64140429250306"
url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7&aqi=no&alerts=no"
res = requests.get(url)
weather = res.json() if res.status_code == 200 else None

# --- Tabs --- #
tab1, tab2 = st.tabs(["Rainfall Forecast", "Flood Risk Maps"])

# --- Tab 1: Rainfall --- #
with tab1:
    if weather:
        st.subheader(f"7-Day Forecast for {selected_city}, {selected_state}")
        forecast_data = [
            {
                "Date": day["date"],
                "Condition": day["day"]["condition"]["text"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"]
            }
            for day in weather["forecast"]["forecastday"]
        ]
        df = pd.DataFrame(forecast_data)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("Date")["Rainfall (mm)"])
        st.line_chart(df.set_index("Date")["Rainfall (mm)"])
    else:
        st.error("Unable to fetch weather data. Check your internet connection or API key.")

# --- Tab 2: Maps --- #
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔹 Selected Location Map")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10),
            layers=[pdk.Layer("ScatterplotLayer", data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                               get_position='[lon, lat]', get_radius=6000, get_color='[255, 0, 0, 160]')]
        ))

    with col2:
        st.markdown("#### 🔸 National Risk Areas")
        all_coords = [
            {"lat": v[0], "lon": v[1]}
            for state in flood_map.values() for v in state.values()
        ]
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=4.2, longitude=109.5, zoom=5),
            layers=[pdk.Layer("ScatterplotLayer", data=pd.DataFrame(all_coords),
                               get_position='[lon, lat]', get_radius=5000, get_color='[255, 140, 0, 160]')]
        ))

# --- Footer --- #
st.markdown("---")
st.caption("Developed for BVI1234 - Technology System Programming II - Flood Forecast Mini Project")
