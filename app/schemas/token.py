from typing import Literal
from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    """Пара JWT-токенов, которую отдаём на /auth/register и /auth/login."""
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    model_config = ConfigDict(extra="forbid")


class TokenRefresh(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    """Полезная нагрузка внутри JWT. Декодируем и валидируем ей."""
    sub: str               # user_id как строка, приводим к int по месту
    type: Literal["access", "refresh"]
    exp: int               # unix timestamp истечения (проверяется на декоде)
    model_config = ConfigDict(extra="ignore")
