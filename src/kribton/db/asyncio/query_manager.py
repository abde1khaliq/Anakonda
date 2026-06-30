from sqlalchemy import select
from kribton.db.base_query_manager import BaseQueryManager


class AsyncQueryManager(BaseQueryManager):
    async def all(self):
        async with self.db.session() as session:
            result = await session.execute(select(self.model))
            rows = result.scalars().all()
            return [self.serialize(row) for row in rows]

    async def filter(self, **kwargs):
        async with self.db.session() as session:
            stmt = self._apply_filters(select(self.model), kwargs)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self.serialize(row) for row in rows]

    async def get(self, **kwargs):
        async with self.db.session() as session:
            stmt = self._apply_filters(select(self.model), kwargs)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            return self.serialize(row) if row is not None else None

    async def create(self, **kwargs):
        self._validate_fields(kwargs)
        async with self.db.session() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.flush()
            await session.refresh(obj)
            return self.serialize(obj)

    async def update(self, pk, **kwargs):
        self._validate_fields(kwargs)
        pk_column = self._primary_key_column()
        async with self.db.session() as session:
            stmt = select(self.model).where(pk_column == pk)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            if obj is None:
                return None
            for field, value in kwargs.items():
                setattr(obj, field, value)
            await session.flush()
            await session.refresh(obj)
            return self.serialize(obj)

    async def delete(self, pk):
        pk_column = self._primary_key_column()
        async with self.db.session() as session:
            stmt = select(self.model).where(pk_column == pk)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            if obj is None:
                return False
            await session.delete(obj)
            return True

    def _apply_filters(self, stmt, kwargs):
        self._validate_fields(kwargs)
        for field, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, field) == value)
        return stmt

    def _validate_fields(self, kwargs):
        for field in kwargs:
            if not hasattr(self.model, field):
                raise AttributeError(
                    f"{self.model.__name__} has no column '{field}'"
                )

    def _primary_key_column(self):
        pk_columns = list(self.model.__mapper__.primary_key)
        if len(pk_columns) != 1:
            raise NotImplementedError(
                f"{self.model.__name__} has a composite or missing primary key; "
                "update()/delete() currently only support single-column primary keys"
            )
        return pk_columns[0]

    def serialize(self, obj):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}