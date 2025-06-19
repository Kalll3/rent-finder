import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
import requests
from datetime import datetime

def get_location_by_ip():
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            data = response.json()
            loc = data.get("loc", "")  # "lat,lon"
            lat, lon = loc.split(",") if loc else ("", "")
            return {
                "city": data.get("city", ""),
                "region": data.get("region", ""),
                "country": data.get("country", ""),
                "lat": float(lat) if lat else None,
                "lon": float(lon) if lon else None,
            }
    except Exception as e:
        print("IP location error:", e)
    return None

def get_local_time(timezone: str):
    """
    Get current time from WorldTimeAPI by timezone string.
    Example timezone: "Asia/Kuala_Lumpur"
    """
    try:
        url = f"http://worldtimeapi.org/api/timezone/{timezone}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            datetime_str = data.get("datetime")  # e.g. "2025-06-19T17:45:00.123456+08:00"
            dt = datetime.fromisoformat(datetime_str[:-6])  # strip offset for parsing
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            return formatted_time
    except Exception as e:
        print("Time API error:", e)
    return None

rental_items = [
    {
        "name": "📷 Camera",
        "location": "Kampung Ketepang Tengah",
        "lat": 3.5173,
        "lon": 103.4262,
        "price": 200,
        "image": "https://i.ebayimg.com/images/g/sOwAAOSwBr1kWZ3e/s-l1200.jpg",
        "contact": "https://wa.me/60148190876?text=Hi%2C%20I%20want%20to%20rent%20your%20Camera"
    },
    {
        "name": "🔨 Hammer",
        "location": "Taman Permata",
        "lat": 3.5225,
        "lon": 103.4185,
        "price": 50,
        "image": "https://www.qualtry.com/cdn/shop/products/CU7B9350_staged_800x.jpg?v=1666289440",
        "contact": "https://wa.me/60148190876?text=Hi%2C%20I%20want%20to%20rent%20your%20Hammer"
    },
    {
        "name": "📸 Tripod",
        "location": "Taman Harmoni",
        "lat": 3.5068,
        "lon": 103.4299,
        "price": 20,
        "image": "https://i.ebayimg.com/images/g/z0oAAOSwKx9e27sQ/s-l400.jpg",
        "contact": "https://wa.me/60148190876?text=Interested%20in%20your%20Tripod%20rental"
    },
    {
        "name": "🔌 Generator",
        "location": "Pekan",
        "lat": 3.4976,
        "lon": 103.4246,
        "price": 300,
        "image": "https://d172ov9zf7ze1q.cloudfront.net/2021/06/Screenshot_20210531-235422_Chrome.jpg",
        "contact": "mailto:jokerz1403@gmail.com?subject=Rent%20Generator"
    },
    {
        "name": "⛺ Tent",
        "location": "Kampung Padang Polo",
        "lat": 3.4912,
        "lon": 103.4140,
        "price": 80,
        "image": "https://down-my.img.susercontent.com/file/my-11134233-7r98u-ludj1z3e6tbx13",
        "contact": "https://wa.me/60148190876?text=Interested%20in%20renting%20the%20Tent"
    },
]

# Streamlit UI setup
st.set_page_config(page_title="Nearby Rentals", layout="wide")
st.title("🔍 Find Items for Rent Near You")

# Get IP location info
ip_location = get_location_by_ip()
default_location = ip_location["city"] if ip_location and ip_location.get("city") else ""

location = st.text_input("📍 Enter your location (e.g. Pekan, UMPSA Pekan, Kuantan):", value=default_location)
radius = st.slider("📏 Search radius (in km)", 1, 20, 5)

# Show detected IP location info box under slider
if ip_location:
    st.markdown(
        f"**Detected Location from IP:** {ip_location['city']}, {ip_location['region']}, {ip_location['country']}  \n"
        f"Latitude: {ip_location['lat']}, Longitude: {ip_location['lon']}"
    )
else:
    st.info("Could not detect location from IP.")

# Show Malaysia local time box
local_time = get_local_time("Asia/Kuala_Lumpur")
if local_time:
    st.info(f"🕒 Current Malaysia Time: **{local_time}** (Asia/Kuala_Lumpur)")
else:
    st.info("Could not fetch Malaysia local time.")

if location:
    geolocator = Nominatim(user_agent="rent_app")
    user_loc = geolocator.geocode(location)

    if user_loc:
        user_point = (user_loc.latitude, user_loc.longitude)

        nearby_items = []
        map_points = [{"lat": user_loc.latitude, "lon": user_loc.longitude}]

        for item in rental_items:
            item_point = (item["lat"], item["lon"])
            distance = geodesic(user_point, item_point).km
            if distance <= radius:
                item["distance_km"] = round(distance, 2)
                nearby_items.append(item)
                map_points.append({"lat": item["lat"], "lon": item["lon"]})

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

        st.subheader("🗺️ Map of Nearby Items:")
        st.map(pd.DataFrame(map_points))

    else:
        st.error("Location not found. Try using a nearby place (e.g. Pekan, UMPSA).")

else:
    st.info("Please enter a location or allow location detection.")
