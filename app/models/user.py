from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.db import Base
from fastapi_users.db import SQLAlchemyBaseUserTable


class User(Base, SQLAlchemyBaseUserTable):
    """
    Модель пользователя.

    Хранит базовую информацию о клиенте Telegram, который создал хотя бы один монитор.
    `tg_id` — идентификатор пользователя в Telegram (уникален).
    `email` — адрес, на который отправляются уведомления.
    `created_at` — дата регистрации в системе.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        doc="Первичный ключ пользователя."
    )
    tg_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        doc="Уникальный Telegram ID пользователя."
    )
    email: Mapped[str] = mapped_column(
        String(250),
        unique=True,
        nullable=False,
        doc="Электронная почта для оповещений и идентификации."
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Хэш пароля пользователя."
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Метка времени создания записи."
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Статус активности пользователя."
    )
    monitors = relationship(
        "Monitor",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Список мониторов, принадлежащих пользователю."
    )