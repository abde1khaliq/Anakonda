from urllib.parse import parse_qs
from typing import Any, AsyncGenerator

class PayloadTooLarge(Exception):
    pass

class Request:
    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB Max
 
    def __init__(self, scope: dict, receive):
        self._scope = scope
        self._receive = receive
        self._body: bytes | None = None
 
        # Core
        self.method: str = scope["method"].upper()
        self.path: str = scope["path"]
        self.scheme: str = scope.get("scheme", "http")
 
        # Headers — lowercase-keyed dict (HTTP spec: case-insensitive)
        self.headers: dict[str, str] = {
            k.decode().lower(): v.decode()
            for k, v in scope.get("headers", [])
        }
 
        # Query params — single value as str, multiple as list[str]
        raw_qs: str = scope.get("query_string", b"").decode("utf-8")
        self.query_params: dict[str, str | list[str]] = {
            k: v[0] if len(v) == 1 else v
            for k, v in parse_qs(raw_qs, keep_blank_values=True).items()
        }
 
        # Populated by the router after path matching
        self.path_params: dict[str, str] = {}
 
        # Middleware scratch-pad — auth user, request-id, trace context, etc.
        self.state: dict[str, Any] = {}
 
        # Client address
        client = scope.get("client")
        self.client_host: str | None = client[0] if client else None
        self.client_port: int | None = client[1] if client else None
 
    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "")
 
    @property
    def url(self) -> str:
        qs = self._scope.get("query_string", b"").decode("utf-8")
        host = self.headers.get("host", "")
        base = f"{self.scheme}://{host}{self.path}"
        return f"{base}?{qs}" if qs else base
 
    async def body(self, max_size: int = MAX_BODY_SIZE) -> bytes:
        if self._body is not None:
            return self._body
 
        chunks: list[bytes] = []
        total = 0
 
        while True:
            message = await self._receive()
            if message["type"] == "http.request":
                chunk = message.get("body", b"")
                total += len(chunk)
                if total > max_size:
                    raise PayloadTooLarge(
                        f"Request body exceeds the maximum allowed size of {max_size} bytes."
                    )
                chunks.append(chunk)
                if not message.get("more_body", False):
                    break
 
        self._body = b"".join(chunks)
        return self._body
 
    async def text(self, encoding: str = "utf-8") -> str:
        return (await self.body()).decode(encoding)
 
    async def json(self) -> Any:
        """Raises json.JSONDecodeError on malformed input — intentional."""
        return json.loads(await self.text())
 
    async def form(self) -> dict[str, str | list[str]]:
        """Parses application/x-www-form-urlencoded bodies."""
        raw = await self.text()
        return {
            k: v[0] if len(v) == 1 else v
            for k, v in parse_qs(raw, keep_blank_values=True).items()
        }
 
