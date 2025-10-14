from typing import Literal
from pydantic import BaseModel, ConfigDict

# Пара токенов на ответ register/login/refresh
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    model_config = ConfigDict(extra="forbid")

# Полезная нагрузка внутри JWT (то, что декодируем)
class TokenPayload(BaseModel):
    sub: str  # user_id как строка; в коде приводим к int по месту
    type: Literal["access", "refresh"]
    exp: int  # unix timestamp
    model_config = ConfigDict(extra="ignore")  # JWT может нести лишние поля
