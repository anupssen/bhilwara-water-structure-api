"""Convert the Max Water Extent raster to a polygon shapefile.

Input:  data/MaxWaterExtent/MaxWaterExtent.tif
        uint8, EPSG:32643, values 1 = water, 0 = dry, 255 = NoData.
Output: data/MaxWaterExtent/MaxWaterExtent_polygons.shp
        One polygon per connected water body (4-connected pixels), kept in
        EPSG:32643 so area is in square metres. Edges follow the pixel grid
        exactly (no simplification).

Run from the backend folder:
    .venv-win\\Scripts\\python.exe scripts\\convert_max_water_extent.py
"""

from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "MaxWaterExtent"
RASTER_PATH = DATA_DIR / "MaxWaterExtent.tif"
OUTPUT_PATH = DATA_DIR / "MaxWaterExtent_polygons.shp"

WATER_VALUE = 1


def main() -> None:
    with rasterio.open(RASTER_PATH) as ds:
        band = ds.read(1)
        water = band == WATER_VALUE
        geoms = [
            shape(geom)
            for geom, _ in shapes(band, mask=water, connectivity=4, transform=ds.transform)
        ]
        crs = ds.crs

    gdf = gpd.GeoDataFrame(geometry=geoms, crs=crs)
    gdf.insert(0, "id", range(1, len(gdf) + 1))
    gdf.insert(1, "area_m2", gdf.geometry.area.round(2))
    gdf.to_file(OUTPUT_PATH, driver="ESRI Shapefile")

    print(f"Wrote {len(gdf)} polygons to {OUTPUT_PATH}")
    print(f"Total water area: {gdf['area_m2'].sum() / 1e6:.3f} km2")


if __name__ == "__main__":
    main()
