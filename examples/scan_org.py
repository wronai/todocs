#!/usr/bin/env python3
"""Example: Scan an entire organization and generate WordPress articles.

Usage:
    python examples/scan_org.py /path/to/wronai --output articles/
"""

import sys
from pathlib import Path

from todocs.core import scan_organization, generate_articles


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_org.py <org_root> [--output <dir>]")
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    output_dir = Path("articles")

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = Path(sys.argv[idx + 1])

    print(f"Scanning organization at {root}...")
    profiles = scan_organization(root)
    print(f"Found {len(profiles)} projects\n")

    # Print quick summary
    for p in sorted(profiles, key=lambda x: -x.code_stats.source_lines):
        print(f"  {p.name:30s}  {p.maturity.grade:>3s}  "
              f"{p.code_stats.source_lines:>6,} SLOC  "
              f"{p.tech_stack.primary_language:>10s}  "
              f"v{p.metadata.version or '?'}")

    # Category distribution
    categories = {}
    for p in profiles:
        categories[p.category] = categories.get(p.category, 0) + 1
    print(f"\nCategories:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat:30s}  {count}")

    # Generate articles
    print(f"\nGenerating articles to {output_dir}...")
    paths = generate_articles(
        profiles,
        output_dir,
        org_name="WronAI",
        org_url="https://github.com/wronai",
    )
    print(f"\nGenerated {len(paths)} files:")
    for p in paths:
        size = p.stat().st_size
        print(f"  {p.name:40s}  {size:>6} bytes")


if __name__ == "__main__":
    main()
