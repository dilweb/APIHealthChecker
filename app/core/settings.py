from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """
    Application settings loaded from the `.env` file and environment variables.

    Attributes:
        DB_HOST (str): Hostname of the PostgreSQL server (e.g. 'localhost' or 'postgres' in Docker).
        DB_PORT (int): Port number of the PostgreSQL server (default 5432).
        DB_USER (str): Database username.
        DB_PASS (str): Database password.
        DB_NAME (str): Database name to connect to.
        API_DEBUG (bool): Flag for enabling debug mode in the API.

    Properties:
        database_url (str): Assembled async connection URL for SQLAlchemy with asyncpg driver.
    """

    # ========================== Data Base ========================== #
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    API_DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    # ========================== JWT ========================== #
    # Возможно, стоит вынести в отдельный класс настроек, если будет JWT
    JWT_SECRET: str
    JWT_ALG: Literal["HS256"] = "HS256"
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days


    # ========================== Auth Cookies ========================== #
    AUTH_COOKIE_NAME: str = "fastapi_users_access_token"
    AUTH_COOKIE_LIFETIME_MINUTES: int = 60 * 24
    HTTPS_ENABLED: bool = os.getenv("HTTPS_ENABLED", "False").lower() in ("true", "1", "t") # Включение флага Secure


settings = Settings()


# print(settings.database_url)
# print(os.getenv("DB_HOST"))