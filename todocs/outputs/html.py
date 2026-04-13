"""HTML output — standalone HTML report from project profiles."""

from __future__ import annotations

import html
from pathlib import Path
from typing import TYPE_CHECKING, List

from todocs.generators.base import BaseGenerator

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


class HTMLOutput(BaseGenerator):
    """Write project profiles as a standalone HTML report."""

    def write(self, profiles: List["ProjectProfile"], output_path: Path) -> None:
        """Write a single HTML report covering all profiles."""
        content = self.render(profiles)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

    def render(self, profiles: List["ProjectProfile"]) -> str:
        """Render the full HTML report as a string."""
        rows = "\n".join(self._render_row(p) for p in sorted(profiles, key=lambda x: x.name))
        cards = "\n".join(self._render_card(p) for p in sorted(profiles, key=lambda x: x.name))

        total_sloc = sum(p.code_stats.source_lines for p in profiles)
        avg_maturity = sum(p.maturity.score for p in profiles) / len(profiles) if profiles else 0

        return _HTML_TEMPLATE.format(
            org_name=html.escape(self.org_name),
            org_url=html.escape(self.org_url),
            generated_at=self.generated_at,
            project_count=len(profiles),
            total_sloc=f"{total_sloc:,}",
            avg_maturity=f"{avg_maturity:.0f}",
            table_rows=rows,
            project_cards=cards,
        )

    def _render_row(self, p: "ProjectProfile") -> str:
        name = html.escape(p.name)
        ver = html.escape(p.metadata.version or "—")
        lang = html.escape(p.tech_stack.primary_language)
        grade = html.escape(p.maturity.grade)
        grade_cls = (
            "grade-good" if p.maturity.score >= 70
            else "grade-mid" if p.maturity.score >= 40
            else "grade-low"
        )
        return (
            f"<tr>"
            f"<td><a href='#{name}'>{name}</a></td>"
            f"<td>{ver}</td>"
            f"<td>{lang}</td>"
            f"<td class='num'>{p.code_stats.source_lines:,}</td>"
            f"<td class='{grade_cls}'>{grade}</td>"
            f"<td class='num'>{p.maturity.score:.0f}</td>"
            f"<td>{'✅' if p.maturity.has_tests else '❌'}</td>"
            f"<td>{'✅' if p.maturity.has_ci else '❌'}</td>"
            f"</tr>"
        )

    def _render_card(self, p: "ProjectProfile") -> str:
        name = html.escape(p.name)
        desc = html.escape(p.metadata.description or "No description.")
        if len(desc) > 200:
            desc = desc[:197] + "..."
        grade_cls = (
            "grade-good" if p.maturity.score >= 70
            else "grade-mid" if p.maturity.score >= 40
            else "grade-low"
        )
        features = []
        if p.maturity.has_tests:
            features.append("Tests")
        if p.maturity.has_ci:
            features.append("CI/CD")
        if p.maturity.has_docker:
            features.append("Docker")
        if p.maturity.has_docs:
            features.append("Docs")
        feat_html = " · ".join(f"<span class='feat'>{f}</span>" for f in features) if features else "—"

        return (
            f"<div class='card' id='{name}'>"
            f"<h3>{name} <span class='badge {grade_cls}'>{html.escape(p.maturity.grade)}</span></h3>"
            f"<p class='desc'>{desc}</p>"
            f"<div class='meta'>"
            f"<span>{html.escape(p.tech_stack.primary_language)}</span>"
            f"<span>v{html.escape(p.metadata.version or '?')}</span>"
            f"<span>{p.code_stats.source_lines:,} SLOC</span>"
            f"</div>"
            f"<div class='features'>{feat_html}</div>"
            f"</div>"
        )


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{org_name} — Project Portfolio</title>
<style>
  :root {{ --bg: #f8f9fa; --card: #fff; --border: #dee2e6; --accent: #0d6efd; --good: #198754; --mid: #ffc107; --low: #dc3545; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: #212529; margin: 0; padding: 2rem; max-width: 1200px; margin: 0 auto; }}
  h1 {{ border-bottom: 2px solid var(--accent); padding-bottom: 0.5rem; }}
  .stats {{ display: flex; gap: 2rem; margin: 1rem 0 2rem; flex-wrap: wrap; }}
  .stat {{ background: var(--card); padding: 1rem 1.5rem; border-radius: 8px; border: 1px solid var(--border); text-align: center; }}
  .stat .val {{ font-size: 1.8rem; font-weight: 700; color: var(--accent); }}
  .stat .label {{ font-size: 0.85rem; color: #6c757d; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1.5rem 0; background: var(--card); border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }}
  th {{ background: #e9ecef; padding: 0.75rem; text-align: left; font-size: 0.85rem; }}
  td {{ padding: 0.6rem 0.75rem; border-top: 1px solid var(--border); }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .grade-good {{ color: var(--good); font-weight: 700; }}
  .grade-mid {{ color: var(--mid); font-weight: 700; }}
  .grade-low {{ color: var(--low); font-weight: 700; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; margin: 2rem 0; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin: 0 0 0.5rem; font-size: 1.1rem; }}
  .badge {{ font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; color: #fff; }}
  .badge.grade-good {{ background: var(--good); }}
  .badge.grade-mid {{ background: var(--mid); color: #000; }}
  .badge.grade-low {{ background: var(--low); }}
  .desc {{ color: #495057; font-size: 0.9rem; margin: 0.5rem 0; }}
  .meta {{ display: flex; gap: 1rem; font-size: 0.8rem; color: #6c757d; margin: 0.5rem 0; }}
  .features {{ font-size: 0.8rem; }}
  .feat {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; }}
  footer {{ margin-top: 3rem; text-align: center; color: #6c757d; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>{org_name} — Project Portfolio</h1>

<div class="stats">
  <div class="stat"><div class="val">{project_count}</div><div class="label">Projects</div></div>
  <div class="stat"><div class="val">{total_sloc}</div><div class="label">Total SLOC</div></div>
  <div class="stat"><div class="val">{avg_maturity}/100</div><div class="label">Avg Maturity</div></div>
</div>

<h2>Summary Table</h2>
<table>
<thead><tr><th>Project</th><th>Version</th><th>Language</th><th>SLOC</th><th>Grade</th><th>Score</th><th>Tests</th><th>CI</th></tr></thead>
<tbody>
{table_rows}
</tbody>
</table>

<h2>Project Cards</h2>
<div class="cards">
{project_cards}
</div>

<footer>Generated by <a href="https://github.com/wronai/todocs">todocs</a> on {generated_at}.</footer>
</body>
</html>"""
