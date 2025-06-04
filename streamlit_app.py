import streamlit as st
import requests
import pandas as pd
import datetime
import calendar
import pydeck as pdk

# --- API Key ---
API_KEY = "1468e5c2a4b24ce7a64140429250306"

# --- States and cities prone or possibly prone to flooding ---
state_city_data = {
    "Johor": {
        "flood_prone": ["Muar", "Kota Tinggi", "Batu Pahat", "Pontian", "Segamat", "Mersing"],
        "possibly_prone": ["Johor Bahru", "Kluang"]
    },
    "Kedah": {
        "flood_prone": ["Kuala Muda", "Pendang", "Pokok Sena", "Sik"],
        "possibly_prone": ["Alor Setar", "Langkawi"]
    },
    "Kelantan": {
        "flood_prone": ["Kota Bharu", "Pasir Mas", "Tumpat", "Tanah Merah"],
        "possibly_prone": ["Machang", "Gua Musang"]
    },
    "Melaka": {
        "flood_prone": ["Melaka Tengah", "Jasin", "Alor Gajah"],
        "possibly_prone": []
    },
    "Negeri Sembilan": {
        "flood_prone": ["Port Dickson", "Seremban", "Jelebu"],
        "possibly_prone": ["Jempol"]
    },
    "Pahang": {
        "flood_prone": ["Kuantan", "Temerloh", "Jerantut", "Pekan"],
        "possibly_prone": ["Raub", "Bentong"]
    },
    "Perak": {
        "flood_prone": ["Larut Matang", "Hilir Perak", "Manjung"],
        "possibly_prone": ["Kuala Kangsar", "Kerian"]
    },
    "Perlis": {
        "flood_prone": ["Kangar", "Arau"],
        "possibly_prone": []
    },
    "Penang": {
        "flood_prone": ["Seberang Perai", "George Town"],
        "possibly_prone": []
    },
    "Sabah": {
        "flood_prone": ["Sandakan", "Kota Kinabalu", "Tawau"],
        "possibly_prone": ["Lahad Datu", "Keningau"]
    },
    "Sarawak": {
        "flood_prone": ["Kuching", "Sibu", "Miri"],
        "possibly_prone": ["Bintulu", "Sri Aman"]
    },
    "Selangor": {
        "flood_prone": ["Hulu Langat", "Klang", "Sabak Bernam", "Kuala Selangor"],
        "possibly_prone": ["Petaling", "Gombak"]
    },
    "Terengganu": {
        "flood_prone": ["Kuala Terengganu", "Dungun", "Kemaman"],
        "possibly_prone": ["Hulu Terengganu"]
    },
    "Federal Territory of Kuala Lumpur": {
        "flood_prone": ["Kuala Lumpur"],
        "possibly_prone": []
    },
    "Federal Territory of Putrajaya": {
        "flood_prone": ["Putrajaya"],
        "possibly_prone": []
    },
    "Federal Territory of Labuan": {
        "flood_prone": ["Labuan"],
        "possibly_prone": []
    },
}

