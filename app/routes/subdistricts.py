from fastapi import APIRouter, HTTPException

from ..models.schemas import SubdistrictInfo
from ..services.subdistrict_service import (
    get_subdistrict_geojson,
    get_subdistricts_geojson,
    list_subdistricts,
)

router = APIRouter()


@router.get("/api/subdistricts")
def get_subdistricts_geojson_endpoint():
    """Return all Bhilwara subdistrict polygons as GeoJSON (EPSG:4326).

    Each feature carries its subdistrict name in properties.name.
    """
    return get_subdistricts_geojson()


@router.get("/api/subdistricts/list", response_model=list[SubdistrictInfo])
def get_subdistricts_list():
    """List subdistricts with centroid coordinates, from the shapefile."""
    return list_subdistricts()


@router.get("/api/subdistricts/{subdistrict_name}")
def get_subdistrict_endpoint(subdistrict_name: str):
    """Return the GeoJSON Feature for a single named subdistrict."""
    feature = get_subdistrict_geojson(subdistrict_name)
    if feature is None:
        raise HTTPException(status_code=404, detail="Subdistrict not found")
    return feature