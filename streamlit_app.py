# Full Streamlit App with Highlighted High-Risk Cities Map and Updated Tabs
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime
import calendar

# Set Streamlit page config
st.set_page_config(page_title="FloodSight Malaysia", layout="wide")

# ========== Sidebar Instructions ==========
st.sidebar.title("📘 FloodSight Malaysia")
st.sidebar.markdown("""
**How to use this app:**
1. Select your **State** and **City**.
2. Pick the **Year** and **Month** for rainfall history.
3. Click **Check Flood Risk** for latest weather and flood risk.
4. View **daily rainfall history** as a **bar chart**.
5. See **7-day rainfall forecast trends**.
6. All **high-risk cities** are highlighted on map.
7. Read **latest flood news** to stay informed.

💧 **Flood Preparedness Tips**  
- Secure important documents in waterproof bags.  
- Prepare emergency kit (food, water, medicine).  
- Know evacuation routes & nearest shelters.  
- Keep devices charged.  
- Monitor local news & alerts.
""")

# ========== Flood-Prone Areas ==========
flood_prone_areas = {
    "Johor": ["Johor Bahru", "Batu Pahat", "Muar", "Kulai", "Pontian"],
    "Kedah": ["Alor Setar", "Kulim", "Baling", "Pendang", "Yan"],
    "Kelantan": ["Kota Bharu", "Pasir Mas", "Tumpat", "Gua Musang"],
    "Melaka": ["Melaka Tengah", "Jasin"],
    "Negeri Sembilan": ["Seremban", "Tampin", "Port Dickson"],
    "Pahang": ["Kuantan", "Pekan", "Temerloh", "Bentong", "Raub"],
    "Penang": ["Seberang Perai", "George Town", "Balik Pulau"],
    "Perak": ["Ipoh", "Teluk Intan", "Lumut", "Taiping"],
    "Perlis": ["Kangar"],
    "Sabah": ["Kota Kinabalu", "Sandakan", "Tawau", "Beaufort", "Keningau"],
    "Sarawak": ["Kuching", "Sibu", "Miri", "Bintulu", "Sri Aman"],
    "Selangor": ["Shah Alam", "Klang", "Petaling Jaya", "Hulu Langat", "Gombak"],
    "Terengganu": ["Kuala Terengganu", "Dungun", "Kemaman"],
    "Wilayah Persekutuan": ["Kuala Lumpur", "Putrajaya", "Labuan"]
}

# ========== Input Selection ==========
st.title("🌧️ FloodSight Malaysia: Forecast & Risk Tracker")

state = st.selectbox("Select State", list(flood_prone_areas.keys()))
city = st.selectbox("Select City", flood_prone_areas[state])

year = st.selectbox("Select Year", list(range(2021, datetime.now().year + 1)))
month_names = list(calendar.month_name)[1:]
selected_month_name = st.selectbox("Select Month", month_names)
selected_month = month_names.index(selected_month_name) + 1

# ========== API Configuration ==========
API_KEY = "1468e5c2a4b24ce7a64140429250306"

def get_city_coords(city_name):
    coords_lookup = {
        "Kuala Lumpur": (3.139, 101.6869),
        "Shah Alam": (3.0738, 101.5183),
        "Kuantan": (3.8077, 103.3260),
        "Johor Bahru": (1.4927, 103.7414),
        "Kota Bharu": (6.1254, 102.2381),
        "Kuching": (1.5533, 110.3592),
        "Kota Kinabalu": (5.9804, 116.0735),
        "Penang": (5.4164, 100.3327),
        "Ipoh": (4.5975, 101.0901),
        "Melaka": (2.1896, 102.2501),
        "Seremban": (2.7258, 101.9424),
        "Kangar": (6.4401, 100.1986),
        "Putrajaya": (2.9264, 101.6964),
        "Labuan": (5.2831, 115.2308),
        "Pekan": (3.4939, 103.3990)
    }
    return coords_lookup.get(city_name, (4.2105, 101.9758))

lat, lon = get_city_coords(city)

# ========== Weather API Call ==========
@st.cache_data(show_spinner=False)
def fetch_weather_forecast():
    url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=7"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

