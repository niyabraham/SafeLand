import json
import time
from functools import wraps
from typing import Any, Callable

# In-memory cache store
cache_store = {}

def cache_result(expiry_hours: int = 24):
    """
    Decorator to cache API results to reduce external API calls.
    
    Args:
        expiry_hours: Number of hours before cache expires
        
    Usage:
        @cache_result(expiry_hours=24)
        def expensive_api_call(lat, lon):
            return fetch_data_from_api(lat, lon)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check if cached result exists and is still valid
            if cache_key in cache_store:
                data, timestamp = cache_store[cache_key]
                if time.time() - timestamp < expiry_hours * 3600:
                    print(f"✓ Cache hit for {func.__name__}")
                    return data
            
            # Call the actual function
            print(f"⟳ Fetching fresh data for {func.__name__}")
            result = func(*args, **kwargs)
            
            # Store in cache with timestamp
            cache_store[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

def clear_cache():
    """Clear all cached data"""
    global cache_store
    cache_store = {}
    print("Cache cleared")

def get_cache_stats():
    """Get cache statistics"""
    return {
        'total_entries': len(cache_store),
        'cache_keys': list(cache_store.keys())
    }
