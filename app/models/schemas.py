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


class RecommendationAlternative(BaseModel):
    name: str
    score: float


class SubdistrictInfo(BaseModel):
    subdistrict: str
    latitude: float
    longitude: float
    area_km2: float


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