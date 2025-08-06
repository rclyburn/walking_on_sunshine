from pydantic import BaseModel


class Config(BaseModel):
    lala: str | None = None
