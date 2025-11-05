import os

from walking_on_sunshine.app.album_length import AlbumLength
from walking_on_sunshine.app.config import Config
from walking_on_sunshine.app.path_gen import PathGen
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


class App:
    def __init__(self, config: Config):
        self.config = config
        self.album_length = AlbumLength(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))
        self.path_gen = PathGen(os.getenv("OPENROUTE_API_KEY"))

    def run(self, album_name: str, start_address: str, album_id: str | None = None):
        try:
            album_details = self.album_length.get_album_details(album_name, album_id=album_id)

            length_ms = album_details["total_ms"]
            length_label = self.album_length._time_format(length_ms)
            length_minutes = round(length_ms / 60_000, 2)

            maps_url, normalized_address, preview_coords, map_embed_html = self.path_gen.generate_path(
                start_address, length_ms
            )

            walking_speed_kmh = 2.5
            distance_km = (length_ms / 3_600_000) * walking_speed_kmh

            return {
                "album_name": album_details.get("name", album_name),
                "artist": album_details.get("artist"),
                "album_id": album_details.get("id", album_id),
                "length_minutes": length_minutes,
                "album_duration_label": length_label,
                "track_count": album_details.get("track_count"),
                "release_year": album_details.get("release_year"),
                "album_image_url": album_details.get("image_url"),
                "distance_km": round(distance_km, 2),
                "maps_url": maps_url,
                "start_address": normalized_address,
                "route_preview": preview_coords,
                "map_embed_html": map_embed_html,
            }
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise e
