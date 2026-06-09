import json

class Response:
    media_type: str | None = None
    charset: str = "utf-8"
 
    def __init__(
        self,
        content: bytes | str | None = None,
        status: int = 200,
        headers: list[tuple[str | bytes, str | bytes]] | None = None,
        media_type: str | None = None,
    ):
        self.status = status
        self.media_type = media_type or self.__class__.media_type
 
        # Normalize content to bytes
        if content is None:
            self.content = b""
        elif isinstance(content, str):
            self.content = content.encode(self.charset)
        else:
            self.content = content
 
        # Normalize caller-supplied headers to (bytes, bytes)
        self._headers: list[tuple[bytes, bytes]] = [
            self._coerce_header(k, v) for k, v in (headers or [])
        ]
        existing = {k.lower() for k, _ in self._headers}
 
        # Inject Content-Type when the subclass declares a media_type
        if self.media_type and b"content-type" not in existing:
            ct = self.media_type
            if "text/" in self.media_type and self.charset:
                ct = f"{self.media_type}; charset={self.charset}"
            self._headers.append((b"content-type", ct.encode("latin-1")))
 
        # Always set Content-Length — required for HTTP/1.1 keep-alive
        if b"content-length" not in existing:
            self._headers.append(
                (b"content-length", str(len(self.content)).encode())
            )
 
    @staticmethod
    def _coerce_header(
        key: str | bytes, value: str | bytes
    ) -> tuple[bytes, bytes]:
        k = key.encode("latin-1") if isinstance(key, str) else key
        v = value.encode("latin-1") if isinstance(value, str) else value
        return (k.lower(), v)
 
    async def send(self, send) -> None:
        await send({
            "type": "http.response.start",
            "status": self.status,
            "headers": self._headers,
        })
        await send({
            "type": "http.response.body",
            "body": self.content,
        })
 
class JSONResponse(Response):
    media_type = "application/json"
 
    def __init__(
        self,
        content: dict | list,
        status: int = 200,
        headers: list | None = None,
    ):
        super().__init__(
            content=json.dumps(content, ensure_ascii=False),
            status=status,
            headers=headers,
        )
 
 
class HTMLResponse(Response):
    media_type = "text/html"
 
    def __init__(self, content: str, status: int = 200, headers: list | None = None):
        super().__init__(content=content, status=status, headers=headers)
 
 
class PlainTextResponse(Response):
    media_type = "text/plain"
 
    def __init__(self, content: str, status: int = 200, headers: list | None = None):
        super().__init__(content=content, status=status, headers=headers)
 
 
class RedirectResponse(Response):
    def __init__(self, url: str, status: int = 307, headers: list | None = None):
        super().__init__(
            content=b"",
            status=status,
            headers=[(b"location", url.encode("utf-8"))] + (headers or []),
        )
 
 
class StreamingResponse(Response):
    """
    Streams the body via an async generator.
    Content-Length is intentionally omitted — body length is unknown upfront.
    The client reads until the connection closes or more_body=False.
    """
 
    def __init__(
        self,
        content: AsyncGenerator[bytes | str, None],
        status: int = 200,
        headers: list | None = None,
        media_type: str = "application/octet-stream",
    ):
        self.status = status
        self.media_type = media_type
        self._stream = content
 
        self._headers: list[tuple[bytes, bytes]] = [
            self._coerce_header(k, v) for k, v in (headers or [])
        ]
        existing = {k for k, _ in self._headers}
        if b"content-type" not in existing:
            self._headers.append((b"content-type", media_type.encode("latin-1")))
 
    async def send(self, send) -> None:
        await send({
            "type": "http.response.start",
            "status": self.status,
            "headers": self._headers,
        })
        async for chunk in self._stream:
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            await send({
                "type": "http.response.body",
                "body": chunk,
                "more_body": True,
            })
        # Signal end of stream
        await send({
            "type": "http.response.body",
            "body": b"",
            "more_body": False,
        })
