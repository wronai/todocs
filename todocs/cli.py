"""CLI interface for todocs — generate project documentation articles."""

from __future__ import annotations

import json
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


@click.group()
@click.version_option(version="0.1.0", prog_name="todocs")
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
    from todocs.core import scan_organization, generate_articles

    root = Path(root_dir).resolve()
    out = Path(output_dir)
    scanned_projects = []

    if HAS_RICH:
        console = Console()
        console.print(f"[bold]todocs[/bold] — Scanning [cyan]{root}[/cyan]")

        # Discover projects first
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Discovering projects...", total=None)
            # Quick discovery to show count
            from todocs.core import _discover_projects
            project_dirs = _discover_projects(root, exclude=list(exclude))
            progress.update(task, description=f"Found {len(project_dirs)} projects")

        if project_dirs:
            console.print()
            # Scan each project with real-time feedback
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
        else:
            profiles = []

        console.print(f"\n[green]✓[/green] Analyzed [bold]{len(profiles)}[/bold] projects")

        # Summary table
        if profiles:
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

        # Generate articles
        if profiles:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating articles...", total=None)
                paths = generate_articles(profiles, out, org_name=org_name, org_url=org_url)
                progress.update(task, description=f"Generated {len(paths)} articles")

            console.print(f"\n[green]✓[/green] Generated [bold]{len(paths)}[/bold] articles in [cyan]{out}[/cyan]")

    else:
        # No rich — plain output with verbose progress
        print(f"todocs — Scanning {root}")

        # Quick discovery
        from todocs.core import _discover_projects
        project_dirs = _discover_projects(root, exclude=list(exclude))
        print(f"Found {len(project_dirs)} projects")

        if project_dirs:
            print()
            profiles = []
            for i, proj_dir in enumerate(project_dirs, 1):
                from todocs.core import scan_project
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
        else:
            profiles = []
            print("No projects found.")

    # Optional JSON report
    if json_report:
        report_data = [p.to_dict() for p in profiles]
        Path(json_report).write_text(
            json.dumps(report_data, indent=2, default=str), encoding="utf-8"
        )
        if HAS_RICH:
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


if __name__ == "__main__":
    main()
