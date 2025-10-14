from fastapi import FastAPI

from app.api.routers import monitors, users, checks, auth

from app.core.logging_middleware import DBLoggingMiddleware

# from app.api.deps.views import router as demo_router

def create_app() -> FastAPI:
    app = FastAPI(title="API Health Checker")
    app.add_middleware(DBLoggingMiddleware)
    app.include_router(users.router)
    app.include_router(monitors.router)
    app.include_router(checks.router)
    # app.include_router(demo_router)
    app.include_router(auth.router)
    return app

app = create_app()