# --- Helper function to get lat/lon of cities for map plotting (some major cities) ---
city_coordinates = {
    # Johor
    "Muar": [2.0459, 102.5715],
    "Kota Tinggi": [1.7339, 103.8333],
    "Batu Pahat": [1.8544, 102.9317],
    "Pontian": [1.4925, 103.3814],
    "Segamat": [2.5221, 102.8376],
    "Mersing": [2.4246, 103.8407],
    "Johor Bahru": [1.4927, 103.7414],
    "Kluang": [2.0307, 103.3167],
    # Kedah
    "Kuala Muda": [5.7041, 100.5201],
    "Pendang": [5.6024, 100.4551],
    "Pokok Sena": [5.8260, 100.4606],
    "Sik": [5.8623, 100.9307],
    "Alor Setar": [6.1219, 100.3685],
    "Langkawi": [6.3463, 99.7977],
    # Kelantan
    "Kota Bharu": [6.1333, 102.2435],
    "Pasir Mas": [6.0534, 102.2456],
    "Tumpat": [6.1614, 102.2525],
    "Tanah Merah": [5.8681, 102.2027],
    "Machang": [5.8155, 102.1717],
    "Gua Musang": [4.7976, 101.9616],
    # Melaka
    "Melaka Tengah": [2.1896, 102.2501],
    "Jasin": [2.2491, 102.4269],
    "Alor Gajah": [2.3294, 102.1994],
    # Negeri Sembilan
    "Port Dickson": [2.4802, 101.7965],
    "Seremban": [2.7290, 101.9386],
    "Jelebu": [2.9173, 102.2166],
    "Jempol": [2.9287, 102.4944],
    # Pahang
    "Kuantan": [3.8074, 103.3260],
    "Temerloh": [3.4308, 102.4224],
    "Jerantut": [3.9505, 102.3643],
    "Pekan": [3.4854, 103.4195],
    "Raub": [3.7966, 101.8544],
    "Bentong": [3.5332, 101.8596],
    # Perak
    "Larut Matang": [4.7537, 100.8689],
    "Hilir Perak": [4.2020, 100.9749],
    "Manjung": [4.2507, 100.8955],
    "Kuala Kangsar": [4.7669, 100.9401],
    "Kerian": [5.0720, 100.4381],
    # Perlis
    "Kangar": [6.4444, 100.2000],
    "Arau": [6.4244, 100.2139],
    # Penang
    "Seberang Perai": [5.3882, 100.4380],
    "George Town": [5.4141, 100.3288],
    # Sabah
    "Sandakan": [5.8409, 118.0596],
    "Kota Kinabalu": [5.9804, 116.0735],
    "Tawau": [4.2429, 117.8867],
    "Lahad Datu": [5.0300, 118.3267],
    "Keningau": [5.3305, 116.1433],
    # Sarawak
    "Kuching": [1.5533, 110.3593],
    "Sibu": [2.2872, 111.8257],
    "Miri": [4.3990, 113.9914],
    "Bintulu": [3.1686, 113.0282],
    "Sri Aman": [1.2110, 111.4602],
    # Selangor
    "Hulu Langat": [3.0380, 101.8095],
    "Klang": [3.0317, 101.4437],
    "Sabak Bernam": [3.8489, 100.9333],
    "Kuala Selangor": [3.3434, 101.2413],
    "Petaling": [3.0738, 101.6067],
    "Gombak": [3.2669, 101.6898],
    # Terengganu
    "Kuala Terengganu": [5.3306, 103.1404],
    "Dungun": [4.8007, 103.2883],
    "Kemaman": [4.2584, 103.4195],
    "Hulu Terengganu": [5.1736, 102.9847],
    # Federal Territories
    "Kuala Lumpur": [3.1390, 101.6869],
    "Putrajaya": [2.9264, 101.6967],
    "Labuan": [5.2803, 115.2420],
}

# --- Flood risk color coding for map ---
risk_color_map = {
    "🔴 High": [255, 0, 0, 160],
    "🟠 Moderate": [255, 165, 0, 160],
    "🟢 Low": [0, 255, 0, 160],
}

# --- Sidebar content ---
st.sidebar.title("FloodSight Malaysia")
st.sidebar.markdown("""
### How to use this app:
- Select your State and City.
- Pick the Year and Month for rainfall history.
- Click Check Flood Risk for the latest weather and risk.
- View daily rainfall history as bar chart.
- View 7-day rainfall forecast trends.
- See all high-risk cities highlighted on map.
- Read latest flood news to stay informed.

💧 **Flood Preparedness Tips**
- Secure important documents in waterproof bags.
- Prepare emergency kit (food, water, medicine).
- Know evacuation routes & nearest shelters.
- Keep devices charged.
- Monitor local news & alerts.
""")

# --- Main app layout ---
st.title("FloodSight Malaysia 🌧️")

# Tabs for organizing the UI
tab1, tab2, tab3 = st.tabs(["Check Flood Risk", "Daily Rainfall History", "7-day Rainfall Forecast"])

# Select State & City
selected_state = st.selectbox("Select State", list(state_city_data.keys()))
# Combine flood_prone + possibly_prone for dropdown
all_cities = state_city_data[selected_state]["flood_prone"] + state_city_data[selected_state]["possibly_prone"]
if not all_cities:
    all_cities = ["No flood-prone cities listed"]
selected_city = st.selectbox("Select City", all_cities)

