import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pydeck as pdk

# ---------------------- APP CONFIG ---------------------- #
st.set_page_config(
    page_title="Malaysia Flood Risk Dashboard",
    page_icon="🌧️",
    layout="wide"
)

# ---------------------- SIDEBAR ---------------------- #
st.sidebar.title("🚨 Emergency Flood Prep")
st.sidebar.markdown("""
### 🌊 Instructions:
1. Select a state and city from the dropdown.
2. View rainfall trends, forecast and risk maps.

### ⚠️ Flood Preparedness Tips:
- Stay tuned to weather alerts.
- Prepare an emergency kit.
- Avoid walking or driving through flood waters.
- Know your evacuation routes.
""")

# ---------------------- FLOOD-PRONE CITIES BY STATE ---------------------- #
flood_areas = {
    "Selangor": {
        "Klang": (3.03, 101.45), "Shah Alam": (3.07, 101.52), "Hulu Langat": (3.1, 101.8), "Kajang": (2.99, 101.78), "Subang Jaya": (3.05, 101.58)
    },
    "Johor": {
        "Johor Bahru": (1.49, 103.74), "Batu Pahat": (1.85, 102.93), "Segamat": (2.51, 102.81), "Muar": (2.05, 102.57), "Kulai": (1.66, 103.6)
    },
    "Kedah": {
        "Alor Setar": (6.12, 100.37), "Sungai Petani": (5.65, 100.49), "Baling": (5.67, 100.92), "Pendang": (5.98, 100.47), "Langkawi": (6.33, 99.84)
    },
    "Kelantan": {
        "Kota Bharu": (6.13, 102.24), "Pasir Mas": (6.04, 102.14), "Tumpat": (6.2, 102.17), "Machang": (5.76, 102.23), "Tanah Merah": (5.8, 102.15)
    },
    "Melaka": {
        "Melaka City": (2.19, 102.25), "Jasin": (2.3, 102.43), "Alor Gajah": (2.38, 102.2), "Merlimau": (2.16, 102.43), "Masjid Tanah": (2.35, 102.1)
    },
    "Negeri Sembilan": {
        "Seremban": (2.73, 101.94), "Port Dickson": (2.52, 101.8), "Jempol": (2.73, 102.4), "Tampin": (2.47, 102.23), "Rembau": (2.6, 102.08)
    },
    "Pahang": {
        "Kuantan": (3.82, 103.33), "Temerloh": (3.45, 102.42), "Bentong": (3.52, 101.9), "Raub": (3.79, 101.85), "Jerantut": (3.93, 102.37)
    },
    "Penang": {
        "George Town": (5.41, 100.33), "Bukit Mertajam": (5.36, 100.47), "Balik Pulau": (5.32, 100.23), "Bayan Lepas": (5.29, 100.28), "Butterworth": (5.4, 100.38)
    },
    "Perak": {
        "Ipoh": (4.6, 101.07), "Taiping": (4.85, 100.74), "Teluk Intan": (4.03, 101.02), "Manjung": (4.17, 100.68), "Lumut": (4.23, 100.63)
    },
    "Perlis": {
        "Kangar": (6.44, 100.2), "Arau": (6.43, 100.28), "Padang Besar": (6.65, 100.3), "Kaki Bukit": (6.6, 100.2), "Simpang Empat": (6.4, 100.15)
    },
    "Sabah": {
        "Kota Kinabalu": (5.98, 116.07), "Tawau": (4.26, 117.88), "Sandakan": (5.84, 118.11), "Lahad Datu": (5.02, 118.33), "Keningau": (5.33, 116.16)
    },
    "Sarawak": {
        "Kuching": (1.55, 110.33), "Sibu": (2.3, 111.83), "Bintulu": (3.17, 113.03), "Miri": (4.4, 113.98), "Sri Aman": (1.24, 111.45)
    },
    "Terengganu": {
        "Kuala Terengganu": (5.33, 103.14), "Dungun": (4.77, 103.42), "Kemaman": (4.23, 103.45), "Marang": (5.2, 103.22), "Besut": (5.73, 102.56)
    },
    "Putrajaya": {
        "Putrajaya": (2.93, 101.7), "Precinct 8": (2.91, 101.68), "Precinct 14": (2.95, 101.69), "Precinct 18": (2.94, 101.72), "Precinct 5": (2.89, 101.68)
    },
    "Kuala Lumpur": {
        "Kuala Lumpur": (3.14, 101.69), "Cheras": (3.08, 101.74), "Wangsa Maju": (3.2, 101.73), "Setapak": (3.2, 101.72), "Sentul": (3.19, 101.7)
    },
    "Labuan": {
        "Labuan": (5.28, 115.25), "Victoria": (5.28, 115.24), "Bebuloh": (5.26, 115.23), "Patau-Patau": (5.29, 115.25), "Sungai Miri": (5.3, 115.26)
    }
}

# ---------------------- USER SELECTION ---------------------- #
st.title("Malaysia 🇲🇾 Flood Risk Forecast Dashboard")
st.markdown("""An interactive dashboard with live rainfall data, historical charts, flood-prone areas and preparedness guide.
""")

state = st.selectbox("📝 Select State", list(flood_areas.keys()))
city = st.selectbox("🏠 Select City", list(flood_areas[state].keys()))
city_coords = flood_areas[state][city]

# ---------------------- WEATHER API ---------------------- #
API_KEY = "1468e5c2a4b24ce7a64140429250306"
endpoint = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7"
response = requests.get(endpoint)
data = response.json() if response.status_code == 200 else None

# ---------------------- TABS ---------------------- #
tab1, tab2 = st.tabs(["7-Day Rainfall ☔️", "🌍 Flood Risk Maps"])

# ---------------------- TAB 1: RAINFALL ---------------------- #
with tab1:
    if data:
        st.subheader(f"🌇 Forecast for {city}, {state}")
        forecast = data["forecast"]["forecastday"]

        # Table View
        forecast_table = pd.DataFrame([{
            "Date": day["date"],
            "Condition": day["day"]["condition"]["text"],
            "Rainfall (mm)": day["day"]["totalprecip_mm"]
        } for day in forecast])

        st.dataframe(forecast_table, use_container_width=True)
        st.bar_chart(forecast_table.set_index("Date")["Rainfall (mm)"])
        st.line_chart(forecast_table.set_index("Date")["Rainfall (mm)"])
    else:
        st.error("Unable to retrieve data. Please check your API key or internet connection.")

# ---------------------- TAB 2: MAPS ---------------------- #
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔹 Selected Location")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=city_coords[0], longitude=city_coords[1], zoom=10),
            layers=[pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame([{"lat": city_coords[0], "lon": city_coords[1]}]),
                get_position='[lon, lat]',
                get_radius=6000,
                get_color='[255, 0, 0, 160]',
            )]
        ))

    with col2:
        st.markdown("#### 🔸 National Risk Areas")
        all_points = [
            {"lat": lat, "lon": lon}
            for cities in flood_areas.values()
            for lat, lon in cities.values()
        ]
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=4.2, longitude=109.5, zoom=5),
            layers=[pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(all_points),
                get_position='[lon, lat]',
                get_radius=5000,
                get_color='[255, 140, 0, 160]',
            )]
        ))

# ---------------------- FOOTER ---------------------- #
st.markdown("---")
st.caption("Developed for BVI1234 • Technology System Programming II • Streamlit Flood Project")
