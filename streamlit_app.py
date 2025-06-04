import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# Your WeatherAPI key (keep yours)
API_KEY = "1468e5c2a4b24ce7a64140429250306"

# ============ DATA =============
states = [
    "Johor", "Kedah", "Kelantan", "Malacca", "Negeri Sembilan",
    "Pahang", "Perak", "Perlis", "Penang", "Sabah",
    "Sarawak", "Selangor", "Terengganu", "Kuala Lumpur", "Putrajaya", "Labuan"
]

# Flood prone and possibly prone areas per state with emojis
flood_areas = {
    "Johor": {
        "flood_prone": {
            "Muar 🌊": (2.0474, 102.5669),
            "Kluang 🌧️": (2.0316, 103.3163),
            "Batu Pahat 🌊": (1.8553, 102.9314),
            "Tangkak 🌧️": (2.3247, 102.5636),
            "Pontian 🌊": (1.4919, 103.0399),
        },
        "possibly_prone": {
            "Segamat 💧": (2.5341, 102.8309),
            "Kulai 💧": (1.6680, 103.5928),
        }
    },
    "Pahang": {
        "flood_prone": {
            "Kuantan 🌊": (3.8076, 103.3260),
            "Temerloh 🌧️": (3.4415, 102.4183),
            "Jerantut 🌊": (3.9240, 102.3700),
            "Pekan 🌊": (3.4836, 103.4010),  # Added Pekan as requested
        },
        "possibly_prone": {
            "Raub 💧": (3.7990, 101.8597),
            "Bera 💧": (3.3500, 102.7200),
        }
    },
    # Add other states similarly here ...
    # For brevity, you should fill in the rest as in your original data
}

# Sidebar content with instructions and tips
def sidebar_content():
    st.sidebar.title("🌧️ FloodSight Malaysia 🌊")
    st.sidebar.markdown("""
    **How to use this app:**
    - Select your State 🇲🇾 and City/Area 🏙️.
    - Choose a specific Date (year, month, day).
    - Click **Check Flood Risk** to fetch rainfall data and risk levels.
    - Use tabs to view Rainfall History, 7-Day Forecast, and Flood Risk Map.
    - Separate map shows the selected state's flood-prone and possibly prone areas.
    """)
    st.sidebar.markdown("---")
    st.sidebar.subheader("💧 Flood Preparedness Tips:")
    tips = [
        "Prepare an emergency kit with essentials (water, food, meds).",
        "Know your evacuation routes and centers.",
        "Avoid driving or walking through flooded areas.",
        "Stay tuned to local weather updates and warnings.",
        "Protect important documents in waterproof bags."
    ]
    for tip in tips:
        st.sidebar.markdown(f"- {tip}")

    facts = [
        "Floods are the most common natural disaster worldwide.",
        "Malaysia experiences seasonal monsoon floods from Nov to Mar.",
        "Early flood warning systems save lives and reduce damages.",
        "Urbanization increases flood risks due to poor drainage.",
        "Trees and mangroves help reduce flood impact by absorbing water."
    ]
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Did you know? 🤔**")
    import random
    st.sidebar.info(random.choice(facts))

# Fetch past rainfall for selected date (WeatherAPI history works only per date)
def fetch_historical_rainfall(city_name, date):
    url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city_name}&dt={date}"
    res = requests.get(url)
    rainfall = 0.0
    if res.status_code == 200:
        try:
            data = res.json()
            rainfall = data["forecast"]["forecastday"][0]["day"].get("totalprecip_mm", 0.0)
        except Exception:
            rainfall = 0.0
    return rainfall

# Fetch 7-day forecast rainfall
def fetch_7day_forecast(city_name):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city_name}&days=7"
    res = requests.get(url)
    dates = []
    rainfall_forecast = []
    if res.status_code == 200:
        data = res.json()
        forecastdays = data.get("forecast", {}).get("forecastday", [])
        for day in forecastdays:
            dates.append(datetime.strptime(day["date"], "%Y-%m-%d"))
            rainfall_forecast.append(day["day"].get("totalprecip_mm", 0.0))
    else:
        dates = [datetime.today() + timedelta(days=i) for i in range(7)]
        rainfall_forecast = [0]*7

    df = pd.DataFrame({"Date": dates, "Forecast Rainfall (mm)": rainfall_forecast})
    return df

# Risk classification based on rainfall
def risk_level(rainfall):
    if rainfall >= 100:
        return "High 🔴"
    elif rainfall >= 50:
        return "Medium 🟠"
    elif rainfall > 0:
        return "Low 🟡"
    else:
        return "None 🟢"

