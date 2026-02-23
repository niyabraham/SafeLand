"""
Bhuvan (ISRO) API interface for SafeLand.

Accesses CartoDEM for elevation and terrain slope data.
"""

import requests
from typing import Tuple
from backend.config import Config
from backend.cache import cache_result

class BhuvanAPI:
    """Interface with ISRO's Bhuvan Geoportal for elevation data"""
    
    def __init__(self):
        self.wms_url = Config.BHUVAN_WMS_URL
        self.api_key = Config.BHUVAN_API_KEY
        
    @cache_result(expiry_hours=720)  # Cache for 30 days (elevation doesn't change)
    def get_elevation(self, lat: float, lon: float) -> float:
        """
        Fetch elevation at coordinates using Bhuvan CartoDEM.
        
        Note: Bhuvan WMS requires specific setup. For now, using Open-Meteo
        as fallback until Bhuvan API access is configured.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Elevation in meters
        """
        try:
            # TODO: Implement actual Bhuvan WMS query when API access is set up
            # For now, using Open-Meteo elevation API as it's more accessible
            
            url = "https://api.open-meteo.com/v1/elevation"
            params = {
                "latitude": lat,
                "longitude": lon
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                elevation = data.get('elevation', [0])[0]
                return float(elevation)
            else:
                return 50.0  # Default elevation
                
        except Exception as e:
            print(f"Error fetching elevation: {e}")
            return 50.0
    
    @cache_result(expiry_hours=720)
    def get_slope(self, lat: float, lon: float, radius: int = 500) -> float:
        """
        Calculate terrain slope at location.
        
        Uses elevation data from surrounding points to estimate slope.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Radius for slope calculation in meters
            
        Returns:
            Slope in degrees (0-90)
        """
        try:
            # Sample elevation at 4 points around the location
            offset = radius / 111000  # Convert meters to degrees (approx)
            
            elevations = {
                'center': self.get_elevation(lat, lon),
                'north': self.get_elevation(lat + offset, lon),
                'south': self.get_elevation(lat - offset, lon),
                'east': self.get_elevation(lat, lon + offset),
                'west': self.get_elevation(lat, lon - offset)
            }
            
            # Calculate slope in each direction
            north_south_slope = abs(elevations['north'] - elevations['south']) / (2 * radius)
            east_west_slope = abs(elevations['east'] - elevations['west']) / (2 * radius)
            
            # Take maximum slope
            max_slope = max(north_south_slope, east_west_slope)
            
            # Convert to degrees
            import math
            slope_degrees = math.degrees(math.atan(max_slope))
            
            return round(slope_degrees, 2)
            
        except Exception as e:
            print(f"Error calculating slope: {e}")
            return 5.0  # Default moderate slope

# Singleton instance
bhuvan_api = BhuvanAPI()
