import math
from unittest.mock import MagicMock, patch

import pytest

from walking_on_sunshine.app.path_gen import PathGen


@pytest.fixture
def mock_client():
    with patch("walking_on_sunshine.app.path_gen.openrouteservice.Client") as MockClient:
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


@patch("walking_on_sunshine.app.path_gen.PathGen._get_coords_from_addr")
@patch("walking_on_sunshine.app.path_gen.PathGen._get_maps_url")
@patch("walking_on_sunshine.app.path_gen.PathGen._build_folium_map")
@patch("walking_on_sunshine.app.path_gen.PathGen._get_maps_url")
@patch("walking_on_sunshine.app.path_gen.PathGen._get_coords_from_addr")
@pytest.mark.parametrize(
    "album_ms,expected_m",
    [
        (30 * 60 * 1000, 1250.0),
        (60 * 60 * 1000, 2500.0),
    ],
)
def test_generate_path_distance_conversion(mock_get_coords_from_addr, mock_get_maps_url, mock_map, album_ms, expected_m):
    mock_get_coords_from_addr.return_value = [[-122.4, 37.78], [-122.41, 37.79]]
    mock_get_maps_url.return_value = "https://www.google.com/maps/dir/37.78,-122.4/37.79,-122.41/"
    mock_map.return_value = "data:text/html;base64,abc"

    pg = PathGen(key="dummy")
    url, resolved, preview, map_html = pg.generate_path("Somewhere", album_ms)

    assert url.startswith("https://www.google.com/maps/dir/")
    assert resolved == "Somewhere"
    assert preview == [
        {"lat": 37.78, "lon": -122.4},
        {"lat": 37.79, "lon": -122.41},
    ]
    assert map_html == "data:text/html;base64,abc"
    args, _ = mock_get_coords_from_addr.call_args
    assert args[0] == "Somewhere"
    assert math.isclose(args[1], expected_m, rel_tol=1e-9)


@patch("walking_on_sunshine.app.path_gen.PathGen._build_folium_map")
@patch("walking_on_sunshine.app.path_gen.PathGen._get_maps_url")
@patch("walking_on_sunshine.app.path_gen.PathGen._get_coords_from_addr")
def test_generate_path_with_coordinate_string_uses_reverse_geocode(
    mock_get_coords_from_addr, mock_get_maps_url, mock_map, mock_client
):
    mock_client.pelias_reverse.return_value = {
        "features": [
            {
                "properties": {
                    "label": "1 Market St, San Francisco, CA",
                }
            }
        ]
    }
    mock_get_coords_from_addr.return_value = [[-122.4, 37.78], [-122.41, 37.79]]
    mock_get_maps_url.return_value = "https://www.google.com/maps/dir/37.78,-122.4/37.79,-122.41/"
    mock_map.return_value = "data:text/html;base64,abc"

    pg = PathGen(key="dummy")
    url, resolved, preview, map_html = pg.generate_path("37.78,-122.41", 30 * 60 * 1000)

    assert resolved == "1 Market St, San Francisco, CA"
    assert preview == [
        {"lat": 37.78, "lon": -122.4},
        {"lat": 37.79, "lon": -122.41},
    ]
    assert map_html == "data:text/html;base64,abc"
    mock_client.pelias_reverse.assert_called_once()
    mock_get_coords_from_addr.assert_called_once()
    args, _ = mock_get_coords_from_addr.call_args
    assert args[0] == "1 Market St, San Francisco, CA"


@patch("walking_on_sunshine.app.path_gen.PathGen._build_folium_map")
@patch("walking_on_sunshine.app.path_gen.PathGen._get_maps_url")
@patch("walking_on_sunshine.app.path_gen.PathGen._get_coords_from_list")
def test_generate_path_with_coordinate_string_falls_back_without_reverse(
    mock_get_coords_from_list, mock_get_maps_url, mock_map, mock_client
):
    mock_client.pelias_reverse.return_value = {}
    mock_get_coords_from_list.return_value = [[-122.4, 37.78], [-122.41, 37.79]]
    mock_get_maps_url.return_value = "https://www.google.com/maps/dir/37.78,-122.4/37.79,-122.41/"
    mock_map.return_value = "data:text/html;base64,abc"

    pg = PathGen(key="dummy")
    url, resolved, preview, map_html = pg.generate_path("37.78,-122.41", 30 * 60 * 1000)

    assert resolved == "37.78,-122.41"
    assert preview == [
        {"lat": 37.78, "lon": -122.4},
        {"lat": 37.79, "lon": -122.41},
    ]
    assert map_html == "data:text/html;base64,abc"
    mock_get_coords_from_list.assert_called_once_with([[-122.41, 37.78]], pytest.approx(1250.0))
