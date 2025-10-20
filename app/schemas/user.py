from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from fastapi_users import schemas
from sqlalchemy import DateTime

# ========================== User Schemas ========================== #

class UserRead(schemas.BaseUser[int]):
    tg_id: Optional[int] = None
    created_at: DateTime


class UserCreate(schemas.BaseUserCreate):
    tg_id: Optional[int] = None
    password: str = Field(min_length=8, max_length=64)


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
    tg_id: Optional[int] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=64)