import logging

from anakonda.route import Route
from anakonda.request import Request
from anakonda.response import Response, JSONResponse

logger = logging.getLogger(__name__)


class Konda:
    def __init__(self, title: str | None = None, description: str | None = None):
        self.title = title
        self.description = description
        self.routers: list = []
        self.routes: list[Route] = []

    def add_router(self, router) -> None:
        self.routers.append(router)
        self.routes.extend(router.routes)

    def add_route(self, path: str, handler, methods: list[str] | None = None) -> None:
        self.routes.append(Route(path, handler, methods=methods))

    async def __call__(self, scope: dict, receive, send) -> None:
        scope_type = scope["type"]

        if scope_type == "lifespan":
            await self._handle_lifespan(receive, send)
            return

        if scope_type != "http":
            # WebSocket and any future scope types are not handled yet
            return

        await self._handle_http(scope, receive, send)

    async def _handle_http(self, scope: dict, receive, send) -> None:
        request = Request(scope, receive)
        path_matched = False  # tracks a path hit with a wrong method → 405

        for route in self.routes:
            match = route.matches(scope)

            if match is None:
                continue  # path did not match at all

            # Path matched — check the method before marking a hit
            if not route.method_allowed(request.method):
                path_matched = True
                continue

            # Full match — inject path params and dispatch
            request.path_params = match

            try:
                response = await route.handler(request)
            except Exception as exc:
                logger.exception("Unhandled exception in route handler: %s", exc)
                response = Response("Internal Server Error", status=500)
                await response.send(send)
                return

            # Guard against handlers that forget to return a response
            if not isinstance(response, Response):
                logger.error(
                    "Handler %r returned %r instead of a Response.",
                    route.handler,
                    type(response).__name__,
                )
                response = Response("Internal Server Error", status=500)

            await response.send(send)
            return

        # No full match found — decide between 404 and 405
        if path_matched:
            response = Response("Method Not Allowed", status=405)
        else:
            response = Response("Not Found", status=404)

        await response.send(send)

    async def _handle_lifespan(self, receive, send) -> None:
        """
        Handles ASGI lifespan events (startup / shutdown).
        Without this, servers like uvicorn emit a warning and may refuse to start.
        Override startup_handler / shutdown_handler for real init logic.
        """
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
        """Override to run logic on server startup — DB pool init, cache warmup, etc."""

    async def on_shutdown(self) -> None:
        """Override to run logic on server shutdown — close connections, flush queues, etc."""