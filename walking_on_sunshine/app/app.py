from walking_on_sunshine.app.config import Config
from walking_on_sunshine.common.logging.logger import get_logger

logger = get_logger(__name__)


class App:
    def __init__(self, config: Config):
        self.config = config

    def run(self, album_name):
        return "API Test"
