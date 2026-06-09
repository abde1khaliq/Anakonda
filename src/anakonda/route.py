import re
from typing import Callable

# Matches {param_name} placeholders in path templates
_PARAM_REGEX = re.compile(r"\{(\w+)\}")


def _compile_path(path: str) -> re.Pattern:
    """
    Converts a path template into a compiled named-group regex.

        /users/{id}/posts/{post_id}
        → ^/users/(?P<id>[^/]+)/posts/(?P<post_id>[^/]+)$

    Static segments are re.escaped so dots, plus signs, etc. are treated
    as literals rather than regex operators.
    """
    result = []
    cursor = 0

    for match in _PARAM_REGEX.finditer(path):
        # Escape the static segment before this param
        result.append(re.escape(path[cursor:match.start()]))
        # Named capture group — stops at the next slash
        result.append(f"(?P<{match.group(1)}>[^/]+)")
        cursor = match.end()

    # Escape any remaining static tail
    result.append(re.escape(path[cursor:]))
    return re.compile(f"^{''.join(result)}$")


# The `Route` class represents a route with a path, handler function, and optional methods restriction
# for a web application.
class Route:
    def __init__(
        self,
        path: str,
        handler: Callable,
        methods: list[str] | None = None,
    ):
        self.path = path
        self.handler = handler
        # None means no method restriction (catch-all); store as uppercase set
        self.methods: set[str] | None = (
            {m.upper() for m in methods} if methods else None
        )
        self._pattern: re.Pattern = _compile_path(path)

    def matches(self, scope: dict) -> dict | None:
        """
        Returns a dict of extracted path params if the path matches,
        or None if it does not.

        An empty dict {} means the path matched with no params.
        Callers must also check method_allowed() separately.
        """
        m = self._pattern.match(scope["path"])
        return m.groupdict() if m else None

    def method_allowed(self, method: str) -> bool:
        """
        Returns True if no method restriction is set,
        or if the given method is in the allowed set.
        """
        if self.methods is None:
            return True
        return method.upper() in self.methods

    def __repr__(self) -> str:
        methods = ",".join(sorted(self.methods)) if self.methods else "*"
        return f"<Route [{methods}] {self.path}>"