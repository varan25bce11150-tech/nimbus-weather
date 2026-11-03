import unittest
from app import app
from services.weather_service import WeatherService

class TestNimbusApplication(unittest.TestCase):

    def setUp(self):
        """Set up Flask test client before each test."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    # --- Unit Tests: Service Layer ---
    def test_get_coordinates_valid_city(self):
        """Test retrieving valid coordinates for a known city."""
        result = WeatherService.get_coordinates_by_city("Tokyo")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Tokyo")
        self.assertIn("latitude", result)
        self.assertIn("longitude", result)

    def test_get_coordinates_invalid_city(self):
        """Test handling for a non-existent city name."""
        result = WeatherService.get_coordinates_by_city("XYZNonExistentCity999")
        self.assertIsNone(result)

    def test_get_weather_by_coordinates(self):
        """Test retrieving structured weather metrics via coordinates."""
        lat, lon = 35.6762, 139.6503 # Tokyo coordinates
        data = WeatherService.get_weather_by_coordinates(lat, lon, location_name="Tokyo", country="Japan")
        
        self.assertEqual(data["location"]["name"], "Tokyo")
        self.assertIn("temperature", data["current"])
        self.assertIn("humidity", data["current"])
        self.assertTrue(len(data["hourly"]) > 0)
        self.assertTrue(len(data["daily"]) > 0)

    # --- Integration Tests: Flask API Routes ---
    def test_index_route(self):
        """Test main HTML dashboard route loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Nimbus', response.data)

    def test_api_weather_city_success(self):
        """Test /api/weather endpoint with valid city."""
        response = self.client.get('/api/weather?city=Paris')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['location']['name'], 'Paris')

    def test_api_weather_city_missing_param(self):
        """Test /api/weather endpoint with missing city parameter."""
        response = self.client.get('/api/weather?city=')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_api_weather_coords_success(self):
        """Test /api/weather/coords endpoint with valid lat/lon."""
        response = self.client.get('/api/weather/coords?lat=48.8566&lon=2.3522')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('temperature', data['current'])

    def test_api_weather_coords_invalid_params(self):
        """Test /api/weather/coords endpoint with invalid coordinates."""
        response = self.client.get('/api/weather/coords?lat=invalid&lon=invalid')
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()