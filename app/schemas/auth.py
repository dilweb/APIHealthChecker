# app/schemas/auth.py
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    tg_id: Optional[int] = None
    model_config = ConfigDict(extra="forbid")

class UserLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    model_config = ConfigDict(extra="forbid")

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    model_config = ConfigDict(extra="forbid")
