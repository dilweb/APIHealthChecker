# app/services/monitor_checks.py

import httpx
import time
from datetime import datetime
import asyncio # Для демонстрации асинхронного выполнения вне Celery

# Возможно, вам понадобятся модели для сохранения результатов
# from app.models.check import Check  # Пример: модель для записи результатов проверки
# from app.repositories.checks import ChecksRepository # Пример: репозиторий для работы с БД

async def perform_monitor_check_async(monitor_id: int, url: str, expected_status_code: int = 200, timeout: int = 10):
    """
    Выполняет асинхронный HTTP-запрос к указанному URL и записывает результат.

    Args:
        monitor_id (int): ID монитора, к которому относится проверка.
        url (str): URL для проверки.
        expected_status_code (int): Ожидаемый HTTP-статус код.
        timeout (int): Таймаут для запроса в секундах.

    Returns:
        dict: Словарь с результатами проверки (статус, время ответа, ошибки).
    """
    start_time = time.monotonic()
    status = "UNKNOWN"
    response_time = -1.0
    error_message = None
    http_status_code = None

    try:
        async with httpx.AsyncClient() as client: # Используем AsyncClient для асинхронных запросов
            response = await client.get(url, timeout=timeout) # await для асинхронного вызова
        end_time = time.monotonic()
        response_time = (end_time - start_time) * 1000  # Время ответа в миллисекундах
        http_status_code = response.status_code

        if response.status_code == expected_status_code:
            status = "SUCCESS"
        else:
            status = "FAILED"
            error_message = f"Unexpected status code: {response.status_code}, expected {expected_status_code}"

    except httpx.TimeoutException: # Изменено исключение
        status = "FAILED"
        error_message = f"Request timed out after {timeout} seconds."
    except httpx.ConnectError: # Изменено исключение
        status = "FAILED"
        error_message = "Connection error: Could not connect to the server."
    except httpx.RequestError as e: # Изменено исключение
        status = "FAILED"
        error_message = f"An unexpected HTTPX request error occurred: {e}"
    except Exception as e:
        status = "FAILED"
        error_message = f"An unhandled error occurred: {e}"

    result = {
        "monitor_id": monitor_id,
        "url": url,
        "timestamp": datetime.utcnow(),
        "status": status,
        "http_status_code": http_status_code,
        "response_time_ms": response_time,
        "error_message": error_message,
    }

    # Здесь будет логика сохранения результата в базу данных
    # Например:
    # check_repo = ChecksRepository()
    # check_data = Check(**result)
    # await check_repo.create_check(check_data) # Если репозиторий тоже асинхронный

    print(f"Check for monitor_id={monitor_id} (URL: {url}): Status={status}, HTTP={http_status_code}, Time={response_time:.2f}ms, Error={error_message}")
    return result

# Пример использования (для тестирования)
async def main():
    print("Performing test checks...")
    await perform_monitor_check_async(1, "https://www.google.com", expected_status_code=200)
    await perform_monitor_check_async(2, "https://httpstat.us/500", expected_status_code=200)
    await perform_monitor_check_async(3, "http://nonexistent-domain-12345.com", expected_status_code=200, timeout=5)
    await perform_monitor_check_async(4, "https://www.google.com", expected_status_code=404)

if __name__ == "__main__":
    asyncio.run(main())
