import os
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(f'sqlite+aiosqlite:///{os.environ.get("SQLITE_PATH")}', echo=True)
#engine = create_async_engine('sqlite+aiosqlite:///rolls.db', echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class Base(DeclarativeBase):
    pass

