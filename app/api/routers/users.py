"""
Users HTTP router.
Keeps HTTP/auth/transactions here; delegates DB work to the repository.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.core.security import hash_password
from app.schemas.user import (
    UserRegisterIn,
    UserUpdateIn,
    UserOut,
)
from app.models import User
from app.repositories import users as repo


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_own_profile(
    current_user: User = Depends(...),
) -> UserOut:
    """
    Get current user's profile.
    """
    return UserOut.model_validate(current_user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(...),
) -> UserOut:
    """
    Get user by id.
    Only allows admin users to get other users' profiles.
    """
    # Пользователь может запросить только свой профиль по ID,
    # либо администратор может запросить любой.
    # (Логика для администратора пока не реализована, поэтому проверка строгая)
    if user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only view your own profile")

    user = await repo.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
async def update_own_profile(
    payload: UserUpdateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(...),
) -> UserOut:
    """
    Partially update current user's fields.
    """
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        # Если нет полей для обновления, просто возвращаем текущего пользователя
        return UserOut.model_validate(current_user)

    try:
        # Обновляем текущего пользователя (current_user.id)
        updated_user = await repo.patch(db, user_id=current_user.id, fields=fields)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this tg_id or email already exists",
        )
    
    if not updated_user:
         raise HTTPException(status_code=404, detail="User not found")

    return UserOut.model_validate(updated_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(...),
) -> None:
    """
    Delete current user's profile.
    """
    deleted = await repo.delete_by_id(db, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    await db.commit()
    return None
