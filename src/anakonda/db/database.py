# sync_db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from anakonda.db.base import BaseDatabaseConfig


class Database(BaseDatabaseConfig):
    def __init__(self, url: str, **kwargs):
        super().__init__(url, **kwargs)
        self._engine = create_engine(self.url, **self._engine_kwargs())
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    def session(self):
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def close(self) -> None:
        self._engine.dispose()
