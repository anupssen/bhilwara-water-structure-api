"""Mock recommendation service.

This module returns a deterministic placeholder recommendation. It will later
be replaced with real GIS/raster/shapefile-based processing, so the route layer
only ever calls compute_recommendation().
"""

MOCK_STRUCTURES = [
    {
        "name": "Check Dam",
        "score": 85,
        "reasons": [
            "Suitable slope and elevation",
            "Good rainfall and runoff potential",
            "Favorable soil and geological condition",
            "Nearby water flow accumulation",
            "High groundwater recharge potential",
        ],
        "alternatives": [
            {"name": "Farm Pond", "score": 72},
            {"name": "Percolation Tank", "score": 64},
            {"name": "Nala Bund", "score": 58},
        ],
    },
    {
        "name": "Farm Pond",
        "score": 78,
        "reasons": [
            "Moderate slope and suitable terrain",
            "Good runoff potential",
            "Suitable soil condition",
            "Nearby drainage network",
        ],
        "alternatives": [
            {"name": "Check Dam", "score": 74},
            {"name": "Nala Bund", "score": 66},
            {"name": "Percolation Tank", "score": 60},
        ],
    },
    {
        "name": "Nala Bund",
        "score": 82,
        "reasons": [
            "Strong drainage-line connectivity",
            "Suitable terrain and elevation",
            "Good runoff concentration",
            "Favorable recharge potential",
        ],
        "alternatives": [
            {"name": "Check Dam", "score": 76},
            {"name": "Farm Pond", "score": 69},
            {"name": "Percolation Tank", "score": 62},
        ],
    },
    {
        "name": "Percolation Tank",
        "score": 74,
        "reasons": [
            "Good percolation rates expected",
            "Suitable terrain and elevation",
            "Moderate runoff concentration",
            "Nearby drainage network",
        ],
        "alternatives": [
            {"name": "Check Dam", "score": 70},
            {"name": "Farm Pond", "score": 68},
            {"name": "Nala Bund", "score": 61},
        ],
    },
]


def compute_recommendation(latitude: float, longitude: float, subdistrict: str) -> dict:
    """Return a mock recommendation for the given location.

    Args:
        latitude: Location latitude between -90 and 90.
        longitude: Location longitude between -180 and 180.
        subdistrict: Bhilwara subdistrict/tehsil name.

    Returns:
        A dict matching RecommendationResponse. All fields here are
        placeholders until the real GIS/raster analysis is implemented.
    """
    index = sum(ord(ch) for ch in subdistrict) % len(MOCK_STRUCTURES)
    structure = MOCK_STRUCTURES[index]

    return {
        "latitude": latitude,
        "longitude": longitude,
        "subdistrict": subdistrict,
        "recommendation": structure["name"],
        "score": structure["score"],
        "area_km2": "1,285",
        "reasons": structure["reasons"],
        "alternatives": structure["alternatives"],
        "message": "Mock recommendation for development",
    }