from fastapi import APIRouter

from ..services.water_body_service import get_water_bodies_geojson

router = APIRouter()


@router.get("/api/water-bodies")
def get_water_bodies():
    """Return the Max Water Extent polygons as GeoJSON (EPSG:4326).

    Each feature carries only its id; a water body's details come back from
    /api/recommendation when the location lies on it.
    """
    return get_water_bodies_geojson()