def main():
    st.title("🌧️ FloodSight Malaysia 🌊")
    st.markdown("Explore rainfall history, forecast, and flood risks by Malaysian states and cities.")

    sidebar_content()

    # State selectbox
    state = st.selectbox("Select State 🇲🇾", ["-- Choose a state --"] + states)

    # Date picker (year, month, day)
    selected_date = st.date_input("Select Date for Rainfall History (max past 7 days)", max_value=datetime.today())

    # City selectbox, populated after state chosen
    if state and state != "-- Choose a state --":
        flood_prone_cities = list(flood_areas[state]["flood_prone"].keys())
        possibly_prone_cities = list(flood_areas[state]["possibly_prone"].keys())
        all_cities = flood_prone_cities + possibly_prone_cities
        city = st.selectbox(f"Select City/Area in {state} 🏙️", ["-- Choose a city/area --"] + all_cities)
    else:
        city = None

    # Check button triggers data fetch
    if st.button("✅ Check Flood Risk"):

        if state == "-- Choose a state --" or not city or city == "-- Choose a city/area --":
            st.warning("Please select a valid state and city/area.")
        else:
            # Get lat/lon coords for selected city
            if city in flood_areas[state]["flood_prone"]:
                lat, lon = flood_areas[state]["flood_prone"][city]
            else:
                lat, lon = flood_areas[state]["possibly_prone"][city]

            st.write(f"### Selected Location: {city} in {state}")
            st.write(f"📍 Coordinates: {lat}, {lon}")
            st.write(f"📅 Date chosen for rainfall history: {selected_date.strftime('%Y-%m-%d')}")

            # Fetch historical rainfall for selected date
            hist_rain = fetch_historical_rainfall(city.replace(" 🌊","").replace(" 🌧️","").replace(" 💧",""), selected_date.strftime('%Y-%m-%d'))
            hist_risk = risk_level(hist_rain)

            # Show results in tabs
            tab1, tab2, tab3 = st.tabs(["📅 Rainfall History", "📈 7-Day Forecast", "🗺️ Flood Risk Map"])

            with tab1:
                st.subheader(f"Rainfall on {selected_date.strftime('%Y-%m-%d')} in {city}")
                st.write(f"Total Rainfall: **{hist_rain} mm**")
                st.write(f"Flood Risk Level: **{hist_risk}**")

            with tab2:
                st.subheader(f"7-Day Rainfall Forecast for {city}")
                forecast_df = fetch_7day_forecast(city.replace(" 🌊","").replace(" 🌧️","").replace(" 💧",""))
                st.line_chart(forecast_df.set_index("Date")["Forecast Rainfall (mm)"])

                st.markdown("""
                **Risk Legend:**
                - 🔴 High risk (≥ 100mm)
                - 🟠 Medium risk (50mm–99mm)
                - 🟡 Low risk (1mm–49mm)
                - 🟢 No risk (0mm)
                """)

                forecast_df["Risk Level"] = forecast_df["Forecast Rainfall (mm)"].apply(risk_level)
                st.dataframe(forecast_df.style.applymap(
                    lambda val: 'background-color: red; color: white' if "High" in val else
                                ('background-color: orange; color: black' if "Medium" in val else
                                 ('background-color: yellow; color: black' if "Low" in val else
                                  'background-color: lightgreen; color: black')), subset=["Risk Level"]
                ))

            with tab3:
                st.subheader("Flood Risk Map for Selected Location")
                # Show map zoomed on city location
                map_data = pd.DataFrame({"lat": [lat], "lon": [lon]})
                st.map(map_data, zoom=10)

            # Show a separate map for the whole selected state with all flood prone + possibly prone areas
            st.markdown("---")
            st.subheader(f"🌍 Flood-Prone and Possibly Prone Areas in {state}")

            # Prepare map data for state
            def marker_color(city_name):
                # Determine color based on category
                if city_name in flood_areas[state]["flood_prone"]:
                    return "red"
                elif city_name in flood_areas[state]["possibly_prone"]:
                    return "orange"
                else:
                    return "blue"

            # Collect all points for this state
            points = []
            for c, coords in flood_areas[state]["flood_prone"].items():
                points.append({"city": c, "lat": coords[0], "lon": coords[1], "color": "red"})
            for c, coords in flood_areas[state]["possibly_prone"].items():
                points.append({"city": c, "lat": coords[0], "lon": coords[1], "color": "orange"})

            if points:
                df_points = pd.DataFrame(points)
                # Streamlit map only colors markers by a single color column if used with pydeck or folium, but 
                # since we do not want extra libraries, we'll show a simple map with all points.
                st.map(df_points.rename(columns={"lat":"latitude", "lon":"longitude"}))
                st.markdown("**Legend:** 🔴 Flood-Prone Areas | 🟠 Possibly Prone Areas")
            else:
                st.info(f"No flood prone data available for {state}.")

    else:
        st.info("Select your state, city, and date then click **Check Flood Risk**.")

if __name__ == "__main__":
    main()
