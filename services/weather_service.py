import requests
from config import Config

class WeatherService:
    """Service class for interacting with Open-Meteo APIs."""
    
    # WMO Weather Interpretation Codes (WW) mapping
    WMO_CODE_MAP = {
        0: {"description": "Clear sky", "icon": "clear-day"},
        1: {"description": "Mainly clear", "icon": "partly-cloudy-day"},
        2: {"description": "Partly cloudy", "icon": "partly-cloudy-day"},
        3: {"description": "Overcast", "icon": "cloudy"},
        45: {"description": "Foggy", "icon": "fog"},
        48: {"description": "Depositing rime fog", "icon": "fog"},
        51: {"description": "Light drizzle", "icon": "drizzle"},
        53: {"description": "Moderate drizzle", "icon": "drizzle"},
        55: {"description": "Dense drizzle", "icon": "drizzle"},
        61: {"description": "Slight rain", "icon": "rain"},
        63: {"description": "Moderate rain", "icon": "rain"},
        65: {"description": "Heavy rain", "icon": "heavy-rain"},
        71: {"description": "Slight snowfall", "icon": "snow"},
        73: {"description": "Moderate snowfall", "icon": "snow"},
        75: {"description": "Heavy snowfall", "icon": "snow"},
        80: {"description": "Slight rain showers", "icon": "showers"},
        81: {"description": "Moderate rain showers", "icon": "showers"},
        82: {"description": "Violent rain showers", "icon": "showers"},
        95: {"description": "Thunderstorm", "icon": "thunderstorm"},
        96: {"description": "Thunderstorm with light hail", "icon": "thunderstorm"},
        99: {"description": "Thunderstorm with heavy hail", "icon": "thunderstorm"}
    }

    @classmethod
    def get_coordinates_by_city(cls, city_name):
        """Fetches latitude, longitude, country, and city name from Geocoding API."""
        if not city_name or not city_name.strip():
            raise ValueError("City name cannot be empty.")
            
        url = f"{Config.GEOCODING_BASE_URL}/search"
        params = {"name": city_name.strip(), "count": 1, "language": "en", "format": "json"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data.get("results"):
            return None
            
        result = data["results"][0]
        return {
            "name": result.get("name"),
            "country": result.get("country", ""),
            "country_code": result.get("country_code", ""),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "timezone": result.get("timezone", "UTC")
        }

    @classmethod
    def get_weather_by_coordinates(cls, lat, lon, location_name="Current Location", country=""):
        """Fetches current, hourly, and daily weather metrics using latitude and longitude."""
        url = f"{Config.OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "is_day", "precipitation", "weather_code", "surface_pressure",
                "wind_speed_10m"
            ],
            "hourly": ["temperature_2m", "weather_code", "precipitation_probability"],
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        code = current.get("weather_code", 0)
        condition_info = cls.WMO_CODE_MAP.get(code, {"description": "Unknown", "icon": "unknown"})
        
        return {
            "location": {
                "name": location_name,
                "country": country,
                "latitude": lat,
                "longitude": lon
            },
            "current": {
                "temperature": round(current.get("temperature_2m", 0)),
                "feels_like": round(current.get("apparent_temperature", 0)),
                "humidity": current.get("relative_humidity_2m", 0),
                "wind_speed": round(current.get("wind_speed_10m", 0), 1),
                "pressure": round(current.get("surface_pressure", 0)),
                "condition": condition_info["description"],
                "icon": condition_info["icon"],
                "is_day": current.get("is_day", 1)
            },
            "hourly": cls._parse_hourly(data.get("hourly", {})),
            "daily": cls._parse_daily(data.get("daily", {}))
        }

    @classmethod
    def _parse_hourly(cls, raw_hourly):
        """Parses raw hourly API payload into structured list (next 24 hours)."""
        times = raw_hourly.get("time", [])[:24]
        temps = raw_hourly.get("temperature_2m", [])[:24]
        codes = raw_hourly.get("weather_code", [])[:24]
        precip_probs = raw_hourly.get("precipitation_probability", [])[:24]
        
        hourly_list = []
        for i in range(len(times)):
            code = codes[i] if i < len(codes) else 0
            condition_info = cls.WMO_CODE_MAP.get(code, {"description": "Unknown", "icon": "unknown"})
            hourly_list.append({
                "time": times[i],
                "temp": round(temps[i]) if i < len(temps) else 0,
                "condition": condition_info["description"],
                "icon": condition_info["icon"],
                "precip_probability": precip_probs[i] if i < len(precip_probs) else 0
            })
        return hourly_list

    @classmethod
    def _parse_daily(cls, raw_daily):
        """Parses raw daily API payload into structured list (7-day forecast)."""
        dates = raw_daily.get("time", [])[:7]
        max_temps = raw_daily.get("temperature_2m_max", [])[:7]
        min_temps = raw_daily.get("temperature_2m_min", [])[:7]
        codes = raw_daily.get("weather_code", [])[:7]
        precip_max = raw_daily.get("precipitation_probability_max", [])[:7]
        
        daily_list = []
        for i in range(len(dates)):
            code = codes[i] if i < len(codes) else 0
            condition_info = cls.WMO_CODE_MAP.get(code, {"description": "Unknown", "icon": "unknown"})
            daily_list.append({
                "date": dates[i],
                "temp_max": round(max_temps[i]) if i < len(max_temps) else 0,
                "temp_min": round(min_temps[i]) if i < len(min_temps) else 0,
                "condition": condition_info["description"],
                "icon": condition_info["icon"],
                "precip_probability": precip_max[i] if i < len(precip_max) else 0
            })
        return daily_list