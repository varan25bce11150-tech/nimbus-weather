import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base application configuration for Nimbus."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-fallback-secret-key")
    DEBUG = os.getenv("FLASK_ENV") == "development"
    
    # Open-Meteo REST API Endpoints
    OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"
    GEOCODING_BASE_URL = "https://geocoding-api.open-meteo.com/v1"