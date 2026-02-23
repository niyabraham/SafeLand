"""
Extract training data points from Sentinel-1 flood footprints.

This script processes the combined multi-year flood footprint GeoJSON
and generates training data for the SafeLand ML model.

Usage:
    python scripts/extract_flood_training_data.py

Output:
    data/flood_training_data.csv
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random
import os

# Ensure we're in the SafeLand root directory
if not os.path.exists('data'):
    print("❌ Error: 'data' folder not found.")
    print("Please run this script from the SafeLand root directory:")
    print("  cd c:\\Users\\soura\\Desktop\\C\\SafeLand")
    print("  python scripts\\extract_flood_training_data.py")
    exit(1)

# Check if flood footprint file exists
footprint_path = 'data/kerala_flood_footprints.geojson'
if not os.path.exists(footprint_path):
    print(f"❌ Error: {footprint_path} not found.")
    print("\nPlease:")
    print("1. Download 'kerala_floods_2018_2019_2021_combined.geojson' from Google Drive")
    print("2. Rename it to 'kerala_flood_footprints.geojson'")
    print("3. Place it in the 'data' folder")
    exit(1)

print("Loading flood footprint data...")

# Load the combined flood footprint (all three years)
flood_areas = gpd.read_file(footprint_path)

print(f"✓ Loaded {len(flood_areas)} flood polygons")
print(f"✓ Flood years present: {flood_areas['flood_year'].unique()}")

# Sample random points inside flooded areas
print("\nExtracting training points...")
training_points = []
skipped_count = 0

for idx, polygon_row in flood_areas.iterrows():
    polygon = polygon_row.geometry
    flood_year = polygon_row['flood_year']
    
    # Skip invalid geometries
    if polygon is None or polygon.is_empty:
        skipped_count += 1
        continue
    
    # Sample 5 points per polygon
    for _ in range(5):
        # Get a random point inside the polygon
        minx, miny, maxx, maxy = polygon.bounds
        
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            # Generate random point within bounding box
            random_point = Point(
                random.uniform(minx, maxx),
                random.uniform(miny, maxy)
            )
            # Check if point is actually inside polygon
            if polygon.contains(random_point):
                break
            attempts += 1
        
        if attempts < 100:  # Successfully found point
            training_points.append({
                'latitude': random_point.y,
                'longitude': random_point.x,
                f'flooded_{flood_year}': 1
            })
    
    # Progress indicator
    if (idx + 1) % 100 == 0:
        print(f"  Processed {idx + 1}/{len(flood_areas)} polygons...")

print(f"✓ Extracted {len(training_points)} raw training points")
if skipped_count > 0:
    print(f"⚠ Skipped {skipped_count} invalid/empty geometries")

# Convert to DataFrame
df = pd.DataFrame(training_points)

print("\nGrouping by location to count flood occurrences...")

# Group by location to count total flood occurrences
# (Some locations may have been flooded multiple years)
df_grouped = df.groupby(['latitude', 'longitude']).agg({
    'flooded_2018': 'max',
    'flooded_2019': 'max', 
    'flooded_2021': 'max'
}).reset_index()

# Fill NaN with 0 (location not flooded that year)
df_grouped = df_grouped.fillna(0)

# Calculate total flood count
df_grouped['flood_history_count'] = (
    df_grouped['flooded_2018'] + 
    df_grouped['flooded_2019'] + 
    df_grouped['flooded_2021']
).astype(int)

# Assign risk level based on flood frequency
def assign_risk(row):
    if row['flood_history_count'] >= 2:
        return 'High'  # Flooded 2+ times
    elif row['flood_history_count'] == 1:
        return 'Medium'  # Flooded once
    else:
        return 'Low'  # Never flooded

df_grouped['risk'] = df_grouped.apply(assign_risk, axis=1)

# Save to CSV
output_path = 'data/flood_training_data.csv'
df_grouped.to_csv(output_path, index=False)

print(f"\n{'='*60}")
print("✅ EXTRACTION COMPLETE!")
print(f"{'='*60}")
print(f"\nExtracted {len(df_grouped)} unique training locations")
print(f"\nFlood frequency distribution:")
print(df_grouped['flood_history_count'].value_counts().sort_index())
print(f"\nRisk distribution:")
print(df_grouped['risk'].value_counts())
print(f"\nSaved to: {output_path}")
print(f"\n{'='*60}")
print("Next steps:")
print("1. Review the CSV file to verify data quality")
print("2. Combine with other data sources (KSDMA, OSM, etc.)")
print("3. Update ml/train_model.py with new features")
print("4. Retrain your ML model")
print(f"{'='*60}")
