import streamlit as st
import requests
import matplotlib.pyplot as plt
import geocoder
from datetime import datetime

# ---- API Keys ----
WEATHERAPI_KEY = "8d1088fce6184e97937155132250609 "  # अपनी WeatherAPI key डालो
WEATHERAPI_BASE = "http://api.weatherapi.com/v1/current.json"
WEATHERAPI_FORECAST = "http://api.weatherapi.com/v1/forecast.json"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# ---- Function: Select Background ----
def get_bg_image(condition):
    condition = condition.lower()
    if "sunny" in condition or "clear" in condition:
        return "images/sunny.jpg"
    elif "cloud" in condition:
        return "images/cloudy.jpg"
    elif "rain" in condition or "drizzle" in condition:
        return "images/rainy.jpg"
    elif "snow" in condition:
        return "images/snowy.jpg"
    else:
        return "images/default.jpg"

# ---- Function: Select Icon ----
def get_icon(condition):
    condition = condition.lower()
    if "sunny" in condition or "clear" in condition:
        return "images/icons/clear.png"
    elif "cloud" in condition:
        return "images/icons/clouds.png"
    elif "rain" in condition or "drizzle" in condition:
        return "images/icons/rain.png"
    elif "snow" in condition:
        return "images/icons/snow.png"
    elif "mist" in condition or "fog" in condition:
        return "images/icons/mist.png"
    else:
        return "images/icons/clouds.png"

# ---- Streamlit UI ----
st.set_page_config(page_title="🌦 Real-Time Weather App", page_icon="⛅", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-size: cover;
        background-position: center;
        color: white;
    }
    .block-container {
        background-color: rgba(0, 0, 0, 0.55);
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌍 Real-Time Weather App (Dual Source)")
st.write("Live weather with accuracy boosted by Open-Meteo cross-checking ✅")

# ---- Auto Location Detection ----
g = geocoder.ip("me")
default_city = g.city if g.city else "Delhi"

# ---- User Input ----
city = st.text_input("🔎 Enter City", default_city)
unit_choice = st.radio("🌡 Select Temperature Unit", ["Celsius (°C)", "Fahrenheit (°F)"])

if unit_choice.startswith("Celsius"):
    temp_symbol = "°C"
else:
    temp_symbol = "°F"

if st.button("Get Weather"):
    if city:
        # ---- Current Weather from WeatherAPI ----
        params = {"key": WEATHERAPI_KEY, "q": city}
        response = requests.get(WEATHERAPI_BASE, params=params)

        if response.status_code == 200:
            data = response.json()
            location = data["location"]["name"]
            country = data["location"]["country"]
            lat = data["location"]["lat"]
            lon = data["location"]["lon"]
            current = data["current"]

            # Primary WeatherAPI values
            if unit_choice.startswith("Celsius"):
                temp = current["temp_c"]
                feels_like = current["feelslike_c"]
            else:
                temp = current["temp_f"]
                feels_like = current["feelslike_f"]

            humidity = current["humidity"]
            wind = current["wind_kph"]
            desc = current["condition"]["text"]

            # ---- Cross-check with Open-Meteo ----
            o_params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m", "windspeed_10m"],
            }
            o_response = requests.get(OPEN_METEO_URL, params=o_params)

            if o_response.status_code == 200:
                o_data = o_response.json()["current"]
                if unit_choice.startswith("Celsius"):
                    temp = round((temp + o_data["temperature_2m"]) / 2, 1)
                else:
                    # Open-Meteo default is °C → convert to °F
                    om_temp_f = (o_data["temperature_2m"] * 9/5) + 32
                    temp = round((temp + om_temp_f) / 2, 1)

                humidity = round((humidity + o_data["relative_humidity_2m"]) / 2, 1)
                wind = round((wind + o_data["windspeed_10m"]) / 2, 1)

            # ---- Set Background ----
            bg_img = get_bg_image(desc)
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url('{bg_img}');
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

            # ---- Weather Icon ----
            icon = get_icon(desc)
            st.image(icon, width=100)

            # ---- Show Current Weather ----
            st.success(f"📍 Weather in {location}, {country}")
            st.metric("🌡 Temperature", f"{temp} {temp_symbol}")
            st.write(f"**☁ Condition:** {desc}")
            st.write(f"**💧 Humidity:** {humidity}%")
            st.write(f"**💨 Wind Speed:** {wind} km/h")

            # ---- 5-Day Forecast from WeatherAPI ----
            st.subheader("📊 5-Day Forecast")
            f_params = {"key": WEATHERAPI_KEY, "q": city, "days": 5}
            f_response = requests.get(WEATHERAPI_FORECAST, params=f_params)

            if f_response.status_code == 200:
                f_data = f_response.json()
                dates, temps = [], []

                for forecast in f_data["forecast"]["forecastday"]:
                    dt = forecast["date"]
                    if unit_choice.startswith("Celsius"):
                        temps.append(forecast["day"]["avgtemp_c"])
                    else:
                        temps.append(forecast["day"]["avgtemp_f"])
                    dates.append(dt)

                # ---- Chart ----
                plt.figure(figsize=(8,4))
                plt.plot(dates, temps, marker="o", linestyle="-", color="yellow")
                plt.title(f"5-Day Temperature Forecast for {city}")
                plt.xlabel("Date")
                plt.ylabel(f"Temp ({temp_symbol})")
                plt.grid(True, linestyle="--", alpha=0.6)
                st.pyplot(plt)

        else:
            st.error("❌ City not found or API error.")
    else:
        st.warning("Please enter a city name.")
