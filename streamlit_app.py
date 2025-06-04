# Malaysia Flood Risk Forecast Dashboard
# New Layout - Created for BVI1234 - Technology System Programming II


import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- Page Configuration --- #
st.set_page_config(
    page_title="Malaysia Flood Risk Forecast",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- Sidebar Content --- #
st.sidebar.markdown("""
# 🇲🇾 Malaysia Flood Dashboard
### 📅 Real-Time Forecast Interface

**🔹 Instructions:**
- Select your **State** and **City**.
- View 7-day **rainfall forecast**, **charts**, and **maps**.

**⚠️ Tips:**
- Be aware during monsoon season.
- Keep an emergency kit ready.
- Stay updated with alerts.

---
**Emoji Legend:**
- 🇲🇾 — Malaysia Flag (contextual branding)
- 📅 — Calendar/Forecast tool
- 🔹 — Sidebar steps/instructions
- ⚠️ — Emergency advice section
- 📊 — Charts tab (rainfall visuals)
- 📆 — Table tab (data breakdown)
- 🌍 — Maps tab (visualizing locations)
- 🔸/🔹 — Local/National indicators
""")

# --- Flood Map Dictionary (must be defined externally or above this block) --- #
# Example: flood_map = {"State": {"City": (lat, lon), ...}, ...}

# --- Main Layout --- #
st.title("Malaysia Flood Risk Forecast Dashboard 🌇")
st.markdown("""
Real-time rainfall tracking and flood-prone mapping for Malaysian states.
Built to promote public awareness and safety.
""")

col1, col2 = st.columns([1, 3])
with col1:
    selected_state = st.selectbox("Select State", list(flood_map.keys()))
with col2:
    selected_city = st.selectbox("Select City", list(flood_map[selected_state].keys()))

lat, lon = flood_map[selected_state][selected_city]

# --- Fetch Weather Data from WeatherAPI --- #
API_KEY = "1468e5c2a4b24ce7a64140429250306"
url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7&aqi=no&alerts=no"
response = requests.get(url)
weather = response.json() if response.status_code == 200 else None

# --- Tabs for Navigation --- #
tab1, tab2, tab3 = st.tabs(["📊 Rainfall Charts", "📆 Forecast Table", "🌍 Flood Risk Maps"])

# --- Tab 1: Visual Charts --- #
with tab1:
    st.subheader(f"Rainfall Chart for {selected_city}, {selected_state}")
    if weather:
        forecast_data = [
            {
                "Date": day["date"],
                "Condition": day["day"]["condition"]["text"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"]
            }
            for day in weather["forecast"]["forecastday"]
        ]
        df = pd.DataFrame(forecast_data).set_index("Date")

        chart_col1, chart_col2, chart_col3 = st.columns(3)
        with chart_col1:
            st.markdown("**Bar Chart**")
            st.bar_chart(df["Rainfall (mm)"])
        with chart_col2:
            st.markdown("**Line Chart**")
            st.line_chart(df["Rainfall (mm)"])
        with chart_col3:
            st.markdown("**Area Chart**")
            st.area_chart(df["Rainfall (mm)"])
    else:
        st.error("Weather data unavailable. Check API or internet.")

# --- Tab 2: Table View --- #
with tab2:
    st.subheader(f"7-Day Rainfall Forecast for {selected_city}, {selected_state}")
    if weather:
        st.table(df.reset_index())
    else:
        st.warning("Could not load table data.")

# --- Tab 3: Map View --- #
with tab3:
    map1, map2 = st.columns(2)

    with map1:
        st.markdown("### 🔹 City Flood Zone")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10),
            layers=[pdk.Layer("ScatterplotLayer", data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                               get_position='[lon, lat]', get_radius=6000, get_color='[255, 0, 0, 160]')]
        ))

    with map2:
        st.markdown("### 🔸 National Flood Risk Overview")
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
st.caption("Malaysia Flood Forecast | BVI1234 | Group VC24001 · VC24009 · VC24011")
