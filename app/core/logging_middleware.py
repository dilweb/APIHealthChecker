import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.db import SessionLocal
from app.models.request_log import RequestLog


class DBLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP-запросов в базу данных.

    Основная задача — фиксировать каждое обращение к API:
    - метод запроса (GET, POST и т.д.),
    - путь (например, /monitors/5),
    - статус ответа,
    - задержку обработки в миллисекундах,
    - IP клиента.

    Механизм работы:
        1. Приходит HTTP-запрос от клиента.
        2. Middleware сохраняет момент начала обработки.
        3. Передаёт запрос дальше в приложение (`call_next(request)`).
        4. После выполнения эндпоинта считает время выполнения.
        5. Записывает данные о запросе в таблицу `request_logs`.
        6. Возвращает ответ пользователю.

    Таким образом, логирование происходит «прозрачно» для всей логики API
    и не влияет на работу самих эндпоинтов.
    """

    async def dispatch(self, request: Request, call_next):
        t0 = time.perf_counter()
        # Передаём запрос дальше в цепочку (эндпоинт или следующую middleware)
        response = await call_next(request)
        dt_ms = int((time.perf_counter() - t0) * 1000)
        # Извлекаем IP клиента, если возможно
        ip = request.client.host if request.client else None
        # Асинхронно записываем лог в базу в будущем отправлять метрики в Prometheus
        async with SessionLocal() as s:
            s.add(RequestLog(
                method=request.method,
                path=str(request.url.path),
                status=response.status_code,
                latency_ms=dt_ms,
                ip=ip
            ))
            await s.commit()

        # Возвращаем ответ клиенту
        return response
