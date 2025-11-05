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
async def generate_route(request: Request, album_name: str, start_address: str, album_id: str | None = None):
    print(f"Received request with album_name: {album_name}, start_address: {start_address}")
    app = request.state.app
    try:
        result = app.run(album_name, start_address, album_id)
        print(f"Success response: {result}")
        return JSONResponse(
            {
                "status": "success",
                "album_name": result["album_name"],
                "album_id": result.get("album_id", album_id),
                "artist": result.get("artist"),
                "length_minutes": result["length_minutes"],
                "album_duration_label": result.get("album_duration_label"),
                "track_count": result.get("track_count"),
                "release_year": result.get("release_year"),
                "album_image_url": result.get("album_image_url"),
                "distance_km": result["distance_km"],
                "maps_url": result["maps_url"],
                "start_address": result.get("start_address", start_address),
                "route_preview": result.get("route_preview", []),
                "map_embed_html": result.get("map_embed_html"),
            }
        )
    except Exception as e:
        print(f"Error in generate_route: {str(e)}")
        return JSONResponse(
            {
                "status": "error",
                "detail": str(e),
            },
            status_code=400,
        )


@router.get("/search_albums")
async def search_albums(request: Request, query: str):
    app = request.state.app
    try:
        albums = app.album_length.sp.search(f"album:{query}", type="album", limit=10)["albums"]["items"]
        results = [
            {
                "id": album["id"],
                "name": album["name"],
                "artist": album["artists"][0]["name"],
                "image": album["images"][0]["url"] if album["images"] else None,
            }
            for album in albums
        ]
        return JSONResponse({"results": results})
    except Exception as e:
        return JSONResponse({"results": [], "error": str(e)}, status_code=400)


@router.get("/maps_config")
async def maps_config(request: Request):
    app = request.state.app
    key = None

    if getattr(app, "config", None):
        key = getattr(app.config, "GOOGLE_MAPS_API_KEY", None)

    if not key:
        key = os.getenv("GOOGLE_MAPS_API_KEY")

    return JSONResponse(
        {
            "google_maps_api_key": key or "",
            "places_autocomplete_enabled": bool(key),
        }
    )
