from fastapi import APIRouter
from app.api.schemas.check import CheckOut
from app.core.db import get_db
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

router = APIRouter(prefix="/checks", tags=["checks"])


@router.post("/stub")
async def create_monitor() -> str:
    return "This is a stub endpoint for creating a monitor."

