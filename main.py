from fastapi import FastAPI

from app.api.routers import users, monitors, checks

from app.core.logging_middleware import DBLoggingMiddleware

from app.api.deps.views import router as demo_router

def create_app() -> FastAPI:
    import app.models
    app = FastAPI(title="API Health Checker")
    app.add_middleware(DBLoggingMiddleware)
    app.include_router(users.router)
    app.include_router(monitors.router)
    app.include_router(checks.router)
    app.include_router(demo_router)
    return app

app = create_app()