#!/usr/bin/env python3
"""Example: Generate organization health report with detailed metrics.

Demonstrates how to scan an organization, analyze project health,
and generate a comprehensive health report with maturity distribution.

Usage:
    python examples/organization_health_report.py /path/to/org
    python examples/organization_health_report.py /path/to/org -o report.md
"""

import argparse
import sys
from pathlib import Path

from todocs import scan_organization
from todocs.generators.comparison import ComparisonGenerator


def analyze_maturity_distribution(profiles: list) -> dict:
    """Analyze maturity grade distribution across projects."""
    grades = {}
    scores = []

    for p in profiles:
        grade = p.maturity.grade
        grades[grade] = grades.get(grade, 0) + 1
        scores.append(p.maturity.score)

    return {
        "by_grade": grades,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
    }


def analyze_code_metrics(profiles: list) -> dict:
    """Aggregate code metrics across all projects."""
    total_lines = sum(p.code_stats.source_lines for p in profiles)
    total_files = sum(p.code_stats.source_files for p in profiles)
    total_tests = sum(p.code_stats.test_files for p in profiles)

    complexities = [p.code_stats.avg_complexity for p in profiles if p.code_stats.avg_complexity > 0]

    return {
        "total_projects": len(profiles),
        "total_lines": total_lines,
        "total_files": total_files,
        "total_tests": total_tests,
        "avg_complexity": sum(complexities) / len(complexities) if complexities else 0,
    }


def analyze_tech_stacks(profiles: list) -> dict:
    """Analyze technology distribution across projects."""
    languages = {}
    frameworks = set()
    build_tools = set()

    for p in profiles:
        # Languages
        for lang, count in p.tech_stack.languages.items():
            languages[lang] = languages.get(lang, 0) + count

        # Frameworks and build tools
        frameworks.update(p.tech_stack.frameworks)
        build_tools.update(p.tech_stack.build_tools)

    return {
        "languages": dict(sorted(languages.items(), key=lambda x: -x[1])),
        "frameworks": sorted(frameworks),
        "build_tools": sorted(build_tools),
    }


def find_critical_projects(profiles: list, threshold: int = 40) -> list:
    """Find projects with low maturity scores."""
    critical = []
    for p in profiles:
        if p.maturity.score < threshold:
            critical.append({
                "name": p.name,
                "score": p.maturity.score,
                "grade": p.maturity.grade,
                "issues": [],
            })
            if not p.maturity.has_tests:
                critical[-1]["issues"].append("No tests")
            if not p.maturity.has_ci:
                critical[-1]["issues"].append("No CI/CD")
            if not p.maturity.has_docs:
                critical[-1]["issues"].append("No docs")
    return sorted(critical, key=lambda x: x["score"])


def print_health_summary(profiles: list, org_name: str) -> None:
    """Print a formatted health summary to console."""
    print()
    print("█" * 70)
    print(f"  {org_name} — ORGANIZATION HEALTH REPORT")
    print("█" * 70)
    print()

    # Basic stats
    print(f"Projects analyzed: {len(profiles)}")
    print()

    # Maturity distribution
    maturity = analyze_maturity_distribution(profiles)
    print("┌─ Maturity Distribution ───────────────────────────────────────────┐")
    print()
    for grade in ["A+", "A", "B+", "B", "C+", "C", "D", "D-", "F"]:
        count = maturity["by_grade"].get(grade, 0)
        bar = "█" * count
        pct = (count / len(profiles) * 100) if profiles else 0
        print(f"  {grade:>3}: {bar:<20} {count:>3} ({pct:>5.1f}%)")
    print()
    print(f"  Average score: {maturity['avg_score']:.1f}/100")
    print(f"  Score range: {maturity['min_score']:.0f} - {maturity['max_score']:.0f}")
    print()

    # Code metrics
    metrics = analyze_code_metrics(profiles)
    print("┌─ Code Metrics ──────────────────────────────────────────────────────┐")
    print()
    print(f"  Total projects:     {metrics['total_projects']}")
    print(f"  Total source files: {metrics['total_files']:,}")
    print(f"  Total source lines: {metrics['total_lines']:,}")
    print(f"  Total test files:   {metrics['total_tests']:,}")
    print(f"  Average complexity: {metrics['avg_complexity']:.1f}")
    print()

    # Tech stack
    tech = analyze_tech_stacks(profiles)
    print("┌─ Technology Stack ──────────────────────────────────────────────────┐")
    print()
    print("  Languages:")
    for lang, count in list(tech["languages"].items())[:5]:
        print(f"    • {lang}: {count} files")
    print()
    print(f"  Frameworks: {', '.join(tech['frameworks']) or 'None detected'}")
    print(f"  Build tools: {', '.join(tech['build_tools']) or 'None detected'}")
    print()

    # Critical projects
    critical = find_critical_projects(profiles)
    if critical:
        print("┌─ Critical Projects (Score < 40) ────────────────────────────────────┐")
        print()
        for proj in critical[:5]:
            issues_str = f" [{', '.join(proj['issues'])}]" if proj["issues"] else ""
            print(f"  • {proj['name']:<25} {proj['grade']:>3} ({proj['score']:.0f}/100){issues_str}")
        print()

    print("█" * 70)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate organization health report"
    )
    parser.add_argument("root_dir", help="Root directory containing project subdirectories")
    parser.add_argument("-o", "--output", help="Output file path (default: print to stdout)")
    parser.add_argument("--org-name", default="Organization", help="Organization name")
    parser.add_argument("--threshold", type=int, default=40, help="Critical project threshold (default: 40)")

    args = parser.parse_args()

    root_path = Path(args.root_dir).resolve()

    if not root_path.exists():
        print(f"Error: Directory not found: {root_path}")
        sys.exit(1)

    # Scan organization
    print(f"Scanning {root_path}...", file=sys.stderr)
    profiles = scan_organization(root_path)

    if not profiles:
        print("No projects found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(profiles)} projects.", file=sys.stderr)

    if args.output:
        # Generate full markdown report
        gen = ComparisonGenerator()
        report = gen.generate_health_report(profiles, org_name=args.org_name)

        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"Health report saved to: {output_path}", file=sys.stderr)
    else:
        # Print console summary
        print_health_summary(profiles, args.org_name)


if __name__ == "__main__":
    main()
