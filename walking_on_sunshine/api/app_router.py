import os

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend/src/components/index.html")
    return FileResponse(frontend_path)


@router.get("/generate_route")
async def generate_route(request: Request, album_name: str):
    app = request.state.app
    try:
        result = app.run(album_name)
        return JSONResponse(
            {
                "status": "success",
                "album_name": result["album_name"],
                "length_minutes": result["length_minutes"],
                "distance_km": result["distance_km"],
                "maps_url": result["maps_url"],
            }
        )
    except Exception as e:
        return JSONResponse(
            {
                "status": "error",
                "detail": str(e),
            },
            status_code=400,
        )
