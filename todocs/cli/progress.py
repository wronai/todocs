"""CLI progress utilities with Rich UI support."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .utils import HAS_RICH, CONSTANT_40, CONSTANT_70

if HAS_RICH:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn

if TYPE_CHECKING:
    from rich.console import Console


def discover_and_show_progress(root: Path, exclude: tuple, console) -> list:
    """Discover projects and show progress. Returns list of project directories."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Discovering projects...", total=None)
        from todocs.core import _discover_projects
        project_dirs = _discover_projects(root, exclude=list(exclude))
        progress.update(task, description=f"Found {len(project_dirs)} projects")
    return project_dirs


def scan_with_progress(root: Path, exclude: tuple, console, project_dirs: list) -> list:
    """Scan projects with real-time progress feedback."""
    from todocs.core import scan_organization

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing...", total=len(project_dirs))

        def on_project_scanned(project_name: str, idx: int, total: int):
            progress.update(task, description=f"Analyzing [cyan]{project_name}[/cyan] ({idx}/{total})")

        profiles = scan_organization(
            root,
            exclude=list(exclude),
            progress_callback=on_project_scanned
        )
        progress.update(task, completed=len(project_dirs))
    return profiles


def print_project_summary(console, profiles: list):
    """Print a formatted summary table of analyzed projects."""
    if not profiles:
        return

    table = Table(title="Project Summary")
    table.add_column("Project", style="cyan")
    table.add_column("Version")
    table.add_column("Grade", justify="center")
    table.add_column("Language")
    table.add_column("SLOC", justify="right")
    table.add_column("Tests", justify="center")

    for p in sorted(profiles, key=lambda x: x.name):
        grade_style = (
            "green" if p.maturity.score >= CONSTANT_70
            else "yellow" if p.maturity.score >= CONSTANT_40
            else "red"
        )
        table.add_row(
            p.name,
            p.metadata.version or "—",
            f"[{grade_style}]{p.maturity.grade}[/{grade_style}]",
            p.tech_stack.primary_language,
            f"{p.code_stats.source_lines:,}",
            "✓" if p.maturity.has_tests else "✗",
        )

    console.print(table)


def generate_articles_with_progress(profiles: list, out: Path, org_name: str, org_url: str, console) -> list:
    """Generate articles with progress indicator."""
    from todocs.core import generate_articles

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating articles...", total=None)
        paths = generate_articles(profiles, out, org_name=org_name, org_url=org_url)
        progress.update(task, description=f"Generated {len(paths)} articles")

    return paths


def generate_with_rich(
    root: Path,
    out: Path,
    exclude: tuple,
    org_name: str,
    org_url: str
) -> list:
    """Generate articles with Rich progress UI."""
    from rich.console import Console
    
    console = Console()
    console.print(f"[bold]todocs[/bold] — Scanning [cyan]{root}[/cyan]")

    # Discover projects
    project_dirs = discover_and_show_progress(root, exclude, console)

    # Scan projects
    if project_dirs:
        console.print()
        profiles = scan_with_progress(root, exclude, console, project_dirs)
    else:
        profiles = []

    console.print(f"\n[green]✓[/green] Analyzed [bold]{len(profiles)}[/bold] projects")

    # Print summary table
    print_project_summary(console, profiles)

    # Generate articles
    if profiles:
        paths = generate_articles_with_progress(profiles, out, org_name, org_url, console)
        console.print(f"\n[green]✓[/green] Generated [bold]{len(paths)}[/bold] articles in [cyan]{out}[/cyan]")

    return profiles


def generate_without_rich(root: Path, out: Path, exclude: tuple, org_name: str, org_url: str) -> list:
    """Generate articles without Rich library (plain output)."""
    from todocs.core import _discover_projects, scan_project, generate_articles

    print(f"todocs — Scanning {root}")

    project_dirs = _discover_projects(root, exclude=list(exclude))
    print(f"Found {len(project_dirs)} projects")

    if not project_dirs:
        print("No projects found.")
        return []

    print()
    profiles = []
    for i, proj_dir in enumerate(project_dirs, 1):
        print(f"  [{i}/{len(project_dirs)}] Analyzing {proj_dir.name}...", end=" ")
        try:
            profile = scan_project(proj_dir)
            profiles.append(profile)
            print(f"✓ ({profile.maturity.grade}, {profile.code_stats.source_lines:,} SLOC)")
        except Exception as e:
            print(f"✗ Error: {e}")

    print()
    for p in sorted(profiles, key=lambda x: x.name):
        print(f"  {p.name:30s}  v{p.metadata.version or '?':10s}  "
              f"Grade:{p.maturity.grade:3s}  {p.tech_stack.primary_language:12s}  "
              f"{p.code_stats.source_lines:>6,} SLOC")

    paths = generate_articles(profiles, out, org_name=org_name, org_url=org_url)
    print(f"\nGenerated {len(paths)} articles in {out}")

    return profiles
