from .router import Router

class Konda:
    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description
        self.router = Router()

    async def __call__(self, scope, receive, send):
        for route in self.router.routes:
            if route.matches(scope):
                return await route.handler(scope, receive, send)

        await send({
            "type": "http.response.start",
            "status": 404,
            "headers": [
                [b'content-type', b'text/plain']
            ]
        })

        await send({
            "type": "http.response.body",
            "body": b"Not Found"
        })