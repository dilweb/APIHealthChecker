from fastapi import FastAPI

from app.api.routers import monitors, checks, auth

from app.core.logging_middleware import DBLoggingMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="API Health Checker")
    app.add_middleware(DBLoggingMiddleware)
    app.include_router(auth.router)
    app.include_router(monitors.router)
    app.include_router(checks.router)
    return app

app = create_app()