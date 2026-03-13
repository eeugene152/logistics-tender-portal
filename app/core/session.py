from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
  AsyncSession, async_sessionmaker, create_async_engine
)

from app.core.config import settings

# 1. Создаем движок (engine)
engine = create_async_engine(
    settings.DATABASE_URL,
    # Включаем True на время разработки, чтобы видеть SQL-запросы в консоли
    echo=True,
    future=True
)

# 2. Создаем фабрику сессий (sessionmaker)
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    # Для подстраховки некоторых линтеров
    class_=AsyncSession
)


# 3. dependency для FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
