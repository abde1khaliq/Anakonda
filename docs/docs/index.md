---
icon: lucide/rocket
---

#

<div class="ana-hero" markdown>

![Kribton Logo](https://ik.imagekit.io/cin2tn3bj/kribton_logo_no_bg.png)

![PyPI](https://img.shields.io/pypi/v/kribton)
![Python Versions](https://img.shields.io/pypi/pyversions/kribton)
![License](https://img.shields.io/github/license/abde1khaliq/kribton)
![Discord](https://img.shields.io/discord/1518323557103571094?logo=discord&label=chat)

- **Source:** [github.com/abde1khaliq/kribton](https://github.com/abde1khaliq/kribton)
- **Documentation:** [abde1khaliq.github.io/Kribton/](https://abde1khaliq.github.io/Kribton/)

</div>

## Kribton

Kribton is a lightning‑fast Python web framework built for developers who want to create APIs and web applications effortlessly. It combines speed with a clean, intuitive file structure, so you can focus on building instead of boilerplate. Take a look at how simple its syntax can be.

## A minute of context

Kribton is built directly on the [ASGI](https://asgi.readthedocs.io/) specification, runs on Uvicorn (or Hypercorn/Daphne) in production, and integrates with the existing Python ecosystem like SQLAlchemy, Pydantic, Jinja2 rather than reinventing it.

## Installation

```bash
pip install kribton
```

Kribton comes in with a built-in CLI (command-line interface) for the framework to ease the use, so to confirm the installation was successful, run:

```bash
kribton
```

Now you're all set, it's installed on your machine!

## Features

### Application core

The `Kribton` class is the ASGI entrypoint for your app.

```python
from kribton import Kribton

app = Kribton(title="My API", description="A demo service")
```

- Optional `title` and `description` metadata for the app.
- `add_router(router)` mounts all routes registered on a `Router` instance.
- `add_route(path, handler, methods)` registers a single route directly on the app.
- Implements `__call__(scope, receive, send)`, so any ASGI server (Uvicorn, Hypercorn, Daphne) can run it directly.
- Walks registered routes on every request and dispatches to the first match; if nothing matches, it automatically returns a `404 Not Found` response.

### Routing

```python
from kribton import Router

router = Router()
router.append_route("/users", users_handler)
router.append_route("/users/{id}", get_user_handler)
app.add_router(router)
```

- `Route` pairs a `path` with a `handler` and an optional list of HTTP `methods` (defaults to `["GET"]`).
- **Path parameters** are supported using `{name}` segments — e.g. `/users/{id}` or `/posts/{post_id}/comments/{comment_id}`. Each `{name}` matches exactly one path segment (no slashes) and is compiled into a regex once when the `Route` is created.
- Captured parameters are available in the handler via `request.path_params`, a `dict` keyed by parameter name (always strings — no automatic type coercion yet).
- `Route.matches(scope)` checks both the path pattern and method (case-insensitive) against the incoming ASGI scope.
- `Router` is a lightweight collection that accumulates `Route` objects via `append_route` and can be merged into the app with `add_router`.

```python
async def get_user(request):
    user_id = request.path_params["id"]
    return Response({"id": user_id})

router.append_route("/users/{id}", get_user)
```

### Requests

Every handler receives a `Request` built from the ASGI `scope`/`receive` pair:

- `request.path` and `request.method` — decoded straight from the ASGI scope.
- `request.path_params` — `dict` of values captured from `{name}` segments in the matched route's path (empty `dict` if the route has no path parameters).
- `request.headers` — list of `(name, value)` tuples, decoded from bytes.
- `await request.body()` — buffers and concatenates the full request body across ASGI `http.request` messages.
- `await request.json()` — parses the body as JSON, returning `{}` if parsing fails (never raises).

### Responses

`Response` figures out the right content type for you based on what you pass in:

- `dict` / `list` → serialized to JSON with `application/json`.
- `str` → sent as-is with `text/plain`.
- `bytes` / `bytearray` → sent as-is with `application/octet-stream`.
- Anything else → falls back to `str(content)` as `text/plain`.
- Custom `status` code and `headers` can be supplied to override the defaults.
- `await response.send(send)` emits the ASGI `http.response.start` / `http.response.body` messages.

### Database configuration

`BaseDatabaseConfig` centralizes SQLAlchemy connection pool settings shared by all database backends:

- `url`, `pool_size` (default `5`), `max_overflow` (default `10`), `pool_timeout` (default `30`), `pool_recycle` (default `1800`), `echo` (default `False`).
- Pools are created with `pool_pre_ping=True` to avoid stale connections.

### Async database

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

### Models

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

### Query managers

- `BaseQueryManager` simply pairs a `model` with its `db` connection — the base class all query managers build on.
- `AsyncQueryManager` (used automatically by `AsyncDatabase`) currently provides:
  - `await Model.objects.all()` — runs a `SELECT` over all rows for the model and returns them as a list of plain dicts.
  - `serialize(obj)` — converts a SQLAlchemy model instance into a `{column_name: value}` dict using its table's columns.

## Quick example

Putting the pieces together:

```python
from kribton import Kribton, Router, Response
from kribton.db.asyncio import AsyncDatabase
from kribton.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

db = AsyncDatabase(url="sqlite+aiosqlite:///./app.db")

class User(BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

async def list_users(request):
    users = await User.objects.all()
    return Response(users)

router = Router()
router.append_route("/users", list_users)

app = Kribton(title="My API")
app.add_router(router)
```