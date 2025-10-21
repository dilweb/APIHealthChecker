from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
)
from app.core.db import get_db
from app.models.user import User
from app.models.access_token import AccessToken
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy


async def get_user_db(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """
    Зависимость, предоставляющая адаптер базы данных для FastAPI Users.

    Берет асинхронную сессию из `get_async_session` и "оборачивает" ее
    в `SQLAlchemyUserDatabase`, который предоставляет FastAPI Users
    необходимые методы для работы с моделью User.
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
    session: AsyncSession = Depends(get_db),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=604800)
