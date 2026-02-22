"""
Download Kerala waterways from OSM once and save locally.

After this runs, the enrichment script can calculate distances
from the local file instead of hitting the Overpass API per sample.

Usage:
    python scripts/download_kerala_waterways.py
"""

import requests
import json
from pathlib import Path
import time

OUTPUT_PATH = Path('data') / 'kerala_osm_waterways.geojson'
OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

# Kerala bounding box: south, west, north, east
KERALA_BBOX = "8.2,74.8,12.8,77.5"

def download_waterways():
    print("="*60)
    print("DOWNLOADING KERALA WATERWAYS FROM OSM")
    print("="*60)

    if OUTPUT_PATH.exists():
        print(f"\n✓ File already exists: {OUTPUT_PATH}")
        print("  Delete it to re-download. Skipping.")
        return True

    # Single Overpass query for all waterways in Kerala
    query = f"""
    [out:json][timeout:120];
    (
      way["waterway"="river"]({KERALA_BBOX});
      way["waterway"="stream"]({KERALA_BBOX});
      way["waterway"="canal"]({KERALA_BBOX});
    );
    out geom;
    """

    print(f"\nQuerying Overpass API for all Kerala waterways...")
    print(f"Bounding box: {KERALA_BBOX}")
    print("This may take up to 2 minutes (one-time download)...\n")

    try:
        response = requests.post(
            OVERPASS_URL,
            data={'data': query},
            timeout=180
        )

        if response.status_code != 200:
            print(f"❌ API error: {response.status_code}")
            return False

        data = response.json()
        elements = data.get('elements', [])

        print(f"✓ Downloaded {len(elements)} waterway segments")

        # Convert to GeoJSON format
        features = []
        for element in elements:
            if 'geometry' not in element:
                continue
            coords = [[node['lon'], node['lat']] for node in element['geometry']]
            if len(coords) < 2:
                continue
            features.append({
                "type": "Feature",
                "properties": {
                    "id": element.get('id'),
                    "waterway": element.get('tags', {}).get('waterway', 'unknown'),
                    "name": element.get('tags', {}).get('name', '')
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                }
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        with open(OUTPUT_PATH, 'w') as f:
            json.dump(geojson, f)

        size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
        print(f"✓ Saved {len(features)} waterways to: {OUTPUT_PATH}")
        print(f"  File size: {size_mb:.1f} MB")
        return True

    except requests.exceptions.Timeout:
        print("❌ Overpass API timed out. Try again in a few minutes.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = download_waterways()
    if success:
        print("\n✅ Ready to run enrichment script!")
    else:
        print("\n⚠  Download failed. Fix the error and try again.")
