from fastapi_users.authentication import AuthenticationBackend, BearerTransport

from app.core.auth.dependencies import get_database_strategy


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


auth_backend = AuthenticationBackend(
    name="db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)


