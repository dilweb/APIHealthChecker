from sqlalchemy import String, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.db import Base

class RequestLog(Base):
    """
    Модель логов входящих HTTP-запросов к API.

    Каждая запись отражает один запрос, прошедший через приложение FastAPI.
    Лог хранит минимальный набор данных: метод, путь, статус ответа,
    задержку обработки и IP клиента.

    Используется для базового мониторинга нагрузки, отладки, аудита
    и выявления подозрительной активности (например, DDoS или частых 500-ок).
    """

    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        doc="Первичный ключ записи лога."
    )
    method: Mapped[str] = mapped_column(
        String(8),
        doc="HTTP-метод запроса (GET, POST, PUT, DELETE и т.д.)."
    )
    path: Mapped[str] = mapped_column(
        String(512),
        doc="Путь запроса относительно корня API (например, /monitors/42/checks)."
    )
    status: Mapped[int] = mapped_column(
        Integer,
        doc="HTTP-код ответа, который вернул сервер."
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer,
        doc="Время обработки запроса на сервере, в миллисекундах."
    )
    ip: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="IP-адрес клиента, если удалось определить."
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        doc="Метка времени, когда запрос был выполнен."
    )

    __table_args__ = (
        Index("ix_request_logs_created", "created_at"),
    )
