# walking_on_sunshine/api/server.py
from walking_on_sunshine.api.api import API
from walking_on_sunshine.app.app import App
from walking_on_sunshine.app.config import Config as AppConfig
from walking_on_sunshine.command.config import RootConfig

root_cfg = RootConfig()
app_cfg = root_cfg.app or AppConfig()  # defaults every field to None
api = API(App(app_cfg))
app = api.fast_api
