SCAFFOLD = {
    "app": {
        "__init__.py": "",
        "main.py":     "main.jinja",
        "config": {
            "__init__.py":    "",
            "base.py":        "config/base.jinja",
            "development.py": "config/development.jinja",
            "production.py":  "config/production.jinja",
        },
        "core": {
            "__init__.py":   "",
            "factory.py":    "core/factory.jinja",
            "database.py":   "core/database.jinja",
            "exceptions.py": "core/exceptions.jinja",
        },
        "migrations": {
            "__init__.py": "",
            "versions": {},
        },
        "modules": {},
        "shared": {
            "models":  {},
            "schemas": {},
            "utils":   {},
            "types.py": "",
        },
    },
    "tests": {},
    ".env": "",
    ".gitignore": "",
    "README.md": ""
}