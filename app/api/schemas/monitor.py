from pydantic import BaseModel, AnyHttpUrl, Field, ConfigDict
from typing import Optional


# ========================== Monitor Schemas ========================== #

class MonitorCreate(BaseModel):
    """
    Схема создания монитора.

    Используется при добавлении нового URL для проверки.
    Содержит все параметры, которые задаёт пользователь вручную.
    """
    name: str = Field(min_length=1, max_length=200, description="Имя монитора, отображаемое пользователю.")
    url: AnyHttpUrl = Field(description="Проверяемый URL-адрес.")
    method: str = Field(default="GET", description="HTTP-метод, используемый при проверке.")
    expected_status: int = Field(default=200, description="HTTP-статус, считающийся успешным.")
    interval_s: int = Field(default=60, description="Интервал проверки в секундах.")
    timeout_ms: int = Field(default=2500, description="Тайм-аут HTTP-запроса в миллисекундах.")

    model_config = ConfigDict(extra="forbid")


class MonitorOut(MonitorCreate):
    """
    Схема вывода монитора.

    Возвращается клиенту после создания или запроса данных о мониторе.
    """
    id: int = Field(description="Уникальный идентификатор монитора.")
    user_id: int = Field(default=None, description="ID пользователя-владельца монитора.")

    model_config = ConfigDict(extra="forbid", from_attributes=True)


class MonitorUpdate(BaseModel):
    """
    Схема обновления монитора.

    Используется для PATCH/PUT-запросов при изменении параметров мониторинга.
    Все поля опциональны.
    """
    name: str = Field(min_length=1, max_length=200, description="Новое имя монитора.")
    expected_status: Optional[int] = Field(default=200, description="Ожидаемый статус ответа.")
    interval_s: Optional[int] = Field(default=60, description="Интервал проверки в секундах.")
    timeout_ms: Optional[int] = Field(default=2500, description="Тайм-аут HTTP-запроса в миллисекундах.")
    is_paused: Optional[bool] = Field(default=False, description="Флаг паузы мониторинга.")

    model_config = ConfigDict(extra="forbid")