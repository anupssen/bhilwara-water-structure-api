"""Elevation extraction from the Bhilwara DEM raster.

The raster (data/elevation/DEM_30m.tif) is opened once and reused. It is in
EPSG:32643 (WGS 84 / UTM Zone 43N) with a single int16 band and NoData = 32767
(confirmed by inspecting the file). An incoming EPSG:4326 lat/lon is first
transformed to the raster CRS, then the containing cell is sampled.
"""

from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform as transform_coords
from rasterio.windows import Window

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RASTER_PATH = DATA_DIR / "elevation" / "DEM_30m.tif"

# CRS of incoming coordinates.
INPUT_CRS = "EPSG:4326"

_ds = None


def _load() -> rasterio.io.DatasetReader:
    """Open the raster once and reuse the open handle."""
    global _ds
    if _ds is None:
        _ds = rasterio.open(RASTER_PATH)
    return _ds


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
    ds = _load()

    # Transform the point from EPSG:4326 into the raster CRS (EPSG:32643).
    xs, ys = transform_coords(INPUT_CRS, ds.crs, [longitude], [latitude])
    x, y = xs[0], ys[0]

    if np.isnan(x) or np.isnan(y):
        return None, "Coordinate falls outside the raster coverage"

    try:
        row, col = ds.index(x, y)
    except Exception:
        return None, "Coordinate falls outside the raster coverage"

    if row < 0 or col < 0 or row >= ds.height or col >= ds.width:
        return None, "Coordinate falls outside the raster coverage"

    # Read only the single cell to avoid loading the full band.
    value = ds.read(1, window=Window(col, row, 1, 1))[0, 0]

    if ds.nodata is not None and value == ds.nodata:
        return None, "Raster cell contains NoData"

    return float(value), None