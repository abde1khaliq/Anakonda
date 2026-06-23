SCAFFOLD = {
    "app": {
        "__init__.py": "",
        "main.py": "main.jinja",
        "config": {
            "__init__.py": "",
            "settings.py": "config/settings.jinja",
        },
        "core": {
            "__init__.py": "",
            "database.py": "core/database.jinja",
            "exceptions.py": "core/exceptions.jinja",
            "dependencies.py": "core/dependencies.jinja",
        },
        "migrations": {
            "__init__.py": "",
            "env.py": "migrations/env.jinja",
            "script.py.mako": "migrations/script.jinja",
            "versions": {},
        },
        "modules": {},
        "shared": {
            "models": {},
            "schemas": {},
            "utils": {},
            "types.py": "",
        },
    },
    "tests": {},
    ".env": "",
    ".gitignore": "",
    "README.md": "",
    "alembic.ini": "alembic.ini.jinja", 
}
