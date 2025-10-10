from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Text, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.db import Base


class Check(Base):
    """
    Модель результата проверки.

    Каждая запись фиксирует одну конкретную попытку проверки URL,
    заданного в `Monitor`. Это своего рода журнал выполнения задач:
    время проверки, статус ответа, длительность запроса, успешность
    и возможная ошибка.

    Используется для построения истории проверок, метрик доступности
    и уведомлений о сбоях.
    """

    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        doc="Первичный ключ проверки."
    )
    monitor_id: Mapped[int] = mapped_column(
        ForeignKey("monitors.id", ondelete="CASCADE"),
        nullable=False,
        doc="Внешний ключ на связанный монитор."
    )
    ts: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Метка времени, когда была выполнена проверка."
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Задержка (в миллисекундах) между отправкой запроса и получением ответа."
    )
    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="HTTP-статус ответа от сервера (например, 200, 404, 500)."
    )
    ok: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        doc="Флаг успешности: True, если `status_code` совпал с ожидаемым."
    )
    error: Mapped[str | None] = mapped_column(
        Text,
        doc="Описание ошибки, если запрос завершился сбоем или тайм-аутом."
    )
    monitor: Mapped["Check"] = relationship(
        "Monitor",
        back_populates="checks",
        doc="Связанный монитор.",
    )
    __table_args__ = (
        Index("ix_checks_monitor_ts", "monitor_id", "ts"),
        CheckConstraint("latency_ms >= 0", name="ck_check_latency_nonnegative"),
        CheckConstraint("status_code BETWEEN 100 AND 599", name="ck_check_status_range"),
    )