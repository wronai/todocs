"""CLI command implementations."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from .utils import HAS_RICH, detect_org_from_git, write_json_report
from .progress import (
    generate_with_rich,
    generate_without_rich,
)

if HAS_RICH:
    from rich.console import Console


@click.command()
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
        profiles = generate_with_rich(root, out, exclude, org_name, org_url)
        console = Console()
    else:
        # Plain output without Rich
        profiles = generate_without_rich(root, out, exclude, org_name, org_url)
        console = None

    # Optional JSON report
    write_json_report(profiles, json_report, console, HAS_RICH)


@click.command()
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


@click.command()
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


@click.command()
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


@click.command()
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
        org_name, org_url = detect_org_from_git(root)
        if verbose:
            click.echo(f"Detected organization: {org_name} ({org_url})")
    else:
        org_url = f"https://github.com/{org_name}"

    gen = ComparisonGenerator(org_name=org_name, org_url=org_url)
    gen.generate_readme_list(profiles, Path(output_path), title=title)
    click.echo(f"README written to {output_path} ({len(profiles)} projects)")


@click.command()
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


@click.command()
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


@click.command()
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


@click.command(name="export")
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
