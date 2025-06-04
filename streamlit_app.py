import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# ---------------- PAGE SETTINGS ---------------- #
st.set_page_config(
    page_title="🌧 Malaysia Flood Forecast Dashboard",
    page_icon="🌀",
    layout="wide",
)

# ---------------- FLOOD-PRONE LOCATIONS ---------------- #
flood_map = {
    "Johor": {
        "Johor Bahru": (1.4927, 103.7414),
        "Segamat": (2.5090, 102.8106),
        "Batu Pahat": (1.8544, 102.9325),
    },
    "Kelantan": {
        "Kota Bharu": (6.1254, 102.2381),
        "Gua Musang": (4.8826, 101.9620),
        "Pasir Mas": (6.0495, 102.1396),
    },
    "Pahang": {
        "Kuantan": (3.8077, 103.3260),
        "Temerloh": (3.4521, 102.4158),
        "Pekan": (3.4981, 103.3890),
    },
    "Terengganu": {
        "Kuala Terengganu": (5.3302, 103.1408),
        "Dungun": (4.7586, 103.4250),
    },
    "Selangor": {
        "Shah Alam": (3.0738, 101.5183),
        "Hulu Langat": (3.1002, 101.7900),
    },
    "Penang": {
        "George Town": (5.4164, 100.3327),
        "Seberang Perai": (5.3962, 100.4663),
    },
    "Sabah": {
        "Kota Kinabalu": (5.9804, 116.0735),
        "Sandakan": (5.8380, 118.1170),
    },
    "Sarawak": {
        "Kuching": (1.5535, 110.3593),
        "Sibu": (2.2930, 111.8261),
    },
    "Perak": {
        "Ipoh": (4.5975, 101.0901),
        "Teluk Intan": (4.0163, 101.0246),
    },
    "Negeri Sembilan": {
        "Seremban": (2.7297, 101.9381),
        "Port Dickson": (2.5369, 101.8069),
    }
}

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("🌀 FloodSight Malaysia")
st.sidebar.markdown("""
## 🛠 How to Use:
1. Select your *State* and *City*
2. View 📊 rainfall charts & 📍 flood maps
3. Stay informed and safe ⚠

---

### 🧭 Tips:
- Monsoon peaks: Nov - Jan ☔
- Always prepare an emergency kit 🎒
- Follow METMalaysia for alerts 📢
""")

# ---------------- HEADER ---------------- #
st.title("🌧 Malaysia Flood Forecast & Risk Dashboard")
st.markdown("#### Real-time rainfall forecast, risk zones, and city-level insights 🚨")

# ---------------- USER SELECTION ---------------- #
col1, col2 = st.columns([1, 2])
with col1:
    state = st.selectbox("🏙 Select State", list(flood_map.keys()))
with col2:
    city = st.selectbox("🏘 Select City", list(flood_map[state].keys()))

lat, lon = flood_map[state][city]

# ---------------- GET WEATHER DATA ---------------- #
API_KEY = "1468e5c2a4b24ce7a64140429250306"
url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7&aqi=no&alerts=no"
response = requests.get(url)
weather = response.json() if response.status_code == 200 else None

# ---------------- TABS ---------------- #
tab1, tab2, tab3 = st.tabs(["📊 Charts", "📋 Data Table", "🗺 Risk Map"])

# ---------------- TAB 1: CHARTS ---------------- #
with tab1:
    st.subheader(f"📉 Rainfall Forecast for {city}, {state}")
    if weather:
        data = [
            {
                "Date": day["date"],
                "Condition": day["day"]["condition"]["text"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"]
            }
            for day in weather["forecast"]["forecastday"]
        ]
        df = pd.DataFrame(data).set_index("Date")

        chart1, chart2 = st.columns(2)
        with chart1:
            st.markdown("🌧 *Bar Chart*")
            st.bar_chart(df["Rainfall (mm)"])

        with chart2:
            st.markdown("📈 *Line Chart*")
            st.line_chart(df["Rainfall (mm)"])

        st.markdown("🌊 *Area Chart*")
        st.area_chart(df["Rainfall (mm)"])
    else:
        st.error("❌ Could not retrieve forecast. Check API or connection.")

# ---------------- TAB 2: TABLE ---------------- #
with tab2:
    st.subheader(f"🧾 7-Day Rainfall Data for {city}, {state}")
    if weather:
        st.dataframe(df.reset_index())
    else:
        st.warning("⚠ No data available.")

# ---------------- TAB 3: MAP ---------------- #
with tab3:
    st.subheader("🗺 City-Level & National Flood Risk Map")

    map1, map2 = st.columns(2)

    # 🔹 Single City View
    with map1:
        st.markdown("📍 *City Risk Zone*")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                    get_position='[lon, lat]',
                    get_radius=6000,
                    get_color='[255, 0, 0, 160]'
                )
            ]
        ))

    # 🔸 Nationwide View
    with map2:
        st.markdown("🌐 *National Overview*")
        all_coords = [
            {"lat": coord[0], "lon": coord[1]}
            for state_dict in flood_map.values()
            for coord in state_dict.values()
        ]
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=4.5, longitude=109.5, zoom=5),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=pd.DataFrame(all_coords),
                    get_position='[lon, lat]',
                    get_radius=5000,
                    get_color='[255, 140, 0, 160]'
                )
            ]
        ))

# ---------------- FOOTER ---------------- #
st.markdown("---")
st.caption("📍 Built for BVI1234 | Group VC24001 · VC24009 · VC24011 | Stay safe, Malaysia 🇲🇾")
