"""
KSDMA (Kerala State Disaster Management Authority) flood zone processor.

Maps flood vulnerability zones for construction feasibility assessment.
"""

import json
import os
from typing import Optional, Dict
from shapely.geometry import Point, shape
from backend.config import Config
from backend.cache import cache_result

class KSDMAZones:
    """Process KSDMA flood vulnerability zones"""
    
    def __init__(self):
        self.zones_path = Config.KSDMA_ZONES_PATH
        self.zones_data = None
        self._load_zones()
        
    def _load_zones(self):
        """Load KSDMA flood zone data if available"""
        try:
            if os.path.exists(self.zones_path):
                with open(self.zones_path, 'r') as f:
                    self.zones_data = json.load(f)
                print("✓ KSDMA zones loaded successfully")
            else:
                print("⚠ KSDMA zones file not found. Using default vulnerability assessment.")
                self.zones_data = None
        except Exception as e:
            print(f"Error loading KSDMA zones: {e}")
            self.zones_data = None
    
    @cache_result(expiry_hours=720)  # Cache for 30 days
    def get_vulnerability_zone(self, lat: float, lon: float) -> int:
        """
        Get KSDMA flood vulnerability zone level.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Zone level (1=very low, 2=low, 3=moderate, 4=high, 5=very high)
        """
        if not self.zones_data:
            # Fallback: estimate based on elevation
            # This is a simplified model until actual KSDMA data is available
            from backend.data_sources.bhuvan_api import bhuvan_api
            elevation = bhuvan_api.get_elevation(lat, lon)
            
            if elevation < 10:
                return 5  # Very high risk (coastal/low-lying)
            elif elevation < 30:
                return 4  # High risk
            elif elevation < 60:
                return 3  # Moderate risk
            elif elevation < 100:
                return 2  # Low risk
            else:
                return 1  # Very low risk (highlands)
        
        try:
            # Check if point falls within any vulnerability zone polygon
            point = Point(lon, lat)
            
            for feature in self.zones_data.get('features', []):
                polygon = shape(feature['geometry'])
                if polygon.contains(point):
                    # Get zone level from properties
                    zone_level = feature['properties'].get('vulnerability', 3)
                    return int(zone_level)
            
            return 3  # Default moderate if not in any zone
            
        except Exception as e:
            print(f"Error checking vulnerability zone: {e}")
            return 3
    
    def is_in_flood_prone_area(self, lat: float, lon: float) -> bool:
        """
        Check if location is in a flood-prone area.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if in high/very high vulnerability zone
        """
        zone = self.get_vulnerability_zone(lat, lon)
        return zone >= 4
    
    def get_zone_metadata(self, lat: float, lon: float) -> Dict:
        """
        Get detailed metadata for vulnerability zone.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with zone information
        """
        zone_level = self.get_vulnerability_zone(lat, lon)
        
        zone_descriptions = {
            1: {"level": "Very Low", "color": "#00C853", "recommendation": "Suitable for construction"},
            2: {"level": "Low", "color": "#64DD17", "recommendation": "Generally suitable with standard precautions"},
            3: {"level": "Moderate", "color": "#FFD600", "recommendation": "Requires flood mitigation measures"},
            4: {"level": "High", "color": "#FF6D00", "recommendation": "Construction discouraged, extensive mitigation needed"},
            5: {"level": "Very High", "color": "#DD2C00", "recommendation": "Not recommended for construction"}
        }
        
        return {
            "zone_level": zone_level,
            **zone_descriptions.get(zone_level, zone_descriptions[3])
        }

# Singleton instance
ksdma_zones = KSDMAZones()
