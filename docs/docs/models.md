---
icon: lucide/box
---

# Models

`BaseModel` is a thin layer on top of SQLAlchemy's `DeclarativeBase`:

```python
from kribton.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

class User(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
```

- Every subclass that defines `__tablename__` is automatically tracked in a class-level `_registry`.
- Models expose an `objects` attribute (a `QueryManagerDescriptor`) for querying without manually instantiating a query manager.
- Accessing `Model.objects` lazily resolves the correct query manager from the database registered via `BaseModel._db`, and raises a clear `RuntimeError` if no database has been initialized yet.
- The resolved manager is cached on the class as `_objects_cache` after first access.

```python
users = await User.objects.all()
```

See **[Query Managers](query-managers.md)** for what `objects` can currently do.