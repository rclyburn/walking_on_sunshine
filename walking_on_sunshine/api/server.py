# walking_on_sunshine/api/server.py
from walking_on_sunshine.api.api import API
from walking_on_sunshine.app.app import App
from walking_on_sunshine.command.config import RootConfig

root_cfg = RootConfig()
assert root_cfg.app is not None, "app config is required"
api = API(App(root_cfg.app))
app = api.fast_api  # uvicorn will import this
