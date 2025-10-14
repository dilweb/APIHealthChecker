from fastapi import APIRouter

router = APIRouter(prefix="/checks", tags=["checks"])


@router.post("/stub")
async def create_monitor() -> str:
    return "This is a stub endpoint for creating a monitor."

