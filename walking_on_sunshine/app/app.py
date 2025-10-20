from walking_on_sunshine.app.album_length import AlbumLength
from walking_on_sunshine.app.config import Config
from walking_on_sunshine.app.path_gen import PathGen
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


class App:
    def __init__(self, config: Config):
        self.config = config
        self.album_length = AlbumLength(self.config.SPOTIFY_CLIENT_ID, self.config.SPOTIFY_CLIENT_SECRET)
        self.path_gen = PathGen(self.config.OPENROUTE_API_KEY)

    def run(self, album_name: str):
        try:
            length_ms = self.album_length.get_album_length(album_name)

            length = self.album_length._time_format(length_ms)

            maps_url = self.path_gen.generate_path("4050 17th St, San Francisco, CA", length_ms)

            walking_speed_kmh = 2.5
            distance_km = (length_ms / 3_600_000) * walking_speed_kmh

            print(distance_km)

            return {
                "album_name": album_name,
                "length_minutes": length,
                "distance_km": round(distance_km, 2),
                "maps_url": maps_url,
            }
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise e
