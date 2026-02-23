"""
Enrich training data with Indian data sources (no rainfall - added later).

Features added:
  - elevation        (Open-Meteo batched, fast)
  - slope            (4-point elevation sampling, batched)
  - ksdma_zone       (derived from elevation per KSDMA fallback logic)
  - river_distance   (local OSM waterways file, vectorized)
  - drainage_density (local OSM waterways file, vectorized)

Rainfall (IMD) will be added in a future update once IMD gridded
data is downloaded or rate limits are resolved.

Usage:
    python scripts/enrich_with_indian_sources.py

Input:
    data/balanced_training_data.csv  (12,000 samples, 7 features)

Output:
    data/enhanced_training_data.csv  (12,000 samples, 12 features)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import requests
import json
import math
from pathlib import Path
from tqdm import tqdm
import time

DATA_DIR       = Path('data')
INPUT_CSV      = 'balanced_training_data.csv'
OUTPUT_CSV     = 'enhanced_training_data.csv'
WATERWAYS_PATH = DATA_DIR / 'kerala_osm_waterways.geojson'

# ──────────────────────────────────────────────────────────────────
# 1.  ELEVATION  (Open-Meteo, batched 1000 coords per call)
# ──────────────────────────────────────────────────────────────────
def fetch_elevations_batch(lats, lons, batch_size=100):
    """Fetch elevation in batches of 100 using JSON POST to avoid URL length limits."""
    elevations = [50.0] * len(lats)
    url = "https://api.open-meteo.com/v1/elevation"
    for i in tqdm(range(0, len(lats), batch_size), desc="  Elevation", unit="batch"):
        bl, blo = lats[i:i+batch_size], lons[i:i+batch_size]
        try:
            r = requests.get(url, params={
                "latitude":  bl,
                "longitude": blo
            }, timeout=30)
            if r.status_code == 200:
                for j, v in enumerate(r.json().get("elevation", [])):
                    if v is not None:
                        elevations[i+j] = float(v)
            elif r.status_code == 414:
                # Fallback: fetch one at a time
                for j, (la, lo) in enumerate(zip(bl, blo)):
                    try:
                        r2 = requests.get(url, params={"latitude": la, "longitude": lo}, timeout=10)
                        if r2.status_code == 200:
                            v = r2.json().get("elevation", [50.0])[0]
                            elevations[i+j] = float(v) if v else 50.0
                    except:
                        pass
            else:
                print(f"  Elev batch HTTP {r.status_code}")
        except Exception as e:
            print(f"  Elev batch error: {e}")
        time.sleep(0.2)
    return elevations

# ──────────────────────────────────────────────────────────────────
# 2.  SLOPE  (4 batched elevation lookups per point, vectorized)
# ──────────────────────────────────────────────────────────────────
def compute_slopes(lats, lons):
    offset = 0.005          # ~500 m
    dist_m = offset * 111000
    print("  Fetching N/S elevations...")
    n_elevs = fetch_elevations_batch([la+offset for la in lats], lons)
    s_elevs = fetch_elevations_batch([la-offset for la in lats], lons)
    print("  Fetching E/W elevations...")
    e_elevs = fetch_elevations_batch(lats, [lo+offset for lo in lons])
    w_elevs = fetch_elevations_batch(lats, [lo-offset for lo in lons])
    slopes = []
    for i in range(len(lats)):
        ns = abs(n_elevs[i] - s_elevs[i]) / (2 * dist_m)
        ew = abs(e_elevs[i] - w_elevs[i]) / (2 * dist_m)
        slopes.append(round(math.degrees(math.atan(max(ns, ew))), 2))
    return slopes

# ──────────────────────────────────────────────────────────────────
# 3.  KSDMA ZONE  (elevation-based, matches ksdma_zones.py fallback)
# ──────────────────────────────────────────────────────────────────
def compute_ksdma_zones(elevations):
    def zone(e):
        if   e < 10:  return 5
        elif e < 30:  return 4
        elif e < 60:  return 3
        elif e < 100: return 2
        else:         return 1
    return [zone(e) for e in elevations]

# ──────────────────────────────────────────────────────────────────
# 4.  RIVER DISTANCE + DRAINAGE  (local OSM file, NumPy vectorized)
# ──────────────────────────────────────────────────────────────────
def load_waterway_nodes():
    if not WATERWAYS_PATH.exists():
        print(f"❌ {WATERWAYS_PATH} not found!")
        print("   Run first: python scripts/download_kerala_waterways.py")
        return None
    print("  Loading local waterways file...")
    with open(WATERWAYS_PATH) as f:
        data = json.load(f)
    coords = []
    for feat in data.get('features', []):
        coords.extend(feat.get('geometry', {}).get('coordinates', []))
    arr = np.array(coords)           # (N, 2)  →  [lon, lat]
    print(f"  ✓ {len(arr):,} waterway nodes loaded")
    return arr

def _haversine_km(lat, lon, nodes):
    """Vectorised haversine from one point to many [lon, lat] nodes."""
    dlat = np.radians(nodes[:, 1] - lat)
    dlon = np.radians(nodes[:, 0] - lon)
    a    = np.sin(dlat/2)**2 + math.cos(math.radians(lat)) * np.cos(np.radians(nodes[:, 1])) * np.sin(dlon/2)**2
    return 6371 * 2 * np.arcsin(np.sqrt(a))

def compute_river_distances(lats, lons, nodes):
    wlat, wlon = nodes[:, 1], nodes[:, 0]
    dists = []
    for lat, lon in tqdm(zip(lats, lons), total=len(lats), desc="  River dist"):
        mask   = (np.abs(wlat - lat) < 0.5) & (np.abs(wlon - lon) < 0.5)
        nearby = nodes[mask]
        if len(nearby) == 0:
            dists.append(10.0)
        else:
            dists.append(round(float(np.min(_haversine_km(lat, lon, nearby))), 3))
    return dists

def compute_drainage_density(lats, lons, nodes, radius_km=1.0):
    wlat, wlon = nodes[:, 1], nodes[:, 0]
    densities = []
    deg = radius_km / 111.0
    for lat, lon in tqdm(zip(lats, lons), total=len(lats), desc="  Drainage  "):
        mask   = (np.abs(wlat - lat) < deg * 1.5) & (np.abs(wlon - lon) < deg * 1.5)
        nearby = nodes[mask]
        if len(nearby) == 0:
            densities.append(0.0)
        else:
            cnt = int(np.sum(_haversine_km(lat, lon, nearby) <= radius_km))
            densities.append(round(min(cnt / 100.0, 1.0), 3))
    return densities

# ──────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("ENRICHING TRAINING DATA (no rainfall – added later)")
    print("=" * 65)

    df = pd.read_csv(DATA_DIR / INPUT_CSV)
    print(f"\n✓ Loaded {len(df):,} samples with {len(df.columns)} features")

    lats = df['latitude'].tolist()
    lons = df['longitude'].tolist()
    t0   = time.time()

    # 1. Elevation
    print("\n[1/4] Elevation (batched API)...")
    elevations = fetch_elevations_batch(lats, lons)
    print(f"  ✓ {min(elevations):.0f} – {max(elevations):.0f} m")

    # 2. Slope
    print("\n[2/4] Slope (4-point batch sampling)...")
    slopes = compute_slopes(lats, lons)
    print(f"  ✓ {min(slopes):.1f} – {max(slopes):.1f}°")

    # 3. KSDMA
    print("\n[3/4] KSDMA vulnerability zones...")
    ksdma = compute_ksdma_zones(elevations)
    dist  = pd.Series(ksdma).value_counts().sort_index().to_dict()
    print(f"  ✓ Distribution: {dist}")

    # 4. OSM river features
    print("\n[4/4] River distances & drainage (local OSM file)...")
    nodes = load_waterway_nodes()
    if nodes is None:
        return
    river_dist = compute_river_distances(lats, lons, nodes)
    drainage   = compute_drainage_density(lats, lons, nodes)
    print(f"  ✓ River dist: {min(river_dist):.2f} – {max(river_dist):.2f} km")
    print(f"  ✓ Drainage:   {min(drainage):.3f} – {max(drainage):.3f}")

    # Combine & save
    df['ksdma_zone']      = ksdma
    df['elevation']       = elevations
    df['slope']           = slopes
    df['river_distance']  = river_dist
    df['drainage_density']= drainage

    out = DATA_DIR / OUTPUT_CSV
    df.to_csv(out, index=False)

    elapsed = time.time() - t0
    print(f"\n{'='*65}")
    print("✅  DONE!")
    print(f"    Time    : {elapsed/60:.1f} min")
    print(f"    Rows    : {len(df):,}")
    print(f"    Features: {len(df.columns)}  (was {len(df.columns)-5})")
    print(f"    Saved   : {out}")
    print(f"\n    TODO (later): add annual_rainfall, extreme_rain_events")
    print(f"    Next    : python ml/train_model.py")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
