from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config.settings import settings


def create_engine() -> AsyncEngine:
    return create_async_engine(settings.DATABASE.URL, pool_pre_ping=True)


engine = create_engine()
