import streamlit as st
import requests
import pandas as pd
import datetime
import calendar
import plotly.express as px

# -----------------------------
# Constants and Configuration
# -----------------------------
API_KEY = "1468e5c2a4b24ce7a64140429250306"  # Replace with your actual WeatherAPI key

# Mapping of Malaysian states to their flood-prone and possibly flood-prone cities with coordinates
# 🌊 = Highly flood-prone; ⚠️ = Possibly flood-prone
state_city_coords = {
    "Johor": {
        "Johor Bahru 🌊": [1.4927, 103.7414],
        "Muar ⚠️": [2.0500, 102.5667],
        "Batu Pahat 🌊": [1.8500, 102.9333],
        "Kluang 🌊": [2.0305, 103.3169],
        "Pontian ⚠️": [1.4856, 103.3895],
        "Segamat 🌊": [2.5143, 102.8105],
        "Tangkak ⚠️": [2.3077, 102.5647],
        "Kota Tinggi ⚠️": [1.7406, 103.9400],
        "Ledang ⚠️": [2.3512, 102.6441]
    },
    "Kedah": {
        "Alor Setar 🌊": [6.1200, 100.3700],
        "Sungai Petani ⚠️": [5.6500, 100.4800],
        "Kulim ⚠️": [5.4000, 100.5200],
        "Baling ⚠️": [5.8900, 100.9600],
        "Padang Terap ⚠️": [5.8000, 100.5000]
    },
    "Kelantan": {
        "Kota Bharu 🌊": [6.1256, 102.2513],
        "Pasir Mas 🌊": [6.0290, 102.2010],
        "Tanah Merah ⚠️": [5.9369, 102.1523],
        "Machang ⚠️": [5.8333, 102.1833],
        "Tumpat ⚠️": [6.1933, 102.2250]
    },
    "Melaka": {
        "Melaka City ⚠️": [2.1896, 102.2501],
        "Alor Gajah ⚠️": [2.3292, 102.2586],
        "Jasin ⚠️": [2.3720, 102.4333]
    },
    "Negeri Sembilan": {
        "Seremban ⚠️": [2.7261, 101.9384],
        "Port Dickson 🌊": [2.5196, 101.7942],
        "Rembau ⚠️": [2.6541, 102.0320],
        "Tampin ⚠️": [2.4528, 102.2431]
    },
    "Pahang": {
        "Kuantan 🌊": [3.8073, 103.3260],
        "Temerloh ⚠️": [3.4399, 102.4188],
        "Bentong ⚠️": [3.5033, 101.9510],
        "Jerantut ⚠️": [3.9139, 102.3637],
        "Raub ⚠️": [3.8000, 101.8500],
        "Cameron Highlands ⚠️": [4.4700, 101.3800],
        "Pekan 🌊": [3.4910, 103.3995]
    },
    "Perak": {
        "Ipoh 🌊": [4.5975, 101.0901],
        "Teluk Intan ⚠️": [4.0152, 100.9421],
        "Bagan Serai ⚠️": [5.0531, 100.7003],
        "Parit Buntar ⚠️": [5.0840, 100.4880],
        "Taiping ⚠️": [4.8521, 100.7401],
        "Kuala Kangsar ⚠️": [4.7667, 100.9333]
    },
    "Perlis": {
        "Kangar ⚠️": [6.4445, 100.1999],
        "Arau ⚠️": [6.4420, 100.2060]
    },
    "Pulau Pinang": {
        "George Town 🌊": [5.4164, 100.3327],
        "Bukit Mertajam ⚠️": [5.3510, 100.4409],
        "Butterworth ⚠️": [5.3997, 100.3638],
        "Nibong Tebal ⚠️": [5.1633, 100.4351],
        "Sungai Bakap ⚠️": [5.2865, 100.3463]
    },
    "Sabah": {
        "Kota Kinabalu 🌊": [5.9804, 116.0735],
        "Sandakan ⚠️": [5.8407, 118.1171],
        "Tawau ⚠️": [4.2443, 117.8912],
        "Keningau ⚠️": [5.3290, 116.1671],
        "Lahad Datu ⚠️": [5.0333, 118.3333]
    },
    "Sarawak": {
        "Kuching 🌊": [1.5533, 110.3593],
        "Sibu ⚠️": [2.2872, 111.8305],
        "Bintulu ⚠️": [3.1716, 113.0273],
        "Miri ⚠️": [4.3990, 113.9914],
        "Sarikei ⚠️": [2.0450, 111.5281]
    },
    "Selangor": {
        "Shah Alam 🌊": [3.0738, 101.5183],
        "Klang 🌊": [3.0333, 101.4500],
        "Petaling Jaya ⚠️": [3.1073, 101.6067],
        "Kajang 🌊": [2.9927, 101.7882],
        "Ampang 🌊": [3.1496, 101.7600],
        "Gombak ⚠️": [3.2960, 101.7255],
        "Puchong ⚠️": [3.0153, 101.6096],
        "Seri Kembangan ⚠️": [3.0319, 101.7126],
        "Rawang ⚠️": [3.3001, 101.5325],
        "Sungai Buloh ⚠️": [3.2095, 101.5707]
    },
    "Terengganu": {
        "Kuala Terengganu 🌊": [5.3300, 103.1400],
        "Dungun ⚠️": [4.8285, 103.4247],
        "Kemaman ⚠️": [4.2400, 103.4400],
        "Besut ⚠️": [5.7391, 102.8096]
    },
    "Kuala Lumpur": {
        "Kuala Lumpur 🌊": [3.1390, 101.6869],
        "Setapak 🌊": [3.1979, 101.7146],
        "Cheras 🌊": [3.0723, 101.7405],
        "Bukit Bintang ⚠️": [3.1467, 101.7114],
        "Segambut ⚠️": [3.1905, 101.6386]
    }
}

