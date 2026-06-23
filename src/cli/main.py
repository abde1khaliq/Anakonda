import typer
import alembic.config
from pathlib import Path
from typing import Optional

from cli.commands.init import run_init
from cli.commands.new import run_new_module

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
    help="Anakonda",
)

new_app = typer.Typer(
    no_args_is_help=True,
    help="Scaffold a resource inside an existing project",
)

migrations_app = typer.Typer(
    no_args_is_help=True,
    help="Manage database migrations",
)

app.add_typer(new_app, name="new")
app.add_typer(migrations_app, name="migrate")


@app.command("init")
def init(project_name: Optional[str] = typer.Argument(None, help="Project directory name")) -> None:
    """Create a new project."""
    run_init(project_name)


@new_app.command("module")
def new_module(name: Optional[str] = typer.Argument(None, help="Module name (snake_case)")) -> None:
    """Add a new vertical-slice module to the project."""
    run_new_module(name)


@migrations_app.command("makemigrations")
def makemigrations(message: str = "auto") -> None:
    """Autogenerate a new migration script."""
    project_path = Path.cwd()
    alembic_ini = project_path / "alembic.ini"
    alembic.config.main(argv=[
        "-c", str(alembic_ini),
        "revision", "--autogenerate", "-m", message,
        f"--version-path={project_path}/app/migrations/versions"
    ])


@migrations_app.command("upgrade")
def upgrade(revision: str = "head") -> None:
    """Apply migrations up to the given revision (default: head)."""
    project_path = Path.cwd()
    alembic_ini = project_path / "alembic.ini"
    alembic.config.main(argv=[
        "-c", str(alembic_ini),
        "upgrade", revision
    ])



@migrations_app.command("downgrade")
def downgrade(revision: str = "-1") -> None:
    """Revert migrations by one step or to a specific revision."""
    project_path = Path.cwd()
    alembic_ini = project_path / "alembic.ini"
    alembic.config.main(argv=[
        "-c", str(alembic_ini),
        "downgrade", revision
    ])


if __name__ == "__main__":
    app()
