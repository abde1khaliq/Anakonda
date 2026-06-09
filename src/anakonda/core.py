import logging

from anakonda.routing import RouteRegistry
from anakonda.request import Request
from anakonda.response import Response

logger = logging.getLogger(__name__)


class Konda(RouteRegistry):
    def __init__(self, title: str | None = None, description: str | None = None):
        super().__init__()
        self.title = title
        self.description = description
        self.routers: list = []


    def add_router(self, router) -> None:
        self.routers.append(router)
        self.routes.extend(router.routes)


    async def __call__(self, scope: dict, receive, send) -> None:
        scope_type = scope["type"]

        if scope_type == "lifespan":
            await self._handle_lifespan(receive, send)
            return

        if scope_type != "http":
            return

        await self._handle_http(scope, receive, send)


    async def _handle_http(self, scope: dict, receive, send) -> None:
        request = Request(scope, receive)
        path_matched = False

        for route in self.routes:
            match = route.matches(scope)

            if match is None:
                continue

            if not route.method_allowed(request.method):
                path_matched = True
                continue

            request.path_params = match

            try:
                response = await route.handler(request)
            except Exception as exc:
                logger.exception("Unhandled exception in route handler: %s", exc)
                response = Response("Internal Server Error", status=500)
                await response.send(send)
                return

            if not isinstance(response, Response):
                logger.error(
                    "Handler %r returned %r instead of a Response.",
                    route.handler,
                    type(response).__name__,
                )
                response = Response("Internal Server Error", status=500)

            await response.send(send)
            return

        response = Response("Method Not Allowed", status=405) if path_matched \
              else Response("Not Found", status=404)
        await response.send(send)


    async def _handle_lifespan(self, receive, send) -> None:
        while True:
            message = await receive()

            if message["type"] == "lifespan.startup":
                try:
                    await self.on_startup()
                    await send({"type": "lifespan.startup.complete"})
                except Exception as exc:
                    logger.exception("Startup failed: %s", exc)
                    await send({"type": "lifespan.startup.failed", "message": str(exc)})
                    return

            elif message["type"] == "lifespan.shutdown":
                try:
                    await self.on_shutdown()
                finally:
                    await send({"type": "lifespan.shutdown.complete"})
                return

    async def on_startup(self) -> None:
        """Override to run logic on server startup."""

    async def on_shutdown(self) -> None:
        """Override to run logic on server shutdown."""