"""
Repository layer for User entity.
Encapsulates DB access so routers stay thin and testable.
"""

from typing import Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create(db: AsyncSession, *, email: str, tg_id: int | None, hashed_password: str, is_active: bool = True) -> User:
    """
    Insert a new user.

    Args:
        db: Async SQLAlchemy session.
        email: User email (must be unique).
        tg_id: Optional Telegram ID (must be unique if provided).
        hashed_password: Argon2id hash (no plaintext here).
        is_active: Whether the user is active.

    Returns:
        Persisted User instance (refreshed).
    """
    obj = User(email=email, tg_id=tg_id, hashed_password=hashed_password, is_active=is_active)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


async def get_by_id(db: AsyncSession, *, user_id: int) -> User | None:
    """
    Fetch user by primary key.

    Args:
        db: Async SQLAlchemy session.
        user_id: Target user id.

    Returns:
        User if found, else None.
    """
    return await db.get(User, user_id)


async def get_by_email(db: AsyncSession, *, email: str) -> User | None:
    """
    Fetch user by email.

    Args:
        db: Async SQLAlchemy session.
        email: User email.

    Returns:
        User if found, else None.
    """
    res = await db.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def list_users(
    db: AsyncSession, *, limit: int = 50, offset: int = 0
) -> Sequence[User]:
    """
    List users with pagination.

    Args:
        db: Async SQLAlchemy session.
        limit: Max rows to return.
        offset: Rows to skip.

    Returns:
        Sequence of User objects.
    """
    res = await db.execute(
        select(User).order_by(User.id).limit(limit).offset(offset)
    )
    return res.scalars().all()


async def patch(
    db: AsyncSession, *, user_id: int, fields: dict
) -> User | None:
    """
    Partially update user fields.

    Args:
        db: Async SQLAlchemy session.
        user_id: Target user id.
        fields: Dict of fields to update (already validated).

    Returns:
        Updated User if found, else None.
    """
    res = await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**fields)
        .returning(User)
    )
    return res.scalar_one_or_none()


async def delete_by_id(db: AsyncSession, *, user_id: int) -> bool:
    """
    Delete user by id.

    Args:
        db: Async SQLAlchemy session.
        user_id: Target user id.

    Returns:
        True if a row was deleted, else False.
    """
    res = await db.execute(delete(User).where(User.id == user_id))
    affected = res.rowcount or 0
    return affected > 0
