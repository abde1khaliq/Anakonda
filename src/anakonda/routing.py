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

    def add_route(
        self,
        path: str,
        handler: Callable,
        methods: list[str] | None = None,
    ) -> None:
        self.routes.append(Route(path, handler, methods=methods))


    def route(self, path: str, methods: list[str] | None = None):
        """
        Multi-method or method-unrestricted decorator.
        
        :param path: The `path` parameter in the `route` method is a string that represents the URL path for
        which the decorated handler function will be invoked
        :type path: str
        :param methods: The `methods` parameter in the `route` method is used to specify the HTTP methods
        that are allowed for the route. It is a list of strings that can include methods such as 'GET',
        'POST', 'PUT', 'DELETE', etc. If the `methods` parameter is not provided
        :type methods: list[str] | None
        :return: The `route` method returns a decorator function that takes a handler function as an
        argument, adds the specified route with the handler to the application, and then returns the handler
        function itself.
        """
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=methods)
            return handler
        return decorator

    def get(self, path: str):
        """
        The `get` function is a decorator that adds a route for handling GET requests in a Python web
        framework.
        
        :param path: The `path` parameter in the `get` method is a string that represents the URL path for
        which the handler function will be invoked. It is used to specify the route for the HTTP GET request
        :type path: str
        :return: The `decorator` function is being returned.
        """
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["GET"])
            return handler
        return decorator

    def post(self, path: str):
        """
        The `post` function is a decorator that adds a route for handling POST requests in a web
        application.
        
        :param path: The `path` parameter in the `post` method is a string that represents the URL path for
        which the decorated handler function will be invoked when an HTTP POST request is made to that path
        :type path: str
        :return: The `post` method is returning a decorator function that takes a handler function as an
        argument and adds a route for the specified path with the handler function for the "POST" method.
        The decorator function then returns the original handler function.
        """
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["POST"])
            return handler
        return decorator

    def put(self, path: str):
        """
        The `put` function is a decorator in Python that adds a route for handling PUT requests.
        
        :param path: The `path` parameter in the `put` method is a string that represents the URL path for
        which the decorated handler function will be invoked when an HTTP PUT request is made to that path
        :type path: str
        :return: The `put` method is returning the `decorator` function.
        """
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["PUT"])
            return handler
        return decorator

    def patch(self, path: str):
        """
        The `patch` function is a decorator that adds a route for handling PATCH requests in a Python web
        framework.
        
        :param path: The `path` parameter in the `patch` method is a string that represents the URL path for
        which the handler function will be invoked when an HTTP PATCH request is made to that path
        :type path: str
        :return: The `patch` method is returning a decorator function that takes a handler function as an
        argument and adds a route for the specified path with the handler function for the "PATCH" method.
        The decorator function then returns the original handler function.
        """
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["PATCH"])
            return handler
        return decorator

    def delete(self, path: str):
        """
        The `delete` function is a decorator in Python that adds a route for handling DELETE requests.
        
        :param path: The `path` parameter in the `delete` method is a string that represents the URL path
        for which the decorated function will be called when an HTTP DELETE request is made to that path
        :type path: str
        :return: The `delete` method is returning a decorator function that takes a handler function as an
        argument and adds a route for the specified path with the handler function for the "DELETE" method.
        The decorator function then returns the original handler function.
        """
        def decorator(handler: Callable) -> Callable:
            self.add_route(path, handler, methods=["DELETE"])
            return handler
        return decorator