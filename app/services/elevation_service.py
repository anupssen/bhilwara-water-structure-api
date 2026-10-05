"""Elevation extraction from the Bhilwara DEM.

The DEM (data/elevation/DEM_30m.tif) is EPSG:32643 (WGS 84 / UTM Zone 43N),
a single int16 band with NoData = 32767. It is read here from a NumPy export
of that band (DEM_30m.npy + DEM_30m.json, made by scripts/export_dem_array.py)
rather than with rasterio, whose Linux wheels need the system libexpat that
the Vercel Python runtime lacks. The array is memory-mapped, so a lookup
reads only the one cell it needs.

An incoming EPSG:4326 lat/lon is transformed to the DEM CRS and the
containing cell is sampled.
"""

import json
import math
from pathlib import Path

import numpy as np
from pyproj import Transformer

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ARRAY_PATH = DATA_DIR / "elevation" / "DEM_30m.npy"
META_PATH = DATA_DIR / "elevation" / "DEM_30m.json"

# CRS of incoming coordinates.
INPUT_CRS = "EPSG:4326"

_band = None
_meta = None
_transformer = None


def _load() -> None:
    """Memory-map the DEM once and reuse it."""
    global _band, _meta, _transformer
    if _band is None:
        _meta = json.loads(META_PATH.read_text())
        _band = np.load(ARRAY_PATH, mmap_mode="r")
        _transformer = Transformer.from_crs(INPUT_CRS, _meta["crs"], always_xy=True)


def get_elevation(latitude: float, longitude: float) -> tuple:
    """Return the elevation at (latitude, longitude) in metres.

    Args:
        latitude: Latitude in degrees (EPSG:4326).
        longitude: Longitude in degrees (EPSG:4326).

    Returns:
        A tuple (elevation_m, message). elevation_m is the sampled value or
        None when the point is outside the raster coverage or hits a NoData
        cell. message is None on success and explains the None result
        otherwise.
    """
    _load()

    # Transform the point from EPSG:4326 into the DEM CRS (EPSG:32643).
    x, y = _transformer.transform(longitude, latitude)
    if not (math.isfinite(x) and math.isfinite(y)):
        return None, "Coordinate falls outside the raster coverage"

    # North-up affine transform (no rotation): x = c + col*a, y = f + row*e.
    a, _, c, _, e, f = _meta["transform"]
    col = math.floor((x - c) / a)
    row = math.floor((y - f) / e)

    if row < 0 or col < 0 or row >= _meta["height"] or col >= _meta["width"]:
        return None, "Coordinate falls outside the raster coverage"

    value = _band[row, col]

    if _meta["nodata"] is not None and value == _meta["nodata"]:
        return None, "Raster cell contains NoData"

    return float(value), None
