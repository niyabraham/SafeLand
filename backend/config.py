import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration for SafeLand data sources and API keys"""
    
    # API Keys (set these in .env file)
    BHUVAN_API_KEY = os.getenv('BHUVAN_API_KEY', '')
    IMD_API_KEY = os.getenv('IMD_API_KEY', '')
    GOOGLE_EARTH_ENGINE_KEY = os.getenv('GEE_KEY', '')
    
    # Data Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
    
    KSDMA_ZONES_PATH = os.path.join(DATA_DIR, 'ksdma_flood_zones.geojson')
    OSM_KERALA_PATH = os.path.join(DATA_DIR, 'kerala_osm_waterways.geojson')
    SENTINEL_FOOTPRINTS_PATH = os.path.join(DATA_DIR, 'kerala_flood_footprints.geojson')
    
    # Cache Settings
    ENABLE_CACHE = True
    CACHE_EXPIRY_HOURS = 24
    
    # API Endpoints
    BHUVAN_WMS_URL = 'https://bhuvan-vec1.nrsc.gov.in/bhuvan/wms'
    OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'
    OVERPASS_API_URL = 'https://overpass-api.de/api/interpreter'
    
    # Kerala Bounding Box (for data filtering)
    KERALA_BBOX = {
        'min_lat': 8.2,
        'max_lat': 12.8,
        'min_lon': 74.8,
        'max_lon': 77.5
    }
