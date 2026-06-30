---
icon: lucide/check-square
---

# Tutorial: Building a Task Manager

This walks through building a small but complete task manager API with Kribton — covering routing, path parameters, the database layer, models, and full CRUD through query managers. By the end you'll have working `GET`/`POST`/`PATCH`/`DELETE` endpoints backed by SQLite.

If you haven't read **[Getting Started](getting-started.md)** yet, do that first — this tutorial assumes Kribton is already installed.

## 1. Project setup

```bash
pip install kribton sqlalchemy aiosqlite
```

Create a project folder with two files: `main.py` (the app) and `init_db.py` (a one-time setup script). We'll build both up piece by piece.

## 2. Define the database and model

```python
from kribton.db.asyncio import AsyncDatabase
from kribton.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

db = AsyncDatabase(url="sqlite+aiosqlite:///./tasks.db")

class Task(BaseModel):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)
```

Creating `AsyncDatabase` automatically registers itself as the backend for every `BaseModel` subclass — that's why `Task.objects` will work without any extra wiring. See **[Database](database.md)** and **[Models](models.md)** for the full details.

!!! note
    Kribton doesn't include a migrations tool. For this tutorial, we'll create the table once with a small setup script — see [step 7](#7-set-up-the-database).

## 3. List all tasks

```python
from kribton import Response

async def list_tasks(request):
    tasks = await Task.objects.all()
    return Response(tasks)
```

`Task.objects.all()` returns a list of plain dicts, which `Response` automatically serializes to JSON. See **[Query Managers](query-managers.md)**.

## 4. Get a single task by id

```python
async def get_task(request):
    task_id = request.path_params["id"]
    task = await Task.objects.get(id=task_id)
    if task is None:
        return Response({"error": "task not found"}, status=404)
    return Response(task)
```

`{id:int}` in the route path (see step 8) means `request.path_params["id"]` arrives already converted to an `int` — no manual casting needed. See **[Routing](routing.md)**.

## 5. Create a task

```python
async def create_task(request):
    data = await request.json()
    if "title" not in data:
        return Response({"error": "'title' is required"}, status=400)

    task = await Task.objects.create(title=data["title"])
    return Response(task, status=201)
```

`.json()` never raises on a malformed body — it returns `{}` instead — so the explicit `"title" not in data` check is what actually catches missing/bad input here. See **[Requests](requests.md)**.

## 6. Update and delete a task

```python
async def update_task(request):
    task_id = request.path_params["id"]
    data = await request.json()

    try:
        task = await Task.objects.update(task_id, **data)
    except AttributeError:
        return Response({"error": "invalid field in request body"}, status=400)

    if task is None:
        return Response({"error": "task not found"}, status=404)
    return Response(task)


async def delete_task(request):
    task_id = request.path_params["id"]
    deleted = await Task.objects.delete(task_id)
    if not deleted:
        return Response({"error": "task not found"}, status=404)
    return Response(None, status=204)
```

!!! warning
    `update_task` passes the request body straight into `.update(**data)`. If the client sends a field that isn't a real column on `Task`, this raises `AttributeError` — which is why it's caught explicitly above. Kribton doesn't have global exception-handling middleware yet, so unhandled errors elsewhere will still surface as a generic failure.

## 7. Set up the database

Kribton doesn't run any code automatically on startup, so table creation happens via a small standalone script, run once before you start the server.

**`init_db.py`:**

```python
import asyncio

from main import db
from kribton.models import BaseModel


async def init_db():
    async with db._engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
```

## 8. Wire up routes

```python
from kribton import Kribton, Router

router = Router()
router.append_route("/tasks", list_tasks, methods=["GET"])
router.append_route("/tasks", create_task, methods=["POST"])
router.append_route("/tasks/{id:int}", get_task, methods=["GET"])
router.append_route("/tasks/{id:int}", update_task, methods=["PATCH"])
router.append_route("/tasks/{id:int}", delete_task, methods=["DELETE"])

app = Kribton(title="Task Manager")
app.add_router(router)
```

## 9. Full `main.py`

```python
from kribton import Kribton, Router, Response
from kribton.db.asyncio import AsyncDatabase
from kribton.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

db = AsyncDatabase(url="sqlite+aiosqlite:///./tasks.db")

class Task(BaseModel):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)


async def list_tasks(request):
    tasks = await Task.objects.all()
    return Response(tasks)


async def get_task(request):
    task = await Task.objects.get(id=request.path_params["id"])
    if task is None:
        return Response({"error": "task not found"}, status=404)
    return Response(task)


async def create_task(request):
    data = await request.json()
    if "title" not in data:
        return Response({"error": "'title' is required"}, status=400)
    task = await Task.objects.create(title=data["title"])
    return Response(task, status=201)


async def update_task(request):
    data = await request.json()
    try:
        task = await Task.objects.update(request.path_params["id"], **data)
    except AttributeError:
        return Response({"error": "invalid field in request body"}, status=400)
    if task is None:
        return Response({"error": "task not found"}, status=404)
    return Response(task)


async def delete_task(request):
    deleted = await Task.objects.delete(request.path_params["id"])
    if not deleted:
        return Response({"error": "task not found"}, status=404)
    return Response(None, status=204)


router = Router()
router.append_route("/tasks", list_tasks, methods=["GET"])
router.append_route("/tasks", create_task, methods=["POST"])
router.append_route("/tasks/{id:int}", get_task, methods=["GET"])
router.append_route("/tasks/{id:int}", update_task, methods=["PATCH"])
router.append_route("/tasks/{id:int}", delete_task, methods=["DELETE"])

app = Kribton(title="Task Manager")
app.add_router(router)
```

## 10. Run it

```bash
python init_db.py        # one-time: creates tasks.db and the tasks table
uvicorn main:app --reload
```

## 11. Try it out

```bash
# Create a task
curl -X POST localhost:8000/tasks -d '{"title": "Write docs"}'
# {"id": 1, "title": "Write docs", "done": false}

# List tasks
curl localhost:8000/tasks

# Get one
curl localhost:8000/tasks/1

# Mark it done
curl -X PATCH localhost:8000/tasks/1 -d '{"done": true}'

# Delete it
curl -X DELETE localhost:8000/tasks/1
```

## What this tutorial doesn't cover (yet)

Being upfront about the current framework's limits, so you don't hit surprises:

- **No global exception handling** — any unhandled error (besides the `AttributeError` we caught explicitly above) will crash the request rather than returning a clean 500.
- **No request body validation/schema** — the `"title" not in data` check above is manual; there's no built-in validation layer.
- **No query string parsing** — you can't do `GET /tasks?done=false` yet.
- **No migrations tool** — `create_all` works for a tutorial/SQLite, but isn't a real migration strategy for schema changes over time.
- **No startup/shutdown hooks** — that's why database setup lives in a separate `init_db.py` script rather than running automatically when the server starts.

For the full list of what's implemented versus planned, see the framework overview on the **[home page](index.md)**.