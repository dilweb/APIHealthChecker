from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.db import Base
from typing import List
from app.models.user import User

class Monitor(Base):
    """
    Модель мониторинга.

    Хранит параметры задачи, которая периодически проверяет доступность URL для конкретного пользователя.
    Каждая запись описывает один монитор: какой сайт проверять, каким методом, какой статус считать успешным,
    с какой периодичностью выполнять запрос и что делать при паузе.

    `user_id` связывает монитор с владельцем (`User`).
    """

    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        doc="Первичный ключ монитора."
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Внешний ключ на пользователя, которому принадлежит монитор."
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Имя монитора, задаётся пользователем для удобства."
    )
    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
        doc="URL-адрес, который требуется проверять."
    )
    method: Mapped[str] = mapped_column(
        String(10),
        default="GET",
        nullable=False,
        doc="HTTP-метод проверки (GET, POST, HEAD и т.д.)."
    )
    expected_status: Mapped[int] = mapped_column(
        Integer,
        default=200,
        nullable=False,
        doc="Ожидаемый HTTP-код ответа, при котором монитор считается успешным."
    )
    interval_s: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
        doc="Интервал между проверками, в секундах."
    )
    timeout_ms: Mapped[int] = mapped_column(
        Integer,
        default=2500,
        nullable=False,
        doc="Тайм-аут HTTP-запроса, в миллисекундах."
    )
    is_paused: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Флаг паузы. Если True, проверки временно не выполняются."
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Дата и время создания монитора."
    )
    checks: Mapped[List["Check"]] = relationship(
        "Check",
        back_populates="monitor",
        cascade="all, delete-orphan",
        doc="Связанные результаты проверок.",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="monitors",
        doc="Пользователь, которому принадлежит монитор."
    )


    __table_args__ = (
        CheckConstraint("interval_s BETWEEN 10 AND 86400", name="ck_monitor_interval_range"),
        CheckConstraint("timeout_ms BETWEEN 100 AND 60000", name="ck_monitor_timeout_range"),
        CheckConstraint("method IN ('GET','POST','HEAD','PUT','DELETE')", name="ck_monitor_method_valid"),
        UniqueConstraint("user_id", "url", name="uq_monitor_user_url"),
        UniqueConstraint("user_id", "name", name="uq_monitor_user_name"),
        Index("ix_monitor_user_created", "user_id", "created_at"),
    )