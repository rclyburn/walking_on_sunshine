import math
from unittest.mock import MagicMock, patch

import pytest

from walking_on_sunshine.app.path_gen import PathGen


@pytest.fixture
def mock_client():
    with patch("walking_on_sunshine.command.path_gen.openrouteservice.Client") as MockClient:
        client = MagicMock()
        MockClient.return_value = client
        yield client


def _geojson(coords):
    return {"features": [{"geometry": {"coordinates": coords}}]}


def test_addr_to_coords_returns_lon_lat_list(mock_client):
    mock_client.pelias_search.return_value = {"features": [{"geometry": {"coordinates": [-122.4194, 37.7749]}}]}
    pg = PathGen(key="dummy")
    out = pg._addr_to_coords("San Francisco, CA")
    assert out == [[-122.4194, 37.7749]]


def test_get_coords_from_list_basic(mock_client):
    input_coords = [[-122.4, 37.78], [-122.41, 37.79]]
    route_coords = [[-122.4, 37.78], [-122.405, 37.785], [-122.41, 37.79]]
    mock_client.directions.return_value = _geojson(route_coords)

    pg = PathGen(key="dummy")
    out = pg._get_coords_from_list(input_coords, distance=3000.0)

    assert out == route_coords
    mock_client.directions.assert_called_once()


@pytest.mark.parametrize("count,max_waypoints", [(2, 23), (10, 23), (50, 23)])
def test_downsample_coords_keeps_ends_and_limits_size(count, max_waypoints):
    route = [[-122.0 + i * 0.001, 37.0 + i * 0.001] for i in range(count)]
    pg = PathGen(key="dummy")

    out = pg._downsample_coords(route, max_waypoints=max_waypoints)

    assert out[0] == route[0]
    assert out[-1] == route[-1]

    assert len(out) <= max_waypoints + 2


def test_get_maps_url_lat_lon_formatting():
    coords = [
        [-122.400, 37.780],
        [-122.401, 37.781],
        [-122.403, 37.783],
    ]
    pg = PathGen(key="dummy")
    url = pg._get_maps_url(coords)

    assert url.startswith("https://www.google.com/maps/dir/")
    assert "37.78,-122.4" in url
    assert "37.781,-122.401" in url
    assert url.rstrip("/").endswith("37.783,-122.403")


@patch("walking_on_sunshine.command.path_gen.PathGen._get_coords_from_addr")
@patch("walking_on_sunshine.command.path_gen.PathGen._get_maps_url")
@pytest.mark.parametrize(
    "album_ms,expected_m",
    [
        (30 * 60 * 1000, 1250.0),
        (60 * 60 * 1000, 2500.0),
    ],
)
def test_generate_path_distance_conversion(mock_get_maps_url, mock_get_coords_from_addr, album_ms, expected_m):
    mock_get_coords_from_addr.return_value = [[-122.4, 37.78], [-122.41, 37.79]]
    mock_get_maps_url.return_value = "https://www.google.com/maps/dir/37.78,-122.4/37.79,-122.41/"

    pg = PathGen(key="dummy")
    url = pg.generate_path("Somewhere", album_ms)

    assert url.startswith("https://www.google.com/maps/dir/")
    args, _ = mock_get_coords_from_addr.call_args
    assert args[0] == "Somewhere"
    assert math.isclose(args[1], expected_m, rel_tol=1e-9)
