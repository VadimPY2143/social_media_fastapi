from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from database_files.database import engine

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        yield session
