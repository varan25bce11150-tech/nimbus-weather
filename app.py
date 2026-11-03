from flask import Flask, render_template, request, jsonify
from config import Config
from services.weather_service import WeatherService

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def index():
    """Renders the main Nimbus Weather Application dashboard."""
    return render_template("index.html")

@app.route("/api/weather", methods=["GET"])
def get_weather_by_city():
    """
    API endpoint: Fetch weather by city search term.
    Query param: ?city=London
    """
    city = request.args.get("city", "").strip()
    
    if not city:
        return jsonify({"error": "Please provide a city name."}), 400
        
    try:
        geo_data = WeatherService.get_coordinates_by_city(city)
        if not geo_data:
            return jsonify({"error": f"City '{city}' not found. Please check spelling."}), 444
            
        weather_data = WeatherService.get_weather_by_coordinates(
            lat=geo_data["latitude"],
            lon=geo_data["longitude"],
            location_name=geo_data["name"],
            country=geo_data["country"]
        )
        return jsonify(weather_data), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch weather data. Please try again later."}), 500

@app.route("/api/weather/coords", methods=["GET"])
def get_weather_by_coords():
    """
    API endpoint: Fetch weather using latitude and longitude coordinates.
    Query params: ?lat=51.5074&lon=-0.1278
    """
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing latitude and longitude coordinates."}), 400

    try:
        weather_data = WeatherService.get_weather_by_coordinates(
            lat=lat,
            lon=lon,
            location_name="Current Location",
            country=""
        )
        return jsonify(weather_data), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch location weather data."}), 500

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=5000)