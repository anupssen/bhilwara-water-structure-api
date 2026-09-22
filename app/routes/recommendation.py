from fastapi import APIRouter, HTTPException

from ..models.schemas import RecommendationRequest, RecommendationResponse
from ..services.elevation_service import get_elevation
from ..services.recommendation_service import compute_recommendation
from ..services.subdistrict_service import find_subdistrict
from ..utils.validation import validate_subdistrict

router = APIRouter()


@router.post("/api/recommendation", response_model=RecommendationResponse)
def get_recommendation(payload: RecommendationRequest):
    """Return the GIS-derived subdistrict and elevation for a location.

    The real subdistrict (from the shapefile) and elevation (from the DEM
    raster) are resolved from latitude/longitude. The recommended structure
    itself is still mock — the recommendation logic lives in the service layer
    and will later be replaced with real GIS/raster-based processing.
    """
    try:
        subdistrict = validate_subdistrict(payload.subdistrict)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    latitude = payload.latitude
    longitude = payload.longitude

    detected_subdistrict, subdistrict_message = find_subdistrict(
        latitude, longitude
    )
    elevation, elevation_message = get_elevation(latitude, longitude)

    # Mock structure recommendation keyed on the best-known subdistrict name.
    effective_subdistrict = detected_subdistrict or subdistrict
    result = compute_recommendation(latitude, longitude, effective_subdistrict)

    result["subdistrict"] = detected_subdistrict
    result["subdistrict_message"] = subdistrict_message
    result["elevation"] = elevation
    result["elevation_message"] = elevation_message

    return result