"""
Add non-flooded (Low risk) samples to the training dataset.

This script samples random points within Kerala's bounding box and checks
if they flooded in any of the three years (2018, 2019, 2021). Points that
never flooded are added as "Low" risk samples to balance the dataset.

Usage:
    python scripts/add_non_flooded_samples.py

Input:
    - data/kerala_flood_2018_raster.tif
    - data/kerala_flood_2019_raster.tif
    - data/kerala_flood_2021_raster.tif
    - data/flood_training_data.csv (existing flood data)

Output:
    - data/balanced_training_data.csv (flood + non-flood samples)
"""

import rasterio
import numpy as np
import pandas as pd
import random
from pathlib import Path

# Configuration
DATA_DIR = Path('data')
RASTERS = {
    '2018': 'kerala_flood_2018_raster.tif',
    '2019': 'kerala_flood_2019_raster.tif',
    '2021': 'kerala_flood_2021_raster.tif'
}
EXISTING_DATA = 'flood_training_data.csv'
OUTPUT_CSV = 'balanced_training_data.csv'
NON_FLOOD_SAMPLES = 6000  # Match the number of flood samples

def load_raster_data():
    """Load all three flood rasters into memory"""
    rasters = {}
    transforms = {}
    
    for year, filename in RASTERS.items():
        path = DATA_DIR / filename
        if not path.exists():
            print(f"❌ Error: {path} not found")
            return None, None
            
        with rasterio.open(path) as src:
            rasters[year] = src.read(1)
            transforms[year] = src.transform
            
    print(f"✓ Loaded {len(rasters)} flood rasters")
    return rasters, transforms

def point_to_pixel(lon, lat, transform):
    """Convert geographic coordinates to pixel coordinates"""
    # Inverse transform: (lon, lat) -> (col, row)
    col, row = ~transform * (lon, lat)
    return int(row), int(col)

def is_flooded(lon, lat, rasters, transform):
    """Check if a point flooded in any year"""
    for year, raster in rasters.items():
        try:
            row, col = point_to_pixel(lon, lat, transform)
            
            # Check bounds
            if 0 <= row < raster.shape[0] and 0 <= col < raster.shape[1]:
                if raster[row, col] > 0:
                    return True  # Flooded in this year
            else:
                # Point outside raster bounds - skip it
                return None
        except Exception as e:
            return None
            
    return False  # Not flooded in any year

def generate_non_flood_samples(rasters, transform, num_samples):
    """Generate random points that did NOT flood"""
    # Get Kerala bounding box from one of the rasters
    sample_raster = list(rasters.values())[0]
    height, width = sample_raster.shape
    
    # Get geographic bounds
    with rasterio.open(DATA_DIR / RASTERS['2018']) as src:
        bounds = src.bounds
        
    print(f"\nKerala bounding box:")
    print(f"  Longitude: {bounds.left:.2f} to {bounds.right:.2f}")
    print(f"  Latitude: {bounds.bottom:.2f} to {bounds.top:.2f}")
    
    non_flood_points = []
    attempts = 0
    max_attempts = num_samples * 50  # Try up to 50x the target
    
    print(f"\nGenerating {num_samples} non-flooded samples...")
    
    while len(non_flood_points) < num_samples and attempts < max_attempts:
        # Random point within bounds
        lon = random.uniform(bounds.left, bounds.right)
        lat = random.uniform(bounds.bottom, bounds.top)
        
        # Check if it flooded
        flood_status = is_flooded(lon, lat, rasters, transform)
        
        if flood_status is False:  # Explicitly not flooded
            non_flood_points.append({
                'latitude': lat,
                'longitude': lon,
                'flooded_2018': 0,
                'flooded_2019': 0,
                'flooded_2021': 0,
                'flood_history_count': 0,
                'risk': 'Low'
            })
            
            # Progress indicator
            if len(non_flood_points) % 500 == 0:
                print(f"  Generated {len(non_flood_points)}/{num_samples} samples...")
        
        attempts += 1
        
    print(f"✓ Generated {len(non_flood_points)} non-flooded samples")
    print(f"  (Took {attempts} attempts, {attempts/len(non_flood_points):.1f}x sampling rate)")
    
    return non_flood_points

def main():
    print("="*60)
    print("ADDING NON-FLOODED SAMPLES TO TRAINING DATA")
    print("="*60)
    
    # Load existing flood data
    existing_path = DATA_DIR / EXISTING_DATA
    if not existing_path.exists():
        print(f"❌ Error: {existing_path} not found")
        print("Please run extract_flood_training_data_raster.py first")
        return
        
    df_flood = pd.read_csv(existing_path)
    print(f"\n✓ Loaded {len(df_flood)} existing flood samples")
    print(f"  Risk distribution: {df_flood['risk'].value_counts().to_dict()}")
    
    # Load raster data
    rasters, transforms = load_raster_data()
    if rasters is None:
        return
        
    # Use the same transform for all (they should be aligned)
    transform = transforms['2018']
    
    # Generate non-flooded samples
    non_flood_samples = generate_non_flood_samples(rasters, transform, NON_FLOOD_SAMPLES)
    
    if not non_flood_samples:
        print("❌ Failed to generate non-flooded samples")
        return
        
    # Combine datasets
    df_non_flood = pd.DataFrame(non_flood_samples)
    df_combined = pd.concat([df_flood, df_non_flood], ignore_index=True)
    
    # Shuffle the dataset
    df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    output_path = DATA_DIR / OUTPUT_CSV
    df_combined.to_csv(output_path, index=False)
    
    print(f"\n{'='*60}")
    print("✅ BALANCED DATASET CREATED!")
    print(f"{'='*60}")
    print(f"\nTotal samples: {len(df_combined)}")
    print(f"\nRisk distribution:")
    print(df_combined['risk'].value_counts())
    print(f"\nFlood frequency distribution:")
    print(df_combined['flood_history_count'].value_counts().sort_index())
    print(f"\nSaved to: {output_path}")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Review the balanced dataset")
    print("2. Add additional features (elevation, rainfall, etc.)")
    print("3. Update ml/train_model.py to use the new dataset")
    print("4. Retrain your model")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
