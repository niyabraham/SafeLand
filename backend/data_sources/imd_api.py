"""
India Meteorological Department (IMD) API interface for SafeLand.

Accesses historical and gridded rainfall data for construction feasibility assessment.
"""

import requests
from typing import Dict, List
from datetime import datetime, timedelta
from backend.config import Config
from backend.cache import cache_result

class IMDAPI:
    """Interface with India Meteorological Department for rainfall data"""
    
    def __init__(self):
        self.api_key = Config.IMD_API_KEY
        # Note: IMD doesn't have a public REST API yet
        # We'll use Open-Meteo's historical weather API as a proxy
        # and plan to integrate actual IMD data when available
        
    @cache_result(expiry_hours=168)  # Cache for 1 week
    def get_annual_rainfall(self, lat: float, lon: float, years: int = 10) -> float:
        """
        Get average annual rainfall over specified years.
        
        Args:
            lat: Latitude
            lon: Longitude
            years: Number of years to average (default 10)
            
        Returns:
            Average annual rainfall in mm
        """
        try:
            # Use Open-Meteo Archive API for historical data
            # Note: Replace with actual IMD API when available
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * years)
            
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "daily": "precipitation_sum",
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                daily_precip = data.get('daily', {}).get('precipitation_sum', [])
                
                if daily_precip:
                    # Calculate average annual rainfall
                    total_rainfall = sum(p for p in daily_precip if p is not None)
                    avg_annual = total_rainfall / years
                    return round(avg_annual, 2)
            
            return 2000.0  # Kerala average fallback
            
        except Exception as e:
            print(f"Error fetching annual rainfall: {e}")
            return 2000.0
    
    @cache_result(expiry_hours=168)
    def get_seasonal_rainfall(self, lat: float, lon: float, season: str = 'monsoon') -> float:
        """
        Get average seasonal rainfall.
        
        Args:
            lat: Latitude
            lon: Longitude
            season: 'monsoon' (Jun-Sep) or 'post-monsoon' (Oct-Dec)
            
        Returns:
            Average seasonal rainfall in mm
        """
        try:
            # Define season months
            if season == 'monsoon':
                months = [6, 7, 8, 9]  # June to September
            elif season == 'post-monsoon':
                months = [10, 11, 12]  # October to December
            else:
                months = [6, 7, 8, 9]  # Default to monsoon
            
            # Get last 5 years of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * 5)
            
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "daily": "precipitation_sum",
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                dates = data.get('daily', {}).get('time', [])
                precip = data.get('daily', {}).get('precipitation_sum', [])
                
                # Filter for season months
                seasonal_rainfall = []
                for date_str, rain in zip(dates, precip):
                    if rain is not None:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                        if date.month in months:
                            seasonal_rainfall.append(rain)
                
                if seasonal_rainfall:
                    # Average per season over 5 years
                    total = sum(seasonal_rainfall)
                    avg_seasonal = total / 5
                    return round(avg_seasonal, 2)
            
            return 1500.0 if season == 'monsoon' else 500.0
            
        except Exception as e:
            print(f"Error fetching seasonal rainfall: {e}")
            return 1500.0 if season == 'monsoon' else 500.0
    
    @cache_result(expiry_hours=168)
    def get_extreme_rainfall_events(self, lat: float, lon: float, years: int = 10) -> int:
        """
        Count extreme rainfall events (>100mm in a day).
        
        Args:
            lat: Latitude
            lon: Longitude
            years: Number of years to analyze
            
        Returns:
            Count of extreme rainfall events
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * years)
            
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "daily": "precipitation_sum",
                "timezone": "Asia/Kolkata"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                daily_precip = data.get('daily', {}).get('precipitation_sum', [])
                
                # Count days with >100mm rainfall
                extreme_events = sum(1 for p in daily_precip if p and p > 100)
                return extreme_events
            
            return 5  # Default moderate count
            
        except Exception as e:
            print(f"Error fetching extreme events: {e}")
            return 5

# Singleton instance
imd_api = IMDAPI()
