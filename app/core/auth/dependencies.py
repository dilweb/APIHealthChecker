from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.db import SQLAlchemyUserDatabase

from app.core.db import get_db
from app.models.user import User


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

