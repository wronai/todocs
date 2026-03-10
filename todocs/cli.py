"""CLI interface for todocs — generate project documentation articles."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def _detect_org_from_git(root_dir: Path) -> tuple[str, str]:
    """Detect organization name and URL from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Parse github.com/user/repo or git@github.com:user/repo
            match = re.search(r"github\.com[/:]([^/]+)", url)
            if match:
                org = match.group(1)
                return org, f"https://github.com/{org}"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fallback: use parent directory name
    org = root_dir.parent.name if root_dir.parent.name else root_dir.name
    return org, f"https://github.com/{org}"


@click.group()
@click.version_option(version="0.1.7", prog_name="todocs")
def main():
    """todocs — Static-analysis documentation generator for project portfolios.

    Generates WordPress-ready markdown articles from source code analysis.
    No LLM required.
    """
    pass


@main.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_dir", default="articles",
              help="Output directory for generated articles")
@click.option("--org-name", default="WronAI", help="Organization name")
@click.option("--org-url", default="https://github.com/wronai", help="Organization URL")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
@click.option("--json-report", type=click.Path(), default=None,
              help="Also write a JSON report of all profiles")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def generate(
    root_dir: str,
    output_dir: str,
    org_name: str,
    org_url: str,
    exclude: tuple,
    json_report: Optional[str],
    verbose: bool,
):
    """Scan projects and generate WordPress markdown articles.

    ROOT_DIR is the directory containing project subdirectories.
    """
    root = Path(root_dir).resolve()
    out = Path(output_dir)

    if HAS_RICH:
        console = Console()
        console.print(f"[bold]todocs[/bold] — Scanning [cyan]{root}[/cyan]")

        # Discover projects
        project_dirs = _discover_and_show_progress(root, exclude, console)

        # Scan projects
        if project_dirs:
            console.print()
            profiles = _scan_with_progress(root, exclude, console, project_dirs)
        else:
            profiles = []

        console.print(f"\n[green]✓[/green] Analyzed [bold]{len(profiles)}[/bold] projects")

        # Print summary table
        _print_project_summary(console, profiles)

        # Generate articles
        if profiles:
            paths = _generate_articles_with_progress(profiles, out, org_name, org_url, console)
            console.print(f"\n[green]✓[/green] Generated [bold]{len(paths)}[/bold] articles in [cyan]{out}[/cyan]")
    else:
        # Plain output without Rich
        profiles = _generate_without_rich(root, out, exclude, org_name, org_url)

    # Optional JSON report
    _write_json_report(profiles, json_report, console if HAS_RICH else None, HAS_RICH)

def _discover_and_show_progress(root: Path, exclude: tuple, console) -> list:
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


def _scan_with_progress(root: Path, exclude: tuple, console, project_dirs: list) -> list:
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


def _print_project_summary(console, profiles: list):
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
            "green" if p.maturity.score >= 70
            else "yellow" if p.maturity.score >= 40
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


def _generate_articles_with_progress(profiles: list, out: Path, org_name: str, org_url: str, console) -> list:
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


def _generate_without_rich(root: Path, out: Path, exclude: tuple, org_name: str, org_url: str) -> list:
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


def _write_json_report(profiles: list, json_report: Optional[str], console, has_rich: bool):
    """Write optional JSON report."""
    if not json_report:
        return

    report_data = [p.to_dict() for p in profiles]
    Path(json_report).write_text(
        json.dumps(report_data, indent=2, default=str), encoding="utf-8"
    )
    if has_rich:
        console.print(f"[green]✓[/green] JSON report written to [cyan]{json_report}[/cyan]")
    else:
        print(f"JSON report written to {json_report}")


@main.command()
@click.argument("project_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", type=click.Path(), default=None,
              help="Output file (default: stdout)")
@click.option("--format", "fmt", type=click.Choice(["markdown", "json"]), default="markdown",
              help="Output format")
def inspect(project_dir: str, output: Optional[str], fmt: str):
    """Inspect a single project and show its profile.

    PROJECT_DIR is the path to the project directory.
    """
    from todocs.core import scan_project

    path = Path(project_dir).resolve()
    profile = scan_project(path)

    if fmt == "json":
        text = profile.to_json()
    else:
        from todocs.generators.article import ArticleGenerator
        gen = ArticleGenerator()
        text = gen._render_article(profile)

    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Written to {output}")
    else:
        print(text)


@main.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_path", default="comparison.md",
              help="Output file path")
@click.option("--org-name", default="WronAI", help="Organization name")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
def compare(root_dir: str, output_path: str, org_name: str, exclude: tuple):
    """Generate cross-project comparison report.

    ROOT_DIR is the directory containing project subdirectories.
    """
    from todocs.core import scan_organization
    from todocs.generators.comparison import ComparisonGenerator

    root = Path(root_dir).resolve()
    profiles = scan_organization(root, exclude=list(exclude))

    if len(profiles) < 2:
        click.echo("Need at least 2 projects for comparison.", err=True)
        raise SystemExit(1)

    gen = ComparisonGenerator(org_name=org_name)
    gen.generate_comparison(profiles, Path(output_path))
    click.echo(f"Comparison report written to {output_path} ({len(profiles)} projects)")


@main.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_path", default="health-report.md",
              help="Output file path")
