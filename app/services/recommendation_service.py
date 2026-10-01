"""Mock recommendation service.

This module returns a random placeholder recommendation from the water
structures the project works with. It will later be replaced with real
GIS/raster/shapefile-based processing, so the route layer only ever calls
compute_recommendation().
"""

import random
from typing import Optional

# Water structures the project works with (the Activity values in
# WaterStructurePoints.shp).
STRUCTURES = [
    "WHS",
    "Percolation Tank",
    "Mini Percolation Tank",
    "Anicut",
    "Farm Pond",
    "Talab",
    "Pakka Check Dam",
    "Loose Stone Check Dam",
]

ALTERNATIVE_COUNT = 3


def compute_recommendation(
    latitude: float,
    longitude: float,
    subdistrict: str,
    previous: Optional[str] = None,
) -> dict:
    """Return a random mock recommendation for the given location.

    Args:
        latitude: Location latitude between -90 and 90.
        longitude: Location longitude between -180 and 180.
        subdistrict: Bhilwara subdistrict/tehsil name.
        previous: Structure shown last time; it is not picked again, so every
            request shows a different name.

    Returns:
        A dict matching RecommendationResponse. All fields here are
        placeholders until the real GIS/raster analysis is implemented.
    """
    choices = [name for name in STRUCTURES if name != previous]
    structure = random.choice(choices)
    score = random.randint(65, 95)

    others = random.sample(
        [name for name in STRUCTURES if name != structure], ALTERNATIVE_COUNT
    )
    alt_scores = sorted(random.sample(range(40, score), ALTERNATIVE_COUNT), reverse=True)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "subdistrict": subdistrict,
        "recommendation": structure,
        "score": score,
        "area_km2": "1,285",
        "reasons": [],
        "alternatives": [
            {"name": name, "score": alt_score}
            for name, alt_score in zip(others, alt_scores)
        ],
        "message": "Mock recommendation for development (random placeholder)",
    }
