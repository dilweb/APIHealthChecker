from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.db import Base


class User(Base):
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
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Метка времени создания записи."
    )

    monitors = relationship(
        "Monitor",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Список мониторов, принадлежащих пользователю."
    )