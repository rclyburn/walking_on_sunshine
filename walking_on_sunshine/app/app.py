from walking_on_sunshine.app.album_length import AlbumLength
from walking_on_sunshine.app.config import Config
from walking_on_sunshine.app.path_gen import PathGen
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


class App:
    def __init__(self, config: Config):
        self.config = config

    def run(self, album_name):
        album = AlbumLength(self.config.SPOTIFY_CLIENT_ID, self.config.SPOTIFY_CLIENT_SECRET)
        path_gen = PathGen(self.config.OPENROUTE_API_KEY)
        album_length = album.get_album_length(album_name)
        link = path_gen.generate_path("4050 17th St San Francisco, CA", album_length)
        print(link)
        print(album._time_format(album_length))
        return link
