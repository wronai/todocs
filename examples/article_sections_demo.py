#!/usr/bin/env python3
"""Example: Using article_sections module directly for custom output.

Demonstrates how to use individual section renderers from the refactored
article_sections module to build custom documentation formats.

Usage:
    python examples/article_sections_demo.py /path/to/project
"""

import sys
from pathlib import Path

from todocs.core import scan_project
from todocs.generators.article_sections import (
    render_architecture,
    render_api_surface,
    render_dependencies,
    render_docker,
    render_footer,
    render_frontmatter,
    render_header,
    render_metrics,
    render_maturity,
    render_overview,
    render_tech_stack,
    render_usage,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python article_sections_demo.py <project_path>")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()
    profile = scan_project(project_path)

    org_name = "WronAI"
    org_url = "https://github.com/wronai"
    generated_at = "2026-03-08"

    print("═" * 60)
    print("  Custom Article Assembly Demo")
    print("═" * 60)
    print()

    # Example 1: Build minimal article (just metrics + maturity)
    print("┌─ Minimal Article (Metrics + Maturity) ─────────────┐")
    print()
    minimal = "\n\n".join([
        render_frontmatter(profile, org_name, generated_at),
        render_header(profile, org_url),
        render_metrics(profile),
        render_maturity(profile),
        render_footer(generated_at),
    ])
    print(minimal[:800] + "..." if len(minimal) > 800 else minimal)
    print()

    # Example 2: Build tech-focused article
    print("┌─ Tech-Focused Article ────────────────────────────┐")
    print()
    tech_article = "\n\n".join([
        render_frontmatter(profile, org_name, generated_at),
        render_header(profile, org_url),
        render_overview(profile, org_name),
        render_tech_stack(profile),
        render_architecture(profile),
        render_dependencies(profile),
        render_docker(profile),
        render_footer(generated_at),
    ])
    # Print just the tech stack section as example
    print(render_tech_stack(profile))
    print()

    # Example 3: Build API documentation
    print("┌─ API Documentation ────────────────────────────────┐")
    print()
    api_section = render_api_surface(profile)
    if api_section:
        print(api_section)
    else:
        print("(No API surface detected for this project)")
    print()

    # Example 4: Build usage guide
    print("┌─ Usage Guide ─────────────────────────────────────┐")
    print()
    usage_section = render_usage(profile)
    print(usage_section)
    print()

    # Example 5: Save custom article to file
    print("┌─ Saving Custom Article ───────────────────────────┐")
    print()
    custom_article = "\n\n".join([
        render_frontmatter(profile, org_name, generated_at),
        render_header(profile, org_url),
        render_overview(profile, org_name),
        render_metrics(profile),
        render_maturity(profile),
        render_footer(generated_at),
    ])

    output_path = Path(f"{profile.name}-custom-article.md")
    output_path.write_text(custom_article, encoding="utf-8")
    print(f"✓ Saved custom article to: {output_path}")
    print(f"  Size: {len(custom_article)} chars")
    print()

    print("═" * 60)
    print("  Demo complete!")
    print("═" * 60)


if __name__ == "__main__":
    main()
