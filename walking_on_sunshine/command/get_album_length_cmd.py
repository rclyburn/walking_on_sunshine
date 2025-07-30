import os

import click
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from walking_on_sunshine.command.root import root_cmd


def _time_format(duration: int) -> str:
    """
    Convert a duration in milliseconds to a formatted string.
    Returns "Album Duration: HH:MM:SS" if hours > 0, else "Album Duration: MM:SS".
    """
    seconds = duration // 1000
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"Album Duration: {h:02}:{m:02}:{s:02}"
    else:
        return f"Album Duration: {m:02}:{s:02}"


def _search_query(spotify_obj: Spotify, album_name: str) -> str:
    """
    Return album id of first spotify search result
    """
    search_query = "album:" + album_name
    album_search = spotify_obj.search(search_query, type="album", limit=1)
    albums_in_search = album_search["albums"]
    first_result = albums_in_search["items"][0]
    return first_result["id"]


def _get_tracks(spotify_obj: Spotify, album_id: str) -> list[dict]:
    """
    Return list of tracks for a given album id
    """
    album_tracks = spotify_obj.album_tracks(album_id)
    tracks = []
    tracks.extend(album_tracks["items"])

    while album_tracks["next"]:
        album_tracks = spotify_obj.next(album_tracks)

        tracks.extend(album_tracks["items"])

    return tracks


@root_cmd.command()
@click.option("--album_name", prompt="Please enter your album name")
def get_album_length(album_name: str):
    """
    CLI command to fetch and display the total length of a Spotify album.
    Prompts the user for an album name, searches Spotify, and prints each track name and the total album duration.
    """
    # Get Spotify API credentials from environment variables
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    # Authenticate with Spotify using client credentials
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id, client_secret))

    album_id = _search_query(sp, album_name=album_name)

    tracks = _get_tracks(sp, album_id=album_id)

    album_duration = 0

    song_number = 0

    album = sp.album(album_id)
    print(f"Album name: {album['name']}")

    # Iterate through all tracks, print their names, and sum their durations
    for item in tracks:
        song_name = item["name"]
        duration = item["duration_ms"]

        album_duration += duration
        song_number += 1

        print(f"{song_number} Song name: {song_name}")

    # Format and print the total album duration
    formatted_duration = _time_format(album_duration)
    print(f"{formatted_duration}")
    # return album_duration
