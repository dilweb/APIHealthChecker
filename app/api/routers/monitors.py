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
from app.schemas.user import UserOut
from app.repositories import monitors as repo

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


@router.post("/", response_model=MonitorOut, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    payload: MonitorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(...),
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
    url_str = str(payload.url)

    if await repo.exists_url_for_user(db, user_id=current_user.id, url=url_str):
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")

    try:
        obj = await repo.create(
            db,
            user_id=current_user.id,
            name=payload.name,
            url=url_str,
            method=payload.method,
            expected_status=payload.expected_status,
            interval_s=payload.interval_s,
            timeout_ms=payload.timeout_ms,
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # race or DB unique constraint
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")

    return MonitorOut.model_validate(obj)


@router.get("/", response_model=List[MonitorOut])
async def list_monitors(
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(...),
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
    rows = await repo.list_for_user(db, user_id=current_user.id, limit=limit, offset=offset)
    return [MonitorOut.model_validate(r) for r in rows]


@router.get("/{monitor_id}", response_model=MonitorOut)
async def get_monitor(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(...),
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
    obj = await repo.get_by_id_for_user(db, user_id=current_user.id, monitor_id=monitor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return MonitorOut.model_validate(obj)


@router.patch("/{monitor_id}", response_model=MonitorOut)
async def update_monitor(
    monitor_id: int,
    payload: MonitorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(...),
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
    fields = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "url" in fields:
        fields["url"] = str(fields["url"])

    try:
        obj = await repo.patch(db, user_id=current_user.id, monitor_id=monitor_id, fields=fields)
        if not obj:
            raise HTTPException(status_code=404, detail="Monitor not found")
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Monitor with this url already exists")

    return MonitorOut.model_validate(obj)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitor(
    monitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(...),
) -> None:
    """
    Delete a monitor owned by the current user.

    Path:
        monitor_id: target monitor id.

    Raises:
        HTTPException 404: monitor not found.
    """
    deleted = await repo.delete_for_user(db, user_id=current_user.id, monitor_id=monitor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Monitor not found")
    await db.commit()
    return None
