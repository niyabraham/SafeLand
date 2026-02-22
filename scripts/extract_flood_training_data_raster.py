"""
Extract training data points from Sentinel-1 flood raster (GeoTIFF) files.

This script processes the individual year flood rasters extracted from Google Earth Engine
and generates training data for the SafeLand ML model.

Usage:
    python scripts/extract_flood_training_data_raster.py

Output:
    data/flood_training_data.csv
"""

import rasterio
import numpy as np
import pandas as pd
import os
from rasterio.windows import Window

# Configuration
DATA_DIR = 'data'
RASTERS = {
    '2018': 'kerala_flood_2018_raster.tif',
    '2019': 'kerala_flood_2019_raster.tif',
    '2021': 'kerala_flood_2021_raster.tif'
}
FREQUENCY_MAP = 'kerala_flood_frequency_map.tif'
OUTPUT_CSV = 'data/flood_training_data.csv'
SAMPLES_PER_FILE = 2000  # Number of points to sample per file

def extract_points_from_raster(raster_path, label_year, num_samples):
    """Extract sample points from a raster where flood value > 0"""
    points = []
    
    if not os.path.exists(raster_path):
        print(f"⚠ Warning: {raster_path} not found. Skipping.")
        return []
        
    print(f"Reading {raster_path}...")
    with rasterio.open(raster_path) as src:
        # Read the entire raster
        # For typical regional analysis (Kerala size), this is manageable in memory
        # Band 1 contains the data
        data = src.read(1)
        
        # Find indices where flood (value=1) occurred
        # Adding a small threshold just in case of float/byte conversions
        rows, cols = np.where(data > 0)
        
        total_flood_pixels = len(rows)
        if total_flood_pixels == 0:
            print(f"⚠ No flood pixels found in {label_year} data")
            return []
            
        print(f"  Found {total_flood_pixels} flood pixels in {label_year} data")
        
        # Randomly sample indices
        num_to_sample = min(num_samples, total_flood_pixels)
        if num_to_sample < num_samples:
            print(f"  Note: Taking all available {num_to_sample} points (requested {num_samples})")
            
        sampled_indices = np.random.choice(total_flood_pixels, num_to_sample, replace=False)
        
        sampled_rows = rows[sampled_indices]
        sampled_cols = cols[sampled_indices]
        
        # Convert to coordinates
        # transform maps pixel coordinates (row, col) to map coordinates (x, y)
        xs, ys = rasterio.transform.xy(src.transform, sampled_rows, sampled_cols)
        
        for x, y in zip(xs, ys):
            points.append({
                'latitude': y,
                'longitude': x,
                f'flooded_{label_year}': 1
            })
            
    return points

def extract_non_flood_samples(raster_paths, num_samples=2000):
    """
    Extract samples from areas that did NOT flood.
    This is tricky without a boundary polygon, but we can sample from the raster extent
    and check if values are 0 in all rasters.
    """
    # For now, let's keep it simple and focus on positive samples first.
    # Negative sampling logic:
    # 1. Get bounds of one raster
    # 2. Generate random points
    # 3. Check if value is 0 in all rasters
    pass

def main():
    if not os.path.exists(DATA_DIR):
        print(f"❌ Error: '{DATA_DIR}' folder not found.")
        print("Please ensure you run this from the project root.")
        return

    all_points = []
    
    print("="*60)
    print("EXTRACTING FLOOD TRAINING DATA FROM RASTERS")
    print("="*60)
    
    # Extract points for each year
    for year, filename in RASTERS.items():
        path = os.path.join(DATA_DIR, filename)
        print(f"\nProcessing {year} flood data...")
        points = extract_points_from_raster(path, year, SAMPLES_PER_FILE)
        all_points.extend(points)
        print(f"  Extracted {len(points)} points")
        
    if not all_points:
        print("\n❌ No training data extracted. Check your input files in 'data/' folder.")
        print("Expected files:")
        for f in RASTERS.values():
            print(f"  - {f}")
        return

    # Convert to DataFrame
    df = pd.DataFrame(all_points)
    
    # Consolidate by location (latitude, longitude)
    # We round coordinates to group effectively (raster pixels are aligned so this works)
    # 4 decimal places is ~11 meters, raster is ~10-30m usually
    df['lat_round'] = df['latitude'].round(4)
    df['lon_round'] = df['longitude'].round(4)
    
    print("\nConsolidating duplicates and calculating statistics...")
    
    # Fill missing years with 0
    years = list(RASTERS.keys())
    for year in years:
        col = f'flooded_{year}'
        if col not in df.columns:
            df[col] = 0
        df[col] = df[col].fillna(0)

    # Group by location matching
    # We aggregate by taking the max (1 if flooded in that year)
    agg_dict = {f'flooded_{year}': 'max' for year in years}
    # Keep original lat/lon (mean)
    agg_dict['latitude'] = 'mean'
    agg_dict['longitude'] = 'mean'
    
    df_grouped = df.groupby(['lat_round', 'lon_round']).agg(agg_dict).reset_index()
    
    # Calculate flood count
    df_grouped['flood_history_count'] = sum(df_grouped[f'flooded_{year}'] for year in years)
    
    # Assign risk
    def assign_risk(count):
        if count >= 2: return 'High'
        elif count == 1: return 'Medium'
        return 'Low'
        
    df_grouped['risk'] = df_grouped['flood_history_count'].apply(assign_risk)
    
    # Clean up columns
    final_cols = ['latitude', 'longitude'] + [f'flooded_{year}' for year in years] + ['flood_history_count', 'risk']
    df_final = df_grouped[final_cols]
    
    print(f"\n✅ Extracted {len(df_final)} unique flood locations")
    print(f"\nFlood frequency distribution:")
    print(df_final['flood_history_count'].value_counts().sort_index())
    
    print(f"\nRisk distribution:")
    print(df_final['risk'].value_counts())
    
    df_final.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved training data to {OUTPUT_CSV}")
    print("="*60)

if __name__ == "__main__":
    main()
