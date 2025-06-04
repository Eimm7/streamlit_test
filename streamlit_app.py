import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
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
# UI Layout
# ----------------------------

st.set_page_config("Malaysia Flood Forecasting", layout="wide")

st.title("🌊 Malaysia Flood Forecasting App")
st.markdown("This app provides rainfall data, forecast trends, and high-risk flood zones in Malaysia.")

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

# Assign risk levels based on random recent rainfall
df_cities["Recent Rainfall"] = [random.uniform(30, 120) for _ in range(len(df_cities))]
df_cities["Risk"] = df_cities["Recent Rainfall"].apply(get_risk_level)

# ----------------------------
# Map of High-Risk Cities
# ----------------------------

st.subheader("🗺️ High-Risk Flood Cities Map")

fig = px.scatter_mapbox(
    df_cities, lat="Latitude", lon="Longitude",
    hover_name="City", hover_data=["State", "Risk", "Recent Rainfall"],
    color="Risk", size="Recent Rainfall",
    color_discrete_map={"High": "red", "Moderate": "orange", "Low": "green"},
    zoom=5, height=500
)
fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# City Details & Trends
# ----------------------------

st.subheader("📊 Rainfall Trends & Forecast")

selected_city = st.selectbox("Select a city to view details:", df_cities["City"])
col1, col2 = st.columns(2)

# Last 30 days rainfall
with col1:
    st.markdown("**📈 Last 30 Days Rainfall**")
    df_history = get_mock_rainfall_data(selected_city)
    fig1 = px.line(df_history, x="Date", y="Rainfall (mm)", title=f"{selected_city} - Historical Rainfall", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

# Next 7-day forecast
with col2:
    st.markdown("**🌧️ 7-Day Rainfall Forecast**")
    df_forecast = get_forecast_data(selected_city)
    fig2 = px.bar(df_forecast, x="Date", y="Forecast (mm)", title=f"{selected_city} - Forecast", color="Forecast (mm)",
                  color_continuous_scale="Blues")
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# Risk Summary Table
# ----------------------------

st.subheader("⚠️ City Risk Summary")

st.dataframe(df_cities[["City", "State", "Recent Rainfall", "Risk"]].sort_values(by="Risk", ascending=False),
             use_container_width=True)
