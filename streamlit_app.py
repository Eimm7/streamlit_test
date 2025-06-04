import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random

# ----------------------------
# Simulated Data Functions
# ----------------------------

def get_mock_rainfall_data(city):
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(30)]
    dates.reverse()
    rainfall = [round(random.uniform(0, 120), 1) for _ in dates]
    return pd.DataFrame({"Date": dates, "Rainfall (mm)": rainfall})

def get_forecast_data(city):
    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(7)]
    forecast = [round(random.uniform(10, 100), 1) for _ in dates]
    return pd.DataFrame({"Date": dates, "Forecast (mm)": forecast})

def get_risk_level(value):
    if value > 80:
        return "High"
    elif value > 40:
        return "Moderate"
    else:
        return "Low"

# ----------------------------
# Page Settings
# ----------------------------

st.set_page_config("Malaysia Flood Forecasting", layout="wide")
st.title("🌊 Malaysia Flood Forecasting (No Plotly)")
st.markdown("Real-time forecast and rainfall trends for key flood-prone cities in Malaysia.")

# ----------------------------
# City Data
# ----------------------------

city_data = {
    "City": ["Kuala Lumpur", "Shah Alam", "George Town", "Johor Bahru", "Kota Bharu"],
    "State": ["Kuala Lumpur", "Selangor", "Penang", "Johor", "Kelantan"],
    "Latitude": [3.1390, 3.0738, 5.4164, 1.4927, 6.1254],
    "Longitude": [101.6869, 101.5183, 100.3327, 103.7414, 102.2381],
}
df_cities = pd.DataFrame(city_data)

df_cities["Recent Rainfall"] = [random.uniform(30, 120) for _ in range(len(df_cities))]
df_cities["Risk"] = df_cities["Recent Rainfall"].apply(get_risk_level)

# ----------------------------
# Streamlit Map (High-Risk)
# ----------------------------

st.subheader("🗺️ Map of Flood-Prone Cities")

# Filter only high/moderate risk for emphasis
high_risk_map = df_cities[df_cities["Risk"] != "Low"][["Latitude", "Longitude"]]
st.map(high_risk_map)

# ----------------------------
# City Selection and Charts
# ----------------------------

st.subheader("📊 Rainfall History & Forecast")

selected_city = st.selectbox("Choose a city to analyze:", df_cities["City"])

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📈 Last 30 Days Rainfall**")
    df_history = get_mock_rainfall_data(selected_city)
    st.line_chart(df_history.set_index("Date"))

with col2:
    st.markdown("**🌧️ 7-Day Forecast**")
    df_forecast = get_forecast_data(selected_city)
    st.bar_chart(df_forecast.set_index("Date"))

# ----------------------------
# Risk Table
# ----------------------------

st.subheader("⚠️ Risk Summary")

st.dataframe(
    df_cities[["City", "State", "Recent Rainfall", "Risk"]].sort_values(by="Risk", ascending=False),
    use_container_width=True
)
