# Malaysia FloodSight+ Dashboard
# Developed for BVI1234 - Technology System Programming II
# Enhanced Layout Version

import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- Page Config --- #
st.set_page_config(
    page_title="FloodSight+ Malaysia",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Redesign --- #
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/6/63/Flag_of_Malaysia.svg", use_column_width=True)
st.sidebar.title("FloodSight+ Malaysia")
st.sidebar.markdown("""
### 🌧️ Real-time Flood Risk Forecast
#### Stay safe. Stay informed.

**Instructions:**
- Choose a **State** and **City**.
- View **rainfall forecast** and **risk maps**.

**Emergency Tips:**
- Prepare emergency kit.
- Avoid flood-prone areas.
- Stay tuned to updates.
""")

# --- Title and Intro --- #
st.markdown("""
# 🌇 FloodSight+ Malaysia 
### Real-time Rainfall & Flood Risk Forecast Dashboard
""")

# --- State/City Selectors --- #
col_select1, col_select2 = st.columns([2, 3])
with col_select1:
    selected_state = st.selectbox("Select Malaysian State", list(flood_map.keys()))
with col_select2:
    selected_city = st.selectbox("Select Flood-prone City", list(flood_map[selected_state].keys()))

lat, lon = flood_map[selected_state][selected_city]

# --- WeatherAPI Fetch --- #
API_KEY = "1468e5c2a4b24ce7a64140429250306"
url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7&aqi=no&alerts=no"
res = requests.get(url)
weather = res.json() if res.status_code == 200 else None

# --- Tabs Layout --- #
tab1, tab2 = st.tabs(["📈 Rainfall Forecast", "🗺️ Flood Risk Maps"])

# --- Tab 1: Rainfall Forecast --- #
with tab1:
    if weather:
        st.success(f"7-Day Rainfall Forecast for {selected_city}, {selected_state}")
        forecast_data = [
            {
                "Date": day["date"],
                "Condition": day["day"]["condition"]["text"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"]
            }
            for day in weather["forecast"]["forecastday"]
        ]
        df = pd.DataFrame(forecast_data)

        chart_col, table_col = st.columns(2)
        with chart_col:
            st.bar_chart(df.set_index("Date")["Rainfall (mm)"])
            st.line_chart(df.set_index("Date")["Rainfall (mm)"])
        with table_col:
            st.dataframe(df, use_container_width=True)
    else:
        st.error("Unable to load weather data. Please check your connection or API key.")

# --- Tab 2: Flood Maps --- #
with tab2:
    loc_col, nation_col = st.columns(2)
    with loc_col:
        st.markdown("#### 📍 Selected City Map")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10),
            layers=[pdk.Layer("ScatterplotLayer", data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                               get_position='[lon, lat]', get_radius=6000, get_color='[255, 0, 0, 160]')]
        ))

    with nation_col:
        st.markdown("#### 🌐 National Flood Risk Map")
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
st.caption("FloodSight+ Malaysia | BVI1234 | Created by VC24001 · VC24009 · VC24011")
