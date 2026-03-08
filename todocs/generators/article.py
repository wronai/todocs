"""Generate WordPress-ready markdown articles from ProjectProfile data."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


class ArticleGenerator:
    """Generate markdown articles for WordPress from analyzed project profiles."""

    def __init__(self, org_name: str = "WronAI", org_url: str = "https://github.com/wronai"):
        self.org_name = org_name
        self.org_url = org_url
        self.generated_at = datetime.now().strftime("%Y-%m-%d")

    def generate(self, profile: "ProjectProfile", output_path: Path) -> None:
        """Generate a single project article."""
        md = self._render_article(profile)
        output_path.write_text(md, encoding="utf-8")

    def generate_index(self, profiles: List["ProjectProfile"], output_path: Path) -> None:
        """Generate an index/overview article listing all projects."""
        md = self._render_index(profiles)
        output_path.write_text(md, encoding="utf-8")

    # ── Single project article ──────────────────────────────────────

    def _render_article(self, p: "ProjectProfile") -> str:
        sections = []

        # WordPress frontmatter (YAML)
        sections.append(self._frontmatter(p))

        # Title and badges
        sections.append(self._header(p))

        # Overview / Description
        sections.append(self._overview(p))

        # Tech Stack
        sections.append(self._tech_stack_section(p))

        # Architecture / Key Modules
        sections.append(self._architecture_section(p))

        # Code Metrics
        sections.append(self._metrics_section(p))

        # Maturity Assessment
        sections.append(self._maturity_section(p))

        # Dependencies
        sections.append(self._dependencies_section(p))

        # API Surface
        sections.append(self._api_surface_section(p))

        # Build Targets
        sections.append(self._build_targets_section(p))

        # Docker Infrastructure
        sections.append(self._docker_section(p))

        # Recent Changes
        sections.append(self._changelog_section(p))

        # Installation / Usage (from README)
        sections.append(self._usage_section(p))

        # Footer
        sections.append(self._footer(p))

        return "\n\n".join(s for s in sections if s)

    def _frontmatter(self, p: "ProjectProfile") -> str:
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
            f'date: "{self.generated_at}"',
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
            f'generated_at: "{self.generated_at}"',
            "---",
        ])

    def _header(self, p: "ProjectProfile") -> str:
        meta = p.metadata
        name = meta.name or p.name
        repo = meta.repository or f"{self.org_url}/{p.name}"

        lines = [f"# {name}"]

        # Badge line
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

    def _overview(self, p: "ProjectProfile") -> str:
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
                         f"in the {self.org_name} organization.")

        return "\n".join(lines)

    def _tech_stack_section(self, p: "ProjectProfile") -> str:
        ts = p.tech_stack
        lines = ["## Technology Stack"]

        # Languages
        if ts.languages:
            lang_parts = []
            for lang, count in sorted(ts.languages.items(), key=lambda x: -x[1]):
                lang_parts.append(f"{lang} ({count} files)")
            lines.append(f"**Languages**: {', '.join(lang_parts)}")

        # Frameworks
        if ts.frameworks:
            lines.append(f"**Frameworks**: {', '.join(ts.frameworks)}")

        # Build tools
        if ts.build_tools:
            lines.append(f"**Build Tools**: {', '.join(ts.build_tools)}")

        # Test frameworks
        if ts.test_frameworks:
            lines.append(f"**Testing**: {', '.join(ts.test_frameworks)}")

        # CI/CD
        if ts.ci_cd:
            lines.append(f"**CI/CD**: {', '.join(ts.ci_cd)}")

        # Containerization
        if ts.containerization:
            lines.append(f"**Containerization**: {', '.join(ts.containerization)}")

        return "\n\n".join(lines)

    def _architecture_section(self, p: "ProjectProfile") -> str:
        if not p.key_modules:
            return ""

        lines = ["## Architecture & Key Modules"]
        lines.append(
            f"The project contains **{p.code_stats.source_files}** source files "
            f"totaling **{p.code_stats.source_lines:,}** lines of code."
        )

        # Top modules table
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

        # Class highlights
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

    def _metrics_section(self, p: "ProjectProfile") -> str:
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

        # Hotspots
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

    def _maturity_section(self, p: "ProjectProfile") -> str:
        mat = p.maturity
        lines = [f"## Maturity Assessment — Grade: {mat.grade} ({mat.score:.0f}/100)"]

        checks = [
            ("README", True),  # always have if we got this far
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

    def _dependencies_section(self, p: "ProjectProfile") -> str:
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

    def _api_surface_section(self, p: "ProjectProfile") -> str:
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

        lines = ["## API Surface"]

        if entry_pts:
            lines.append("")
            lines.append("**Entry Points**: " + ", ".join(
                f"`{cmd}` → `{target}`" for cmd, target in entry_pts.items()
            ))

        if cli_cmds:
            lines.append("")
            lines.append("### CLI Commands")
            lines.append("")
            for cmd in cli_cmds[:10]:
                desc = f" — {cmd['description']}" if cmd.get("description") else ""
                lines.append(f"- `{cmd['name']}`{desc} (`{cmd['file']}`)")

        if endpoints:
            lines.append("")
            lines.append("### REST Endpoints")
            lines.append("")
            lines.append("| Method | Path | File |")
            lines.append("|--------|------|------|")
            for ep in endpoints[:15]:
                lines.append(f"| {ep['method']} | `{ep['path']}` | `{ep['file']}` |")

        if pub_classes:
            lines.append("")
            lines.append("### Public Classes")
            lines.append("")
            for cls in pub_classes[:10]:
                desc = f" — {cls['description']}" if cls.get("description") else ""
                methods = cls.get("methods", [])
                method_str = f" ({len(methods)} public methods)" if methods else ""
                lines.append(f"- **{cls['name']}**{desc}{method_str}")

        return "\n".join(lines)

    def _build_targets_section(self, p: "ProjectProfile") -> str:
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

    def _docker_section(self, p: "ProjectProfile") -> str:
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

    def _changelog_section(self, p: "ProjectProfile") -> str:
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

    def _usage_section(self, p: "ProjectProfile") -> str:
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
            # Generate basic installation hint
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

    def _footer(self, p: "ProjectProfile") -> str:
        return "\n".join([
            "---",
            "",
            f"*Generated by [todocs](https://github.com/wronai/todocs) v0.1.0 "
            f"on {self.generated_at}. "
            f"Analysis based on static code inspection — no LLM was used.*",
        ])

    # ── Index article ───────────────────────────────────────────────

    def _render_index(self, profiles: List["ProjectProfile"]) -> str:
        sections = []

        # Frontmatter
        sections.append("\n".join([
            "---",
            f'title: "{self.org_name} — Organization Project Portfolio"',
            f'slug: "{self.org_name.lower()}-portfolio"',
            f'date: "{self.generated_at}"',
            f'category: "Portfolio"',
            f'generated_by: "todocs v0.1.0"',
            "---",
        ]))

        sections.append(f"# {self.org_name} — Project Portfolio")
        sections.append(
            f"Overview of **{len(profiles)}** projects in the {self.org_name} organization, "
            f"analyzed on {self.generated_at}."
        )

        # Summary stats
        total_lines = sum(p.code_stats.source_lines for p in profiles)
        total_files = sum(p.code_stats.source_files for p in profiles)
        avg_maturity = sum(p.maturity.score for p in profiles) / len(profiles) if profiles else 0

        sections.append("\n".join([
            "## Summary Statistics",
            "",
            f"- **Total projects**: {len(profiles)}",
            f"- **Total source files**: {total_files:,}",
            f"- **Total source lines**: {total_lines:,}",
            f"- **Average maturity score**: {avg_maturity:.0f}/100",
        ]))

        # Group by category
        categories: dict[str, list] = {}
        for p in profiles:
            categories.setdefault(p.category, []).append(p)

        for cat, projs in sorted(categories.items()):
            lines = [f"## {cat}"]
            lines.append("")
            lines.append("| Project | Version | Grade | Language | Source Lines | Tests |")
            lines.append("|---------|---------|:-----:|----------|------------:|:-----:|")

            for p in sorted(projs, key=lambda x: x.name):
                ver = p.metadata.version or "—"
                grade = p.maturity.grade
                lang = p.tech_stack.primary_language
                sloc = f"{p.code_stats.source_lines:,}"
                tests = "✅" if p.maturity.has_tests else "❌"
                link = f"[{p.name}]({p.name}.md)"
                lines.append(f"| {link} | {ver} | {grade} | {lang} | {sloc} | {tests} |")

            sections.append("\n".join(lines))

        # Maturity distribution
        grades: dict[str, int] = {}
        for p in profiles:
            grades[p.maturity.grade] = grades.get(p.maturity.grade, 0) + 1

        grade_lines = ["## Maturity Distribution", ""]
        for g in ["A+", "A", "B+", "B", "C+", "C", "D", "D-", "F"]:
            count = grades.get(g, 0)
            if count:
                bar = "█" * count
                grade_lines.append(f"  {g:>3}: {bar} {count}")
        sections.append("\n".join(grade_lines))

        # Footer
        sections.append("\n".join([
            "---",
            "",
            f"*Generated by [todocs](https://github.com/wronai/todocs) v0.1.0 on {self.generated_at}.*",
        ]))

        return "\n\n".join(sections)
