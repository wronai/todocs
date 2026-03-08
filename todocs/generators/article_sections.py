"""Section renderer helpers for ArticleGenerator.

This module contains helper functions for rendering individual sections
of the markdown article, extracted from article.py to reduce complexity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


def render_frontmatter(p: "ProjectProfile", org_name: str, generated_at: str) -> str:
    """Render WordPress YAML frontmatter."""
    meta = p.metadata
    tags = list(set(
        [p.category, p.tech_stack.primary_language]
        + p.tech_stack.frameworks
        + meta.keywords[:5]
    ))
    tags = [t for t in tags if t and t != "unknown"]

    return "\n".join([
        "---",
        f'title: "{meta.name or p.name} — Project Status Report"',
        f'slug: "{p.name}-status"',
        f'date: "{generated_at}"',
        f'category: "{p.category}"',
        f'tags: [{", ".join(repr(t) for t in tags)}]',
        f'version: "{meta.version}"',
        f'maturity_grade: "{p.maturity.grade}"',
        f'maturity_score: {p.maturity.score}',
        f'primary_language: "{p.tech_stack.primary_language}"',
        f'source_lines: {p.code_stats.source_lines}',
        f'test_files: {p.code_stats.test_files}',
        f'repository: "{meta.repository}"',
        f'generated_by: "todocs v0.1.0"',
        f'generated_at: "{generated_at}"',
        "---",
    ])


def render_header(p: "ProjectProfile", org_url: str) -> str:
    """Render title and badges section."""
    meta = p.metadata
    name = meta.name or p.name
    repo = meta.repository or f"{org_url}/{p.name}"

    lines = [f"# {name}"]

    badges = []
    if meta.version:
        badges.append(f"![Version](https://img.shields.io/badge/version-{meta.version}-blue)")
    badges.append(f"![Grade](https://img.shields.io/badge/maturity-{p.maturity.grade}-"
                   f"{'brightgreen' if p.maturity.score >= 70 else 'yellow' if p.maturity.score >= 40 else 'red'})")
    lang = p.tech_stack.primary_language
    if lang != "unknown":
        badges.append(f"![Language](https://img.shields.io/badge/language-{lang}-informational)")
    badges.append(f"![Lines](https://img.shields.io/badge/lines-{p.code_stats.source_lines:,}-lightgrey)")

    lines.append(" ".join(badges))
    lines.append(f"\n> **Repository**: [{repo}]({repo})")

    return "\n".join(lines)


def render_overview(p: "ProjectProfile", org_name: str) -> str:
    """Render overview/description section."""
    lines = ["## Overview"]

    desc = p.metadata.description
    readme_desc = p.readme_sections.get("description", "")

    if desc:
        lines.append(desc)
    if readme_desc and readme_desc != desc:
        lines.append("")
        lines.append(readme_desc[:500])

    if not desc and not readme_desc:
        lines.append(f"{p.name} is a {p.tech_stack.primary_language} project "
                     f"in the {org_name} organization.")

    return "\n".join(lines)


def render_tech_stack(p: "ProjectProfile") -> str:
    """Render technology stack section."""
    ts = p.tech_stack
    lines = ["## Technology Stack"]

    if ts.languages:
        lang_parts = []
        for lang, count in sorted(ts.languages.items(), key=lambda x: -x[1]):
            lang_parts.append(f"{lang} ({count} files)")
        lines.append(f"**Languages**: {', '.join(lang_parts)}")

    if ts.frameworks:
        lines.append(f"**Frameworks**: {', '.join(ts.frameworks)}")

    if ts.build_tools:
        lines.append(f"**Build Tools**: {', '.join(ts.build_tools)}")

    if ts.test_frameworks:
        lines.append(f"**Testing**: {', '.join(ts.test_frameworks)}")

    if ts.ci_cd:
        lines.append(f"**CI/CD**: {', '.join(ts.ci_cd)}")

    if ts.containerization:
        lines.append(f"**Containerization**: {', '.join(ts.containerization)}")

    return "\n\n".join(lines)


def render_architecture(p: "ProjectProfile") -> str:
    """Render architecture and key modules section."""
    if not p.key_modules:
        return ""

    lines = ["## Architecture & Key Modules"]
    lines.append(
        f"The project contains **{p.code_stats.source_files}** source files "
        f"totaling **{p.code_stats.source_lines:,}** lines of code."
    )

    # Add Directory Structure subsection with tree
    structure = p.structure
    if structure and structure.get("top_dirs"):
        lines.append("")
        lines.append("### Directory Structure")
        lines.append("")
        lines.append("```")
        lines.append(f"{p.name}/")
        for i, dir_name in enumerate(structure["top_dirs"]):
            is_last = i == len(structure["top_dirs"]) - 1
            prefix = "└── " if is_last else "├── "
            lines.append(f"{prefix}{dir_name}/")
        lines.append("```")

    lines.append("")
    lines.append("| Module | Lines | Classes | Functions | Description |")
    lines.append("|--------|------:|:-------:|:---------:|-------------|")

    for mod in p.key_modules[:10]:
        path = mod["path"]
        loc = mod["lines"]
        n_classes = len(mod.get("classes", []))
        n_funcs = len(mod.get("functions", []))
        doc = mod.get("docstring", "").replace("\n", " ").strip()
        if len(doc) > 80:
            doc = doc[:80] + "…"
        lines.append(f"| `{path}` | {loc} | {n_classes} | {n_funcs} | {doc} |")

    all_classes = []
    for mod in p.key_modules:
        for cls in mod.get("classes", []):
            all_classes.append({
                "name": cls["name"],
                "methods": len(cls.get("methods", [])),
                "file": mod["path"],
            })

    if all_classes:
        all_classes.sort(key=lambda c: c["methods"], reverse=True)
        lines.append("")
        lines.append("### Key Classes")
        lines.append("")
        for cls in all_classes[:8]:
            lines.append(f"- **{cls['name']}** — {cls['methods']} methods (`{cls['file']}`)")

    return "\n".join(lines)


def render_metrics(p: "ProjectProfile") -> str:
    """Render code metrics section."""
    stats = p.code_stats
    lines = ["## Code Metrics"]

    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|------:|")
    lines.append(f"| Source files | {stats.source_files} |")
    lines.append(f"| Source lines | {stats.source_lines:,} |")
    lines.append(f"| Test files | {stats.test_files} |")
    lines.append(f"| Test lines | {stats.test_lines:,} |")
    lines.append(f"| Test ratio | {p.maturity.test_ratio:.1%} |")
    lines.append(f"| Avg. cyclomatic complexity | {stats.avg_complexity:.1f} |")
    lines.append(f"| Max cyclomatic complexity | {stats.max_complexity:.0f} |")
    if stats.maintainability_index > 0:
        lines.append(f"| Maintainability index | {stats.maintainability_index:.1f} |")

    if stats.hotspots:
        lines.append("")
        lines.append("### Complexity Hotspots")
        lines.append("")
        lines.append("| Function | File | CC | Rank |")
        lines.append("|----------|------|----|------|")
        for hs in stats.hotspots[:5]:
            lines.append(
                f"| `{hs['name']}` | `{hs['file']}` | {hs['complexity']} | {hs.get('rank', '?')} |"
            )

    return "\n".join(lines)


def render_maturity(p: "ProjectProfile") -> str:
    """Render maturity assessment section."""
    mat = p.maturity
    lines = [f"## Maturity Assessment — Grade: {mat.grade} ({mat.score:.0f}/100)"]

    checks = [
        ("README", True),
        ("Tests", mat.has_tests),
        ("CI/CD", mat.has_ci),
        ("Documentation (docs/)", mat.has_docs),
        ("Changelog", mat.has_changelog),
        ("License", mat.has_license),
        ("Examples", mat.has_examples),
        ("Docker", mat.has_docker),
        ("Makefile / Taskfile", mat.has_makefile),
        ("VERSION file", mat.has_version_file),
    ]

    lines.append("")
    for label, present in checks:
        icon = "✅" if present else "❌"
        lines.append(f"- {icon} {label}")

    lines.append("")
    lines.append(f"**Test coverage ratio**: {mat.test_ratio:.1%}")
    lines.append(f"**Documentation completeness**: {mat.doc_completeness:.0%}")

    return "\n".join(lines)


def render_dependencies(p: "ProjectProfile") -> str:
    """Render dependencies section."""
    if not p.dependencies and not p.dev_dependencies:
        return ""

    lines = ["## Dependencies"]

    if p.dependencies:
        lines.append("")
        lines.append(f"**Runtime** ({len(p.dependencies)}): "
                     + ", ".join(f"`{d}`" for d in p.dependencies[:20]))
        if len(p.dependencies) > 20:
            lines.append(f"  … and {len(p.dependencies) - 20} more")

    if p.dev_dependencies:
        lines.append("")
        lines.append(f"**Development** ({len(p.dev_dependencies)}): "
                     + ", ".join(f"`{d}`" for d in p.dev_dependencies[:15]))

    return "\n".join(lines)


def _render_entry_points(entry_pts: dict) -> str:
    if not entry_pts:
        return ""
    return "\n".join([
        "",
        "**Entry Points**: " + ", ".join(
            f"`{cmd}` → `{target}`" for cmd, target in entry_pts.items()
        ),
    ])


def _render_cli_commands(cli_cmds: list) -> str:
    if not cli_cmds:
        return ""
    lines = ["", "### CLI Commands", ""]
    for cmd in cli_cmds[:10]:
        desc = f" — {cmd['description']}" if cmd.get("description") else ""
        lines.append(f"- `{cmd['name']}`{desc} (`{cmd['file']}`)")
    return "\n".join(lines)


def _render_rest_endpoints(endpoints: list) -> str:
    if not endpoints:
        return ""
    lines = ["", "### REST Endpoints", "",
             "| Method | Path | File |",
             "|--------|------|------|",
             ]
    for ep in endpoints[:15]:
        lines.append(f"| {ep['method']} | `{ep['path']}` | `{ep['file']}` |")
    return "\n".join(lines)


def _render_public_classes(pub_classes: list) -> str:
    if not pub_classes:
        return ""
    lines = ["", "### Public Classes", ""]
    for cls in pub_classes[:10]:
        desc = f" — {cls['description']}" if cls.get("description") else ""
        methods = cls.get("methods", [])
        method_str = f" ({len(methods)} public methods)" if methods else ""
        lines.append(f"- **{cls['name']}**{desc}{method_str}")
    return "\n".join(lines)


def render_api_surface(p: "ProjectProfile") -> str:
    """Render API surface section."""
    api = p.api_surface
    if not api:
        return ""

    cli_cmds = api.get("cli_commands", [])
    pub_classes = api.get("public_classes", [])
    pub_funcs = api.get("public_functions", [])
    endpoints = api.get("rest_endpoints", [])
    entry_pts = api.get("entry_points", {})

    if not cli_cmds and not pub_classes and not pub_funcs and not endpoints:
        return ""

    parts = ["## API Surface"]
    parts.append(_render_entry_points(entry_pts))
    parts.append(_render_cli_commands(cli_cmds))
    parts.append(_render_rest_endpoints(endpoints))
    parts.append(_render_public_classes(pub_classes))
    return "\n".join(s for s in parts if s)


def render_build_targets(p: "ProjectProfile") -> str:
    """Render build targets section."""
    targets = p.makefile_targets
    if not targets:
        return ""

    lines = ["## Build Targets"]
    lines.append("")

    for t in targets[:12]:
        name = t.get("name", "")
        desc = t.get("description", "")
        cmds = t.get("commands", [])

        entry = f"- **`make {name}`**"
        if desc:
            entry += f" — {desc}"
        lines.append(entry)

        if cmds:
            for cmd in cmds[:2]:
                lines.append(f"  - `{cmd[:80]}`")

    return "\n".join(lines)


def render_docker(p: "ProjectProfile") -> str:
    """Render Docker infrastructure section."""
    docker = p.docker_info
    if not docker or (not docker.get("has_dockerfile") and not docker.get("has_compose")):
        return ""

    lines = ["## Docker Infrastructure"]

    if docker.get("base_images"):
        lines.append("")
        lines.append("**Base Images**: " + ", ".join(f"`{img}`" for img in docker["base_images"]))

    services = docker.get("services", [])
    if services:
        lines.append("")
        lines.append("### Services")
        lines.append("")
        lines.append("| Service | Image | Ports | Depends On |")
        lines.append("|---------|-------|-------|------------|")
        for svc in services[:10]:
            image = svc.get("image") or "(build)"
            ports = ", ".join(svc.get("ports", [])) or "—"
            deps = ", ".join(svc.get("depends_on", [])) or "—"
            lines.append(f"| {svc['name']} | `{image}` | {ports} | {deps} |")

    if docker.get("exposed_ports"):
        lines.append("")
        lines.append("**Exposed Ports**: " + ", ".join(docker["exposed_ports"]))

    return "\n".join(lines)


def render_changelog(p: "ProjectProfile") -> str:
    """Render recent changes section."""
    if not p.changelog_entries:
        return ""

    lines = ["## Recent Changes"]

    for entry in p.changelog_entries[:3]:
        ver = entry.get("version", "?")
        date = entry.get("date", "")
        content = entry.get("content", "")

        header = f"### v{ver}"
        if date:
            header += f" ({date})"
        lines.append("")
        lines.append(header)
        if content:
            lines.append("")
            lines.append(content)

    return "\n".join(lines)


def render_usage(p: "ProjectProfile") -> str:
    """Render installation/usage section."""
    parts = []

    install = p.readme_sections.get("installation", "")
    usage = p.readme_sections.get("usage", "")

    if install:
        parts.append("## Installation")
        parts.append("")
        parts.append(install[:800])

    if usage:
        parts.append("")
        parts.append("## Usage")
        parts.append("")
        parts.append(usage[:800])

    if not parts:
        meta = p.metadata
        ep = meta.entry_points
        name = meta.name or p.name

        parts.append("## Installation")
        parts.append("")
        if "pyproject" in p.tech_stack.build_tools or "setuptools" in p.tech_stack.build_tools:
            parts.append(f"```bash\npip install {name}\n```")
        elif "npm" in p.tech_stack.build_tools:
            parts.append(f"```bash\nnpm install {name}\n```")
        elif "cargo" in p.tech_stack.build_tools:
            parts.append(f"```bash\ncargo install {name}\n```")

        if ep:
            parts.append("")
            parts.append("### CLI Entry Points")
            for cmd, target in ep.items():
                parts.append(f"- `{cmd}` → `{target}`")

    return "\n".join(parts)


def render_footer(generated_at: str) -> str:
    """Render article footer."""
    return "\n".join([
        "---",
        "",
        f"*Generated by [todocs](https://github.com/wronai/todocs) v0.1.0 "
        f"on {generated_at}. "
        f"Analysis based on static code inspection — no LLM was used.*",
    ])
