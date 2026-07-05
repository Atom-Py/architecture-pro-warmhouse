from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infra.db.engine import engine

session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
