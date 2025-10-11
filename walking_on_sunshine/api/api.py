import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

import walking_on_sunshine.api.app_router as app_router
from walking_on_sunshine.app.app import App


class API:
    def __init__(self, app: App):
        self.app = app
        self.fast_api = FastAPI()
        self.fast_api.add_middleware(AppMiddleware, app=self.app)
        self.fast_api.include_router(app_router.router)

    def run(self):
        uvicorn.run(self.fast_api, port=8000, log_level="info")


class AppMiddleware(BaseHTTPMiddleware):
    def __init__(self, asgi_app, app: App):
        super().__init__(asgi_app)
        self.my_app = app

    async def dispatch(self, request, call_next):
        request.state.app = self.my_app
        response = await call_next(request)
        return response
