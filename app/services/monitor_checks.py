# app/services/monitor_checks.py
import httpx
import time
from datetime import datetime
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal, engine
from app.models.check import Check
from app.repositories.checks import ChecksRepository
from app.repositories.monitors import MonitorRepository
from app.models.monitor import Monitor
from app.celery.celery_app import celery_app


async def perform_monitor_check_async(
    db: AsyncSession,
    monitor_id: int,
    url: str,
    expected_status_code: int = 200,
    timeout: int = 10,
) -> Check:
    """
    Выполняет асинхронный HTTP-запрос к указанному URL и записывает результат.

    Args:
        db (AsyncSession): Асинхронная сессия SQLAlchemy.
        monitor_id (int): ID монитора, к которому относится проверка.
        url (str): URL для проверки.
        expected_status_code (int): Ожидаемый HTTP-статус код.
        timeout (int): Таймаут для запроса в секундах.

    Returns:
        Check: Созданный объект Check.
    """
    start_time = time.monotonic()
    ok_status = False
    latency_ms = -1
    error_message = None
    status_code = None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
        end_time = time.monotonic()
        latency_ms = (end_time - start_time) * 1000
        status_code = response.status_code

        if response.status_code == expected_status_code:
            ok_status = True
        else:
            error_message = f"Unexpected status code: {response.status_code}, expected {expected_status_code}"

    except httpx.TimeoutException:
        error_message = f"Request timed out after {timeout} seconds."
        status_code = 599
        latency_ms = 0
    except httpx.ConnectError:
        error_message = "Connection error: Could not connect to the server."
        status_code = 599
        latency_ms = 0
    except httpx.RequestError as e:
        error_message = f"An unexpected HTTPX request error occurred: {e}"
        status_code = 599
        latency_ms = 0
    except Exception as e:
        error_message = f"An unhandled error occurred: {e}"
        status_code = 599
        latency_ms = 0

    check_repo = ChecksRepository(db)
    created_check = await check_repo.create(
        monitor_id=monitor_id,
        ts=datetime.now(),
        latency_ms=int(latency_ms),
        status_code=status_code,
        ok=ok_status,
        error=error_message,
    )
    await db.commit() # Фиксируем изменения здесь
    await db.refresh(created_check) # Обновляем объект, чтобы получить актуальные данные (например, ID)

    print(
        f"Check for monitor_id={monitor_id} (URL: {url}): OK={ok_status}, "
        f"HTTP={status_code}, Time={latency_ms:.2f}ms, Error={error_message}"
    )
    return created_check


@celery_app.task(name="perform_monitor_check_task", bind=True)
async def perform_monitor_check_task(self, monitor_id: int):
    """
    Задача Celery для выполнения мониторинга URL.
    Получает monitor_id, извлекает параметры из БД и вызывает perform_monitor_check_async.
    """
    async with SessionLocal() as session:
        monitor_repo = MonitorRepository(session)
        monitor = await monitor_repo.get_by_id(monitor_id=monitor_id)

        if not monitor or monitor.is_paused:
            print(f"Monitor {monitor_id} not found or paused. Skipping check.")
            return None

        timeout_s = monitor.timeout_ms / 1000

        print(f"Starting check for monitor_id={monitor.id} (URL: {monitor.url})")
        check_result = await perform_monitor_check_async(
            session,
            monitor.id,
            monitor.url,
            monitor.expected_status,
            timeout_s
        )
        # await session.commit() # Удаляем явный коммит отсюда
        print(f"Check for monitor_id={monitor.id} completed. Result ID: {check_result.id}")
        return check_result.id

# Пример использования (для тестирования)
async def main():
    print("Performing test checks...")
    async with SessionLocal() as session:
        # Для тестирования Celery задачи, вы можете вызвать ее так:
        # await perform_monitor_check_task(1) # Замените 1 на реальный monitor_id из вашей БД

        # Или, если вы хотите протестировать perform_monitor_check_async напрямую:
        # Важно: для этого нужно, чтобы в БД был монитор с ID 1
        from app.repositories.monitors import MonitorRepository
        monitor_repo = MonitorRepository(session)
        test_monitor = await monitor_repo.get_by_id(monitor_id=1)
        if test_monitor:
            check1 = await perform_monitor_check_async(session, test_monitor.id, test_monitor.url, test_monitor.expected_status, test_monitor.timeout_ms / 1000)
            print(f"Direct Check 1 result: id={check1.id}, ok={check1.ok}, status_code={check1.status_code}, latency={check1.latency_ms}ms, error={check1.error}")
        else:
            print("Test monitor with ID 1 not found. Please create one for direct testing.")

        print("To test Celery task, run Celery worker and beat, then trigger task via API or manually.")

# if __name__ == "__main__":
#     asyncio.run(main())

