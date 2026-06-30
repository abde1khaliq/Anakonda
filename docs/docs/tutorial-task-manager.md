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

Create a single file, `main.py`. We'll build it up piece by piece.

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
    Kribton doesn't include a migrations tool. For this tutorial, create the table directly via SQLAlchemy's metadata before running the app — see [step 7](#7-create-the-table) below.

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

    task = await Task.objects.update(task_id, **data)
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
    `update_task` passes the entire request body straight into `.update(**data)`. If the client sends a field that isn't a real column on `Task`, this will raise `AttributeError` and crash the request — Kribton has no built-in exception handling yet. Keep client input to known fields until that's added, or wrap the call in a `try`/`except` yourself:

```python
    try:
        task = await Task.objects.update(task_id, **data)
    except AttributeError:
        return Response({"error": "invalid field in request body"}, status=400)
```

## 7. Create the table

Since Kribton has no migrations tool, create the table once at startup using SQLAlchemy's metadata directly, via the engine on your `AsyncDatabase`:

```python
async def init_db():
    async with db._engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
```

You'll call this once before serving requests — see step 9.

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
import asyncio

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


async def init_db():
    async with db._engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

asyncio.run(init_db())
```

## 10. Run it

```bash
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

- **No exception handling middleware** — any unhandled error (besides the `AttributeError` we explicitly caught above) will crash the request rather than returning a clean 500. See the warning in [step 6](#6-update-and-delete-a-task).
- **No request body validation/schema** — the `"title" not in data` check above is manual; there's no Pydantic-style model validation built in despite SQLAlchemy/Pydantic being mentioned as ecosystem integrations.
- **No query string parsing** — you can't do `GET /tasks?done=false` yet; filtering by status would currently need a separate route or a body-based approach.
- **No migrations tool** — `create_all` is fine for a tutorial/SQLite, but isn't a real migration strategy for schema changes over time.

For the full list of what's implemented versus planned, see the framework overview on the **[home page](index.md)**.