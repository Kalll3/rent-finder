import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
import requests  # for calling weather API

# Your rental_items list stays the same...

# Add your OpenWeatherMap API key here
OWM_API_KEY = 306e61f79b97c022b94eb5695101aceb

def get_weather(lat, lon):
    url = (
        f"http://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "temp": data["main"]["temp"],
            "desc": data["weather"][0]["description"].title(),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
        return weather
    else:
        return None

# UI
st.set_page_config(page_title="Nearby Rentals", layout="wide")
st.title("🔍 Find Items for Rent Near You")

location = st.text_input("📍 Enter your location ( e.g. Pekan, UMPSA Pekan, Kuantan ):")
radius = st.slider("📏 Search radius (in km)", 1, 20, 5)

if location:
    geolocator = Nominatim(user_agent="rent_app")
    user_loc = geolocator.geocode(location)

    if user_loc:
        user_point = (user_loc.latitude, user_loc.longitude)

        # Show current weather at user's location
        weather = get_weather(user_loc.latitude, user_loc.longitude)
        if weather:
            st.subheader("🌤️ Current Weather at Your Location:")
            st.write(
                f"Temperature: {weather['temp']}°C\n"
                f"Condition: {weather['desc']}\n"
                f"Humidity: {weather['humidity']}%\n"
                f"Wind Speed: {weather['wind_speed']} m/s"
            )
        else:
            st.info("Weather info not available right now.")

        nearby_items = []
        map_points = [{"lat": user_loc.latitude, "lon": user_loc.longitude}]

        for item in rental_items:
            item_point = (item["lat"], item["lon"])
            distance = geodesic(user_point, item_point).km
            if distance <= radius:
                item["distance_km"] = round(distance, 2)
                nearby_items.append(item)
                map_points.append({"lat": item["lat"], "lon": item["lon"]})

        # List Items
        if nearby_items:
            st.subheader("📦 Available Items Nearby:")
            for item in nearby_items:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(item["image"], width=200)
                with col2:
                    st.markdown(f"### {item['name']}")
                    st.write(f"📍 {item['location']}")
                    st.write(f"💰 RM{item['price']} / day")
                    st.write(f"🧭 {item['distance_km']} km away")
                    st.markdown(f"[📞 Book Now]({item['contact']})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.warning("No items found within this radius.")

        # Map of Nearby Items
        st.subheader("🗺️ Map of Nearby Items:")
        st.map(pd.DataFrame(map_points))

    else:
        st.error("Location not found. Try using a nearby place (e.g. Pekan, UMPSA).")
