#!/usr/bin/env python3
"""Example: Scan a single project and display its profile.

Usage:
    python examples/scan_single.py /path/to/project
    python examples/scan_single.py /path/to/project --json
"""

import sys
from pathlib import Path

from todocs.core import scan_project

CONSTANT_5 = 5
CONSTANT_60 = 60



def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_single.py <project_path> [--json]")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()
    output_json = "--json" in sys.argv

    if not project_path.is_dir():
        print(f"Error: {project_path} is not a directory")
        sys.exit(1)

    print(f"Scanning {project_path.name}...")
    profile = scan_project(project_path)

    if output_json:
        print(profile.to_json())
    else:
        # Pretty print summary
        meta = profile.metadata
        stats = profile.code_stats
        mat = profile.maturity

        print(f"\n{'='*CONSTANT_60}")
        print(f"  {meta.name or profile.name}  v{meta.version or '?'}")
        print(f"{'='*CONSTANT_60}")
        print(f"  Description : {meta.description or '(none)'}")
        print(f"  Language    : {profile.tech_stack.primary_language}")
        print(f"  Category    : {profile.category}")
        print(f"  License     : {meta.license or '(none)'}")
        print(f"\n  Code:")
        print(f"    Source files : {stats.source_files}")
        print(f"    Source lines : {stats.source_lines:,}")
        print(f"    Test files   : {stats.test_files}")
        print(f"    Avg. CC      : {stats.avg_complexity:.1f}")
        print(f"\n  Maturity: {mat.grade} ({mat.score:.0f}/100)")
        print(f"    Tests    : {'✓' if mat.has_tests else '✗'}")
        print(f"    CI/CD    : {'✓' if mat.has_ci else '✗'}")
        print(f"    Docs     : {'✓' if mat.has_docs else '✗'}")
        print(f"    Docker   : {'✓' if mat.has_docker else '✗'}")
        print(f"    Changelog: {'✓' if mat.has_changelog else '✗'}")

        if profile.dependencies:
            print(f"\n  Dependencies ({len(profile.dependencies)}):")
            print(f"    {', '.join(profile.dependencies[:10])}")
            if len(profile.dependencies) > 10:
                print(f"    ... and {len(profile.dependencies) - 10} more")

        if profile.key_modules:
            print(f"\n  Top Modules:")
            for mod in profile.key_modules[:CONSTANT_5]:
                print(f"    {mod['path']:40s} {mod['lines']:>5}L  "
                      f"{len(mod.get('classes',[]))}C {len(mod.get('functions',[]))}F")

        if profile.makefile_targets:
            print(f"\n  Build Targets ({len(profile.makefile_targets)}):")
            for t in profile.makefile_targets[:CONSTANT_5]:
                desc = f" — {t['description']}" if t.get('description') else ""
                print(f"    make {t['name']}{desc}")

        api = profile.api_surface
        if api:
            cli = api.get("cli_commands", [])
            endpoints = api.get("rest_endpoints", [])
            if cli:
                print(f"\n  CLI Commands ({len(cli)}):")
                for cmd in cli[:CONSTANT_5]:
                    print(f"    {cmd['name']}")
            if endpoints:
                print(f"\n  REST Endpoints ({len(endpoints)}):")
                for ep in endpoints[:CONSTANT_5]:
                    print(f"    {ep['method']} {ep['path']}")

        print(f"\n  Summary: {profile.summary}")
        print()


if __name__ == "__main__":
    main()
