import geopandas as gpd

print("Loading GeoJSON...")
gdf = gpd.read_file('data/kerala_flood_footprints.geojson')

print(f"Total rows: {len(gdf)}")
print(f"Columns: {gdf.columns.tolist()}")
print(f"\nGeometry info:")
print(f"  Non-null geometries: {gdf.geometry.notna().sum()}")
print(f"  Null geometries: {gdf.geometry.isna().sum()}")

print(f"\nFirst 5 rows:")
print(gdf.head())

print(f"\nGeometry types in first 20 rows:")
for i in range(min(20, len(gdf))):
    geom = gdf.iloc[i].geometry
    if geom is not None:
        print(f"  Row {i}: {geom.geom_type} - Valid: {geom.is_valid}")
    else:
        print(f"  Row {i}: None")
