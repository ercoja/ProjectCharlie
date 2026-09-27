import json
import os
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, render_template, request

app = Flask(__name__)

WEATHER_ICONS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌦️",
    53: "🌦️",
    55: "🌧️",
    56: "🌧️",
    57: "🌧️",
    61: "🌦️",
    63: "🌧️",
    65: "🌧️",
    66: "🌧️",
    67: "🌧️",
    71: "🌨️",
    73: "🌨️",
    75: "🌨️",
    77: "❄️",
    80: "🌦️",
    81: "🌧️",
    82: "🌧️",
    85: "🌨️",
    86: "🌨️",
    95: "⛈️",
    96: "⛈️",
    99: "⛈️",
}

WEATHER_LABELS = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Heavy thunderstorm with hail",
}


def fetch_json(url):
    req = Request(url, headers={"User-Agent": "ProjectCharlie/1.0"})
    with urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


@app.route("/", methods=["GET", "POST"])
def home():
    city = ""
    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."
        else:
            try:
                geo = fetch_json(
                    f"https://geocoding-api.open-meteo.com/v1/search?name={quote(city)}&count=1&language=en&format=json"
                )
                results = geo.get("results") or []

                if not results:
                    error = f"No weather data found for '{city}'."
                else:
                    place = results[0]
                    latitude = place["latitude"]
                    longitude = place["longitude"]
                    city_name = place.get("name", city)
                    country = place.get("country", "")

                    forecast = fetch_json(
                        "https://api.open-meteo.com/v1/forecast?"
                        f"latitude={latitude}&longitude={longitude}"
                        "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m"
                        "&timezone=auto"
                    )

                    current = forecast.get("current", {})
                    weather_code = current.get("weather_code", 0)
                    weather = {
                        "city": f"{city_name}, {country}".strip(", "),
                        "temperature": current.get("temperature_2m"),
                        "feels_like": current.get("apparent_temperature"),
                        "humidity": current.get("relative_humidity_2m"),
                        "wind": current.get("wind_speed_10m"),
                        "icon": WEATHER_ICONS.get(weather_code, "🌤️"),
                        "description": WEATHER_LABELS.get(weather_code, "Clear sky"),
                    }
            except Exception:
                error = "Unable to load weather right now. Please try again."

    return render_template("index.html", city=city, weather=weather, error=error)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
