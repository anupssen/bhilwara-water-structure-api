from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in degrees, between -90 and 90.",
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in degrees, between -180 and 180.",
    )
    subdistrict: str = Field(
        ...,
        min_length=1,
        description="Subdistrict/tehsil name.",
    )
    previous_recommendation: Optional[str] = Field(
        None,
        description="Structure shown for the previous request; the mock "
        "recommendation will not repeat it.",
    )


class RecommendationAlternative(BaseModel):
    name: str
    score: float


class SubdistrictInfo(BaseModel):
    subdistrict: str
    latitude: float
    longitude: float
    area_km2: float


class WaterBodyInfo(BaseModel):
    """An existing water body and the structure point matched to it."""

    id: int
    area_m2: float
    sr_no: int
    work_name: Optional[str] = None
    activity: Optional[str] = None
    village: Optional[str] = None
    gram_panchayat: Optional[str] = None
    panchayat: Optional[str] = None
    ar: Optional[float] = None
    length: Optional[float] = None
    depth: Optional[float] = None
    match_type: str = Field(
        ...,
        description='"inside": the point lies on the water body; '
        '"nearest": no point on it, the nearest one was used.',
    )
    points_on_body: int
    point_distance_m: float


class RecommendationResponse(BaseModel):
    latitude: float
    longitude: float
    subdistrict: Optional[str] = None
    subdistrict_message: Optional[str] = None
    elevation: Optional[float] = None
    elevation_message: Optional[str] = None
    recommendation: str
    message: str
    score: Optional[float] = None
    area_km2: Optional[str] = None
    reasons: List[str] = []
    alternatives: List[RecommendationAlternative] = []
    water_body: Optional[WaterBodyInfo] = None