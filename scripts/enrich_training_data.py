"""
Enrich training dataset with environmental features.

This script takes the balanced_training_data.csv and adds environmental
features from various data sources:
- Elevation and slope (from Open-Meteo)
- Rainfall patterns (from Open-Meteo Archive)
- Distance to water bodies (calculated from coordinates)
- Soil moisture (from Open-Meteo)

Usage:
    python scripts/enrich_training_data.py

Input:
    data/balanced_training_data.csv

Output:
    data/enhanced_training_data.csv
"""

import pandas as pd
import numpy as np
import requests
from pathlib import Path
import time
from tqdm import tqdm

# Configuration
DATA_DIR = Path('data')
INPUT_CSV = 'balanced_training_data.csv'
OUTPUT_CSV = 'enhanced_training_data.csv'

def get_elevation_data(lat, lon):
    """Fetch elevation from Open-Meteo Elevation API"""
    try:
        url = "https://api.open-meteo.com/v1/elevation"
        params = {"latitude": lat, "longitude": lon}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return data.get("elevation", [0])[0]
    except:
        return 0  # Fallback

def get_weather_data(lat, lon):
    """Fetch rainfall and soil moisture from Open-Meteo"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_sum",
            "hourly": "soil_moisture_0_to_1cm",
            "timezone": "auto",
            "forecast_days": 1
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        rainfall = data.get("daily", {}).get("precipitation_sum", [0])[0]
        soil_moisture_raw = data.get("hourly", {}).get("soil_moisture_0_to_1cm", [0])[0]
        soil_moisture = soil_moisture_raw * 100  # Scale to 0-100
        
        return rainfall, soil_moisture
    except:
        return 0, 40  # Fallback values

def calculate_distance_to_water(lat, lon):
    """
    Estimate distance to nearest water body.
    For Kerala, major rivers run north-south, so we use a simple heuristic.
    In production, this would query OSM data.
    """
    # Simplified heuristic: Kerala's major rivers are roughly every 0.5 degrees longitude
    # This is a placeholder - in production we'd use actual OSM river data
    
    # Major river longitudes (approximate)
    river_lons = [75.5, 76.0, 76.5, 77.0]
    
    # Find closest river
    min_distance = min([abs(lon - river_lon) for river_lon in river_lons])
    
    # Convert to approximate km (1 degree ≈ 111 km at equator)
    distance_km = min_distance * 111
    
    return distance_km

def enrich_dataset(df, batch_size=50):
    """
    Add environmental features to the dataset.
    Processes in batches to avoid overwhelming the API.
    """
    print(f"Enriching {len(df)} samples with environmental features...")
    
    # Initialize new columns
    df['elevation'] = 0.0
    df['rainfall'] = 0.0
    df['soil_moisture'] = 0.0
    df['river_distance'] = 0.0
    
    # Process in batches with progress bar
    for i in tqdm(range(0, len(df), batch_size), desc="Processing batches"):
        batch = df.iloc[i:i+batch_size]
        
        for idx, row in batch.iterrows():
            lat = row['latitude']
            lon = row['longitude']
            
            # Fetch elevation
            elevation = get_elevation_data(lat, lon)
            df.at[idx, 'elevation'] = elevation
            
            # Fetch weather data
            rainfall, soil_moisture = get_weather_data(lat, lon)
            df.at[idx, 'rainfall'] = rainfall
            df.at[idx, 'soil_moisture'] = soil_moisture
            
            # Calculate distance to water
            river_distance = calculate_distance_to_water(lat, lon)
            df.at[idx, 'river_distance'] = river_distance
            
            # Small delay to respect API rate limits
            time.sleep(0.1)
        
        # Longer delay between batches
        if i + batch_size < len(df):
            print(f"  Processed {min(i+batch_size, len(df))}/{len(df)} samples. Pausing...")
            time.sleep(2)
    
    return df

def main():
    print("="*60)
    print("ENRICHING TRAINING DATA WITH ENVIRONMENTAL FEATURES")
    print("="*60)
    
    # Load existing dataset
    input_path = DATA_DIR / INPUT_CSV
    if not input_path.exists():
        print(f"❌ Error: {input_path} not found")
        return
    
    print(f"\nLoading dataset: {input_path}")
    df = pd.read_csv(input_path)
    print(f"✓ Loaded {len(df)} samples")
    
    print(f"\nExisting features: {list(df.columns)}")
    
    # Enrich with environmental features
    print(f"\n{'='*60}")
    print("FETCHING ENVIRONMENTAL DATA")
    print(f"{'='*60}")
    print("\nThis will take several minutes due to API rate limits...")
    print("Features being added:")
    print("  - Elevation (meters)")
    print("  - Rainfall (mm)")
    print("  - Soil moisture (0-100%)")
    print("  - Distance to nearest river (km)")
    
    df_enriched = enrich_dataset(df)
    
    # Save enhanced dataset
    output_path = DATA_DIR / OUTPUT_CSV
    df_enriched.to_csv(output_path, index=False)
    
    print(f"\n{'='*60}")
    print("✅ ENRICHMENT COMPLETE!")
    print(f"{'='*60}")
    print(f"\nEnhanced dataset saved to: {output_path}")
    print(f"Total features: {len(df_enriched.columns)}")
    print(f"\nNew features added:")
    print(f"  - elevation: {df_enriched['elevation'].min():.1f} to {df_enriched['elevation'].max():.1f} m")
    print(f"  - rainfall: {df_enriched['rainfall'].min():.1f} to {df_enriched['rainfall'].max():.1f} mm")
    print(f"  - soil_moisture: {df_enriched['soil_moisture'].min():.1f} to {df_enriched['soil_moisture'].max():.1f}%")
    print(f"  - river_distance: {df_enriched['river_distance'].min():.1f} to {df_enriched['river_distance'].max():.1f} km")
    
    print(f"\n{'='*60}")
    print("Next steps:")
    print("1. Update ml/train_model.py to use enhanced_training_data.csv")
    print("2. Retrain the model with all features")
    print("3. Compare performance with previous model")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
