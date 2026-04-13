"""Generate organization status report — aggregated health & progress overview."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


_QUALITY_GAP_CHECKS = [
    ("No tests", "has_tests"),
    ("No CI/CD", "has_ci"),
    ("No docs", "has_docs"),
    ("No changelog", "has_changelog"),
    ("No license", "has_license"),
    ("No Docker", "has_docker"),
]

_RECOMMENDATION_RULES = [
    ("has_tests", "🧪 **Add tests** to {count} projects: {names}", 3),
    ("has_ci", "⚙️ **Set up CI/CD** for {count} projects", 0),
    ("has_license", "📄 **Add LICENSE** to {count} projects", 0),
]


class StatusReportGenerator:
    """Generate a comprehensive organization status report."""

    def __init__(self, org_name: str = "WronAI", org_url: str = "https://github.com/wronai"):
        self.org_name = org_name
        self.org_url = org_url
        self.generated_at = datetime.now().strftime("%Y-%m-%d")

    def generate(self, profiles: List["ProjectProfile"], output_path: Path) -> None:
        """Generate the status report and write to file."""
        md = self.render(profiles)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")

    def render(self, profiles: List["ProjectProfile"]) -> str:
        """Render the full status report as markdown."""
        sections = [
            self._frontmatter(len(profiles)),
            self._header(len(profiles)),
            self._kpi_dashboard(profiles),
            self._grade_breakdown(profiles),
            self._language_distribution(profiles),
            self._quality_gaps(profiles),
            self._largest_projects(profiles),
            self._recent_activity(profiles),
            self._recommendations(profiles),
            self._footer(),
        ]
        return "\n\n".join(s for s in sections if s)

    # ── Section renderers ──────────────────────────────────────────

    def _frontmatter(self, count: int) -> str:
        return "\n".join([
            "---",
            f'title: "{self.org_name} — Status Report"',
            f'slug: "status-report"',
            f'date: "{self.generated_at}"',
            f'category: "Status"',
            f'project_count: {count}',
            f'generated_by: "todocs"',
            "---",
        ])

    def _header(self, count: int) -> str:
        return "\n".join([
            f"# {self.org_name} — Organization Status Report",
            "",
            f"Report generated on **{self.generated_at}** covering **{count}** projects.",
        ])

    def _kpi_dashboard(self, profiles: List["ProjectProfile"]) -> str:
        total = len(profiles)
        if not total:
            return ""
        total_sloc = sum(p.code_stats.source_lines for p in profiles)
        total_files = sum(p.code_stats.source_files for p in profiles)
        avg_maturity = sum(p.maturity.score for p in profiles) / total
        tested_pct = sum(1 for p in profiles if p.maturity.has_tests) / total * 100
        ci_pct = sum(1 for p in profiles if p.maturity.has_ci) / total * 100
        docker_pct = sum(1 for p in profiles if p.maturity.has_docker) / total * 100

        return "\n".join([
            "## KPI Dashboard",
            "",
            "| KPI | Value |",
            "|-----|------:|",
            f"| Total projects | {total} |",
            f"| Total source lines | {total_sloc:,} |",
            f"| Total source files | {total_files:,} |",
            f"| Average maturity | {avg_maturity:.0f}/100 |",
            f"| Projects with tests | {tested_pct:.0f}% |",
            f"| Projects with CI/CD | {ci_pct:.0f}% |",
            f"| Projects with Docker | {docker_pct:.0f}% |",
        ])

    def _grade_breakdown(self, profiles: List["ProjectProfile"]) -> str:
        grades: Dict[str, List[str]] = {}
        for p in profiles:
            grades.setdefault(p.maturity.grade, []).append(p.name)

        lines = ["## Grade Breakdown", ""]
        for g in ["A+", "A", "B+", "B", "C+", "C", "D", "D-", "F"]:
            names = grades.get(g, [])
            if names:
                bar = "█" * len(names)
                projects = ", ".join(sorted(names)[:5])
                if len(names) > 5:
                    projects += f" +{len(names) - 5}"
                lines.append(f"  **{g:>3}** {bar} ({len(names)}) — {projects}")
        return "\n".join(lines)

    def _language_distribution(self, profiles: List["ProjectProfile"]) -> str:
        from collections import Counter
        langs = Counter(p.tech_stack.primary_language for p in profiles)

        lines = ["## Language Distribution", ""]
        for lang, count in langs.most_common(10):
            pct = count / len(profiles) * 100
            bar = "█" * count
            lines.append(f"  {lang:>12} {bar} {count} ({pct:.0f}%)")
        return "\n".join(lines)

    @staticmethod
    def _truncated_names(names: List[str], limit: int = 4) -> str:
        """Return sorted, comma-separated names truncated at *limit*."""
        display = ", ".join(sorted(names)[:limit])
        if len(names) > limit:
            display += f" +{len(names) - limit}"
        return display

    def _quality_gaps(self, profiles: List["ProjectProfile"]) -> str:
        lines = ["## Quality Gaps", ""]
        lines.append("| Gap | Count | Projects |")
        lines.append("|-----|------:|----------|")
        for label, attr in _QUALITY_GAP_CHECKS:
            names = [p.name for p in profiles if not getattr(p.maturity, attr)]
            if names:
                lines.append(f"| {label} | {len(names)} | {self._truncated_names(names)} |")
        return "\n".join(lines)

    def _largest_projects(self, profiles: List["ProjectProfile"]) -> str:
        top = sorted(profiles, key=lambda p: p.code_stats.source_lines, reverse=True)[:10]
        lines = ["## Largest Projects", ""]
        lines.append("| # | Project | SLOC | Files | Grade |")
        lines.append("|--:|---------|-----:|------:|:-----:|")
        for i, p in enumerate(top, 1):
            lines.append(
                f"| {i} | {p.name} "
                f"| {p.code_stats.source_lines:,} "
                f"| {p.code_stats.source_files} "
                f"| {p.maturity.grade} |"
            )
        return "\n".join(lines)

    def _recent_activity(self, profiles: List["ProjectProfile"]) -> str:
        active = [p for p in profiles if p.changelog_entries]
        if not active:
            return ""

        lines = ["## Recent Activity", ""]
        for p in sorted(active, key=lambda x: x.name):
            latest = p.changelog_entries[0]
            ver = latest.get("version", "?")
            date = latest.get("date", "")
            date_str = f" ({date})" if date else ""
            lines.append(f"- **{p.name}** — latest v{ver}{date_str}")
        return "\n".join(lines)

    def _recommendations(self, profiles: List["ProjectProfile"]) -> str:
        recs: List[str] = []

        for attr, template, name_limit in _RECOMMENDATION_RULES:
            names = [p.name for p in profiles if not getattr(p.maturity, attr)]
            if names:
                fmt_kwargs = {"count": len(names), "names": ""}
                if name_limit:
                    fmt_kwargs["names"] = ", ".join(names[:name_limit])
                recs.append(f"- {template.format(**fmt_kwargs)}")

        high_cc = [p for p in profiles if p.code_stats.max_complexity > 20]
        if high_cc:
            names = ", ".join(p.name for p in high_cc[:3])
            recs.append(f"- 📐 **Reduce complexity** in {len(high_cc)} projects: {names}")

        if not recs:
            return ""

        return "\n".join(["## Recommendations", ""] + recs)

    def _footer(self) -> str:
        return "\n".join([
            "---",
            "",
            f"*Generated by [todocs](https://github.com/wronai/todocs) on {self.generated_at}.*",
        ])
