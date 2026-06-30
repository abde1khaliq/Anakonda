import json


class Request:
    def __init__(self, scope, receive):
        self._scope = scope
        self._receive = receive
        self._body = None
        self.path = self._scope["path"]
        self.method = self._scope["method"]
        self.headers = [
            (m.decode(), n.decode()) for m, n in self._scope.get("headers", [])
        ]
        self.path_params = {}

    async def body(self):
        if self._body is None:
            chunks = []
            while True:
                message = await self._receive()
                if message["type"] == "http.request":
                    chunks.append(message.get("body", b""))
                    if not message.get("more_body", False):
                        break
            self._body = b"".join(chunks)
        return self._body

    async def json(self):
        try:
            return json.loads((await self.body()).decode("utf-8"))
        except Exception:
            return {}
