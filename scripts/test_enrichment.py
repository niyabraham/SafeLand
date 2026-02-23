"""
Quick test of the batched enrichment approach on 100 samples.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pathlib import Path
from scripts.enrich_with_indian_sources import (
    fetch_elevations_batch, compute_slopes_from_elevations, compute_ksdma_zones,
    fetch_rainfall_batch, load_waterways, compute_river_distances,
    compute_drainage_density
)
import time

DATA_DIR = Path('data')
N = 100

print("="*60)
print("BATCH ENRICHMENT TEST (100 samples)")
print("="*60)

df = pd.read_csv(DATA_DIR / 'balanced_training_data.csv').head(N)
lats = df['latitude'].tolist()
lons = df['longitude'].tolist()
start = time.time()

print(f"\n[1/5] Elevations (batch)...")
elevs = fetch_elevations_batch(lats, lons)
print(f"  ✓ {min(elevs):.0f} - {max(elevs):.0f} m")

print(f"\n[2/5] Slopes (4-point sampling)...")
slopes = compute_slopes_from_elevations(lats, lons, elevs)
print(f"  ✓ {min(slopes):.1f} - {max(slopes):.1f} deg")

print(f"\n[3/5] KSDMA zones...")
zones = compute_ksdma_zones(elevs)
print(f"  ✓ Zones: {sorted(set(zones))}")

print(f"\n[4/5] Rainfall (batch)...")
rainfall, extreme = fetch_rainfall_batch(lats, lons, batch_size=10)
print(f"  ✓ Rainfall: {min(rainfall):.0f} - {max(rainfall):.0f} mm")
print(f"  ✓ Extreme events: {min(extreme)} - {max(extreme)}")

print(f"\n[5/5] River distances (local file)...")
nodes = load_waterways()
if nodes is not None:
    rdist = compute_river_distances(lats, lons, nodes)
    dens  = compute_drainage_density(lats, lons, nodes)
    print(f"  ✓ River dist: {min(rdist):.2f} - {max(rdist):.2f} km")
    print(f"  ✓ Drainage: {min(dens):.3f} - {max(dens):.3f}")

elapsed = time.time() - start
print(f"\n{'='*60}")
print(f"✅ Done! Time: {elapsed:.1f}s ({elapsed/60:.1f} min) for {N} samples")
print(f"   Projected full 12K: {elapsed/N*12000/60:.1f} minutes")
print(f"{'='*60}")
