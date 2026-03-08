"""Generate cross-project comparison and category summary articles."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


class ComparisonGenerator:
    """Generate comparative analysis articles across projects."""

    def __init__(self, org_name: str = "WronAI", org_url: str = "https://github.com/wronai"):
        self.org_name = org_name
        self.org_url = org_url
        self.generated_at = datetime.now().strftime("%Y-%m-%d")

    def generate_comparison(
        self,
        profiles: List["ProjectProfile"],
        output_path: Path,
        title: str = "Cross-Project Comparison",
    ) -> None:
        """Generate a comparison table article for a set of projects."""
        md = self._render_comparison(profiles, title)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")

    def generate_category_articles(
        self,
        profiles: List["ProjectProfile"],
        output_dir: Path,
    ) -> List[Path]:
        """Generate one article per category."""
        categories: Dict[str, List["ProjectProfile"]] = {}
        for p in profiles:
            categories.setdefault(p.category, []).append(p)

        paths = []
        for cat, projs in sorted(categories.items()):
            slug = cat.lower().replace(" ", "-").replace("&", "and")
            path = output_dir / f"_category-{slug}.md"
            md = self._render_category(cat, projs)
            path.write_text(md, encoding="utf-8")
            paths.append(path)

        return paths

    def generate_health_report(
        self,
        profiles: List["ProjectProfile"],
        output_path: Path,
    ) -> None:
        """Generate a health/quality overview report."""
        md = self._render_health_report(profiles)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")

    # ── Renderers ───────────────────────────────────────────────────

    def _render_comparison(self, profiles: List["ProjectProfile"], title: str) -> str:
        sections = []

        sections.append("\n".join([
            "---",
            f'title: "{title}"',
            f'slug: "comparison"',
            f'date: "{self.generated_at}"',
            f'category: "Analysis"',
            f'generated_by: "todocs v0.1.0"',
            "---",
        ]))

        sections.append(f"# {title}")
        sections.append(
            f"Comparative analysis of **{len(profiles)}** projects "
            f"in the {self.org_name} organization."
        )

        # Size comparison
        sections.append(self._size_comparison(profiles))

        # Maturity leaderboard
        sections.append(self._maturity_leaderboard(profiles))

        # Complexity comparison
        sections.append(self._complexity_comparison(profiles))

        # Tech stack summary
        sections.append(self._tech_stack_overview(profiles))

        # Dependency overlap
        sections.append(self._dependency_overlap(profiles))

        sections.append(self._footer())
        return "\n\n".join(s for s in sections if s)

    def _size_comparison(self, profiles: List["ProjectProfile"]) -> str:
        sorted_p = sorted(profiles, key=lambda p: p.code_stats.source_lines, reverse=True)

        lines = ["## Size Comparison", ""]
        lines.append("| # | Project | Source Lines | Source Files | Test Files | Test Ratio |")
        lines.append("|--:|---------|------------:|------------:|-----------:|-----------:|")

        for i, p in enumerate(sorted_p[:25], 1):
            lines.append(
                f"| {i} | [{p.name}]({p.name}.md) "
                f"| {p.code_stats.source_lines:,} "
                f"| {p.code_stats.source_files} "
                f"| {p.code_stats.test_files} "
                f"| {p.maturity.test_ratio:.0%} |"
            )

        total_sloc = sum(p.code_stats.source_lines for p in profiles)
        total_files = sum(p.code_stats.source_files for p in profiles)
        lines.append(f"| | **TOTAL** | **{total_sloc:,}** | **{total_files}** | | |")

        return "\n".join(lines)

    def _maturity_leaderboard(self, profiles: List["ProjectProfile"]) -> str:
        sorted_p = sorted(profiles, key=lambda p: p.maturity.score, reverse=True)

        lines = ["## Maturity Leaderboard", ""]
        lines.append("| # | Project | Score | Grade | Tests | CI | Docs | Docker | Changelog |")
        lines.append("|--:|---------|------:|:-----:|:-----:|:--:|:----:|:------:|:---------:|")

        for i, p in enumerate(sorted_p[:25], 1):
            m = p.maturity
            lines.append(
                f"| {i} | [{p.name}]({p.name}.md) "
                f"| {m.score:.0f} | {m.grade} "
                f"| {'✅' if m.has_tests else '❌'} "
                f"| {'✅' if m.has_ci else '❌'} "
                f"| {'✅' if m.has_docs else '❌'} "
                f"| {'✅' if m.has_docker else '❌'} "
                f"| {'✅' if m.has_changelog else '❌'} |"
            )

        return "\n".join(lines)

    def _complexity_comparison(self, profiles: List["ProjectProfile"]) -> str:
        # Only include projects with complexity data
        with_cc = [p for p in profiles if p.code_stats.avg_complexity > 0]
        if not with_cc:
            return ""

        sorted_p = sorted(with_cc, key=lambda p: p.code_stats.avg_complexity, reverse=True)

        lines = ["## Complexity Analysis", ""]
        lines.append("| Project | Avg CC | Max CC | Maintainability | Hotspots |")
        lines.append("|---------|-------:|-------:|----------------:|---------:|")

        for p in sorted_p[:20]:
            s = p.code_stats
            lines.append(
                f"| [{p.name}]({p.name}.md) "
                f"| {s.avg_complexity:.1f} "
                f"| {s.max_complexity:.0f} "
                f"| {s.maintainability_index:.1f} "
                f"| {len(s.hotspots)} |"
            )

        return "\n".join(lines)

    def _tech_stack_overview(self, profiles: List["ProjectProfile"]) -> str:
        from collections import Counter

        lang_counter: Counter = Counter()
        fw_counter: Counter = Counter()
        tool_counter: Counter = Counter()

        for p in profiles:
            ts = p.tech_stack
            lang_counter[ts.primary_language] += 1
            for fw in ts.frameworks:
                fw_counter[fw] += 1
            for tool in ts.build_tools:
                tool_counter[tool] += 1
            for ci in ts.ci_cd:
                tool_counter[f"CI: {ci}"] += 1
            for dock in ts.containerization:
                tool_counter[f"Docker: {dock}"] += 1

        lines = ["## Technology Stack Overview"]

        # Languages
        lines.append("")
        lines.append("### Languages")
        lines.append("")
        for lang, count in lang_counter.most_common(10):
            bar = "█" * count
            lines.append(f"  {lang:>12}: {bar} ({count})")

        # Frameworks
        if fw_counter:
            lines.append("")
            lines.append("### Frameworks")
            lines.append("")
            for fw, count in fw_counter.most_common(10):
                lines.append(f"  {fw:>12}: {'█' * count} ({count})")

        # Tools
        if tool_counter:
            lines.append("")
            lines.append("### Build & DevOps Tools")
            lines.append("")
            for tool, count in tool_counter.most_common(15):
                lines.append(f"  {tool:>20}: {'█' * count} ({count})")

        return "\n".join(lines)

    def _dependency_overlap(self, profiles: List["ProjectProfile"]) -> str:
        """Find shared dependencies across projects."""
        from collections import Counter

        dep_usage: Counter = Counter()
        for p in profiles:
            for dep in set(d.lower() for d in p.dependencies):
                dep_usage[dep] += 1

        # Only show deps used by 2+ projects
        shared = [(dep, count) for dep, count in dep_usage.most_common(30) if count >= 2]
        if not shared:
            return ""

        lines = ["## Shared Dependencies", ""]
        lines.append("Dependencies used by multiple projects:")
        lines.append("")
        lines.append("| Dependency | Used By |")
        lines.append("|------------|--------:|")

        for dep, count in shared:
            pct = count / len(profiles) * 100
            lines.append(f"| `{dep}` | {count} projects ({pct:.0f}%) |")

        return "\n".join(lines)

    def _render_category(self, category: str, profiles: List["ProjectProfile"]) -> str:
        sections = []

        sections.append("\n".join([
            "---",
            f'title: "{category} — Category Overview"',
            f'slug: "category-{category.lower().replace(" ", "-")}"',
            f'date: "{self.generated_at}"',
            f'category: "{category}"',
            f'generated_by: "todocs v0.1.0"',
            "---",
        ]))

        sections.append(f"# {category}")
        sections.append(
            f"This category contains **{len(profiles)}** projects."
        )

        # Summary table
        lines = ["## Projects", ""]
        lines.append("| Project | Version | Description | SLOC | Grade |")
        lines.append("|---------|---------|-------------|-----:|:-----:|")

        for p in sorted(profiles, key=lambda x: x.name):
            desc = (p.metadata.description or "")[:60]
            if len(p.metadata.description or "") > 60:
                desc += "…"
            lines.append(
                f"| [{p.name}]({p.name}.md) "
                f"| {p.metadata.version or '—'} "
                f"| {desc} "
                f"| {p.code_stats.source_lines:,} "
                f"| {p.maturity.grade} |"
            )

        sections.append("\n".join(lines))

        # Category stats
        total_sloc = sum(p.code_stats.source_lines for p in profiles)
        avg_maturity = sum(p.maturity.score for p in profiles) / len(profiles)

        sections.append("\n".join([
            "## Category Statistics",
            "",
            f"- **Total source lines**: {total_sloc:,}",
            f"- **Average maturity**: {avg_maturity:.0f}/100",
            f"- **Projects with tests**: {sum(1 for p in profiles if p.maturity.has_tests)}/{len(profiles)}",
            f"- **Projects with CI**: {sum(1 for p in profiles if p.maturity.has_ci)}/{len(profiles)}",
            f"- **Projects with Docker**: {sum(1 for p in profiles if p.maturity.has_docker)}/{len(profiles)}",
        ]))

        sections.append(self._footer())
        return "\n\n".join(sections)

    def _render_health_report(self, profiles: List["ProjectProfile"]) -> str:
        sections = []

        sections.append("\n".join([
            "---",
            f'title: "{self.org_name} — Organization Health Report"',
            f'slug: "health-report"',
            f'date: "{self.generated_at}"',
            f'category: "Health"',
            f'generated_by: "todocs v0.1.0"',
            "---",
        ]))

        sections.append(f"# {self.org_name} — Organization Health Report")
        sections.append(self._health_executive_summary(profiles))
        sections.append(self._health_grade_distribution(profiles))
        sections.append(self._health_projects_needing_attention(profiles))
        sections.append(self._health_top_performers(profiles))
        sections.append(self._footer())
        return "\n\n".join(sections)

    def _health_executive_summary(self, profiles: List["ProjectProfile"]) -> str:
        total = len(profiles)
        total_sloc = sum(p.code_stats.source_lines for p in profiles)
        avg_score = sum(p.maturity.score for p in profiles) / total if total else 0
        tested = sum(1 for p in profiles if p.maturity.has_tests)
        with_ci = sum(1 for p in profiles if p.maturity.has_ci)

        return "\n".join([
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| Total projects | {total} |",
            f"| Total source lines | {total_sloc:,} |",
            f"| Average maturity | {avg_score:.0f}/100 |",
            f"| Projects with tests | {tested}/{total} ({tested/total*100:.0f}%) |",
            f"| Projects with CI | {with_ci}/{total} ({with_ci/total*100:.0f}%) |",
        ])

    def _health_grade_distribution(self, profiles: List["ProjectProfile"]) -> str:
        grades: Dict[str, int] = {}
        for p in profiles:
            grades[p.maturity.grade] = grades.get(p.maturity.grade, 0) + 1

        lines = ["## Grade Distribution", ""]
        max_count = max(grades.values()) if grades else 0
        for g in ["A+", "A", "B+", "B", "C+", "C", "D", "D-", "F"]:
            count = grades.get(g, 0)
            if count:
                bar = "█" * count + "░" * (max_count - count)
                lines.append(f"  {g:>3}: {bar} {count}")
        return "\n".join(lines)

    @staticmethod
    def _missing_features(m) -> List[str]:
        """Return list of missing maturity features."""
        checks = [
            (m.has_tests, "tests"),
            (m.has_ci, "CI"),
            (m.has_docs, "docs"),
            (m.has_changelog, "changelog"),
            (m.has_license, "license"),
        ]
        return [label for present, label in checks if not present]

    def _health_projects_needing_attention(self, profiles: List["ProjectProfile"]) -> str:
        low = sorted(profiles, key=lambda p: p.maturity.score)[:10]
        lines = ["## Projects Needing Attention", ""]
        lines.append("| Project | Score | Missing |")
        lines.append("|---------|------:|---------|")
        for p in low:
            missing = self._missing_features(p.maturity)
            lines.append(
                f"| [{p.name}]({p.name}.md) | {p.maturity.score:.0f} | {', '.join(missing)} |"
            )
        return "\n".join(lines)

    def _health_top_performers(self, profiles: List["ProjectProfile"]) -> str:
        top = sorted(profiles, key=lambda p: p.maturity.score, reverse=True)[:5]
        lines = ["## Top Performers", ""]
        for p in top:
            lines.append(f"- **{p.name}** — Grade {p.maturity.grade} ({p.maturity.score:.0f}/100)")
        return "\n".join(lines)

    def generate_readme_list(
        self,
        profiles: List["ProjectProfile"],
        output_path: Path,
        title: str = "Project Portfolio",
    ) -> None:
        """Generate a single README.md with a list of all projects and brief descriptions."""
        md = self._render_readme_list(profiles, title)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")

    def _render_readme_list(self, profiles: List["ProjectProfile"], title: str) -> str:
        """Render a compact README with project list and 5-line descriptions."""
        sections = []

        # Header
        sections.append(f"# {title}")
        sections.append("")
        sections.append(f"**Organization:** {self.org_name}  ")
        sections.append(f"**URL:** {self.org_url}  ")
        sections.append(f"**Generated:** {self.generated_at}  ")
        sections.append(f"**Projects:** {len(profiles)}")
        sections.append("")

        sections.append(self._readme_summary_table(profiles))
        sections.append("")

        # Individual project sections
        sections.append("## Projects")
        sections.append("")
        for p in sorted(profiles, key=lambda x: x.name):
            sections.append(self._readme_project_section(p))
            sections.append("")

        sections.append(self._footer())
        return "\n".join(sections)

    def _readme_summary_table(self, profiles: List["ProjectProfile"]) -> str:
        """Render the summary table for the readme list."""
        lines = [
            "## Summary",
            "",
            "| Project | Version | Language | SLOC | Grade | Tests | CI |",
            "|---------|---------|----------|-----:|:-----:|:----:|:-:|",
        ]
        for p in sorted(profiles, key=lambda x: x.name):
            tests = "✓" if p.maturity.has_tests else "✗"
            ci = "✓" if p.maturity.has_ci else "✗"
            lines.append(
                f"| [{p.name}](#{p.name.lower()}) "
                f"| {p.metadata.version or '—'} "
                f"| {p.tech_stack.primary_language} "
                f"| {p.code_stats.source_lines:,} "
                f"| {p.maturity.grade} "
                f"| {tests} "
                f"| {ci} |"
            )
        return "\n".join(lines)

    @staticmethod
    def _project_features(p: "ProjectProfile") -> List[str]:
        """Collect feature labels from a project profile."""
        features = []
        if p.maturity.has_tests:
            features.append(f"tests ({p.code_stats.test_files} files)")
        if p.maturity.has_ci:
            features.append("CI/CD")
        if p.maturity.has_docker:
            features.append("Docker")
        if p.maturity.has_docs:
            features.append("docs")
        return features or ["no special features detected"]

    def _readme_project_section(self, p: "ProjectProfile") -> str:
        """Render 5-line description for a single project."""
        lang = p.tech_stack.primary_language
        version = p.metadata.version or "unversioned"

        desc = p.metadata.description or "No description available."
        if len(desc) > 100:
            desc = desc[:97] + "..."

        deps = p.dependencies[:5]
        deps_str = ", ".join(deps) if deps else "none major"
        if len(p.dependencies) > 5:
            deps_str += f" +{len(p.dependencies) - 5} more"

        return "\n".join([
            f"### {p.name}",
            "",
            f"**{lang}** project, version **{version}** — Grade **{p.maturity.grade}** ({p.maturity.score:.0f}/100)",
            f"- **Size:** {p.code_stats.source_lines:,} lines ({p.code_stats.source_files} files)",
            f"- **Description:** {desc}",
            f"- **Features:** {', '.join(self._project_features(p))}",
            f"- **Dependencies:** {deps_str}",
        ])

    def _footer(self) -> str:
        return "\n".join([
            "---",
            "",
            f"*Generated by [todocs](https://github.com/wronai/todocs) v0.1.0 on {self.generated_at}.*",
        ])
