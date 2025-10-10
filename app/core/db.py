from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .settings import settings


engine = create_async_engine(settings.database_url, pool_pre_ping=True) # pool_pre_ping если соединение в пуле "уснуло" или умерло, движок перед использованием проверит его (ping)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """
    Declarative base class for SQLAlchemy models.

    All ORM models in the project should inherit from this class
    to share metadata and enable Alembic autogeneration.

    Example:
        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
    """
    ...


async def get_db() -> AsyncSession:
    async with SessionLocal() as s:
        yield s