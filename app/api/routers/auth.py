# app/api/routers/auth.py
"""
Auth endpoints: register/login with Argon2id + JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.core.security import (
    hash_password, verify_password, needs_rehash,
    create_access_token, create_refresh_token
)
from app.schemas.user import UserRegisterIn
from app.schemas.token import Token, TokenRefresh, TokenPayload
from app.repositories import users as users_repo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterIn, db: AsyncSession = Depends(get_db)) -> Token:
    """
    Register a new user:
    - hash password with Argon2id
    - store user
    - return access/refresh tokens
    """
    hashed = hash_password(payload.password)
    try:
        user = await users_repo.create(
            db,
            email=str(payload.email),
            tg_id=payload.tg_id,
            hashed_password=hashed,
            is_active=True
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="User with this email or tg_id already exists")

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> Token:
    """
    Login:
    - fetch user by email (from form_data.username)
    - verify password
    - optional rehash
    - return tokens
    """
    user = await users_repo.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(form_data.password)
        await db.commit()

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    payload: TokenRefresh,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Refresh access token
    """
    from jose import jwt, JWTError
    from app.core.settings import settings

    try:
        payload_data = jwt.decode(
            payload.refresh_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG]
        )
        token_payload = TokenPayload.model_validate(payload_data)
        if token_payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await users_repo.get(db, id=int(token_payload.sub))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
