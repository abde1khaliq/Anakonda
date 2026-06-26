class Route:
    def __init__(self, path, handler, methods=None):
        self.path = path
        self.handler = handler
        self.methods = methods or ["GET"]

    def matches(self, scope):
        return (
            self.path == scope["path"]
            and scope["method"].upper() in self.methods
        )
