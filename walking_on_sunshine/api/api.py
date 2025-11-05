import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

import walking_on_sunshine.api.app_router as app_router
from walking_on_sunshine.app.app import App


class API:
    def __init__(self, app: App):
        self.app = app
        self.fast_api = FastAPI()

        # Get the absolute path to the frontend directory
        frontend_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "frontend/src",
        )

        # Print debug info about static files path
        static_path = os.path.join(frontend_path, "assets")
        print(f"Mounting static files from: {static_path}")
        print(f"Does path exist? {os.path.exists(static_path)}")

        # Mount static files
        self.fast_api.mount(
            "/static",
            StaticFiles(directory=static_path),
            name="static",
        )

        # Add CORS middleware
        self.fast_api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.fast_api.add_middleware(AppMiddleware, app=self.app)
        self.fast_api.include_router(app_router.router)
        self.fast_api.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://your-domain.com",
                "http://localhost:8000",  # for local development
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

<<<<<<< HEAD
        # Serve index.html at root
        @self.fast_api.get("/")
        async def serve_frontend():
            return FileResponse(os.path.join(frontend_path, "components/index.html"))

        # Serve index.html at root
        @self.fast_api.get("/")
        async def serve_frontend():
            return FileResponse(os.path.join(frontend_path, "components/index.html"))

=======
>>>>>>> 4939c40 (removed unused function)
    def run(self):
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(self.fast_api, host="0.0.0.0", port=port, log_level="info")


class AppMiddleware(BaseHTTPMiddleware):
    def __init__(self, asgi_app, app: App):
        super().__init__(asgi_app)
        self.my_app = app

    async def dispatch(self, request, call_next):
        request.state.app = self.my_app
        response = await call_next(request)
        return response
