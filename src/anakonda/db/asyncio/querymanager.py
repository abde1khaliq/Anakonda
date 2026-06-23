from sqlalchemy import select

from anakonda.db.base_querymanager import BaseQueryManager


class AsyncQueryManager(BaseQueryManager):
    async def all(self):
        async with self.db.session() as session:
            result = await session.execute(select(self.model))
            return result.scalars().all()