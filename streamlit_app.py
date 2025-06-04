import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import random

# ========== API KEY ==========
API_KEY = "1468e5c2a4b24ce7a64140429250306"

# ========== DATA ==========

states = [
    "Johor", "Kedah", "Kelantan", "Malacca", "Negeri Sembilan",
    "Pahang", "Perak", "Perlis", "Penang", "Sabah",
    "Sarawak", "Selangor", "Terengganu", "Kuala Lumpur", "Putrajaya", "Labuan"
]

# 🚨 Flood-prone and possibly-prone areas with coordinates (all 16 states covered)
flood_areas = {
    "Johor": {
        "flood_prone": {
            "Muar 🌊": (2.0474, 102.5669),
            "Batu Pahat 🌊": (1.8553, 102.9314),
            "Kluang 🌧️": (2.0316, 103.3163),
        },
        "possibly_prone": {
            "Kulai 💧": (1.6680, 103.5928),
            "Segamat 💧": (2.5341, 102.8309),
        }
    },
    "Kedah": {
        "flood_prone": {
            "Alor Setar 🌊": (6.1184, 100.3685),
            "Pendang 🌊": (5.9987, 100.4982),
        },
        "possibly_prone": {
            "Sungai Petani 💧": (5.6470, 100.4872),
        }
    },
    "Kelantan": {
        "flood_prone": {
            "Kota Bharu 🌊": (6.1254, 102.2381),
            "Tumpat 🌧️": (6.1977, 102.1712),
        },
        "possibly_prone": {
            "Pasir Mas 💧": (6.0495, 102.1397),
        }
    },
    "Malacca": {
        "flood_prone": {
            "Jasin 🌊": (2.3084, 102.4381),
        },
        "possibly_prone": {
            "Alor Gajah 💧": (2.3811, 102.2080),
        }
    },
    "Negeri Sembilan": {
        "flood_prone": {
            "Seremban 🌧️": (2.7297, 101.9381),
        },
        "possibly_prone": {
            "Port Dickson 💧": (2.5220, 101.7970),
        }
    },
    "Pahang": {
        "flood_prone": {
            "Temerloh 🌊": (3.4486, 102.4179),
            "Kuantan 🌧️": (3.8148, 103.3380),
        },
        "possibly_prone": {
            "Pekan 💧": (3.5000, 103.4000),
        }
    },
    "Perak": {
        "flood_prone": {
            "Teluk Intan 🌊": (4.0236, 101.0213),
            "Ipoh 🌧️": (4.5975, 101.0901),
        },
        "possibly_prone": {
            "Parit 💧": (4.4371, 100.9201),
        }
    },
    "Perlis": {
        "flood_prone": {
            "Kangar 🌧️": (6.4380, 100.1940),
        },
        "possibly_prone": {
            "Arau 💧": (6.4302, 100.2700),
        }
    },
    "Penang": {
        "flood_prone": {
            "Butterworth 🌊": (5.3996, 100.3638),
            "George Town 🌊": (5.4164, 100.3327),
        },
        "possibly_prone": {
            "Bukit Mertajam 💧": (5.3646, 100.4667),
        }
    },
    "Sabah": {
        "flood_prone": {
            "Beaufort 🌧️": (5.3373, 115.7445),
        },
        "possibly_prone": {
            "Kota Kinabalu 💧": (5.9804, 116.0735),
        }
    },
    "Sarawak": {
        "flood_prone": {
            "Kuching 🌊": (1.5535, 110.3592),
        },
        "possibly_prone": {
            "Sibu 💧": (2.2967, 111.8411),
        }
    },
    "Selangor": {
        "flood_prone": {
            "Klang 🌊": (3.0439, 101.4500),
            "Hulu Langat 🌧️": (3.0762, 101.7881),
        },
        "possibly_prone": {
            "Shah Alam 💧": (3.0738, 101.5183),
        }
    },
    "Terengganu": {
        "flood_prone": {
            "Dungun 🌧️": (4.7692, 103.4257),
        },
        "possibly_prone": {
            "Kuala Terengganu 💧": (5.3302, 103.1408),
        }
    },
    "Kuala Lumpur": {
        "flood_prone": {
            "Sentul 🌧️": (3.1804, 101.6935),
        },
        "possibly_prone": {
            "Setapak 💧": (3.1978, 101.7155),
        }
    },
    "Putrajaya": {
        "flood_prone": {},
        "possibly_prone": {
            "Presint 9 💧": (2.9500, 101.6800),
        }
    },
    "Labuan": {
        "flood_prone": {},
        "possibly_prone": {
            "Victoria 💧": (5.2800, 115.2500),
        }
    },
}

