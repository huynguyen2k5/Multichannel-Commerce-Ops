from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings


def build_async_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(
        database_url,
        pool_pre_ping=True,
    )


settings = get_settings()
engine = build_async_engine(settings.database_url)
SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        yield session
