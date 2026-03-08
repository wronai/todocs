#!/usr/bin/env python3
"""Example: Deep API surface analysis using refactored helpers.

Demonstrates how to use the extracted helper methods from APISurfaceAnalyzer
to perform detailed analysis of public API components.

Usage:
    python examples/api_surface_deep.py /path/to/project
"""

import sys
from pathlib import Path

from todocs.analyzers.api_surface import APISurfaceAnalyzer


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print()
    print("═" * 60)
    print(f"  {title}")
    print("═" * 60)


def analyze_entry_points(analyzer: APISurfaceAnalyzer) -> None:
    """Analyze and display entry points."""
    print_section("Entry Points (from pyproject.toml)")

    entry_points = analyzer._detect_entry_points()
    if entry_points:
        for cmd, target in entry_points.items():
            print(f"  • {cmd} → {target}")
    else:
        print("  (No entry points found)")


def analyze_cli_commands(analyzer: APISurfaceAnalyzer) -> None:
    """Analyze and display CLI commands."""
    print_section("CLI Commands (Click/Typer)")

    commands = analyzer._detect_cli_commands()
    if commands:
        by_framework = {}
        for cmd in commands:
            fw = cmd.get("framework", "unknown")
            by_framework.setdefault(fw, []).append(cmd)

        for framework, cmds in by_framework.items():
            print(f"\n  [{framework.upper()}]")
            for cmd in cmds:
                desc = cmd.get("description", "")
                print(f"    • {cmd['name']}")
                if desc:
                    print(f"      {desc[:60]}{'...' if len(desc) > 60 else ''}")
    else:
        print("  (No CLI commands detected)")


def analyze_public_symbols(analyzer: APISurfaceAnalyzer) -> None:
    """Analyze and display public classes and functions."""
    print_section("Public Symbols (from __init__.py and main modules)")

    # Use the refactored helper to get target files
    target_files = analyzer._collect_target_files()
    print(f"  Scanning {len(target_files)} target files...")

    # Collect all symbols
    all_classes = []
    all_functions = []
    seen_classes = set()
    seen_funcs = set()

    for pyf in target_files[:10]:  # Limit to first 10 for demo
        cls, funcs = analyzer._extract_from_file(pyf, seen_classes, seen_funcs)
        all_classes.extend(cls)
        all_functions.extend(funcs)

    print(f"\n  Found {len(all_classes)} public classes:")
    for cls in all_classes[:8]:
        methods = cls.get("methods", [])
        exported = " (exported)" if cls.get("is_exported") else ""
        print(f"    • {cls['name']} — {len(methods)} methods{exported}")
        print(f"      File: {cls['file']}")

    print(f"\n  Found {len(all_functions)} public functions:")
    for func in all_functions[:8]:
        args = func.get("args", [])
        exported = " (exported)" if func.get("is_exported") else ""
        print(f"    • {func['name']}({', '.join(args[:3])}{'...' if len(args) > 3 else ''}){exported}")
        print(f"      File: {func['file']}")


def analyze_rest_endpoints(analyzer: APISurfaceAnalyzer) -> None:
    """Analyze and display REST API endpoints."""
    print_section("REST Endpoints (FastAPI/Flask)")

    endpoints = analyzer._detect_rest_endpoints()
    if endpoints:
        by_method = {}
        for ep in endpoints:
            method = ep.get("method", "GET")
            by_method.setdefault(method, []).append(ep)

        for method in sorted(by_method.keys()):
            eps = by_method[method]
            print(f"\n  [{method}] — {len(eps)} endpoints")
            for ep in eps[:5]:  # Show first 5 per method
                print(f"    • {ep['path']}")
                print(f"      File: {ep['file']}")
            if len(eps) > 5:
                print(f"    ... and {len(eps) - 5} more")
    else:
        print("  (No REST endpoints detected)")


def analyze_symbol_sources(analyzer: APISurfaceAnalyzer) -> None:
    """Show which files contribute public symbols."""
    print_section("Symbol Sources by File")

    target_files = analyzer._collect_target_files()
    file_symbols = {}

    seen_classes = set()
    seen_funcs = set()

    for pyf in target_files:
        cls, funcs = analyzer._extract_from_file(pyf, seen_classes, seen_funcs)
        if cls or funcs:
            file_symbols[str(pyf.relative_to(analyzer.root))] = {
                "classes": len(cls),
                "functions": len(funcs),
            }

    for filepath, counts in sorted(file_symbols.items(), key=lambda x: -(x[1]["classes"] + x[1]["functions"])):
        total = counts["classes"] + counts["functions"]
        print(f"  • {filepath}")
        print(f"    Classes: {counts['classes']}, Functions: {counts['functions']} (Total: {total})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python api_surface_deep.py <project_path>")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()

    if not project_path.exists():
        print(f"Error: Path not found: {project_path}")
        sys.exit(1)

    print()
    print("█" * 60)
    print("  DEEP API SURFACE ANALYSIS")
    print("█" * 60)
    print(f"  Project: {project_path.name}")
    print(f"  Path: {project_path}")
    print("█" * 60)

    analyzer = APISurfaceAnalyzer(project_path)

    # Run all analyses
    analyze_entry_points(analyzer)
    analyze_cli_commands(analyzer)
    analyze_public_symbols(analyzer)
    analyze_rest_endpoints(analyzer)
    analyze_symbol_sources(analyzer)

    print()
    print("█" * 60)
    print("  Analysis complete!")
    print("█" * 60)
    print()


if __name__ == "__main__":
    main()
