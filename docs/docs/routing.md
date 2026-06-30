---
icon: lucide/route
---

# Routing

```python
from kribton import Router

router = Router()
router.append_route("/users", users_handler)
router.append_route("/users/{id}", get_user_handler)
router.append_route("/users/{id:int}", get_user_by_int_id)
app.add_router(router)
```

- `Route` pairs a `path` with a `handler` and an optional list of HTTP `methods` (defaults to `["GET"]`).
- `Route.matches(scope)` checks both the path pattern and method (case-insensitive) against the incoming ASGI scope.
- `Router` is a lightweight collection that accumulates `Route` objects via `append_route` and can be merged into the app with `add_router`.

### `Router.append_route(path, handler, methods=None)`

- `path` — the route path, supports `{name}` / `{name:type}` segments (see below).
- `handler` — an async callable taking a `Request` and returning a `Response`.
- `methods` — optional list of HTTP methods (e.g. `["GET", "POST"]`). Defaults to `["GET"]` if omitted, matching `Route`'s own default.

```python
router.append_route("/tasks", list_tasks, methods=["GET"])
router.append_route("/tasks", create_task, methods=["POST"])
router.append_route("/tasks/{id:int}", update_task, methods=["PATCH"])
```

## Path parameters

Path parameters are supported using `{name}` segments — e.g. `/users/{id}` or `/posts/{post_id}/comments/{comment_id}`. Each `{name}` matches exactly one path segment (no slashes) and is compiled into a regex once when the `Route` is created.

Captured parameters are available in the handler via `request.path_params`, a `dict` keyed by parameter name.

```python
async def get_user(request):
    user_id = request.path_params["id"]
    return Response({"id": user_id})

router.append_route("/users/{id}", get_user)
```

## Typed path parameters

Use `{name:type}` syntax to constrain *and* automatically convert the captured value:

| Type | Matches | Converts to | Example |
|------|---------|-------------|---------|
| `str` (default) | any single segment | `str` | `{id}` or `{id:str}` |
| `int` | digits, optional leading `-` | `int` | `{id:int}` |
| `float` | digits with optional decimal | `float` | `{price:float}` |
| `uuid` | a UUID-formatted string | `uuid.UUID` | `{sku:uuid}` |
| `path` | one or more segments (slashes allowed) | `str` | `{filepath:path}` |

```python
async def get_user(request):
    user_id = request.path_params["id"]  # already an int
    return Response({"id": user_id})

router.append_route("/users/{id:int}", get_user)
router.append_route("/files/{filepath:path}", serve_file)
router.append_route("/products/{sku:uuid}", get_product)
```

If the captured text doesn't match the type's pattern (e.g. `"abc"` against `{id:int}`), the route simply doesn't match — it falls through to the next route or a 404, rather than raising at request time.

!!! warning "Unknown types fail fast"
    Using an unrecognized type name (e.g. `{id:foo}`) raises `ValueError` at route registration time, not at request time, so typos are caught immediately during app startup rather than silently 404ing in production.

## Known limitations

- No custom converter registration API yet — the built-in types (`str`, `int`, `float`, `uuid`, `path`) are fixed on the `Route` class.
- The `uuid` type only matches the canonical hyphenated form (`8-4-4-4-12` hex groups).
- If two routes could match the same URL (e.g. differing only by param type), the first one registered wins — there's no explicit precedence rule beyond registration order.