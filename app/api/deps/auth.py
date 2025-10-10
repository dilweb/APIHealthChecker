from app.api.schemas.user import UserOut

async def get_current_user_stub() -> UserOut:
    # Возвращаем ID существующего пользователя
    return UserOut(id=1, tg_id=12345, email="test@example.com")