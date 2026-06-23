import time
from pathlib import Path
from typing import Optional

import questionary
import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from cli.build import build
from cli.scaffold import SCAFFOLD
from cli.style import Q_STYLE, console


def _next_steps(name: str) -> None:
    console.print(
        Panel(
            f"  [muted]$[/muted]  cd [bold]{name}[/bold]\n"
            f"  [muted]$[/muted]  cp .env.example .env\n"
            f"  [muted]$[/muted]  make dev",
            title="[muted]next steps[/muted]",
            title_align="left",
            border_style="muted",
            padding=(0, 2),
        )
    )
    console.print()


def run_init(project_name: Optional[str]) -> None:

    if not project_name:
        project_name = questionary.text(
            "Project name",
            default="my-app",
            style=Q_STYLE,
        ).ask()

    if not project_name:
        raise typer.Exit()

    console.print()

    project_path = Path.cwd() / project_name

    if project_path.exists():
        console.print(
            f"  [error]✕[/error]  [bold]{project_name}[/bold] already exists\n"
        )
        raise typer.Exit(1)

    context = {
        "project_name": project_name,
    }

    start = time.monotonic()

    with Progress(
        SpinnerColumn(spinner_name="dots", style="accent"),
        TextColumn("[muted]{task.description}[/muted]"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Creating project structure...", total=None)
        build(SCAFFOLD, project_path, context)

    elapsed = time.monotonic() - start

    console.print(
        f"  [success]✓[/success]  [bold]{project_name}[/bold] "
        f"[muted]ready in {elapsed:.1f}s[/muted]"
    )
    console.print()

    tree = Tree(f"[bold]{project_name}/[/bold]", guide_style="muted")
    app_branch = tree.add("[bold]app/[/bold]")
    app_branch.add("[muted]config/[/muted]")
    app_branch.add("[muted]core/[/muted]")
    app_branch.add("[muted]modules/[/muted]")
    app_branch.add("[muted]shared/[/muted]")
    app_branch.add("[muted]migrations/[/muted]")
    tree.add("[muted].env.example[/muted]")
    tree.add("[muted]pyproject.toml[/muted]")
    tree.add("[muted]Makefile[/muted]")

    console.print(tree)
    console.print()

    _next_steps(project_name)