# -----------------------------------
# Helper Functions for API Interaction
# -----------------------------------

def get_current_weather(city):
    """
    Fetches current weather data for a city from WeatherAPI.
    Returns a dict with temperature, condition, humidity, wind, etc.
    """
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_historical_weather(city, date):
    """
    Fetches historical weather data for a city on a given date (YYYY-MM-DD).
    Returns JSON data with hourly rainfall etc.
    """
    url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_forecast_weather(city, days=7):
    """
    Fetches forecast weather data for a city for the next 'days' days.
    Default is 7-day forecast.
    """
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days={days}&aqi=no&alerts=no"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# -----------------------------------
# Streamlit UI and Main Logic
# -----------------------------------

st.set_page_config(page_title="FloodSight Malaysia", layout="wide")

st.title("🌧️ FloodSight Malaysia - Flood Forecasting & Rainfall History")

# Sidebar: Select State and City for current weather and flood risk
with st.sidebar:
    st.header("Select Location")
    selected_state = st.selectbox("Select State", sorted(state_city_coords.keys()))
    # List of cities for selected state (showing city names without emoji for input)
    city_list = list(state_city_coords[selected_state].keys())
    selected_city_display = st.selectbox("Select City/Town", city_list)
    # Remove emoji for API query by splitting on space and taking first token
    selected_city_name = selected_city_display.split()[0]

    st.markdown("---")
    st.write("**About FloodSight Malaysia:**")
    st.write(
        """
        This app visualizes rainfall history and flood risks in Malaysia using WeatherAPI data.
        Select a state and city to see current weather, a 7-day rainfall forecast,
        and flood risk indicators for flood-prone areas.
        """
    )

# Get coordinates of selected city for map display
coords = state_city_coords[selected_state][selected_city_display]

# --- Tabs for organized UI ---
tab1, tab2, tab3 = st.tabs(["Current Flood Risk", "7-Day Rainfall Forecast", "Daily Rainfall History"])

# --------------------------
# TAB 1: Current Flood Risk
# --------------------------
with tab1:
    st.header(f"Current Flood Risk and Weather in {selected_city_display} ({selected_state})")

    # Fetch current weather data
    current_data = get_current_weather(selected_city_name)
    if current_data:
        temp_c = current_data["current"]["temp_c"]
        condition = current_data["current"]["condition"]["text"]
        humidity = current_data["current"]["humidity"]
        wind_kph = current_data["current"]["wind_kph"]

        # Display weather summary
        st.markdown(f"**Temperature:** {temp_c} °C")
        st.markdown(f"**Condition:** {condition}")
        st.markdown(f"**Humidity:** {humidity}%")
        st.markdown(f"**Wind Speed:** {wind_kph} km/h")

        # Simple flood risk based on rainfall in last hour (if available)
        rain_mm = current_data["current"].get("precip_mm", 0)
        if rain_mm > 10:
            risk_level = "🔴 High"
            risk_color = "red"
        elif rain_mm > 2:
            risk_level = "🟠 Moderate"
            risk_color = "orange"
        else:
            risk_level = "🟢 Low"
            risk_color = "green"

        st.markdown(f"### Flood Risk Level: <span style='color:{risk_color}'>{risk_level}</span>", unsafe_allow_html=True)
    else:
        st.error("Failed to retrieve current weather data.")

    # Show map with location
    st.map(pd.DataFrame({'lat': [coords[0]], 'lon': [coords[1]]}))

