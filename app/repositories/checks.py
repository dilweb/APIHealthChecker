from datetime import datetime
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.check import Check

class ChecksRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        monitor_id: int,
        ts: datetime,
        latency_ms: int,
        status_code: int,
        ok: bool,
        error: str | None = None,
    ) -> Check:
        """
        Создает новую запись проверки в базе данных.
        """
        obj = Check(
            monitor_id=monitor_id,
            ts=ts,
            latency_ms=latency_ms,
            status_code=status_code,
            ok=ok,
            error=error,
        )
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, check_id: int) -> Check | None:
        """
        Получает запись проверки по ID.
        """
        q = select(Check).where(Check.id == check_id)
        res = await self.db.execute(q)
        return res.scalar_one_or_none()

    async def list(self, monitor_id: int | None = None, limit: int = 25, offset: int = 0) -> Sequence[Check]:
        """
        Получает список записей проверок, опционально фильтруя по monitor_id.
        """
        q = select(Check).order_by(Check.ts.desc()).limit(limit).offset(offset)
        if monitor_id:
            q = q.where(Check.monitor_id == monitor_id)
        res = await self.db.execute(q)
        return res.scalars().all()