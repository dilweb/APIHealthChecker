from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.settings import settings

# создаем контекст с Argon2id
pwd_context = CryptContext(
    schemes=["argon2id"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=2,
    argon2__type="ID"
)


def hash_password(plain: str) -> str:
    """Возвращает Argon2id-хэш с параметрами из контекста."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет пароль, независимо от используемой схемы (bcrypt/argon2)."""
    return pwd_context.verify(plain, hashed)


def needs_rehash(hashed: str) -> bool:
    """Проверяет, нужно ли пересчитать хэш пароля с новыми параметрами Argon2id."""
    return pwd_context.needs_update(hashed)


def _exp(minutes: int = 15) -> int:
    return int((datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)).timestamp())


def create_access_token(subject: str | int) -> str:
    payload = {"sub": str(subject), "type": "access", "exp": _exp(settings.ACCESS_EXPIRES_MIN)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_refresh_token(subject: str | int) -> str:
    expires = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_EXPIRES_DAYS)
    payload = {"sub": str(subject), "type": "refresh", "exp": int(expires.timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

