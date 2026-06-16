from pathlib import Path
from cli.renderer import render_template

def build(scaffold: dict, base: Path, context: dict) -> None:
    base.mkdir(parents=True, exist_ok=True)
    for name, value in scaffold.items():
        path = base / name
        if isinstance(value, dict):
            path.mkdir(parents=True, exist_ok=True)
            build(value, path, context)
        else:
            content = render_template(value, context) if value else ""
            path.write_text(content)