@click.option("--org-name", default="WronAI", help="Organization name")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
def health(root_dir: str, output_path: str, org_name: str, exclude: tuple):
    """Generate organization health report.

    ROOT_DIR is the directory containing project subdirectories.
    """
    from todocs.core import scan_organization
    from todocs.generators.comparison import ComparisonGenerator

    root = Path(root_dir).resolve()
    profiles = scan_organization(root, exclude=list(exclude))

    gen = ComparisonGenerator(org_name=org_name)
    gen.generate_health_report(profiles, Path(output_path))
    click.echo(f"Health report written to {output_path} ({len(profiles)} projects)")


@main.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_path", default="README.md",
              help="Output file path")
@click.option("--org-name", default=None, help="Organization name (auto-detected from git if not provided)")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
@click.option("--title", default="Project Portfolio", help="README title")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def readme(root_dir: str, output_path: str, org_name: str, exclude: tuple, title: str, verbose: bool):
    """Generate a single README.md with project list and 5-line descriptions.

    ROOT_DIR is the directory containing project subdirectories.

    Example:
        todocs readme /home/tom/github/wronai --output README.md --org-name WronAI
    """
    from todocs.core import scan_organization
    from todocs.generators.comparison import ComparisonGenerator

    root = Path(root_dir).resolve()
    profiles = scan_organization(root, exclude=list(exclude))

    if not profiles:
        click.echo("No projects found.", err=True)
        raise SystemExit(1)

    # Auto-detect org if not provided
    if org_name is None:
        org_name, org_url = _detect_org_from_git(root)
        if verbose:
            click.echo(f"Detected organization: {org_name} ({org_url})")
    else:
        org_url = f"https://github.com/{org_name}"

    gen = ComparisonGenerator(org_name=org_name, org_url=org_url)
    gen.generate_readme_list(profiles, Path(output_path), title=title)
    click.echo(f"README written to {output_path} ({len(profiles)} projects)")


@main.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_path", default="status-report.md",
              help="Output file path")
@click.option("--org-name", default="WronAI", help="Organization name")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
def status(root_dir: str, output_path: str, org_name: str, exclude: tuple):
    """Generate organization status report with KPIs and recommendations.

    ROOT_DIR is the directory containing project subdirectories.
    """
    from todocs.core import scan_organization
    from todocs.generators.status_report_gen import StatusReportGenerator

    root = Path(root_dir).resolve()
    profiles = scan_organization(root, exclude=list(exclude))

    gen = StatusReportGenerator(org_name=org_name)
    gen.generate(profiles, Path(output_path))
    click.echo(f"Status report written to {output_path} ({len(profiles)} projects)")


@main.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_dir", default="cards",
              help="Output directory for card files")
@click.option("--org-name", default="WronAI", help="Organization name")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
def cards(root_dir: str, output_dir: str, org_name: str, exclude: tuple):
    """Generate project cards (compact single-project summaries).

    ROOT_DIR is the directory containing project subdirectories.
    """
    from todocs.core import scan_organization
    from todocs.generators.project_card_gen import ProjectCardGenerator

    root = Path(root_dir).resolve()
    profiles = scan_organization(root, exclude=list(exclude))

    gen = ProjectCardGenerator(org_name=org_name)
    paths = gen.generate_all(profiles, Path(output_dir))
    click.echo(f"Generated {len(paths)} project cards in {output_dir}")


@main.command()
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_path", default="index.md",
              help="Output file path")
@click.option("--org-name", default="WronAI", help="Organization name")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
def index(root_dir: str, output_path: str, org_name: str, exclude: tuple):
    """Generate organization project index / catalog page.

    ROOT_DIR is the directory containing project subdirectories.
    """
    from todocs.core import scan_organization
    from todocs.generators.org_index_gen import OrgIndexGenerator

    root = Path(root_dir).resolve()
    profiles = scan_organization(root, exclude=list(exclude))

    if not profiles:
        click.echo("No projects found.", err=True)
        raise SystemExit(1)

    gen = OrgIndexGenerator(org_name=org_name)
    gen.generate(profiles, Path(output_path))
    click.echo(f"Index written to {output_path} ({len(profiles)} projects)")


@main.command(name="export")
@click.argument("root_dir", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", "output_path", required=True,
              help="Output file or directory path")
@click.option("--format", "fmt", type=click.Choice(["html", "json"]), required=True,
              help="Export format")
@click.option("--org-name", default="WronAI", help="Organization name")
@click.option("--exclude", multiple=True, help="Directory names to exclude")
def export_cmd(root_dir: str, output_path: str, fmt: str, org_name: str, exclude: tuple):
    """Export organization report in HTML or JSON format.

    ROOT_DIR is the directory containing project subdirectories.

    Examples:
        todocs export /path/to/org --format html -o report.html
        todocs export /path/to/org --format json -o report.json
    """
    from todocs.core import scan_organization

    root = Path(root_dir).resolve()
    profiles = scan_organization(root, exclude=list(exclude))

    if not profiles:
        click.echo("No projects found.", err=True)
        raise SystemExit(1)

    out = Path(output_path)

    if fmt == "html":
        from todocs.outputs.html import HTMLOutput
        writer = HTMLOutput(org_name=org_name)
        writer.write(profiles, out)
    elif fmt == "json":
        from todocs.outputs.json import JSONOutput
        writer = JSONOutput(org_name=org_name)
        writer.write(profiles, out)

    click.echo(f"{fmt.upper()} report written to {output_path} ({len(profiles)} projects)")


if __name__ == "__main__":
    main()
