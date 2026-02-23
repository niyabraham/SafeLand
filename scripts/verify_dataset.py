import pandas as pd

# Load the balanced dataset
df = pd.read_csv('data/balanced_training_data.csv')

print("="*60)
print("BALANCED TRAINING DATASET SUMMARY")
print("="*60)
print(f"\nTotal samples: {len(df)}")
print(f"\nRisk distribution:")
print(df['risk'].value_counts())
print(f"\nFlood frequency distribution:")
print(df['flood_history_count'].value_counts().sort_index())
print(f"\nFlooded by year:")
print(f"  2018: {df['flooded_2018'].sum():.0f} locations")
print(f"  2019: {df['flooded_2019'].sum():.0f} locations")
print(f"  2021: {df['flooded_2021'].sum():.0f} locations")
print(f"\nCoordinate ranges:")
print(f"  Latitude: {df['latitude'].min():.2f} to {df['latitude'].max():.2f}")
print(f"  Longitude: {df['longitude'].min():.2f} to {df['longitude'].max():.2f}")
print("="*60)
