"""Export the DEM GeoTIFF as a NumPy array plus its georeferencing.

The deployed API reads elevations from this array instead of the GeoTIFF:
rasterio's Linux wheels need the system library libexpat, which the
Vercel Python runtime does not have, so rasterio is a dev-only dependency.

Input:  data/elevation/DEM_30m.tif   (int16, EPSG:32643, NoData 32767)
Output: data/elevation/DEM_30m.npy   (the band, row-major, int16)
        data/elevation/DEM_30m.json  (crs, affine transform, nodata, size)

Run from the backend folder:
    .venv-win\\Scripts\\python.exe scripts\\export_dem_array.py
"""

import json
from pathlib import Path

import numpy as np
import rasterio

ELEVATION_DIR = Path(__file__).resolve().parents[1] / "data" / "elevation"
TIF_PATH = ELEVATION_DIR / "DEM_30m.tif"
NPY_PATH = ELEVATION_DIR / "DEM_30m.npy"
META_PATH = ELEVATION_DIR / "DEM_30m.json"


def main() -> None:
    with rasterio.open(TIF_PATH) as ds:
        if ds.transform.b != 0 or ds.transform.d != 0:
            raise ValueError("Rotated rasters are not supported")
        band = ds.read(1)
        meta = {
            "crs": ds.crs.to_string(),
            "transform": list(ds.transform)[:6],  # a, b, c, d, e, f
            "nodata": ds.nodata,
            "width": ds.width,
            "height": ds.height,
        }

    np.save(NPY_PATH, band)
    META_PATH.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"Wrote {NPY_PATH} ({band.nbytes / 1e6:.1f} MB) and {META_PATH}")


if __name__ == "__main__":
    main()
