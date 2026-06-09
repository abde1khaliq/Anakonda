from typing import Callable
from anakonda.routing import RouteRegistry


class Router(RouteRegistry):
    def __init__(self, prefix: str = ""):
        super().__init__()
        self.prefix = "/" + prefix.strip("/") if prefix.strip("/") else ""

    def add_route(
        self,
        path: str,
        handler: Callable,
        methods: list[str] | None = None,
    ) -> None:
        """Prepends the router prefix before delegating to the base registry."""
        super().add_route(self.prefix + path, handler, methods=methods)