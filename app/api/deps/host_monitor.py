from app.api.schemas.monitor import MonitorOut

async def get_current_monitor_stub() -> MonitorOut:
    # Возвращаем ID существующего монитора
    return MonitorOut(id=1, user_id=1)