# ========== SIDEBAR ==========

def sidebar_content():
    st.sidebar.title("🌧️ FloodSight Malaysia 🌊")
    st.sidebar.markdown("""
**How to use this app:**
1. Select your State and City/Area.
2. Pick the date, month, and year for rainfall history.
3. Check 7-day forecast and flood map.
4. Use risk map for visual danger zones.

💧 Flood Preparedness Tips:
- Secure important documents in waterproof bags.
- Prepare emergency kit (food, water, medicine).
- Know evacuation routes & nearest shelters.
- Keep devices charged.
- Monitor local news & alerts.
    """)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Did you know? 🌍**")
    facts = [
        "Floods are Malaysia's most frequent disaster.",
        "Urban areas flood faster due to less green space.",
        "Mangroves reduce coastal flooding by up to 66%.",
        "Drainage maintenance prevents flash floods.",
    ]
    st.sidebar.info(random.choice(facts))


# ========== DATA FETCHING ==========

def fetch_historical(city):
    df = []
    today = datetime.today()
    for i in range(7):
        date = today - timedelta(days=i)
        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date.strftime('%Y-%m-%d')}"
        try:
            r = requests.get(url)
            data = r.json()
            rain = data["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
            df.append({"Date": date.date(), "Rainfall (mm)": rain})
        except:
            df.append({"Date": date.date(), "Rainfall (mm)": 0})
    return pd.DataFrame(df[::-1])

def fetch_forecast(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7"
    r = requests.get(url)
    df = []
    try:
        data = r.json()
        for day in data["forecast"]["forecastday"]:
            df.append({
                "Date": day["date"],
                "Forecast Rainfall (mm)": day["day"]["totalprecip_mm"]
            })
    except:
        today = datetime.today()
        df = [{"Date": (today + timedelta(days=i)).date(), "Forecast Rainfall (mm)": 0} for i in range(7)]
    return pd.DataFrame(df)

def risk_level(val):
    if val >= 100: return "🔴 High"
    if val >= 50: return "🟠 Medium"
    if val > 0: return "🟡 Low"
    return "🟢 None"

# ========== MAIN APP ==========

def main():
    st.set_page_config(page_title="FloodSight Malaysia", layout="wide")
    st.title("🌧️ FloodSight Malaysia 🌊")
    st.markdown("Real-time rainfall, forecast trends & flood risk for all Malaysian states.")

    sidebar_content()

    state = st.selectbox("Select State 🇲🇾", ["--"] + states)
    if state == "--":
        st.warning("Please select a state to begin.")
        return

    all_cities = list(flood_areas[state]["flood_prone"].keys()) + list(flood_areas[state]["possibly_prone"].keys())
    city = st.selectbox("Choose a City/Area 🏙️", ["--"] + all_cities)
    if city == "--":
        return

    # Clean name for API
    city_api = city.replace("🌧️", "").replace("🌊", "").replace("💧", "").strip()

    lat, lon = (
        flood_areas[state]["flood_prone"].get(city)
        or flood_areas[state]["possibly_prone"].get(city)
    )

    tab1, tab2, tab3, tab4 = st.tabs(["📅 Rainfall History", "📈 Forecast", "📍 City Map", "🗺️ Malaysia Risk Map"])

    with tab1:
        st.subheader(f"7-Day Rainfall History for {city}")
        hist = fetch_historical(city_api)
        st.bar_chart(hist.set_index("Date"))

    with tab2:
        st.subheader(f"7-Day Rainfall Forecast for {city}")
        forecast = fetch_forecast(city_api)
        forecast["Risk Level"] = forecast["Forecast Rainfall (mm)"].apply(risk_level)
        st.line_chart(forecast.set_index("Date")["Forecast Rainfall (mm)"])
        st.dataframe(forecast.set_index("Date"))

    with tab3:
        st.subheader(f"📍 {city}, {state}")
        st.map(pd.DataFrame({"latitude": [lat], "longitude": [lon]}))

    with tab4:
        st.subheader("🗺️ High-Risk and Possibly-Risk Areas in Malaysia")
        map_data = []
        for s in flood_areas:
            for city, (lat, lon) in flood_areas[s]["flood_prone"].items():
                map_data.append({"latitude": lat, "longitude": lon})
            for city, (lat, lon) in flood_areas[s]["possibly_prone"].items():
                map_data.append({"latitude": lat, "longitude": lon})
        st.map(pd.DataFrame(map_data))


if __name__ == "__main__":
    main()
