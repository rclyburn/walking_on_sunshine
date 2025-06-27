import os
from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from walking_on_sunshine.command.root import root_cmd


@root_cmd.command()
def get_album_length():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id, client_secret))

    album = sp.album("4aawyAB9vmqN3uQ7FjRGTy")
    item_array = []

    for item in album["tracks"]["items"]:
        item_array.append(item)

    while album["tracks"]["next"]:
        album = sp.next(album)
        item_array.extend(album["items"])

    for item in item_array:
        song_name = item["name"]
        duration = item["duration_ms"]

        print(f"Song name: {song_name} Song duration: {duration}")
