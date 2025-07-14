import os
from pprint import pprint

import click
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from walking_on_sunshine.command.root import root_cmd


def _ms_to_hhmmss(duration: int) -> str:
    """
    Convert album length in ms to HH:MM:SS
    """
    minutes = duration // 60000
    minutes_remainder = (duration % 60000) // 60000
    hours = minutes // 60
    miliseconds = duration % 60000
    seconds = miliseconds // 1000

    if hours > 0:
        return f"Album Duration: {hours:02.0f}:{minutes_remainder:02.0f}:{seconds:05.2f}"
    else:
        return f"Album Duration: {minutes:02.0f}:{seconds:05.2f}"


def _format_album_name(name: str) -> str:
    """
    Convert user-entered search to URL-encoded string
    """
    name.replace(" ", "%20")
    return "album:" + name


@root_cmd.command()
@click.option("--album_name", prompt="Please enter your album name")
def get_album_length(album_name):
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id, client_secret))

    search_query = _format_album_name(album_name)
    album_search = sp.search(search_query, type="album", limit=1)
    first_result = album_search["albums"]

    album = sp.album_tracks(first_result["items"][0]["id"])

    tracks = []

    tracks.extend(album["items"])

    # print(album["tracks"]["next"])

    while album["next"]:
        # pprint(album["next"])
        album = sp.next(album)

        tracks.extend(album["items"])

    # pprint(tracks[-1])

    album_duration = 0

    song_number = 0

    for item in tracks:
        song_name = item["name"]
        duration = item["duration_ms"]

        album_duration += duration
        song_number += 1

        print(f"{song_number} Song name: {song_name}")

    print(_ms_to_hhmmss(album_duration))
