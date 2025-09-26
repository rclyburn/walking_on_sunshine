from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


class AlbumLength:
    def __init__(self, client_id: str | None, client_secret: str | None):
        self.sp = Spotify(auth_manager=SpotifyClientCredentials(client_id, client_secret))

    def _time_format(self, duration: int) -> str:
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

    def _search_query(self, album_name: str) -> str:
        """
        Return album id of first spotify search result
        """
        search_query = "album:" + album_name
        album_search = self.sp.search(search_query, type="album", limit=1)
        albums_in_search = album_search["albums"]
        first_result = albums_in_search["items"][0]
        return first_result["id"]

    def _get_tracks(self, album_id: str) -> list[dict]:
        """
        Return list of tracks for a given album id
        """
        album_tracks = self.sp.album_tracks(album_id)
        tracks = []
        tracks.extend(album_tracks["items"])

        while album_tracks["next"]:
            album_tracks = self.sp.next(album_tracks)

            tracks.extend(album_tracks["items"])

        return tracks

    def get_album_length(self, album_name: str):
        """
        CLI command to fetch and display the total length of a Spotify album.
        Prompts the user for an album name, searches Spotify, and prints each track name and the total album duration.
        """

        album_id = self._search_query(album_name=album_name)

        tracks = self._get_tracks(album_id=album_id)

        album_duration = 0

        # Iterate through all tracks, print their names, and sum their durations
        for item in tracks:
            duration = item["duration_ms"]
            album_duration += duration

        return album_duration

