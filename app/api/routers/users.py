from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.models.user import User
from app.api.schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    """
    Создать пользователя.
    Уникальные поля: tg_id, email.
    """
    res = User(tg_id=payload.tg_id, email=payload.email)
    db.add(res)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="User with this tg_id or email already exists")
    await db.refresh(res)
    return UserOut.model_validate(res)


@router.get("/", response_model=List[UserOut])
async def list_users(
        db: AsyncSession = Depends(get_db),
        limit: int = 50,
        offset: int = 0,
) -> List[UserOut]:
    """
    Получить список всех пользователей с пагинацией.
    """
    res = await db.execute(select(User).order_by(User.id).limit(limit).offset(offset))
    rows = res.scalars().all()
    return [UserOut.model_validate(row) for row in rows]


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> UserOut:
    """
    Получить пользователя по ID.
    """
    res = await db.get(User, user_id)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(res)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)) -> UserOut:
    """
    Частичное обновление пользователя.
    Сейчас поддерживается смена email.
    """
    res = await db.get(User, user_id)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump(exclude_unset=True, exclude_none=True) # игнорируем пустые поля и поля со значением None

    if not data:
        return UserOut.model_validate(res)

    for key, value in data.items():
        setattr(res, key, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="User with this tg_id or email already exists")
    await db.refresh(res)
    return UserOut.model_validate(res)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """
    Удалить пользователя по ID.
    """
    res = await db.get(User, user_id)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(res)
    await db.commit()
    return None