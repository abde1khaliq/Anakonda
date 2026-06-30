---
icon: lucide/send
---

# Responses

`Response` figures out the right content type for you based on what you pass in:

- `dict` / `list` → serialized to JSON with `application/json`.
- `str` → sent as-is with `text/plain`.
- `bytes` / `bytearray` → sent as-is with `application/octet-stream`.
- Anything else → falls back to `str(content)` as `text/plain`.

A custom `status` code and `headers` can be supplied to override the defaults:

```python
from kribton import Response

async def created(request):
    return Response({"id": 1}, status=201)

async def plain_text(request):
    return Response("ok", headers=[(b"content-type", b"text/plain; charset=utf-8")])
```

`await response.send(send)` emits the ASGI `http.response.start` / `http.response.body` messages — this is called automatically by `Kribton.__call__` for whatever your handler returns.