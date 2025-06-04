# Flood Alert and Forecasting System for Malaysia
# Developed for Python Programming Project - BVI1234
# Streamlit-based application using WeatherAPI

import streamlit as st
import requests
import datetime
import pandas as pd

# ------------------ App Configuration ------------------ #
st.set_page_config(page_title="Malaysia Flood Alert System 🇲🇾", layout="wide")
st.title("🌧️ Malaysia Flood Risk Monitoring & Forecast System")

# ------------------ Sidebar Instructions ------------------ #
st.sidebar.header("📋 Instructions")
st.sidebar.markdown("""
1. Select a state and city to view 7-day rainfall history & forecast.
2. View risk level based on cumulative rainfall.
3. Check maps of risk areas and selected location.
4. Follow tips to stay prepared.
""")

st.sidebar.header("🚨 Preparedness Tips")
st.sidebar.markdown("""
- Keep emergency kits ready.
- Charge your phones and power banks.
- Move to higher ground if needed.
- Follow authorities’ instructions.
- Save emergency contact numbers.
""")

# ------------------ Constants ------------------ #
API_KEY = "1468e5c2a4b24ce7a64140429250306"
BASE_URL = "http://api.weatherapi.com/v1"

# 16 Malaysian states with 5 flood-prone cities each
malaysia_states = {
    "Johor": ["Johor Bahru", "Batu Pahat", "Muar", "Kluang", "Pontian"],
    "Kedah": ["Alor Setar", "Sungai Petani", "Kulim", "Baling", "Langkawi"],
    "Kelantan": ["Kota Bharu", "Pasir Mas", "Tumpat", "Machang", "Tanah Merah"],
    "Melaka": ["Melaka", "Alor Gajah", "Jasin", "Durian Tunggal", "Masjid Tanah"],
    "Negeri Sembilan": ["Seremban", "Port Dickson", "Tampin", "Rembau", "Nilai"],
    "Pahang": ["Kuantan", "Temerloh", "Jerantut", "Bentong", "Pekan"],
    "Penang": ["George Town", "Butterworth", "Bukit Mertajam", "Nibong Tebal", "Seberang Jaya"],
    "Perak": ["Ipoh", "Taiping", "Teluk Intan", "Lumut", "Manjung"],
    "Perlis": ["Kangar", "Arau", "Padang Besar", "Kuala Perlis", "Simpang Ampat"],
    "Sabah": ["Kota Kinabalu", "Tawau", "Sandakan", "Lahad Datu", "Keningau"],
    "Sarawak": ["Kuching", "Sibu", "Bintulu", "Miri", "Sri Aman"],
    "Selangor": ["Shah Alam", "Klang", "Kajang", "Subang Jaya", "Ampang"],
    "Terengganu": ["Kuala Terengganu", "Dungun", "Kemaman", "Marang", "Hulu Terengganu"],
    "Kuala Lumpur": ["Kuala Lumpur", "Setapak", "Cheras", "Bangsar", "Gombak"],
    "Putrajaya": ["Putrajaya", "Presint 1", "Presint 8", "Presint 18", "Presint 11"],
    "Labuan": ["Labuan", "Kiamsam", "Bebuloh", "Sungai Lada", "Rancha-Rancha"]
}

# ------------------ User Selection ------------------ #
selected_state = st.selectbox("Select a Malaysian State", list(malaysia_states.keys()))
selected_city = st.selectbox("Select a City", malaysia_states[selected_state])

# ------------------ Get Weather Data ------------------ #
def get_forecast(city):
    url = f"{BASE_URL}/forecast.json?key={API_KEY}&q={city}&days=7&aqi=no&alerts=no"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve data from WeatherAPI.")
        return None

weather_data = get_forecast(selected_city)

# ------------------ Risk Analysis Function ------------------ #
def get_risk_level(total_mm):
    if total_mm >= 100:
        return "🔴 High Risk"
    elif total_mm >= 50:
        return "🟠 Moderate Risk"
    else:
        return "🟢 Low Risk"

# ------------------ Main Content Area ------------------ #
tabs = st.tabs(["📍 Selected Location", "🌧️ Rainfall Trends", "🗺️ Risk Map Malaysia"])

# -------- Tab 1: Location Map -------- #
with tabs[0]:
    st.subheader(f"📍 Map of {selected_city}, {selected_state}")
    st.map(pd.DataFrame([{"lat": weather_data['location']['lat'], "lon": weather_data['location']['lon']}]))

# -------- Tab 2: Rainfall Table and Charts -------- #
with tabs[1]:
    st.subheader(f"📊 7-Day Rainfall Forecast for {selected_city}")
    forecast_days = weather_data['forecast']['forecastday']

    # Table format
    table_data = {
        "Date": [day['date'] for day in forecast_days],
        "Rainfall (mm)": [day['day']['totalprecip_mm'] for day in forecast_days],
    }
    df = pd.DataFrame(table_data)
    total_rainfall = df["Rainfall (mm)"].sum()
    risk = get_risk_level(total_rainfall)

    st.metric("Total Rainfall (7 Days)", f"{total_rainfall:.1f} mm", delta=None)
    st.metric("Flood Risk Level", risk)

    st.dataframe(df, use_container_width=True)
    st.line_chart(df.set_index("Date"))
    st.bar_chart(df.set_index("Date"))

# -------- Tab 3: Nationwide Risk Map -------- #
with tabs[2]:
    st.subheader("🗺️ Flood Risk Zones Across Malaysia")
    map_data = []

    for state, cities in malaysia_states.items():
        for city in cities:
            data = get_forecast(city)
            if data:
                lat = data['location']['lat']
                lon = data['location']['lon']
                total = sum([day['day']['totalprecip_mm'] for day in data['forecast']['forecastday']])
                risk = get_risk_level(total)
                color = "#FF0000" if "High" in risk else "#FFA500" if "Moderate" in risk else "#00FF00"
                map_data.append({"lat": lat, "lon": lon, "risk": risk})

    map_df = pd.DataFrame(map_data)
    st.map(map_df.drop(columns=["risk"]))
    st.markdown("""_Color indicates risk level at each location based on 7-day cumulative rainfall._""")

# ------------------ End ------------------ #
st.success("✅ Application Ready. Stay safe and stay informed!")
