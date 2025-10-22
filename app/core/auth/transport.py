from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from app.core.auth.dependencies import get_database_strategy
from app.core.settings import settings

cookie_transport = CookieTransport(
    cookie_name=settings.AUTH_COOKIE_NAME,
    cookie_max_age=settings.AUTH_COOKIE_LIFETIME_MINUTES * 60,
    cookie_httponly=True,
    cookie_secure=settings.HTTPS_ENABLED,
    cookie_samesite="lax",
)


auth_backend = AuthenticationBackend(
    name="db",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)
