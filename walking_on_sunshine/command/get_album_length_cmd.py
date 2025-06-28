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

    search_query = "remaster%20track:Doxy%20artist:Miles%20Davis"
    album_search = sp.search(search_query, type="album", limit=1)
    first_result = album_search["albums"]

    album = sp.album(first_result["items"][0]["id"])

    item_array = []

    for item in album["tracks"]["items"]:
        item_array.append(item)

    # while album["next"]:
    #     album = sp.next(album)
    #     item_array.extend(album["items"])

    for item in item_array:
        song_name = item["name"]
        duration = item["duration_ms"]

        print(f"Song name: {song_name} Song duration: {duration}")
