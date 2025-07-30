import os
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from walking_on_sunshine.command.get_album_length_cmd import _get_tracks, _search_query, _time_format
from walking_on_sunshine.command.root import root_cmd
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (2873000, "Album Duration: 47:53"),
        (9257000, "Album Duration: 02:34:17"),
        (8254000, "Album Duration: 02:17:34"),
        (0, "Album Duration: 00:00"),
        (10000, "Album Duration: 00:10"),
    ],
)
def test_time_format(test_input, expected):
    output = _time_format(test_input)

    assert output == expected


@pytest.mark.parametrize(
    "album_name, mock_response, expected_id",
    [
        ("Test Album 1", {"albums": {"items": [{"id": "album_id_1"}]}}, "album_id_1"),
        ("Test Album 2", {"albums": {"items": [{"id": "album_id_2"}]}}, "album_id_2"),
    ],
)
def test_search_query(album_name, mock_response, expected_id):
    mock_sp = MagicMock()
    mock_sp.search.return_value = mock_response
    output = _search_query(mock_sp, album_name)

    assert output == expected_id


@pytest.mark.parametrize(
    "album_id, mock_response, next_tracks, expected_tracks",
    [
        (
            "test_album_id_1",
            {"items": ["track1", "track2", "track3"], "next": None},
            None,
            ["track1", "track2", "track3"],
        ),
        (
            "test_album_id_2",
            {"items": ["track_a", "track_b", "track_c"], "next": "fake_next_id"},
            {"items": ["track_d", "track_e", "track_f"], "next": None},
            ["track_a", "track_b", "track_c", "track_d", "track_e", "track_f"],
        ),
    ],
)
def test_get_tracks(album_id, mock_response, next_tracks, expected_tracks):
    mock_sp = MagicMock()
    mock_sp.album_tracks.return_value = mock_response
    mock_sp.next.return_value = next_tracks
    output = _get_tracks(mock_sp, album_id)

    assert output == expected_tracks


@patch("walking_on_sunshine.command.get_album_length_cmd._time_format")
@patch("walking_on_sunshine.command.get_album_length_cmd._get_tracks")
@patch("walking_on_sunshine.command.get_album_length_cmd._search_query")
@patch("walking_on_sunshine.command.get_album_length_cmd.spotipy.Spotify")
@patch("walking_on_sunshine.command.get_album_length_cmd.SpotifyClientCredentials")
def test_get_album_length(mock_auth, mock_spotify, mock_search_query, mock_get_tracks, mock_time_format):
    mock_search_query.return_value = "fake_album_id"

    runner = CliRunner()

    mock_get_tracks.return_value = [
        {"name": "Track One", "duration_ms": 200000},
        {"name": "Track Two", "duration_ms": 180000},
    ]

    mock_sp = MagicMock()
    mock_sp.album.return_value = {"name": "Fake Album"}
    mock_spotify.return_value = mock_sp

    mock_time_format.return_value = "Album Duration: 06:20"

    os.environ["SPOTIFY_CLIENT_ID"] = "dummy_id"
    os.environ["SPOTIFY_CLIENT_SECRET"] = "dummy_secret"

    result = runner.invoke(root_cmd, "get-album-length", input="Fake Album")

    assert "Album name: Fake Album" in result.output
    assert "1 Song name: Track One" in result.output
    assert "2 Song name: Track Two" in result.output
    assert "Album Duration: 06:20" in result.output
