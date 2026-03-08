#!/usr/bin/env python3
"""Example: Use individual analyzers for custom analysis.

Demonstrates how to use todocs analyzers and extractors independently
without the full scan_project pipeline.

Usage:
    python examples/custom_analysis.py /path/to/project
"""

import json
import sys
from pathlib import Path

from todocs.analyzers.code_metrics import CodeMetricsAnalyzer
from todocs.analyzers.structure import StructureAnalyzer
from todocs.analyzers.import_graph import ImportGraphAnalyzer
from todocs.analyzers.api_surface import APISurfaceAnalyzer
from todocs.extractors.toon_parser import ToonParser
from todocs.extractors.makefile_parser import MakefileParser
from todocs.extractors.docker_parser import DockerParser


def _print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("═" * 60)
    print(f"  {title}")
    print("═" * 60)


def _analyze_import_graph(project_path: Path) -> None:
    """Analyze and display import dependency graph."""
    _print_section_header("Import Dependency Graph")

    ig = ImportGraphAnalyzer(project_path)
    graph = ig.build_graph()

    print(f"  Nodes:          {len(graph['nodes'])}")
    print(f"  Internal edges: {graph['total_internal_edges']}")
    print(f"  Cycles:         {len(graph['cycles'])}")

    if graph["external_imports"]:
        print(f"\n  Top external imports:")
        for pkg, count in list(graph["external_imports"].items())[:8]:
            print(f"    {pkg:20s}  {count} imports")

    if graph["fan_in"]:
        print(f"\n  Most imported modules (fan-in):")
        for mod, fi in list(graph["fan_in"].items())[:5]:
            print(f"    {mod:30s}  ←{fi}")

    hubs = ig.get_hub_modules(top_n=5)
    if hubs:
        print(f"\n  Hub modules:")
        for h in hubs:
            print(f"    {h['module']:30s}  in={h['fan_in']} out={h['fan_out']}")


def _analyze_api_surface(project_path: Path) -> None:
    """Analyze and display API surface."""
    _print_section_header("API Surface")

    api = APISurfaceAnalyzer(project_path)
    surface = api.analyze()

    entry_pts = surface.get("entry_points", {})
    if entry_pts:
        print(f"\n  Entry points:")
        for cmd, target in entry_pts.items():
            print(f"    {cmd} → {target}")

    cli_cmds = surface.get("cli_commands", [])
    if cli_cmds:
        print(f"\n  CLI commands ({len(cli_cmds)}):")
        for cmd in cli_cmds:
            desc = f" — {cmd['description']}" if cmd.get('description') else ""
            print(f"    {cmd['name']}{desc}")

    endpoints = surface.get("rest_endpoints", [])
    if endpoints:
        print(f"\n  REST endpoints ({len(endpoints)}):")
        for ep in endpoints[:10]:
            print(f"    {ep['method']:6s} {ep['path']}")

    pub_cls = surface.get("public_classes", [])
    if pub_cls:
        print(f"\n  Public classes ({len(pub_cls)}):")
        for cls in pub_cls[:8]:
            methods = cls.get("methods", [])
            print(f"    {cls['name']:25s}  {len(methods)} public methods")


def _analyze_toon_files(project_path: Path) -> None:
    """Analyze and display TOON file data."""
    toon = ToonParser(project_path)
    toon_files = toon.find_toon_files()
    if not toon_files:
        return

    _print_section_header("TOON Data")

    data = toon.parse_all()
    print(f"  Found files: {', '.join(data.get('toon_files', []))}")

    if "analysis" in data:
        analysis = data["analysis"]
        print(f"  Avg complexity (toon): {analysis.get('avg_complexity', '?')}")
        print(f"  Dependency cycles:     {analysis.get('dependency_cycles', '?')}")
        for w in analysis.get("health_warnings", [])[:3]:
            print(f"    ⚠ {w['function']} CC={w['complexity']}")

    if "flow" in data:
        flow = data["flow"]
        pipes = flow.get("pipelines", [])
        print(f"  Pipelines: {len(pipes)}")
        for pipe in pipes[:3]:
            print(f"    [{pipe['category']}] {pipe['signature']}")


def _analyze_makefile(project_path: Path) -> None:
    """Analyze and display Makefile targets."""
    mk = MakefileParser(project_path)
    mk_data = mk.parse()
    targets = mk_data.get("targets", [])
    if not targets:
        return

    _print_section_header(f"Build Targets ({mk_data['type']})")
    for t in targets[:10]:
        desc = f" — {t['description']}" if t.get('description') else ""
        print(f"  make {t['name']}{desc}")


def _analyze_docker(project_path: Path) -> None:
    """Analyze and display Docker infrastructure."""
    docker = DockerParser(project_path)
    docker_data = docker.parse()
    if not docker_data.get("has_dockerfile") and not docker_data.get("has_compose"):
        return

    _print_section_header("Docker Infrastructure")
    if docker_data.get("base_images"):
        print(f"  Base images: {', '.join(docker_data['base_images'])}")
    for svc in docker_data.get("services", []):
        img = svc.get("image") or "(build)"
        ports = ", ".join(svc.get("ports", [])) or "—"
        print(f"  Service: {svc['name']:15s}  image={img}  ports={ports}")


def _analyze_code_metrics(project_path: Path) -> None:
    """Analyze and display code metrics."""
    _print_section_header("Code Metrics (radon)")

    cm = CodeMetricsAnalyzer(project_path)
    stats = cm.analyze()
    print(f"  Source files:   {stats.source_files}")
    print(f"  Source lines:   {stats.source_lines:,}")
    print(f"  Avg complexity: {stats.avg_complexity:.1f}")
    print(f"  Max complexity: {stats.max_complexity:.0f}")
    print(f"  Maintainability: {stats.maintainability_index:.1f}")

    if stats.hotspots:
        print(f"\n  Hotspots:")
        for hs in stats.hotspots[:5]:
            print(f"    {hs['name']:30s}  CC={hs['complexity']:>3}  "
                  f"rank={hs.get('rank','?')}  {hs['file']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python custom_analysis.py <project_path>")
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()

    _analyze_import_graph(project_path)
    _analyze_api_surface(project_path)
    _analyze_toon_files(project_path)
    _analyze_makefile(project_path)
    _analyze_docker(project_path)
    _analyze_code_metrics(project_path)

    print()


if __name__ == "__main__":
    main()
