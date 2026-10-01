"""Attach water-structure point attributes to the Max Water Extent polygons.

Inputs (data/MaxWaterExtent/):
    MaxWaterExtent_polygons.shp  - water bodies, EPSG:32643
                                   (made by convert_max_water_extent.py)
    WaterStructurePoints.shp     - structure points, EPSG:4326
Output:
    MaxWaterExtent_with_points.shp - every water body with one point's data

Rules, per water body:
    1. Points on the water body (inside or on its edge): if several, take the
       point with the most filled fields.
    2. No point on it: take the nearest point (distance from the polygon edge,
       in metres). If several are equally nearest, take the one with the most
       filled fields.
    Remaining ties go to the lowest Sr_no so the result is reproducible.

A field counts as filled when it holds a real value: text that is not blank
or a placeholder ("0", "NA", "-", ...), and numbers greater than 0 (the
source uses 0 for missing Ar/Length/Depth). Sr_no, District, Latitude and
Longitude are filled on every point, so they are not counted.

Run from the backend folder:
    .venv-win\\Scripts\\python.exe scripts\\join_water_structure_points.py
"""

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import force_2d

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "MaxWaterExtent"
POLYGONS_PATH = DATA_DIR / "MaxWaterExtent_polygons.shp"
POINTS_PATH = DATA_DIR / "WaterStructurePoints.shp"
OUTPUT_PATH = DATA_DIR / "MaxWaterExtent_with_points.shp"

TEXT_FIELDS = ["Work_Name", "Panchayat", "Gram_Panch", "Village", "Activity", "Name"]
NUMBER_FIELDS = ["Ar", "Length", "Depth"]
PLACEHOLDERS = {"", "0", "NA", "N/A", "NULL", "NONE", "NIL", "-", "."}


def _fix_text(value):
    """Decode a string read as latin-1 back to proper Unicode.

    The .dbf is UTF-8 except one emoji stored as a CESU-8 surrogate pair,
    which strict UTF-8 rejects. Reading as latin-1 keeps every byte; this
    re-decodes them and joins any surrogate pair into its real character.
    """
    if not isinstance(value, str):
        return value
    raw = value.encode("latin-1").decode("utf-8", "surrogatepass")
    return raw.encode("utf-16", "surrogatepass").decode("utf-16")


def _load_points(crs) -> gpd.GeoDataFrame:
    points = gpd.read_file(POINTS_PATH, encoding="latin1")
    for col in points.columns.drop("geometry"):
        if points[col].dtype == object or pd.api.types.is_string_dtype(points[col]):
            points[col] = points[col].map(_fix_text)
    points.geometry = force_2d(points.geometry.values)  # Z is always 0
    points = points.to_crs(crs)

    text_filled = [
        ~points[c].fillna("").astype(str).str.strip().str.upper().isin(PLACEHOLDERS)
        for c in TEXT_FIELDS
    ]
    number_filled = [points[c].fillna(0) > 0 for c in NUMBER_FIELDS]
    points["n_filled"] = sum(s.astype(int) for s in text_filled + number_filled)
    return points


def _pick_best(matches: pd.DataFrame) -> pd.DataFrame:
    """Keep one row per polygon: most filled fields, then lowest Sr_no."""
    ordered = matches.sort_values(["id", "n_filled", "Sr_no"], ascending=[True, False, True])
    return ordered.drop_duplicates("id")


def main() -> None:
    polygons = gpd.read_file(POLYGONS_PATH)
    points = _load_points(polygons.crs)
    point_cols = [c for c in points.columns if c != "geometry"]

    # Rule 1: points on the water body.
    inside = gpd.sjoin(polygons, points, how="inner", predicate="intersects")
    n_inside = inside.groupby("id").size().rename("n_inside")
    inside_best = _pick_best(inside)[["id"] + point_cols]
    inside_best["match_type"] = "inside"
    inside_best["dist_m"] = 0.0

    # Rule 2: nearest point(s) for water bodies with no point on them.
    # sjoin_nearest returns every point tied at the minimum distance.
    empty = polygons[~polygons["id"].isin(inside_best["id"])]
    nearest = gpd.sjoin_nearest(empty, points, how="inner", distance_col="dist_m")
    nearest_best = _pick_best(nearest)[["id"] + point_cols + ["dist_m"]]
    nearest_best["match_type"] = "nearest"
    nearest_best["dist_m"] = nearest_best["dist_m"].round(2)

    chosen = pd.concat([inside_best, nearest_best], ignore_index=True)
    result = polygons.merge(chosen, on="id", how="left").merge(
        n_inside, on="id", how="left"
    )
    result["n_inside"] = result["n_inside"].fillna(0).astype(int)
    result = result[
        ["id", "area_m2"] + point_cols + ["match_type", "n_inside", "dist_m", "geometry"]
    ]
    result.to_file(OUTPUT_PATH, driver="ESRI Shapefile", encoding="UTF-8")

    counts = result["match_type"].value_counts()
    print(f"Wrote {len(result)} water bodies to {OUTPUT_PATH}")
    print(f"  inside : {counts.get('inside', 0)}")
    print(f"  nearest: {counts.get('nearest', 0)}")


if __name__ == "__main__":
    main()
