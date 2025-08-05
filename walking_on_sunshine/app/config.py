from pydantic import BaseModel


class Config(BaseModel):
    bar: str | None = None
