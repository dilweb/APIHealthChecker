from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional


# ========================== User Schemas ========================== #

class UserBase(BaseModel):
    """Базовая схема пользователя. Содержит только почту."""
    email: EmailStr
    model_config = ConfigDict(extra="forbid")


class UserRegisterIn(UserBase):
    """Регистрация: email + пароль (+ опционально tg_id)"""
    password: str = Field(min_length=8, max_length=64)
    tg_id: Optional[int] = None
    is_active: bool = True


class UserLoginIn(BaseModel):
    """Вход: только учётные данные"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    model_config = ConfigDict(extra="forbid")


class UserUpdateIn(BaseModel):
    """Схема для обновления данных пользователя."""
    email: Optional[EmailStr] = None
    tg_id: Optional[int] = None
    model_config = ConfigDict(extra="forbid")


class UserOut(BaseModel):
    """Схема для возврата данных пользователю или клиенту."""
    id: int
    email: EmailStr
    tg_id: Optional[int] = None
    is_active: bool
    model_config = ConfigDict(extra="forbid", from_attributes=True)