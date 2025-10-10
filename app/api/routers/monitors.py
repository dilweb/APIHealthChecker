from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.models.monitor import Monitor
from app.api.schemas.monitor import MonitorCreate, MonitorUpdate, MonitorOut
from app.api.schemas.user import UserOut
from app.api.deps.auth import get_current_user_stub

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


@router.post("/", response_model=MonitorOut, status_code=status.HTTP_201_CREATED)
async def create_monitor(payload: MonitorCreate,
                         db: AsyncSession = Depends(get_db),
                         current_user: UserOut = Depends(get_current_user_stub)
) -> MonitorOut:
    """
    Создать монитор.
    Уникальные поля: url.
    """
    data = payload.model_dump()
    data["url"] = str(payload.url)  # конвертируем AnyHttpUrl в str для SQLAlchemy

    res = Monitor(name=payload.name, url=data["url"], method=payload.method,
                  expected_status=payload.expected_status, interval_s=payload.interval_s,
                  timeout_ms=payload.timeout_ms, user_id=current_user.id)
    db.add(res)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")
    await db.refresh(res)
    return MonitorOut.model_validate(res)


@router.get("/", response_model=List[MonitorOut])
async def list_monitors(
        db: AsyncSession = Depends(get_db),
        limit: int = 25,
        offset: int = 0,
) -> List[MonitorOut]:
    """
    Получить список всех мониторов.
    """
    res = await db.execute(select(Monitor).order_by(Monitor.id).limit(limit).offset(offset))
    rows = res.scalars().all()
    return [MonitorOut.model_validate(row) for row in rows]


@router.get("/{monitor_id}", response_model=MonitorOut)
async def get_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)) -> MonitorOut:
    """
    Получить монитор по ID.
    """
    res = await db.get(Monitor, monitor_id)
    if not res:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return MonitorOut.model_validate(res)


@router.patch("/{monitor_id}", response_model=MonitorOut)
async def update_monitor(monitor_id: int, payload: MonitorUpdate, db: AsyncSession = Depends(get_db)) -> MonitorOut:
    """
    Частичное обновление монитора.
    """
    res = await db.get(Monitor, monitor_id)
    if not res:
        raise HTTPException(status_code=404, detail="Monitor not found")

    update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(res, key, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")
    await db.refresh(res)
    return MonitorOut.model_validate(res)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(monitor_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """
    Удалить монитор по ID.
    """
    res = await db.get(Monitor, monitor_id)
    if not res:
        raise HTTPException(status_code=404, detail="Monitor not found")

    await db.delete(res)
    await db.commit()
    return None