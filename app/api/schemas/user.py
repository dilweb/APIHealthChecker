from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


# ========================== User Schemas ========================== #

class UserBase(BaseModel):
    """Базовая схема пользователя. Содержит только почту."""
    email: EmailStr


class UserCreate(UserBase):
    """Используется при регистрации или первом обращении к боту."""
    tg_id: int

    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя (сейчас только email)."""
    email: Optional[EmailStr] = None

    model_config = ConfigDict(extra="forbid")


class UserOut(BaseModel):
    """Схема для возврата данных пользователю или клиенту."""
    id: int
    tg_id: int
    email: EmailStr

    model_config = ConfigDict(extra="forbid", from_attributes=True)