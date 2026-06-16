from cli.module_slice import MODULE_SLICE
from cli.utils import to_class_name
from cli.build import build

def new_module(name: str, project_root: Path) -> None:
    context = {
        "module_name": name,
        "class_name": to_class_name(name),
        "app_name": "myproject",
    }
    build(MODULE_SLICE, project_root / "app" / "modules" / name, context)