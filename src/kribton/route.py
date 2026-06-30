import re
import uuid


class Route:
    CONVERTERS = {
        "str": {
            "pattern": r"[^/]+",
            "convert": lambda v: v,
        },
        "int": {
            "pattern": r"-?\d+",
            "convert": lambda v: int(v),
        },
        "float": {
            "pattern": r"-?\d+(?:\.\d+)?",
            "convert": lambda v: float(v),
        },
        "uuid": {
            "pattern": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            "convert": lambda v: uuid.UUID(v),
        },
        "path": {
            "pattern": r".+",
            "convert": lambda v: v,
        },
    }

    def __init__(self, path, handler, methods=None):
        self.path = path
        self.handler = handler
        self.methods = methods or ["GET"]
        self._pattern, self._param_converters = self._compile(path)

    @classmethod
    def _compile(cls, path):
        param_converters = {}
        pattern_parts = []
        for segment in path.split("/"):
            if segment.startswith("{") and segment.endswith("}"):
                spec = segment[1:-1]
                if ":" in spec:
                    name, type_name = spec.split(":", 1)
                else:
                    name, type_name = spec, "str"

                if type_name not in cls.CONVERTERS:
                    raise ValueError(
                        f"Unknown path parameter type '{type_name}' for '{{{spec}}}'. "
                        f"Available types: {', '.join(cls.CONVERTERS)}"
                    )

                converter = cls.CONVERTERS[type_name]
                param_converters[name] = converter["convert"]
                pattern_parts.append(
                    r"(?P<%s>%s)" % (re.escape(name), converter["pattern"])
                )
            else:
                pattern_parts.append(re.escape(segment))
        pattern = "^" + "/".join(pattern_parts) + "$"
        return re.compile(pattern), param_converters

    def matches(self, scope):
        return (
            scope["method"].upper() in self.methods
            and self._pattern.match(scope["path"]) is not None
        )

    def extract_params(self, scope):
        match = self._pattern.match(scope["path"])
        if not match:
            return {}
        raw = match.groupdict()
        return {
            name: self._param_converters[name](value)
            for name, value in raw.items()
        }