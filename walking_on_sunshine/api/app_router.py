from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
async def run_app(request: Request):
    app = request.state.app
    return app.run("Rumours")
