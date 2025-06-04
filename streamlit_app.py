# --- Import Libraries --- #
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --- Set Page Configuration --- #
st.set_page_config(page_title="Malaysia Flood Risk Forecast", page_icon="🌧", layout="wide")

# --- API Key --- #
API_KEY = "1468e5c2a4b24ce7a64140429250306"

# --- Malaysia Flood-Prone States and Cities (6 per state) --- #
flood_map = {
    "Johor": {
        "Johor Bahru": (1.4927, 103.7414),
        "Batu Pahat": (1.8544, 102.9325),
        "Muar": (2.0442, 102.5689),
        "Segamat": (2.5090, 102.8106),
        "Kluang": (2.0324, 103.3185),
        "Pontian": (1.4897, 103.3895)
    },
    "Kelantan": {
        "Kota Bharu": (6.1254, 102.2381),
        "Gua Musang": (4.8826, 101.9620),
        "Pasir Mas": (6.0495, 102.1396),
        "Tanah Merah": (5.8123, 102.1431),
        "Tumpat": (6.1979, 102.1705),
        "Bachok": (6.0718, 102.3937)
    },
    "Pahang": {
        "Kuantan": (3.8077, 103.3260),
        "Temerloh": (3.4515, 102.4179),
        "Jerantut": (3.9368, 102.3626),
        "Bentong": (3.5214, 101.9081),
        "Raub": (3.7894, 101.8574),
        "Pekan": (3.4833, 103.3990)
    },
    "Sarawak": {
        "Kuching": (1.5535, 110.3593),
        "Sibu": (2.2879, 111.8260),
        "Bintulu": (3.1700, 113.0364),
        "Miri": (4.3990, 113.9914),
        "Kapit": (2.0164, 112.9368),
        "Limbang": (4.7500, 115.0000)
    },
    "Selangor": {
        "Shah Alam": (3.0738, 101.5183),
        "Klang": (3.0333, 101.4500),
        "Gombak": (3.2167, 101.6500),
        "Hulu Langat": (3.0833, 101.8667),
        "Petaling Jaya": (3.1073, 101.6067),
        "Sabak Bernam": (3.6733, 100.9896)
    }
}

# --- Sidebar: Instructions + Emoji Legend --- #
st.sidebar.markdown("""
# 🇲🇾 Malaysia Flood Tracker  
### 📅 Forecast Interface  

🔹 *Steps:*  
1. Select *date, **state, and **city*  
2. Click ✅ *Check*  
3. View risk, forecast, maps & news  

📘 *Emoji Risk Legend:*  
🟢 Low | 🟡 Moderate | 🟠 High | 🔴 Extreme  

⚠ *Tips:*  
- Stay safe during heavy rain  
- Prepare emergency kit  
""")

# --- Main Title --- #
st.title("🌧 Malaysia Flood Risk Forecast Dashboard")
st.markdown("Live rainfall, flood zones, and safety information.")

# --- Date Selection --- #
col_date1, col_date2, col_date3 = st.columns(3)
with col_date1:
    selected_day = st.selectbox("📅 Day", list(range(1, 32)), index=datetime.now().day - 1)
with col_date2:
    selected_month = st.selectbox("🗓 Month", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ], index=datetime.now().month - 1)
with col_date3:
    selected_year = st.selectbox("📆 Year", [datetime.now().year, datetime.now().year + 1])

# --- Location Selection --- #
col_loc1, col_loc2 = st.columns(2)
with col_loc1:
    selected_state = st.selectbox("🏞 Select State", list(flood_map.keys()))
with col_loc2:
    selected_city = st.selectbox("🏘 Select City", list(flood_map[selected_state].keys()))

# --- Button to Trigger Forecast --- #
if st.button("✅ Check Flood Risk"):

    # --- Coordinates for API Request --- #
    lat, lon = flood_map[selected_state][selected_city]
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7&aqi=no&alerts=no"
    response = requests.get(url)

    if response.status_code == 200:
        weather = response.json()

        # --- Format Forecast Data --- #
        forecast_data = [
            {
                "Date": day["date"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"],
                "Avg Temp (°C)": day["day"]["avgtemp_c"],
                "Humidity (%)": day["day"]["avghumidity"],
                "Condition": day["day"]["condition"]["text"]
            }
            for day in weather["forecast"]["forecastday"]
        ]
        df = pd.DataFrame(forecast_data)

        # --- Flood Risk Evaluation by Rainfall --- #
        today_rain = df["Rainfall (mm)"].iloc[0]
        if today_rain < 10:
            risk = "🟢 Low"
        elif today_rain < 30:
            risk = "🟡 Moderate"
        elif today_rain < 60:
            risk = "🟠 High"
        else:
            risk = "🔴 Extreme"

        # --- Display Risk Info --- #
        st.success(f"""
        📌 *{selected_city}, {selected_state}*  
        📅 Selected Date: {selected_day} {selected_month} {selected_year}  
        💧 Rainfall: {today_rain} mm  
        ⚠ *Flood Risk: {risk}*
        """)

        # --- Charts Section --- #
        st.subheader("📊 Weather Charts")

        col_chart1, col_chart2, col_chart3 = st.columns(3)
        with col_chart1:
            st.markdown("*Rainfall (mm)* - Bar Chart")
            st.bar_chart(df.set_index("Date")["Rainfall (mm)"])
        with col_chart2:
            st.markdown("*Avg Temperature (°C)* - Line Chart")
            st.line_chart(df.set_index("Date")["Avg Temp (°C)"])
        with col_chart3:
            st.markdown("*Humidity (%)* - Area Chart")
            st.area_chart(df.set_index("Date")["Humidity (%)"])

        # --- Forecast Table --- #
        st.subheader("📆 7-Day Forecast Data Table")
        st.dataframe(df)

        # --- Map: City Flood Zone --- #
        st.subheader("📍 Local Flood Map")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10),
            layers=[
                pdk.Layer("ScatterplotLayer",
                          data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                          get_position='[lon, lat]',
                          get_radius=7000,
                          get_color='[255, 0, 0, 160]')
            ]
        ))

        # --- Updated National Flood Risk Map (Color-coded by rainfall) --- #
        st.subheader("🌐 National Flood Risk Overview (Color Zones)")

        city_risk_list = []
        for state in flood_map:
            for city, coord in flood_map[state].items():
                city_url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={coord[0]},{coord[1]}&days=1&aqi=no&alerts=no"
                resp = requests.get(city_url)
                if resp.status_code == 200:
                    rain = resp.json()["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
                    # Determine risk level
                    if rain < 10:
                        color = [0, 255, 0, 160]  # 🟢
                    elif rain < 30:
                        color = [255, 255, 0, 160]  # 🟡
                    elif rain < 60:
                        color = [255, 165, 0, 160]  # 🟠
                    else:
                        color = [255, 0, 0, 160]  # 🔴
                    city_risk_list.append({
                        "city": city,
                        "lat": coord[0],
                        "lon": coord[1],
                        "color": color
                    })

        # Plot risk map
        if city_risk_list:
            risk_df = pd.DataFrame(city_risk_list)
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(latitude=4.2, longitude=109.5, zoom=5),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=risk_df,
                        get_position='[lon, lat]',
                        get_fill_color='color',
                        get_radius=5000
                    )
                ]
            ))
        else:
            st.warning("Unable to fetch national flood
