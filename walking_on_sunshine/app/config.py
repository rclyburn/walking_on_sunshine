from pydantic import BaseModel


class Config(BaseModel):
    bar: str | None = None
    SPOTIFY_CLIENT_ID: str | None = None
    SPOTIFY_CLIENT_SECRET: str | None = None
    GOOGLE_MAPS_API_KEY: str | None = None
    OPENROUTE_API_KEY: str | None = None
