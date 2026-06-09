from typing import Callable
from anakonda.route import Route


class RouteRegistry:
    """
    Provides route storage and the HTTP method decorator interface.
    Inherited by both Router and Konda — the registration API is
    identical on both so handlers don't care which they're attached to.
    """

    def __init__(self):
        self.routes: list[Route] = []

    # ── Core ──────────────────────────────────────────────────────────────────

    def add_route(
        self,
        path: str,
        handler: Callable,
        methods: list[str] | None = None,
    ) -> None:
        self.routes.append(Route(path, handler, methods=methods))

    # ── Decorators ────────────────────────────────────────────────────────────

    def route(self, path: str, methods: list[str] | None = None):
        """Multi-method or method-unrestricted decorator."""
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=methods)
            return handler
        return decorator

    def get(self, path: str):
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["GET"])
            return handler
        return decorator

    def post(self, path: str):
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["POST"])
            return handler
        return decorator

    def put(self, path: str):
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["PUT"])
            return handler
        return decorator

    def patch(self, path: str):
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["PATCH"])
            return handler
        return decorator

    def delete(self, path: str):
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["DELETE"])
            return handler
        return decorator