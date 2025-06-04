import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# Your WeatherAPI key
API_KEY = "1468e5c2a4b24ce7a64140429250306"

# ============ DATA =============
states = [
    "Johor", "Kedah", "Kelantan", "Malacca", "Negeri Sembilan",
    "Pahang", "Perak", "Perlis", "Penang", "Sabah",
    "Sarawak", "Selangor", "Terengganu", "Kuala Lumpur", "Putrajaya", "Labuan"
]

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
    # ... [same flood_areas dict as before for other states]
    # (for brevity, paste the same data from the previous code here)
}

def sidebar_content():
    st.sidebar.title("🌧️ FloodSight Malaysia 🌊")
    st.sidebar.markdown("""
    **How to use this app:**
    - Select a Malaysian state and city/area to view rainfall history and 7-day forecast.
    - Explore flood risk maps highlighting flood-prone areas.
    - Use the tabs to switch between data views.
    - Adjust the risk filter slider to view areas by flood risk severity.
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


# Fetch past 7 days historical rainfall from WeatherAPI (max 7 days per free tier)
def fetch_historical_rainfall(city_name):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=6)  # past 7 days
    dates = []
    rainfall = []

    for i in range(7):
        day = start_date + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city_name}&dt={date_str}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            try:
                day_data = data["forecast"]["forecastday"][0]["day"]
                rain = day_data.get("totalprecip_mm", 0.0)
                rainfall.append(rain)
                dates.append(day)
            except Exception:
                rainfall.append(0)
                dates.append(day)
        else:
            rainfall.append(0)
            dates.append(day)

    df = pd.DataFrame({"Date": dates, "Rainfall (mm)": rainfall})
    return df


# Fetch 7-day forecast rainfall from WeatherAPI
def fetch_7day_forecast(city_name):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city_name}&days=7"
    res = requests.get(url)
    dates = []
    rainfall_forecast = []
    if res.status_code == 200:
        data = res.json()
        forecastdays = data.get("forecast", {}).get("forecastday", [])
        for day in forecastdays:
            date = datetime.strptime(day["date"], "%Y-%m-%d")
            rain = day["day"].get("totalprecip_mm", 0.0)
            dates.append(date)
            rainfall_forecast.append(rain)
    else:
        # If API fails, fallback to zeros
        dates = [datetime.today() + timedelta(days=i) for i in range(7)]
        rainfall_forecast = [0]*7

    df = pd.DataFrame({"Date": dates, "Forecast Rainfall (mm)": rainfall_forecast})
    return df


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
    st.markdown("Check real-time rainfall history, 7-day forecast, and flood risks by Malaysian states and cities.")

    sidebar_content()

    state = st.selectbox("Select State 🇲🇾", ["-- Choose a state --"] + states)

    if state and state != "-- Choose a state --":
        flood_prone_cities = list(flood_areas[state]["flood_prone"].keys())
        possibly_prone_cities = list(flood_areas[state]["possibly_prone"].keys())

        all_cities = []
        if flood_prone_cities:
            all_cities += flood_prone_cities
        if possibly_prone_cities:
            all_cities += possibly_prone_cities

        city = st.selectbox(f"Select City/Area in {state} 🏙️", ["-- Choose a city/area --"] + all_cities)

        if city and city != "-- Choose a city/area --":
            # Get lat/lon
            if city in flood_areas[state]["flood_prone"]:
                lat, lon = flood_areas[state]["flood_prone"][city]
            else:
                lat, lon = flood_areas[state]["possibly_prone"][city]

            st.write(f"### Selected Location: {city} in {state}")
            st.write(f"📍 Coordinates: {lat}, {lon}")

            tab1, tab2, tab3 = st.tabs(["📅 Rainfall History", "📈 7-Day Forecast", "🗺️ Flood Risk Map"])

            with tab1:
                st.subheader(f"Rainfall History for {city} (Past 7 days)")
                hist_df = fetch_historical_rainfall(city.replace(" 🌊","").replace(" 🌧️","").replace(" 💧",""))
                st.bar_chart(hist_df.set_index("Date")["Rainfall (mm)"])

            with tab2:
                st.subheader(f"7-Day Rainfall Forecast for {city}")
                forecast_df = fetch_7day_forecast(city.replace(" 🌊","").replace(" 🌧️","").replace(" 💧",""))
                st.line_chart(forecast_df.set_index("Date")["Forecast Rainfall (mm)"])

                st.markdown(
                    """
                    **Risk Legend:**
                    - 🔴 High risk (≥ 100mm)
                    - 🟠 Medium risk (50mm–99mm)
                    - 🟡 Low risk (1mm–49mm)
                    - 🟢 No risk (0mm)
                    """
                )

                forecast_df["Risk Level"] = forecast_df["Forecast Rainfall (mm)"].apply(risk_level)
                st.table(forecast_df.set_index("Date")[["Forecast Rainfall (mm)", "Risk Level"]])

            with tab3:
                st.subheader(f"Flood Risk Map around {city}")
                map_data = []
                for c, (lt, ln) in flood_areas[state]["flood_prone"].items():
                    risk = "High 🔴"
                    map_data.append({"lat": lt, "lon": ln, "city": c, "risk": risk})
                for c, (lt, ln) in flood_areas[state]["possibly_prone"].items():
                    risk = "Medium 🟠"
                    map_data.append({"lat": lt, "lon": ln, "city": c, "risk": risk})

                map_df = pd.DataFrame(map_data)
                st.map(map_df.rename(columns={"lat": "latitude", "lon": "longitude"}))

                st.markdown(
                    f"**Legend:** 🔴 Flood Prone (High Risk), 🟠 Possibly Prone (Medium Risk)"
                )
    else:
        st.info("Please select a state to start exploring flood risk data.")


if __name__ == "__main__":
    main()
