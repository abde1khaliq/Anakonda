---
icon: lucide/inbox
---

# Requests

Every handler receives a `Request` built from the ASGI `scope`/`receive` pair:

- `request.path` and `request.method` — decoded straight from the ASGI scope.
- `request.path_params` — `dict` of values captured from `{name}` (or typed `{name:type}`) segments in the matched route's path, already converted to the declared type. Empty `dict` if the route has no path parameters. See [Routing](routing.md) for details.
- `request.headers` — list of `(name, value)` tuples, decoded from bytes.
- `await request.body()` — buffers and concatenates the full request body across ASGI `http.request` messages.
- `await request.json()` — parses the body as JSON, returning `{}` if parsing fails (never raises).

```python
async def echo(request):
    payload = await request.json()
    return Response({
        "method": request.method,
        "path": request.path,
        "params": request.path_params,
        "body": payload,
    })
```

!!! note
    `request.json()` swallows all parsing errors and returns `{}` rather than raising — a malformed body currently looks identical to an empty one from the handler's perspective.