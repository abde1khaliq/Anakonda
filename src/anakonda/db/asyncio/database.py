# async_db.py
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from anakonda.db.base import BaseDatabaseConfig


class AsyncDatabase(BaseDatabaseConfig):
    def __init__(self, url: str, **kwargs):
        super().__init__(url, **kwargs)
        self._engine = create_async_engine(self.url, **self._engine_kwargs())
        self._session_factory = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    @asynccontextmanager
    async def session(self):
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def health_check(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def close(self) -> None:
        await self._engine.dispose()
