# plugins/weather.py

import os
import urllib.request
import urllib.parse
import json
from typing import Dict, Any

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register 'weather' (and alias 'forecast') commands.
    Expects in config.json under 'weather':
      apikey: your OWM API key
      units: 'metric' or 'imperial'
      default_city: (optional) city name if user omits one
    """
    speak = context["tts"]
    cfg = context["config"].get("weather", {})
    api_key = cfg.get("apikey", "")
    units = cfg.get("units", "metric")
    default_city = cfg.get("default_city", "")

    def weather_handler(args: Dict[str, Any]) -> str:
        # 1. Check API key
        if not api_key:
            return "Weather API key is not configured."

        # 2. Determine city: user param or default
        params = args.get("params", [])
        city = " ".join(params) if params else default_city
        if not city:
            return "Please provide a city name for the weather."

        # 3. Build request URL
        base = "http://api.openweathermap.org/data/2.5/weather"
        query = urllib.parse.urlencode({
            "q": city,
            "appid": api_key,
            "units": units,
            "lang": "en"
        })
        url = f"{base}?{query}"

        # 4. Fetch and parse JSON
        try:
            with urllib.request.urlopen(url) as resp:
                data = json.load(resp)
        except Exception as e:
            return f"Error fetching weather data: {e}"

        # 5. Handle API errors
        if data.get("cod") != 200:
            msg = data.get("message", "unknown error")
            return f"Could not get weather for '{city}': {msg.capitalize()}."

        # 6. Extract and format
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind = data.get("wind", {}).get("speed", "N/A")

        result = (
            f"Weather in {city}: {weather_desc}, "
            f"temp {temp}°, feels like {feels}°, "
            f"humidity {humidity}%, wind {wind} m/s."
        )
        return result

    return {
        "weather": weather_handler,
        "forecast": weather_handler,
    }