# Date selection for rainfall history
year_now = datetime.datetime.now().year
selected_year = st.selectbox("Select Year", list(range(year_now - 5, year_now + 1)), index=5)
month_names = list(calendar.month_name)[1:]
selected_month_name = st.selectbox("Select Month", month_names, index=datetime.datetime.now().month - 1)
selected_month = month_names.index(selected_month_name) + 1

# --- Function to get rainfall history from WeatherAPI ---
def get_rainfall_history(city, year, month):
    url = (
        f"http://api.weatherapi.com/v1/history.json?key={API_KEY}"
        f"&q={city}&dt={year}-{month:02d}-01"
    )
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to get rainfall history from API.")
        return None
    data = response.json()
    days = data.get("forecast", {}).get("forecastday", [])
    records = []
    for day in days:
        date = day["date"]
        rain = day["day"]["totalprecip_mm"]
        records.append({"Date": date, "Rainfall (mm)": rain})
    df = pd.DataFrame(records)
    return df

# --- Function to get 7-day forecast ---
def get_7day_forecast(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to get 7-day forecast from API.")
        return None
    data = response.json()
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    records = []
    for day in forecast_days:
        date = day["date"]
        rain = day["day"]["totalprecip_mm"]
        records.append({"Date": date, "Rainfall (mm)": rain})
    df = pd.DataFrame(records)
    return df

# --- Function to get current flood risk based on latest weather ---
def get_current_flood_risk(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to get current weather from API.")
        return None
    data = response.json()
    # Simple logic for risk: Heavy rain (>30mm) = High risk, moderate (10-30) = Moderate, else low
    precip = data.get("current", {}).get("precip_mm", 0)
    if precip > 30:
        risk = "🔴 High"
    elif precip > 10:
        risk = "🟠 Moderate"
    else:
        risk = "🟢 Low"
    return risk, precip

# --- Get flood risk for all flood-prone cities for map highlight ---
def get_all_cities_risk():
    risk_list = []
    for state, cities_info in state_city_data.items():
        all_cities_in_state = cities_info["flood_prone"] + cities_info["possibly_prone"]
        for city in all_cities_in_state:
            risk, precip = get_current_flood_risk(city)
            latlon = city_coordinates.get(city, [0, 0])
            risk_list.append({"City": city, "State": state, "Risk": risk, "Precipitation": precip, "Lat": latlon[0], "Lon": latlon[1]})
    return pd.DataFrame(risk_list)

# --- Tab 1: Check Flood Risk ---
with tab1:
    st.subheader(f"Flood Risk Check for {selected_city}, {selected_state}")
    risk, precip = get_current_flood_risk(selected_city)
    if risk:
        st.markdown(f"**Current Flood Risk:** {risk}")
        st.markdown(f"**Current Precipitation:** {precip} mm")

    # Show map with high-risk cities highlighted
    st.markdown("### Flood Risk Map - All Flood-Prone & Possibly Prone Cities")
    df_risk = get_all_cities_risk()
    if not df_risk.empty:
        df_risk["color"] = df_risk["Risk"].map(risk_color_map)
        # Show all cities on the map with color by risk
        midpoint = [df_risk["Lat"].mean(), df_risk["Lon"].mean()]
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_risk,
            get_position=["Lon", "Lat"],
            get_fill_color="color",
            get_radius=12000,
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=6)
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{City}\nRisk: {Risk}"})
        st.pydeck_chart(r)

# --- Tab 2: Daily Rainfall History ---
with tab2:
    st.subheader(f"Daily Rainfall History for {selected_city}, {selected_state} ({selected_month_name} {selected_year})")
    df_history = get_rainfall_history(selected_city, selected_year, selected_month)
    if df_history is not None and not df_history.empty:
        df_history['Date'] = pd.to_datetime(df_history['Date'])
        df_history.set_index('Date', inplace=True)
        st.bar_chart(df_history["Rainfall (mm)"])
    else:
        st.info("No rainfall data available for this month.")

# --- Tab 3: 7-day Rainfall Forecast ---
with tab3:
    st.subheader(f"7-day Rainfall Forecast for {selected_city}, {selected_state}")
    df_forecast = get_7day_forecast(selected_city)
    if df_forecast is not None and not df_forecast.empty:
        df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
        df_forecast.set_index('Date', inplace=True)
        st.line_chart(df_forecast["Rainfall (mm)"])
    else:
        st.info("No forecast data available.")

