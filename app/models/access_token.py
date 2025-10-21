from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from app.core.db import Base


class AccessToken(SQLAlchemyBaseAccessTokenTable[int], Base):
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False)