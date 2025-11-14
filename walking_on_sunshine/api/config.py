from pydantic import BaseModel


class Config(BaseModel):
    test: str | None = None
