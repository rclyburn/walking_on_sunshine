import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

fast_api = FastAPI()
templates = Jinja2Templates(directory="walking_on_sunshine/api/templates")


@fast_api.get("/{name}/hello_world", response_class=HTMLResponse)
def read_root(name: str):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hello World</title>
</head>
<body>
    <h1>{name}</h1>
</body>
</html>
"""


@fast_api.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(request=request, name="item.html", context={"id": id})


@fast_api.post("/")
def post_root():
    return {"Hello": "World"}


def run():
    uvicorn.run(fast_api, port=8000, log_level="info")
