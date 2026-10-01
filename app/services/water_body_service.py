"""Max Water Extent water bodies, each carrying its matched structure point.

The shapefile (data/MaxWaterExtent/MaxWaterExtent_with_points.shp) is built
by scripts/convert_max_water_extent.py and scripts/join_water_structure_points.py.
It is in EPSG:32643; it is loaded once, reprojected to EPSG:4326 and reused,
since the file is static.

The map gets only the shapes (GeoJSON); the details of a water body come
from find_water_body() through the recommendation endpoint.
"""

import json
import math
from pathlib import Path

import geopandas as gpd
import shapely
from shapely.geometry import Point
from shapely.strtree import STRtree

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SHAPEFILE_PATH = DATA_DIR / "MaxWaterExtent" / "MaxWaterExtent_with_points.shp"

TARGET_CRS = "EPSG:4326"

# Snap map coordinates to 1e-6 degrees (~0.1 m), far below the ~26 m pixel size.
COORD_PRECISION = 1e-6

_gdf = None
_tree = None
_geojson = None


def _load() -> None:
    """Load and reproject the shapefile once, then reuse it."""
    global _gdf, _tree
    if _gdf is None:
        _gdf = gpd.read_file(SHAPEFILE_PATH).to_crs(TARGET_CRS)
        _tree = STRtree(list(_gdf.geometry))


def get_water_bodies_geojson() -> dict:
    """Return every water body shape as a GeoJSON FeatureCollection (EPSG:4326)."""
    global _geojson
    if _geojson is None:
        _load()
        shapes = gpd.GeoDataFrame(
            {"id": _gdf["id"]},
            geometry=shapely.set_precision(_gdf.geometry.values, COORD_PRECISION),
            crs=_gdf.crs,
        )
        _geojson = json.loads(shapes.to_json(drop_id=True))
    return _geojson


def _text(value):
    """Shapefile text, or None when missing or blank."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    value = str(value).strip()
    return value or None


def _measure(value):
    """Ar/Length/Depth, or None when not recorded (the source uses 0)."""
    return float(value) if value and value > 0 else None


def find_water_body(latitude: float, longitude: float):
    """Return the details of the water body at (latitude, longitude), or None.

    A point on a water body's edge counts as on it.
    """
    _load()
    point = Point(longitude, latitude)
    for idx in _tree.query(point, predicate="intersects"):
        row = _gdf.iloc[idx]
        return {
            "id": int(row["id"]),
            "area_m2": float(row["area_m2"]),
            "sr_no": int(row["Sr_no"]),
            "work_name": _text(row["Work_Name"]),
            "activity": _text(row["Activity"]),
            "village": _text(row["Village"]),
            "gram_panchayat": _text(row["Gram_Panch"]),
            "panchayat": _text(row["Panchayat"]),
            "ar": _measure(row["Ar"]),
            "length": _measure(row["Length"]),
            "depth": _measure(row["Depth"]),
            "match_type": row["match_type"],
            "points_on_body": int(row["n_inside"]),
            "point_distance_m": float(row["dist_m"]),
        }
    return None
