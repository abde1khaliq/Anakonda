from kribton.request import Request
from kribton.response import Response
from kribton.route import Route


class Kribton:
    def __init__(self, title=None, description=None):
        self.title = title
        self.description = description
        self.routers = []
        self.routes = []

    def add_router(self, router):
        self.routers.append(router)
        self.routes.extend(router.routes)

    def add_route(self, path, handler, methods):
        self.routes.append(Route(path, handler, methods))

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive)

        for route in self.routes:
            if route.matches(scope):
                request.path_params = route.extract_params(scope)
                response = await route.handler(request)
                await response.send(send)
                return

        response = Response("Not Found", status=404)
        await response.send(send)
