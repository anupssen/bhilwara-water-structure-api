"""Tests for the real GIS services using the actual Bhilwara datasets.

Test coordinates were derived from the real data:
- Mandal representative point: lon=74.50437, lat=25.45741 (inside polygon,
  inside raster, valid elevation).
- A far-eastern point (26.5, 76.5) lies outside every subdistrict polygon.
- A far-northern point (27.0, 75.5) lies outside the DEM raster coverage.
- Water body 5178 (Sameliya, structure points on it): lat=25.38559, lon=74.51267.
- Water body 1955 (no point on it, nearest point 253.19 m away):
  lat=25.71067, lon=75.27535.
"""

import pytest

from app.services.elevation_service import get_elevation
from app.services.subdistrict_service import find_subdistrict
from app.services.water_body_service import find_water_body, get_water_bodies_geojson


def test_valid_point_inside_subdistrict():
    name, message = find_subdistrict(25.45741, 74.50437)
    assert name == "Mandal"
    assert message is None


def test_point_outside_all_polygons():
    name, message = find_subdistrict(26.5, 76.5)
    assert name is None
    assert "outside" in message.lower()


def test_elevation_extracted_at_valid_point():
    elevation, message = get_elevation(25.45741, 74.50437)
    assert elevation is not None
    assert message is None
    assert 300 <= elevation <= 1000


def test_elevation_outside_raster_coverage():
    elevation, message = get_elevation(27.0, 75.5)
    assert elevation is None
    assert "outside" in message.lower()


@pytest.mark.parametrize(
    "lat, lon",
    [
        (25.79123, 74.48594),  # Antali representative point
        (25.61728, 74.90327),  # Shahpura town
    ],
)
def test_multiple_subdistricts_detected(lat, lon):
    name, _ = find_subdistrict(lat, lon)
    assert name is not None
    elevation, _ = get_elevation(lat, lon)
    assert elevation is not None


def test_water_bodies_geojson():
    geo = get_water_bodies_geojson()
    features = geo["features"]
    assert geo["type"] == "FeatureCollection"
    assert len(features) == 7576

    # Shapes only (details come from find_water_body), within Bhilwara (lon/lat).
    for feature in features:
        assert set(feature["properties"]) == {"id"}
        lon, lat = feature["geometry"]["coordinates"][0][0]
        assert 73.9 <= lon <= 75.6 and 24.9 <= lat <= 26.0


def test_water_body_with_points_on_it():
    body = find_water_body(25.38559, 74.51267)
    assert body["id"] == 5178
    assert body["match_type"] == "inside"
    assert body["points_on_body"] == 16
    assert body["point_distance_m"] == 0
    assert body["sr_no"] == 9075
    assert body["activity"] == "Percolation Tank"
    assert body["village"] == "Sameliya"
    assert body["ar"] == 12000
    assert body["length"] is None  # 0 in the source means not recorded
    assert body["depth"] == 1


def test_water_body_with_nearest_point():
    body = find_water_body(25.71067, 75.27535)
    assert body["id"] == 1955
    assert body["match_type"] == "nearest"
    assert body["points_on_body"] == 0
    assert body["point_distance_m"] == pytest.approx(253.19)
    assert body["sr_no"] == 17963


def test_no_water_body_at_dry_point():
    assert find_water_body(25.45741, 74.50437) is None
