"""
OpenStreetMap (OSM) data processor for SafeLand.

Extracts river networks, water bodies, and calculates distances
for flood risk assessment and construction feasibility.
"""

import requests
from typing import Dict, List, Tuple
from shapely.geometry import Point, LineString, shape
from shapely.ops import nearest_points
import json
from backend.config import Config
from backend.cache import cache_result

class OSMProcessor:
    """Process OpenStreetMap data for water features"""
    
    def __init__(self):
        self.overpass_url = Config.OVERPASS_API_URL
        self.kerala_bbox = Config.KERALA_BBOX
        
    @cache_result(expiry_hours=168)  # Cache for 1 week (OSM data changes slowly)
    def get_nearest_river_distance(self, lat: float, lon: float) -> float:
        """
        Calculate distance to nearest river/waterway.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Distance to nearest river in kilometers
        """
        try:
            # Overpass query for waterways within 10km radius
            query = f"""
            [out:json];
            (
              way["waterway"="river"](around:10000,{lat},{lon});
              way["waterway"="stream"](around:10000,{lat},{lon});
            );
            out geom;
            """
            
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"OSM API error: {response.status_code}")
                return 5.0  # Default safe distance
            
            data = response.json()
            elements = data.get('elements', [])
            
            if not elements:
                return 10.0  # No rivers nearby
            
            # Create point for location
            point = Point(lon, lat)
            
            # Find nearest waterway
            min_distance = float('inf')
            for element in elements:
                if 'geometry' in element:
                    coords = [(node['lon'], node['lat']) for node in element['geometry']]
                    if len(coords) >= 2:
                        line = LineString(coords)
                        distance = point.distance(line) * 111  # Convert degrees to km (approx)
                        min_distance = min(min_distance, distance)
            
            return round(min_distance, 2) if min_distance != float('inf') else 10.0
            
        except Exception as e:
            print(f"Error fetching river distance: {e}")
            return 5.0  # Default fallback
    
    @cache_result(expiry_hours=168)
    def get_water_bodies_nearby(self, lat: float, lon: float, radius: int = 5000) -> float:
        """
        Find distance to nearest lake, reservoir, or water body.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters (default 5km)
            
        Returns:
            Distance to nearest water body in kilometers
        """
        try:
            query = f"""
            [out:json];
            (
              way["natural"="water"](around:{radius},{lat},{lon});
              way["water"="reservoir"](around:{radius},{lat},{lon});
              way["water"="lake"](around:{radius},{lat},{lon});
            );
            out geom;
            """
            
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code != 200:
                return 10.0
            
            data = response.json()
            elements = data.get('elements', [])
            
            if not elements:
                return 10.0
            
            point = Point(lon, lat)
            min_distance = float('inf')
            
            for element in elements:
                if 'geometry' in element:
                    coords = [(node['lon'], node['lat']) for node in element['geometry']]
                    if len(coords) >= 3:  # Polygon
                        poly = shape({'type': 'Polygon', 'coordinates': [coords]})
                        distance = point.distance(poly.exterior) * 111
                        min_distance = min(min_distance, distance)
            
            return round(min_distance, 2) if min_distance != float('inf') else 10.0
            
        except Exception as e:
            print(f"Error fetching water bodies: {e}")
            return 10.0
    
    @cache_result(expiry_hours=168)
    def get_drainage_density(self, lat: float, lon: float, radius: int = 1000) -> float:
        """
        Calculate drainage network density in area.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Analysis radius in meters
            
        Returns:
            Drainage density (0-1 scale, higher = more drainage)
        """
        try:
            query = f"""
            [out:json];
            (
              way["waterway"](around:{radius},{lat},{lon});
            );
            out geom;
            """
            
            response = requests.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code != 200:
                return 0.5
            
            data = response.json()
            elements = data.get('elements', [])
            
            # Calculate total length of waterways
            total_length = 0
            for element in elements:
                if 'geometry' in element:
                    coords = [(node['lon'], node['lat']) for node in element['geometry']]
                    if len(coords) >= 2:
                        line = LineString(coords)
                        total_length += line.length * 111  # Convert to km
            
            # Normalize to 0-1 scale (assume max 10km of waterways in 1km radius)
            density = min(total_length / 10.0, 1.0)
            return round(density, 2)
            
        except Exception as e:
            print(f"Error calculating drainage density: {e}")
            return 0.5

# Singleton instance
osm_processor = OSMProcessor()
