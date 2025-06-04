# --- Import Required Libraries --- #
import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- Page Configuration --- #
st.set_page_config(page_title="Malaysia Flood Risk Forecast", page_icon="🌧", layout="wide")

# --- API Key for WeatherAPI --- #
API_KEY = "1468e5c2a4b24ce7a64140429250306"

# --- Dictionary: States & 6 Flood-Prone Cities Each with Coordinates --- #
# These cities are known flood-prone areas based on historical data
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

# --- Sidebar Information & Emoji Legend --- #
st.sidebar.markdown("""
# 🇲🇾 Malaysia Flood Tracker  
### 📅 Forecast Interface  

🔹 *Instructions*:  
- Select *State* and *City*  
- Click *Check Flood Risk*  
- View forecast, charts, map  

⚠ *Tips*:  
- Prepare during monsoon  
- Stay updated with alerts  
- Avoid flood zones  

📘 *Emoji Legend*:  
🟢 Low | 🟡 Moderate | 🟠 High | 🔴 Extreme  
""")

# --- Page Title & Intro Text --- #
st.title("🏞 Malaysia Flood Risk Forecast Dashboard")
st.markdown("Real-time rainfall & flood-prone map for public safety & awareness.")

# --- User Selects State and City --- #
col1, col2 = st.columns(2)
with col1:
    selected_state = st.selectbox("📍 Select State", list(flood_map.keys()))
with col2:
    selected_city = st.selectbox("🏘 Select City", list(flood_map[selected_state].keys()))

# --- CHECK Button to Trigger Forecast --- #
if st.button("✅ Check Flood Risk"):

    # --- Get Coordinates from Selected City --- #
    lat, lon = flood_map[selected_state][selected_city]

    # --- API Request to WeatherAPI for 3-day Forecast --- #
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=3&aqi=no&alerts=no"
    response = requests.get(url)

    # --- If Response Successful --- #
    if response.status_code == 200:
        weather = response.json()

        # --- Extract Forecast into DataFrame --- #
        forecast_data = [
            {
                "Date": day["date"],
                "Rainfall (mm)": day["day"]["totalprecip_mm"],
                "Condition": day["day"]["condition"]["text"]
            }
            for day in weather["forecast"]["forecastday"]
        ]
        df = pd.DataFrame(forecast_data)

        # --- Determine Risk Level Based on Today's Rainfall --- #
        today_rain = df["Rainfall (mm)"][0]
        if today_rain < 10:
            risk = "🟢 Low"
        elif 10 <= today_rain < 30:
            risk = "🟡 Moderate"
        elif 30 <= today_rain < 60:
            risk = "🟠 High"
        else:
            risk = "🔴 Extreme"

        # --- Display Summary of Risk --- #
        st.success(f"""
        📌 *{selected_city}, {selected_state}*  
        💧 Today's Rainfall: {today_rain} mm  
        ⚠ *Flood Risk Level: {risk}*
        """)

        # --- Rainfall Charts: Bar, Line, Area --- #
        st.subheader("📊 Rainfall Forecast (3 Days)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("*Bar Chart*")
            st.bar_chart(df.set_index("Date")["Rainfall (mm)"])
        with c2:
            st.markdown("*Line Chart*")
            st.line_chart(df.set_index("Date")["Rainfall (mm)"])
        with c3:
            st.markdown("*Area Chart*")
            st.area_chart(df.set_index("Date")["Rainfall (mm)"])

        # --- Forecast Table --- #
        st.subheader("📆 Detailed Forecast Table")
        st.dataframe(df)

        # --- Local City Flood Map --- #
        st.subheader("📍 Flood Zone Map (Selected City)")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=10),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=pd.DataFrame([{"lat": lat, "lon": lon}]),
                    get_position='[lon, lat]',
                    get_radius=7000,
                    get_color='[255, 0, 0, 160]'
                )
            ]
        ))

        # --- National Risk Map for All Cities --- #
        st.subheader("🌐 National Flood Risk Map")
        all_coords = [
            {"lat": coord[0], "lon": coord[1]}
            for state in flood_map.values() for coord in state.values()
        ]
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=4.2, longitude=109.5, zoom=5),
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

        # --- Flood News Section with Links --- #
        st.subheader("📰 Latest Flood News (Manual Source)")
        st.markdown("""
        - [🌊 Floods displace hundreds in Johor - The Star](https://www.thestar.com.my/news/nation/2023/12/10/floods-displace-hundreds-in-johor)
        - [🚨 Flash floods hit parts of Selangor - Malaysiakini](https://www.malaysiakini.com/news/655432)
        - [💦 Updates from Department of Irrigation and Drainage (JPS)](https://publicinfobanjir.water.gov.my/)
        """)

    else:
        st.error("❌ Unable to retrieve weather data. Please check your API key or internet.")

# --- Footer Credit --- #
st.markdown("---")
st.caption("📘 BVI1234 Technology System Programming II — Group VC24001 · VC24009 · VC24011")
