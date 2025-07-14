import os

import click
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from walking_on_sunshine.command.root import root_cmd


def _ms_to_hhmmss(duration: int) -> str:
    """
    Convert a duration in milliseconds to a formatted string.
    Returns "Album Duration: HH:MM:SS" if hours > 0, else "Album Duration: MM:SS".
    """
    minutes = duration // 60000
    minutes_remainder = (duration % 60000) // 60000
    hours = minutes // 60
    miliseconds = duration % 60000
    seconds = miliseconds // 1000

    if hours > 0:
        return f"Album Duration: {hours:02.0f}:{minutes_remainder:02.0f}:{seconds:02.0f}"
    else:
        return f"Album Duration: {minutes:02.0f}:{seconds:02.0f}"


def _format_album_name(name: str) -> str:
    """
    Convert user-entered album name to a Spotify search query string.
    Spaces are replaced with '%20' for URL encoding.
    """
    # Replace spaces with '%20' for URL encoding
    name.replace(" ", "%20")
    return "album:" + name


@root_cmd.command()
@click.option("--album_name", prompt="Please enter your album name")
def get_album_length(album_name):
    """
    CLI command to fetch and display the total length of a Spotify album.
    Prompts the user for an album name, searches Spotify, and prints each track name and the total album duration.
    """
    # Get Spotify API credentials from environment variables
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    # Authenticate with Spotify using client credentials
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id, client_secret))

    # Format the search query for the album
    search_query = _format_album_name(album_name)
    album_search = sp.search(search_query, type="album", limit=1)
    albums_in_search = album_search["albums"]
    first_result = albums_in_search["items"][0]
    album_id = first_result["id"]

    # Fetch album tracks and album details
    album_tracks = sp.album_tracks(album_id)
    album = sp.album(album_id)
    album_name = album["name"]

    tracks = []
    tracks.extend(album_tracks["items"])

    # If there are more tracks (pagination), fetch them all
    while album_tracks["next"]:
        album_tracks = sp.next(album_tracks)

        tracks.extend(album_tracks["items"])

    album_duration = 0

    song_number = 0

    print(f"Album name: {album_name}")

    # Iterate through all tracks, print their names, and sum their durations
    for item in tracks:
        song_name = item["name"]
        duration = item["duration_ms"]

        album_duration += duration
        song_number += 1

        print(f"{song_number} Song name: {song_name}")

    # Format and print the total album duration
    formatted_duration = _ms_to_hhmmss(album_duration)
    print(f"{formatted_duration}")
