import contextlib
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

from app.config import SYNC_DB_URL, ASYNC_DB_URL

async_engine = create_async_engine(
    ASYNC_DB_URL,
    # echo=True,
)
sync_engine = create_engine(SYNC_DB_URL, pool_timeout=5)
AsyncSessionFactory = sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)
SyncSessionFactory = sessionmaker(bind=sync_engine, expire_on_commit=False)


async def create_async_session() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session


@contextlib.asynccontextmanager
async def context_async_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session


def create_sync_session() -> Session:
    return SyncSessionFactory()
