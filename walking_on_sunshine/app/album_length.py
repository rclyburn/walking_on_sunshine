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
            return f"{h:02}:{m:02}:{s:02}"
        else:
            return f"{m:02}:{s:02}"

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

    def get_album_details(self, album_name: str, album_id: str | None = None) -> dict:
        if not album_id:
            album_id = self._search_query(album_name=album_name)
        album = self.sp.album(album_id)

        tracks = self._get_tracks(album_id=album_id)
        total_ms = sum(item.get("duration_ms", 0) for item in tracks)

        release_date = album.get("release_date") or ""
        release_year = release_date.split("-")[0] if release_date else None

        images = album.get("images") or []
        image_url = images[0]["url"] if images else None

        artists = album.get("artists") or []
        artist_name = artists[0]["name"] if artists else ""

        return {
            "id": album_id,
            "name": album.get("name", album_name),
            "artist": artist_name,
            "artists": [artist.get("name") for artist in artists if artist.get("name")],
            "total_ms": total_ms,
            "track_count": album.get("total_tracks"),
            "release_date": release_date,
            "release_year": release_year,
            "image_url": image_url,
        }

    def get_album_length(self, album_name: str) -> int:
        return self.get_album_details(album_name)["total_ms"]
