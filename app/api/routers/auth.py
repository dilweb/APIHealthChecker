from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from app.models.user import User
from app.core.auth.manager import get_user_manager
from app.core.auth.transport import auth_backend
from app.schemas.user import UserCreate, UserRead, UserUpdate


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True) # Зависимость для получения текущего активного пользователя

router = APIRouter()


router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=False), # TODO: change to True in production
    prefix="/auth/jwt",
    tags=["auth"],
)


router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)


router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


