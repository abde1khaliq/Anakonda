import re


class Route:
    def __init__(self, path, handler, methods=None):
        self.path = path
        self.handler = handler
        self.methods = methods or ["GET"]
        self._pattern, self._param_names = self._compile(path)

    @staticmethod
    def _compile(path):
        param_names = []
        pattern_parts = []
        for segment in path.split("/"):
            if segment.startswith("{") and segment.endswith("}"):
                name = segment[1:-1]
                param_names.append(name)
                pattern_parts.append(r"(?P<%s>[^/]+)" % re.escape(name))
            else:
                pattern_parts.append(re.escape(segment))
        pattern = "^" + "/".join(pattern_parts) + "$"
        return re.compile(pattern), param_names

    def matches(self, scope):
        return (
            scope["method"].upper() in self.methods
            and self._pattern.match(scope["path"]) is not None
        )

    def extract_params(self, scope):
        match = self._pattern.match(scope["path"])
        return match.groupdict() if match else {}