# --------------------------------
# TAB 2: 7-Day Rainfall Forecast
# --------------------------------
with tab2:
    st.header(f"7-Day Rainfall Forecast for {selected_city_display}")

    forecast_data = get_forecast_weather(selected_city_name, days=7)
    if forecast_data:
        forecast_days = forecast_data['forecast']['forecastday']
        df_forecast = pd.DataFrame({
            "Date": [day['date'] for day in forecast_days],
            "Avg Rain (mm)": [day['day']['daily_chance_of_rain'] for day in forecast_days],
            "Max Temp (°C)": [day['day']['maxtemp_c'] for day in forecast_days],
            "Min Temp (°C)": [day['day']['mintemp_c'] for day in forecast_days]
        })

        # Plotting rainfall chance as a bar chart
        fig = px.bar(df_forecast, x="Date", y="Avg Rain (mm)",
                     title=f"7-Day Rainfall Chance (%) in {selected_city_display}",
                     labels={"Avg Rain (mm)": "Chance of Rain (%)"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to retrieve forecast data.")

# ------------------------------
# TAB 3: Daily Rainfall History
# ------------------------------
with tab3:
    st.header(f"Daily Rainfall History - Select Month & Year")

    # Select year and month
    current_year = datetime.datetime.now().year
    years = list(range(2022, current_year + 1))
    selected_year = st.selectbox("Select Year", years, index=len(years) - 1)

    month_names = list(calendar.month_name)[1:]  # January to December
    selected_month_name = st.selectbox("Select Month", month_names, index=datetime.datetime.now().month - 1)

    selected_month = month_names.index(selected_month_name) + 1  # month number

    # Calculate days in selected month and year
    days_in_month = calendar.monthrange(selected_year, selected_month)[1]

    # Collect daily rainfall for each day in the month
    rainfall_data = []
    for day in range(1, days_in_month + 1):
        date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
        hist_data = get_historical_weather(selected_city_name, date_str)
        if hist_data and "forecast" in hist_data:
            # Sum hourly rainfall
            total_rain_mm = sum(hour['precip_mm'] for hour in hist_data['forecast']['forecastday'][0]['hour'])
            rainfall_data.append({"Date": date_str, "Rainfall (mm)": total_rain_mm})
        else:
            rainfall_data.append({"Date": date_str, "Rainfall (mm)": None})

    df_rainfall = pd.DataFrame(rainfall_data)
    df_rainfall["Date"] = pd.to_datetime(df_rainfall["Date"])

    # Line plot for daily rainfall
    fig_hist = px.line(df_rainfall, x="Date", y="Rainfall (mm)",
                       title=f"Daily Rainfall History for {selected_city_display} - {selected_month_name} {selected_year}",
                       markers=True)
    st.plotly_chart(fig_hist, use_container_width=True)

# --------------------------------------
# Flood-Prone Cities Map with Markers
# --------------------------------------
st.markdown("---")
st.header("Flood-Prone Cities and Areas in Malaysia")

# Prepare a DataFrame with all flood-prone areas
all_cities = []
for state, cities in state_city_coords.items():
    for city_name, latlon in cities.items():
        # Identify risk level by emoji in city_name
        risk = "Possibly Flood-Prone"
        if "🌊" in city_name:
            risk = "Highly Flood-Prone"
        all_cities.append({
            "State": state,
            "City": city_name.replace("🌊", "").replace("⚠️", "").strip(),
            "Latitude": latlon[0],
            "Longitude": latlon[1],
            "Risk": risk
        })

df_cities = pd.DataFrame(all_cities)

# Map with color-coded markers
risk_colors = {"Highly Flood-Prone": "red", "Possibly Flood-Prone": "orange"}

# Use Plotly scatter mapbox for better marker color control
import plotly.graph_objects as go

fig_map = go.Figure()

for risk_level in df_cities["Risk"].unique():
    df_sub = df_cities[df_cities["Risk"] == risk_level]
    fig_map.add_trace(go.Scattermapbox(
        lat=df_sub["Latitude"],
        lon=df_sub["Longitude"],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color=risk_colors[risk_level],
            opacity=0.7
        ),
        text=df_sub["City"] + ", " + df_sub["State"] + " (" + risk_level + ")",
        name=risk_level
    ))

fig_map.update_layout(
    mapbox_style="open-street-map",
    mapbox_zoom=5.5,
    mapbox_center={"lat": 4.5, "lon": 102.5},
    margin={"r":0,"t":0,"l":0,"b":0},
    legend=dict(title="Flood Risk Level")
)

st.plotly_chart(fig_map, use_container_width=True)
