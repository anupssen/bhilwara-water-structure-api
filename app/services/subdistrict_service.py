"""Subdistrict boundary lookup using the Bhilwara subdistrict shapefile.

The shapefile (data/subdistricts/SubDistBoundary.shp) is loaded once into
memory and reused for every request. The subdistrict name comes from the
actual `Sub_dist` attribute column (confirmed by inspecting the .dbf),
and the file is reprojected to EPSG:4326 so that a point built with
Point(longitude, latitude) can be tested against the polygons directly.
"""

from pathlib import Path

import json
from pathlib import Path

import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point
from shapely.strtree import STRtree

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SHAPEFILE_PATH = DATA_DIR / "subdistricts" / "SubDistBoundary.shp"

# Attribute column holding the tehsil name (inspected from the real .dbf).
SUBDISTRICT_COLUMN = "Sub_dist"

# Attribute column holding the polygon area in km2 (inspected from the .dbf).
AREA_COLUMN = "Area"

# Target CRS used for point-in-polygon tests.
TARGET_CRS = "EPSG:4326"

_gdf_projected = None  # original CRS (EPSG:32643)
_gdf = None  # reprojected to EPSG:4326
_tree = None


def _load() -> None:
    """Load and reproject the shapefile once, then reuse it."""
    global _gdf_projected, _gdf, _tree
    if _gdf is not None:
        return

    projected = gpd.read_file(SHAPEFILE_PATH)
    _gdf_projected = projected

    # The source CRS is EPSG:32643 (WGS 84 / UTM Zone 43N); reproject to
    # EPSG:4326 so lat/lon points can be used directly.
    if projected.crs is not None and projected.crs != TARGET_CRS:
        gdf = projected.to_crs(TARGET_CRS)
    else:
        gdf = projected

    _gdf = gdf
    _tree = STRtree(list(gdf.geometry))


def find_subdistrict(latitude: float, longitude: float) -> tuple:
    """Return the subdistrict containing (latitude, longitude).

    Args:
        latitude: Latitude in degrees (EPSG:4326).
        longitude: Longitude in degrees (EPSG:4326).

    Returns:
        A tuple (subdistrict_name, message). subdistrict_name is the detected
        subdistrict or None when the point is outside every polygon.
        message is None on success and explains the None result otherwise.
    """
    _load()
    point = Point(longitude, latitude)

    for idx in _tree.query(point):
        polygon = _gdf.geometry.iloc[idx]
        if polygon.contains(point):
            name = _gdf[SUBDISTRICT_COLUMN].iloc[idx]
            return str(name), None

    return None, "Point lies outside all subdistrict polygons"


def list_subdistricts() -> list:
    """Return every subdistrict with a representative map point and area.

    The centroid is computed in the original projected CRS (EPSG:32643),
    where geometry math is meaningful, then transformed to EPSG:4326.
    """
    _load()

    source = _gdf_projected if _gdf_projected is not None else _gdf
    centroids = source.geometry.centroid

    if source.crs != TARGET_CRS:
        transformer = Transformer.from_crs(source.crs, TARGET_CRS, always_xy=True)
        lons, lats = transformer.transform(
            centroids.x.to_numpy(), centroids.y.to_numpy()
        )
    else:
        lons, lats = centroids.x.to_numpy(), centroids.y.to_numpy()

    records = []
    names = _gdf[SUBDISTRICT_COLUMN].to_numpy()
    areas = _gdf[AREA_COLUMN].to_numpy()

    for name, lat, lon, area in zip(names, lats, lons, areas):
        records.append(
            {
                "subdistrict": str(name),
                "latitude": round(float(lat), 5),
                "longitude": round(float(lon), 5),
                "area_km2": round(float(area), 1),
            }
        )

    return sorted(records, key=lambda rec: rec["subdistrict"])


def _to_geojson(gdf: "gpd.GeoDataFrame", column: str) -> dict:
    """Convert a GeoDataFrame to a GeoJSON FeatureCollection dict.

    Only the given attribute column is kept (as "name") so the payload stays
    small. The geometry is already in the GeoDataFrame's CRS, which is
    EPSG:4326 here, so coordinates are returned as longitude/latitude.
    """
    frame = gpd.GeoDataFrame(
        gdf[[column, "geometry"]].rename(columns={column: "name"}),
        geometry="geometry",
        crs=gdf.crs,
    )
    return json.loads(frame.to_json())


def get_subdistricts_geojson() -> dict:
    """Return every subdistrict polygon as a GeoJSON FeatureCollection.

    Coordinates are in EPSG:4326 (longitude/latitude), ready for the map.
    """
    _load()
    return _to_geojson(_gdf, SUBDISTRICT_COLUMN)


def get_subdistrict_geojson(subdistrict_name: str):
    """Return the GeoJSON Feature for a single named subdistrict.

    Returns None when the name does not match any subdistrict polygon.
    """
    _load()
    row = _gdf[_gdf[SUBDISTRICT_COLUMN].str.lower() == subdistrict_name.lower()]
    if row.empty:
        return None
    features = _to_geojson(row, SUBDISTRICT_COLUMN)["features"]
    return features[0] if features else None