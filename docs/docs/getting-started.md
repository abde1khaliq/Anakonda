---
icon: lucide/play
---

# Getting Started

## Installation

```bash
pip install kribton
```

Kribton comes in with a built-in CLI (command-line interface) for the framework to ease the use, so to confirm the installation was successful, run:

```bash
kribton
```

Now you're all set, it's installed on your machine!

## Your first app

```python
from kribton import Kribton, Router, Response

router = Router()

async def hello(request):
    return Response({"message": "hello world"})

router.append_route("/", hello)

app = Kribton(title="My API")
app.add_router(router)
```

Run it with any ASGI server, e.g.:

```bash
uvicorn main:app
```

## A full quick example

This puts routing, path parameters, requests/responses, and the async database layer together:

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

async def get_user(request):
    user_id = request.path_params["id"]  # already an int
    return Response({"id": user_id})

router = Router()
router.append_route("/users", list_users)
router.append_route("/users/{id:int}", get_user)

app = Kribton(title="My API")
app.add_router(router)
```

Continue to **[Routing](routing.md)** to see everything path parameters can do.