@st.cache_data(show_spinner=False)
def fetch_rainfall_history():
    results = []
    for day in range(1, calendar.monthrange(year, selected_month)[1] + 1):
        date = f"{year}-{selected_month:02d}-{day:02d}"
        url = f"https://api.weatherapi.com/v1/history.json?key={API_KEY}&q={lat},{lon}&dt={date}"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            rain = data['forecast']['forecastday'][0]['day']['totalprecip_mm']
            results.append({"Date": date, "Rainfall (mm)": rain})
    return results

def evaluate_risk(precip_mm):
    if precip_mm > 80:
        return "🔴 High"
    elif precip_mm > 40:
        return "🟠 Moderate"
    else:
        return "🟢 Low"

# ========== Button Logic ==========
risk_list = []
if st.button("Check Flood Risk"):
    forecast = fetch_weather_forecast()
    if forecast:
        for day in forecast['forecast']['forecastday']:
            precip = day['day']['totalprecip_mm']
            risk = evaluate_risk(precip)
            date = day['date']
            risk_list.append({
                "Date": date,
                "Rainfall (mm)": precip,
                "Risk": risk,
                "City": city,
                "State": state,
                "Latitude": lat,
                "Longitude": lon
            })
        st.success("Flood risk calculated based on 7-day forecast.")

# ========== Tabs ==========
tabs = st.tabs(["📊 Rainfall History", "📈 7-Day Forecast", "⚠️ Flood Risk Chart", "📍 High-Risk Cities Map"])

# ========== Tab 1: Rainfall History ==========
with tabs[0]:
    st.header(f"📊 Daily Rainfall - {selected_month_name} {year}")
    rain_data = fetch_rainfall_history()
    df_rain = pd.DataFrame(rain_data)
    st.bar_chart(df_rain.set_index("Date"))

# ========== Tab 2: 7-Day Forecast ==========
with tabs[1]:
    st.header("📈 7-Day Rainfall Forecast")
    if risk_list:
        df_forecast = pd.DataFrame(risk_list)
        st.line_chart(df_forecast.set_index("Date")["Rainfall (mm)"])
    else:
        st.info("Please click 'Check Flood Risk' to see forecast.")

# ========== Tab 3: Risk Level ==========
with tabs[2]:
    st.header("⚠️ Flood Risk Evaluation")
    if risk_list:
        df_risk = pd.DataFrame(risk_list)
        st.dataframe(df_risk[["Date", "Rainfall (mm)", "Risk"]])
    else:
        st.info("Run flood risk check to display results.")

# ========== Tab 4: High-Risk Map ==========
with tabs[3]:
    st.header("📍 High-Risk Cities Map")

    if not risk_list:
        st.info("No high-risk cities detected. Try checking flood risk first.")
    else:
        df_map = pd.DataFrame(risk_list)

        risk_counts = df_map['Risk'].value_counts().to_dict()

        st.markdown("### 🌡️ Risk Level Summary")
        st.markdown(f"""
        - 🔴 High Risk: **{risk_counts.get('🔴 High', 0)}** cities  
        - 🟠 Moderate Risk: **{risk_counts.get('🟠 Moderate', 0)}** cities  
        - 🟢 Low Risk: **{risk_counts.get('🟢 Low', 0)}** cities  
        """)

        st.markdown("### 🗺️ Map of Cities by Risk Level")

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=4.2105,
                longitude=101.9758,
                zoom=5.4,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df_map,
                    get_position='[Longitude, Latitude]',
                    get_fill_color="""
                        [Risk == '🔴 High' ? 255 : 
                         Risk == '🟠 Moderate' ? 255 : 
                         Risk == '🟢 Low' ? 0 : 0,
                         Risk == '🔴 High' ? 0 : 
                         Risk == '🟠 Moderate' ? 165 : 
                         Risk == '🟢 Low' ? 128 : 0,
                         0, 160]
                    """,
                    get_radius=80000,
                    pickable=True,
                    auto_highlight=True
                )
            ],
            tooltip={"text": "{City}, {State}\nRisk: {Risk}"}
        ))

