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

        # Overall stats
        total_projects = len(profiles)
        total_sloc = sum(p.code_stats.source_lines for p in profiles)
        avg_score = sum(p.maturity.score for p in profiles) / total_projects if total_projects else 0
        tested = sum(1 for p in profiles if p.maturity.has_tests)
        with_ci = sum(1 for p in profiles if p.maturity.has_ci)

        sections.append("\n".join([
            "## Executive Summary",
            "",
            f"| Metric | Value |",
            f"|--------|------:|",
            f"| Total projects | {total_projects} |",
            f"| Total source lines | {total_sloc:,} |",
            f"| Average maturity | {avg_score:.0f}/100 |",
            f"| Projects with tests | {tested}/{total_projects} ({tested/total_projects*100:.0f}%) |",
            f"| Projects with CI | {with_ci}/{total_projects} ({with_ci/total_projects*100:.0f}%) |",
        ]))

        # Grade distribution
        grades: Dict[str, int] = {}
        for p in profiles:
            grades[p.maturity.grade] = grades.get(p.maturity.grade, 0) + 1

        grade_lines = ["## Grade Distribution", ""]
        for g in ["A+", "A", "B+", "B", "C+", "C", "D", "D-", "F"]:
            count = grades.get(g, 0)
            if count:
                bar = "█" * count + "░" * (max(grades.values()) - count)
                grade_lines.append(f"  {g:>3}: {bar} {count}")
        sections.append("\n".join(grade_lines))

        # Projects needing attention (lowest scores)
        low = sorted(profiles, key=lambda p: p.maturity.score)[:10]
        attn_lines = ["## Projects Needing Attention", ""]
        attn_lines.append("| Project | Score | Missing |")
        attn_lines.append("|---------|------:|---------|")
        for p in low:
            m = p.maturity
            missing = []
            if not m.has_tests:
                missing.append("tests")
            if not m.has_ci:
                missing.append("CI")
            if not m.has_docs:
                missing.append("docs")
            if not m.has_changelog:
                missing.append("changelog")
            if not m.has_license:
                missing.append("license")
            attn_lines.append(
                f"| [{p.name}]({p.name}.md) | {m.score:.0f} | {', '.join(missing)} |"
            )
        sections.append("\n".join(attn_lines))

        # Top performers
        top = sorted(profiles, key=lambda p: p.maturity.score, reverse=True)[:5]
        top_lines = ["## Top Performers", ""]
        for p in top:
            top_lines.append(f"- **{p.name}** — Grade {p.maturity.grade} ({p.maturity.score:.0f}/100)")
        sections.append("\n".join(top_lines))

        sections.append(self._footer())
        return "\n\n".join(sections)

    def _footer(self) -> str:
        return "\n".join([
            "---",
            "",
            f"*Generated by [todocs](https://github.com/wronai/todocs) v0.1.0 on {self.generated_at}.*",
        ])
