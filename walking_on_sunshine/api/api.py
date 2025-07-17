import uvicorn
from fastapi import FastAPI

fast_api = FastAPI()


@fast_api.get("/")
def read_root():
    return {"Hello": "World"}


@fast_api.post("/")
def post_root():
    return {"Hello": "World"}


def run():
    uvicorn.run(fast_api, port=8000, log_level="info")
