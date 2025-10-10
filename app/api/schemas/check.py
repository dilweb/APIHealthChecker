from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ========================== Check Schemas ========================== #

class CheckOut(BaseModel):
    """
    Схема результата проверки.

    Возвращается при запросе истории проверок или последнего статуса.
    """
    id: int = Field(description="Уникальный идентификатор проверки.")
    monitor_id: int = Field(description="ID монитора, к которому относится проверка.")
    ts: datetime = Field(description="Время выполнения проверки.")
    latency_ms: int = Field(description="Задержка отклика сервера, в миллисекундах.")
    status_code: int = Field(description="HTTP-код ответа.")
    ok: bool = Field(description="Флаг успешности проверки.")
    error: Optional[str] = Field(default=None, description="Описание ошибки, если она возникла.")