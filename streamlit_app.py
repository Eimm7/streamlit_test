import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import pydeck as pdk

# ========== CONFIGURATION ==========
API_KEY = "1468e5c2a4b24ce7a64140429250306"

# All 16 Malaysian states with multiple flood-prone cities and coordinates
flood_data = {
    "Selangor": {
        "Klang": (3.033, 101.45),
        "Shah Alam": (3.0738, 101.5183),
        "Kajang": (2.9917, 101.7871),
        "Subang Jaya": (3.0432, 101.5807),
        "Ampang": (3.1511, 101.7645)
    },
    "Johor": {
        "Johor Bahru": (1.4927, 103.7414),
        "Batu Pahat": (1.8545, 102.9325),
        "Muar": (2.0463, 102.5684),
        "Segamat": (2.5141, 102.8107),
        "Kluang": (2.0325, 103.3174)
    },
    "Kedah": {
        "Alor Setar": (6.121, 100.367),
        "Sungai Petani": (5.645, 100.487),
        "Kulim": (5.37, 100.56),
        "Pendang": (5.98, 100.47),
        "Baling": (5.673, 100.915)
    },
    "Kelantan": {
        "Kota Bharu": (6.133, 102.238),
        "Pasir Mas": (6.05, 102.14),
        "Tumpat": (6.198, 102.17),
        "Machang": (5.765, 102.23),
        "Tanah Merah": (5.8, 102.15)
    },
    "Melaka": {
        "Melaka City": (2.1896, 102.2501),
        "Jasin": (2.308, 102.43),
        "Alor Gajah": (2.39, 102.2),
        "Merlimau": (2.1564, 102.4286),
        "Masjid Tanah": (2.35, 102.1)
    },
    "Negeri Sembilan": {
        "Seremban": (2.728, 101.938),
        "Port Dickson": (2.5156, 101.801),
        "Rembau": (2.6, 102.083),
        "Tampin": (2.47, 102.23),
        "Jempol": (2.73, 102.4)
    },
    "Pahang": {
        "Kuantan": (3.816, 103.325),
        "Temerloh": (3.45, 102.417),
        "Bentong": (3.516, 101.9),
        "Raub": (3.79, 101.85),
        "Jerantut": (3.93, 102.37)
    },
    "Penang": {
        "George Town": (5.4141, 100.3288),
        "Bukit Mertajam": (5.36, 100.466),
        "Seberang Perai": (5.45, 100.39),
        "Balik Pulau": (5.32, 100.23),
        "Butterworth": (5.4, 100.38)
    },
    "Perak": {
        "Ipoh": (4.6, 101.07),
        "Taiping": (4.85, 100.74),
        "Teluk Intan": (4.03, 101.02),
        "Lumut": (4.23, 100.63),
        "Manjung": (4.17, 100.68)
    },
    "Perlis": {
        "Kangar": (6.44, 100.2),
        "Arau": (6.43, 100.28),
        "Padang Besar": (6.65, 100.3),
        "Simpang Empat": (6.4, 100.15),
        "Kaki Bukit": (6.6, 100.2)
    },
    "Sabah": {
        "Kota Kinabalu": (5.98, 116.07),
        "Sandakan": (5.84, 118.11),
        "Tawau": (4.26, 117.88),
        "Lahad Datu": (5.02, 118.33),
        "Keningau": (5.33, 116.16)
    },
    "Sarawak": {
        "Kuching": (1.55, 110.33),
        "Sibu": (2.3, 111.83),
        "Bintulu": (3.17, 113.03),
        "Miri": (4.4, 113.98),
        "Sri Aman": (1.24, 111.45)
    },
    "Terengganu": {
        "Kuala Terengganu": (5.33, 103.14),
        "Dungun": (4.77, 103.42),
        "Kemaman": (4.23, 103.45),
        "Marang": (5.2, 103.22),
        "Besut": (5.73, 102.56)
    },
    "Putrajaya": {
        "Putrajaya": (2.9264, 101.6964)
    },
    "Kuala Lumpur": {
        "Kuala Lumpur": (3.139, 101.6869)
    },
    "Labuan": {
        "Labuan": (5.28, 115.25)
    }
}


# ========== SIDEBAR ==========
st.sidebar.title("🌧️ Flood Risk Dashboard Malaysia")
st.sidebar.info("🚨 **Instructions:**\n\n- Select a state and city.\n- View weather forecast, rainfall trend, and risk area.\n\n🧰 **Preparedness Tips:**\n\n- Stay informed.\n- Have an emergency kit.\n- Avoid flooded roads.\n- Evacuate early if needed.")

# ========== MAIN ==========
st.title("🇲🇾 Malaysia Flood Risk Forecast Dashboard")
st.markdown("Real-time 🌧️ rainfall forecast, historical data, and flood-prone mapping across Malaysia.")

# ========== USER INPUT ==========
state = st.selectbox("Select a State", list(flood_data.keys()))
city = st.selectbox("Select a City", list(flood_data[state].keys()))
lat, lon = flood_data[state][city]

# ========== FETCH WEATHER DATA ==========
def fetch_weather_data(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7&aqi=no&alerts=no"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

data = fetch_weather_data(city)

# ========== WEATHER INFO ==========
if data:
    st.subheader(f"📍 Weather Forecast for {city}, {state}")
    forecast_days = data["forecast"]["forecastday"]

    # --- Rainfall Table ---
    rainfall_df = pd.DataFrame([{
        "Date": day["date"],
        "Rainfall (mm)": day["day"]["totalprecip_mm"],
        "Condition": day["day"]["condition"]["text"]
    } for day in forecast_days])
    st.dataframe(rainfall_df)

    # --- Rainfall Chart ---
    st.line_chart(rainfall_df.set_index("Date")["Rainfall (mm)"])

    # --- Tabs for Maps ---
    tab1, tab2 = st.tabs(["📌 Local Risk Area", "🌍 National Flood Map"])

    with tab1:
        st.markdown("### Location View")
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                    get_position='[lon, lat]',
                    get_color='[255, 0, 0, 160]',
                    get_radius=8000,
                ),
            ],
        ))

    with tab2:
        st.markdown("### All Risk Areas in Malaysia")
        all_points = [
            {"lat": v[0], "lon": v[1], "city": c, "state": s}
            for s, cities in flood_data.items()
            for c, v in cities.items()
        ]
        df_all = pd.DataFrame(all_points)
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(latitude=4.2, longitude=109.5, zoom=5),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=df_all,
                    get_position='[lon, lat]',
                    get_color='[255, 140, 0, 160]',
                    get_radius=6000,
                )
            ]
        ))
else:
    st.error("⚠️ Could not fetch weather data. Please try again later.")

# ========== END ==========
st.markdown("---")
st.caption("📘 Developed for BVI1234 Technology System Programming II")
