---
icon: lucide/database
---

# Database

## Configuration

`BaseDatabaseConfig` centralizes SQLAlchemy connection pool settings shared by all database backends:

- `url`, `pool_size` (default `5`), `max_overflow` (default `10`), `pool_timeout` (default `30`), `pool_recycle` (default `1800`), `echo` (default `False`).
- Pools are created with `pool_pre_ping=True` to avoid stale connections.

## Async database

`AsyncDatabase` builds on `BaseDatabaseConfig` to provide a SQLAlchemy async engine and session factory:

```python
from kribton.db.asyncio import AsyncDatabase

db = AsyncDatabase(url="postgresql+asyncpg://user:pass@localhost/db")
```

- Creates an `AsyncEngine` via `create_async_engine` and an `async_sessionmaker` (`expire_on_commit=False`).
- Registering an `AsyncDatabase` automatically wires it up as the database backend for all `BaseModel` subclasses.
- `async with db.session() as session:` — yields a session, auto-commits on success, auto-rolls back and re-raises on error, and always closes the session.
- `await db.health_check()` — runs `SELECT 1` and returns `True`/`False` instead of raising.
- `await db.close()` — disposes of the underlying engine pool.

```python
async with db.session() as session:
    session.add(User(name="Ada"))
```

!!! note
    Only an async backend (`AsyncDatabase`) is currently available — there is no synchronous database option yet.