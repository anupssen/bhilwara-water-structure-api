"""Tests for the real GIS services using the actual Bhilwara datasets.

Test coordinates were derived from the real data:
- Mandal representative point: lon=74.50437, lat=25.45741 (inside polygon,
  inside raster, valid elevation).
- A far-eastern point (26.5, 76.5) lies outside every subdistrict polygon.
- A far-northern point (27.0, 75.5) lies outside the DEM raster coverage.
"""

import pytest

from app.services.elevation_service import get_elevation
from app.services.subdistrict_service import find_subdistrict


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