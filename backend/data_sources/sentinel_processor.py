"""
Sentinel-1 SAR flood history processor for SafeLand.

Analyzes historical flood events from satellite imagery.
"""

import json
import os
from typing import Dict
from shapely.geometry import Point, shape
from backend.config import Config
from backend.cache import cache_result

class SentinelProcessor:
    """Process Sentinel-1 SAR data for flood history"""
    
    def __init__(self):
        self.footprints_path = Config.SENTINEL_FOOTPRINTS_PATH
        self.flood_data = None
        self._load_flood_footprints()
        
    def _load_flood_footprints(self):
        """Load pre-processed flood footprints from Sentinel-1 analysis"""
        try:
            if os.path.exists(self.footprints_path):
                with open(self.footprints_path, 'r') as f:
                    self.flood_data = json.load(f)
                print("✓ Sentinel-1 flood footprints loaded successfully")
            else:
                print("⚠ Sentinel-1 footprints not found. Historical flood data unavailable.")
                self.flood_data = None
        except Exception as e:
            print(f"Error loading flood footprints: {e}")
            self.flood_data = None
    
    @cache_result(expiry_hours=720)  # Cache for 30 days
    def get_flood_history(self, lat: float, lon: float) -> int:
        """
        Check if location has flooded before (binary).
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            1 if flooded before, 0 if not
        """
        count = self.get_flood_frequency(lat, lon)
        return 1 if count > 0 else 0
    
    @cache_result(expiry_hours=720)
    def get_flood_frequency(self, lat: float, lon: float) -> int:
        """
        Count number of times location has flooded (2018-2024).
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Number of flood events (0-3+)
        """
        if not self.flood_data:
            # Fallback: estimate based on elevation and vulnerability
            from backend.data_sources.bhuvan_api import bhuvan_api
            from backend.data_sources.ksdma_zones import ksdma_zones
            
            elevation = bhuvan_api.get_elevation(lat, lon)
            zone = ksdma_zones.get_vulnerability_zone(lat, lon)
            
            # Simple heuristic until actual data is available
            if elevation < 10 and zone >= 4:
                return 3  # Likely flooded multiple times
            elif elevation < 30 and zone >= 3:
                return 1  # Likely flooded once
            else:
                return 0  # Unlikely to have flooded
        
        try:
            point = Point(lon, lat)
            flood_count = 0
            
            # Check each flood event (2018, 2019, 2021)
            for feature in self.flood_data.get('features', []):
                polygon = shape(feature['geometry'])
                if polygon.contains(point):
                    flood_count += 1
            
            return flood_count
            
        except Exception as e:
            print(f"Error checking flood history: {e}")
            return 0
    
    def get_flood_events_detail(self, lat: float, lon: float) -> Dict:
        """
        Get detailed information about flood events at location.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with flood event details
        """
        flood_count = self.get_flood_frequency(lat, lon)
        
        return {
            "total_events": flood_count,
            "flooded_2018": flood_count >= 1,  # Simplified
            "flooded_2019": flood_count >= 2,
            "flooded_2021": flood_count >= 3,
            "risk_category": "High" if flood_count >= 2 else "Medium" if flood_count == 1 else "Low"
        }

# Singleton instance
sentinel_processor = SentinelProcessor()
