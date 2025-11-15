# app/api/routers/monitors.py
"""
HTTP router for Monitor CRUD.
Keeps HTTP, auth, and transaction concerns here; delegates DB work to repository.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.schemas.monitor import MonitorCreate, MonitorUpdate, MonitorOut
from app.schemas.user import UserRead
from app.repositories.monitors import MonitorRepository # Импортируем класс репозитория
from app.api.routers.auth import current_active_user
from app.celery.celery_app import celery_app # Импортируем Celery приложение
# from app.services.monitor_checks import perform_monitor_check_task # Импортируем задачу Celery

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


@router.post("/", response_model=MonitorOut, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    payload: MonitorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(current_active_user),
) -> MonitorOut:
    """
    Create a new monitor for the current user.

    Body:
        MonitorCreate: validated payload with AnyHttpUrl, method, expected_status, intervals.

    Returns:
        MonitorOut: created monitor.

    Raises:
        HTTPException 409: if URL already exists for this user.
    """
    monitor_repo = MonitorRepository(db)
    url_str = str(payload.url)

    if await monitor_repo.exists_url_for_user(user_id=current_user.id, url=url_str):
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")

    try:
        obj = await monitor_repo.create(
            user_id=current_user.id,
            name=payload.name,
            url=url_str,
            method=payload.method,
            expected_status=payload.expected_status,
            interval_s=payload.interval_s,
            timeout_ms=payload.timeout_ms,
        )
        await db.commit()
        await db.refresh(obj) # Обновляем объект после коммита для получения ID

        # Добавляем задачу в Celery Beat
        task_name = f"monitor-{obj.id}"
        celery_app.conf.beat_schedule[task_name] = {
            'task': 'perform_monitor_check_task', # Имя задачи Celery
            'schedule': obj.interval_s,
            'args': (obj.id,), # Передаем только monitor_id
            'options': {'queue': 'monitor_checks'} # Опционально: можно использовать отдельную очередь
        }
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")

    return MonitorOut.model_validate(obj)


@router.get("/", response_model=List[MonitorOut])
async def list_monitors(
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(current_active_user),
    limit: int = 25,
    offset: int = 0,
) -> List[MonitorOut]:
    """
    List monitors owned by the current user.

    Query:
        limit: pagination limit (default 25).
        offset: pagination offset (default 0).

    Returns:
        List[MonitorOut]: monitors page.
    """
    monitor_repo = MonitorRepository(db)
    rows = await monitor_repo.list_for_user(user_id=current_user.id, limit=limit, offset=offset)
    return [MonitorOut.model_validate(r) for r in rows]


@router.get("/{monitor_id}", response_model=MonitorOut)
async def get_monitor(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(current_active_user),
) -> MonitorOut:
    """
    Get a single monitor by id limited to current user.

    Path:
        monitor_id: target monitor id.

    Returns:
        MonitorOut.

    Raises:
        HTTPException 404: monitor not found or not owned by user.
    """
    monitor_repo = MonitorRepository(db)
    obj = await monitor_repo.get_by_id_for_user(user_id=current_user.id, monitor_id=monitor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return MonitorOut.model_validate(obj)


@router.patch("/{monitor_id}", response_model=MonitorOut)
async def update_monitor(
    monitor_id: int,
    payload: MonitorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(current_active_user),
) -> MonitorOut:
    """
    Partially update a monitor owned by the current user.

    Path:
        monitor_id: target monitor id.

    Body:
        MonitorUpdate: partial fields to update.

    Returns:
        MonitorOut.

    Raises:
        HTTPException 404: monitor not found.
        HTTPException 409: unique url conflict.
    """
    monitor_repo = MonitorRepository(db)
    fields = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "url" in fields:
        fields["url"] = str(fields["url"])

    try:
        obj = await monitor_repo.patch(user_id=current_user.id, monitor_id=monitor_id, fields=fields)
        if not obj:
            raise HTTPException(status_code=404, detail="Monitor not found")
        await db.commit()
        await db.refresh(obj) # Обновляем объект после коммита для получения актуальных данных

        # Обновляем задачу в Celery Beat, если монитор не на паузе
        if not obj.is_paused:
            task_name = f"monitor-{obj.id}"
            celery_app.conf.beat_schedule[task_name] = {
                'task': 'perform_monitor_check_task',
                'schedule': obj.interval_s,
                'args': (obj.id,),
                'options': {'queue': 'monitor_checks'}
            }
        else:
            # Если монитор поставлен на паузу, удаляем задачу из Celery Beat
            task_name = f"monitor-{obj.id}"
            if task_name in celery_app.conf.beat_schedule:
                del celery_app.conf.beat_schedule[task_name]
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")

    return MonitorOut.model_validate(obj)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(current_active_user),
) -> None:
    """
    Delete a monitor owned by the current user.

    Path:
        monitor_id: target monitor id.

    Raises:
        HTTPException 404: monitor not found.
    """
    monitor_repo = MonitorRepository(db)
    
    # Сначала получаем монитор, чтобы получить его ID для удаления из Celery Beat
    obj = await monitor_repo.get_by_id_for_user(user_id=current_user.id, monitor_id=monitor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitor not found")

    deleted = await monitor_repo.delete_for_user(user_id=current_user.id, monitor_id=monitor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Monitor not found")
    await db.commit()

    # Удаляем задачу из Celery Beat
    task_name = f"monitor-{obj.id}"
    if task_name in celery_app.conf.beat_schedule:
        del celery_app.conf.beat_schedule[task_name]
    return None
