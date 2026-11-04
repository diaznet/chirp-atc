import pytest

from chirp_model import csv_filename, to_chirp_rows
from openaip_frequencies.openaipfrequencies import OpenAIPFrequencies, channel_to_frequency

GENEVA = (46.2381, 6.1090)  # lat, lon


@pytest.mark.parametrize("channel, frequency", [
    (118.000, "118.00000"),  # position 0: 25 kHz channel
    (118.005, "118.00000"),  # position 1: same center frequency
    (118.010, "118.00830"),  # position 2: +8.333 kHz
    (118.015, "118.01670"),  # position 3: +16.667 kHz
    (132.350, "132.35000"),
    (132.355, "132.35000"),
    (132.360, "132.35830"),
    (132.365, "132.36670"),
])
def test_channel_to_frequency(channel, frequency):
    assert channel_to_frequency(channel) == frequency


def square(lat, lon, half_size_deg):
    """GeoJSON polygon centered on (lat, lon); coordinates are [lon, lat]."""
    ring = [[lon - half_size_deg, lat - half_size_deg], [lon + half_size_deg, lat - half_size_deg],
            [lon + half_size_deg, lat + half_size_deg], [lon - half_size_deg, lat + half_size_deg],
            [lon - half_size_deg, lat - half_size_deg]]
    return {"type": "Polygon", "coordinates": [ring]}


@pytest.fixture
def geneva_20km():
    return OpenAIPFrequencies("CH", _radius=20, _location=GENEVA)


def test_location_skips_geocoding_and_defaults_radius():
    source = OpenAIPFrequencies("CH", "1200", _location=GENEVA)
    assert source.location == GENEVA
    assert source.radius == OpenAIPFrequencies.get_default_radius()


def test_no_location_means_no_radius():
    source = OpenAIPFrequencies("CH")
    assert source.location is None and source.radius is None


def test_invalid_country():
    with pytest.raises(ValueError):
        OpenAIPFrequencies("XX")


def test_point_within_radius(geneva_20km):
    lausanne = {"type": "Point", "coordinates": [6.6323, 46.5197]}
    near = {"type": "Point", "coordinates": [6.15, 46.25]}
    assert geneva_20km._is_within_radius(near)
    assert not geneva_20km._is_within_radius(lausanne)


def test_large_polygon_containing_center_is_within_radius(geneva_20km):
    # Centroid is ~110 km away, but the center lies inside the polygon.
    big = square(GENEVA[0] + 1.0, GENEVA[1], 1.5)
    assert geneva_20km._is_within_radius(big)


def test_polygon_edge_distance(geneva_20km):
    # Square of ~11 km half-width whose closest edge is ~10 km from the center.
    close = square(GENEVA[0] + 0.19, GENEVA[1], 0.1)
    far = square(GENEVA[0] + 0.5, GENEVA[1], 0.1)
    assert geneva_20km._is_within_radius(close)
    assert not geneva_20km._is_within_radius(far)


@pytest.mark.parametrize("geometry", [None, {}, {"type": "Point"}, {"type": "Bogus", "coordinates": [1, 2]}])
def test_invalid_geometry(geneva_20km, geometry):
    assert not geneva_20km._is_within_radius(geometry)


def test_get_frequencies_naming_and_filtering(geneva_20km, monkeypatch):
    data = [
        {"_id": "1", "type": 3, "name": "GENEVA", "icaoCode": "LSGG",
         "geometry": {"type": "Point", "coordinates": [6.1090, 46.2381]},
         "frequencies": [{"name": "TOWER", "value": "118.700"}, {"name": "ATIS", "value": None}]},
        {"_id": "2", "type": 3, "name": "FAR AWAY", "icaoCode": "LSZH",
         "geometry": {"type": "Point", "coordinates": [8.5492, 47.4582]},
         "frequencies": [{"name": "TOWER", "value": "118.100"}]},
        {"_id": "3", "type": 1, "name": "GLIDERS", "icaoCode": "LSXX",
         "geometry": {"type": "Point", "coordinates": [6.1090, 46.2381]},
         "frequencies": [{"name": "INFO", "value": "122.500"}]},
        {"_id": "4", "type": 2, "name": "LOCAL FIELD", "altIdentifier": "LSGX",
         "geometry": {"type": "Point", "coordinates": [6.12, 46.24]},
         "frequencies": [{"value": "123.010"}]},
    ]
    monkeypatch.setattr(geneva_20km, "_get_openaip_data", lambda type_: data)
    assert geneva_20km.get_frequencies("airports") == [
        {"frequency": "118.70000", "name": "LSGG TOWER", "comment": "AIRPORTS"},
        {"frequency": "123.00830", "name": "LSGX LOCAL FIELD", "comment": "AIRPORTS"},
    ]


def test_chirp_rows_and_filename():
    rows = to_chirp_rows([{"frequency": "118.70000", "name": "LSGG TOWER", "comment": "AIRPORTS"}])
    assert rows[0]["Location"] == 0
    assert rows[0]["Frequency"] == "118.70000"
    assert rows[0]["Name"] == "LSGG TOWER"
    assert rows[0]["Mode"] == "AM"
    assert csv_filename("CH", "airports", "_Geneva-Leman") == "CH_AIRPORTS_GENEVA-LEMAN.CSV"
