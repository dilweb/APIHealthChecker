"""
Auth dependencies for FastAPI:
- get_current_user: требует валидный access JWT и возвращает ORM-пользователя.
- get_current_active_user: доп.проверка is_active.
- get_current_user_optional: не валит запрос, если токена нет (вернёт None).
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.settings import settings
from app.models.user import User
from app.schemas.token import TokenPayload

# Стандартная схема "Bearer <token>" из заголовка Authorization
# tokenUrl укажи на свой логин-эндпойнт, это полезно для /docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _decode_access_token(token: str) -> TokenPayload:
    """
    Декодирует и валидирует access JWT.
    Бросает HTTP 401 при любой проблеме (нет подписи, истёк, не тот тип).
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        # подпись, формат, и пр.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = TokenPayload.model_validate(payload)
    if data.type != "access":
        # на /auth/refresh проверка "refresh", а здесь нужен ровно access
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return data


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """
    Возвращает текущего пользователя из access JWT.
    Требует заголовок: Authorization: Bearer <access_token>

    Raises:
        401 — если токена нет/он невалиден/истёк/не тот тип.
        401 — если пользователь по sub не найден.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = _decode_access_token(token)
    user_id = int(payload.sub)

    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    То же, что get_current_user, но с дополнительной проверкой is_active.
    """
    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Опциональная авторизация: если токена нет или он невалидный — возвращает None.
    Полезно для публичных эндпойнтов с разным поведением для анонимов.
    """
    if not token:
        return None
    try:
        payload = _decode_access_token(token)
    except HTTPException:
        return None

    user_id = int(payload.sub)
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def get_current_user_from_refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = TokenPayload.model_validate(payload)
    if data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(data.sub)
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
