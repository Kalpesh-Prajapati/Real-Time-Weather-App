import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import requests
from datetime import datetime, timedelta, timezone
from scipy.constants import zero_Celsius

API_KEY = 'd0f28d99c2361dc539b9e434a8c452a5'

def get_lat_lon(zipcode: int, countrycode: str, api_key: str):
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zipcode},{countrycode}&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data["lat"], data["lon"], data["name"]

def fetch_weather(lat: float, lon: float, api_key: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def kelvin_to_celsius(kelvin_temp: float) -> float:
    return kelvin_temp - zero_Celsius

def convert_deg_to_direction(deg: float) -> str:
    directions = ["North", "Northeast", "East", "Southeast", "South", "Southwest", "West", "Northwest"]
    index = round(deg % 360 / 45) % 8
    return directions[index]

def format_timezone(offset_seconds: int) -> str:
    offset_hours = offset_seconds // 3600
    offset_minutes = (offset_seconds % 3600) // 60
    sign = '+' if offset_seconds >= 0 else '-'
    return f"UTC{sign}{abs(offset_hours):02d}:{abs(offset_minutes):02d}"

def preprocess_weather_data(data: dict) -> dict:
    name_list = ["main", "wind", "clouds", "sys"]
    single_keys = ["timezone", "name", "weather"]
    weather_data = {}

    for key in name_list:
        if key in data and isinstance(data[key], dict):
            for sub_key, value in data[key].items():
                weather_data[sub_key] = value

    for key in single_keys:
        if key in data:
            weather_data[key] = data[key]

    tz = timezone(timedelta(seconds=weather_data["timezone"]))
    sunrise_local = datetime.fromtimestamp(weather_data["sunrise"], tz)
    sunset_local = datetime.fromtimestamp(weather_data["sunset"], tz)
    now = datetime.now(tz)

    weather_data["date"] = now.strftime('%A, %d %B %Y')
    weather_data["time"] = now.strftime('%H:%M:%S')
    weather_data["sunrise"] = sunrise_local.strftime('%H:%M')
    weather_data["sunset"] = sunset_local.strftime('%H:%M')

    for temp_key in ["temp", "temp_min", "temp_max", "feels_like"]:
        if temp_key in weather_data:
            celsius_temp = kelvin_to_celsius(weather_data[temp_key])
            weather_data[temp_key] = f"{celsius_temp:.1f}"

    if "speed" in weather_data:
        weather_data["speed"] = round(weather_data["speed"] * 3.6, 1)

    if "deg" in weather_data:
        weather_data["deg"] = convert_deg_to_direction(weather_data["deg"])

    if "gust" in weather_data:
        weather_data["gust"] = round(weather_data["gust"] * 3.6, 1)

    weather_data["description"] = data["weather"][0]["description"].title()

    return weather_data

def update_weather():
    zipcode = zipcode_entry.get()
    countrycode = country_entry.get()

    try:
        lat, lon, city = get_lat_lon(zipcode, countrycode, API_KEY)
        raw_data = fetch_weather(lat, lon, API_KEY)
        weather = preprocess_weather_data(raw_data)

        city_label.config(text=city)
        date_label.config(text=f"{weather['date']}")
        time_label.config(text=f"{weather['time']}")
        weather_details.config(text=f"""
{weather['description']}
Temperature: {weather['temp']}°C (Feels like {weather['feels_like']}°C)
Humidity: {weather['humidity']}%
Wind: {weather['speed']} km/h ({weather['deg']})
Pressure: {weather['pressure']} hPa
Sunrise: {weather['sunrise']}  |  Sunset: {weather['sunset']}
        """.strip())

    except Exception as e:
        messagebox.showerror("Weather Fetch Error", str(e))

# GUI Setup
root = tk.Tk()
root.title("Weather Dashboard")
root.attributes('-fullscreen', True)

# Load and set background image
bg_image = Image.open("9011110.jpg").resize((root.winfo_screenwidth(), root.winfo_screenheight()))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Fonts
font_big = font.Font(family="Helvetica", size=48, weight="bold")
font_medium = font.Font(family="Helvetica", size=28)
font_body = font.Font(family="Helvetica", size=20)

# Input frame
input_frame = tk.Frame(root, bg='#654cd1', bd=1)
tk.Label(input_frame, text="ZIP:", bg='#654cd1', font=font_body,fg="white").grid(row=0, column=0, padx=10, pady=10)
zipcode_entry = tk.Entry(input_frame, font=font_body)
zipcode_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(input_frame, text="Country:", bg='#654cd1', font=font_body,fg="white").grid(row=0, column=2, padx=10, pady=10)
country_entry = tk.Entry(input_frame, font=font_body)
country_entry.insert(0, "IN")
country_entry.grid(row=0, column=3, padx=10, pady=10)

search_button = tk.Button(input_frame, text="Search", font=font_body, command=update_weather)
search_button.grid(row=0, column=4, padx=10, pady=10)
input_frame.place(relx=0.5, rely=0.02, anchor='n')

# Main content frame with soft lavender background
main_frame = tk.Canvas(root, bg="#654cd1", highlightthickness=0)
main_frame.place(relx=0.5, rely=0.1, relwidth=0.9, relheight=0.85, anchor="n")

# Left panel
left_frame = tk.Frame(main_frame, bg="#654cd1")
left_frame.place(relx=0.02, rely=0.05, relwidth=0.45, relheight=0.9)

city_label = tk.Label(left_frame, text="", font=font_big, bg="#654cd1")
city_label.pack(pady=20)

date_label = tk.Label(left_frame, text="", font=font_medium, bg="#654cd1")
date_label.pack(pady=10)

time_label = tk.Label(left_frame, text="", font=font_medium, bg="#654cd1")
time_label.pack(pady=10)

# Right panel
right_frame = tk.Frame(main_frame, bg="#654cd1")
right_frame.place(relx=0.5, rely=0.05, relwidth=0.48, relheight=0.9)

weather_details = tk.Label(right_frame, text="", font=font_body, justify="left", anchor="nw", bg="#654cd1")
weather_details.pack(padx=20, pady=20, fill="both", expand=True,anchor="s")

root.mainloop()
