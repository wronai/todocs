"""Markdown output — WordPress-ready markdown serializer."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


class MarkdownOutput:
    """Write project profiles as markdown files (WordPress-ready)."""

    def __init__(self, org_name: str = "WronAI", org_url: str = "https://github.com/wronai"):
        self.org_name = org_name
        self.org_url = org_url

    def write_all(
        self,
        profiles: List["ProjectProfile"],
        output_dir: Path,
        include_index: bool = True,
        include_cards: bool = False,
        include_comparison: bool = True,
        include_health: bool = True,
        include_status: bool = False,
    ) -> List[Path]:
        """Write all markdown outputs. Returns list of written paths."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: List[Path] = []

        paths.extend(self._write_articles(profiles, output_dir))
        paths.extend(self._write_index(profiles, output_dir, include_index))
        paths.extend(self._write_cards(profiles, output_dir, include_cards))
        paths.extend(self._write_comparison_reports(profiles, output_dir, include_comparison, include_health))
        paths.extend(self._write_status_report(profiles, output_dir, include_status))

        return paths

    def _write_articles(self, profiles: List["ProjectProfile"], output_dir: Path) -> List[Path]:
        """Write per-project articles."""
        from todocs.generators.article import ArticleGenerator

        article_gen = ArticleGenerator(org_name=self.org_name, org_url=self.org_url)
        paths: List[Path] = []

        for p in profiles:
            path = output_dir / f"{p.name}.md"
            article_gen.generate(p, path)
            paths.append(path)

        return paths

    def _write_index(self, profiles: List["ProjectProfile"], output_dir: Path, include: bool) -> List[Path]:
        """Write organization index page."""
        if not include:
            return []

        from todocs.generators.org_index_gen import OrgIndexGenerator

        idx_gen = OrgIndexGenerator(org_name=self.org_name, org_url=self.org_url)
        idx_path = output_dir / "_index.md"
        idx_gen.generate(profiles, idx_path)
        return [idx_path]

    def _write_cards(self, profiles: List["ProjectProfile"], output_dir: Path, include: bool) -> List[Path]:
        """Write project cards."""
        if not include:
            return []

        from todocs.generators.project_card_gen import ProjectCardGenerator

        card_gen = ProjectCardGenerator(org_name=self.org_name, org_url=self.org_url)
        return card_gen.generate_all(profiles, output_dir)

    def _write_comparison_reports(
        self, profiles: List["ProjectProfile"], output_dir: Path, include_comp: bool, include_health: bool
    ) -> List[Path]:
        """Write comparison and health reports (require 2+ projects)."""
        if len(profiles) < 2:
            return []

        from todocs.generators.comparison import ComparisonGenerator

        comp_gen = ComparisonGenerator(org_name=self.org_name, org_url=self.org_url)
        paths: List[Path] = []

        if include_comp:
            comp_path = output_dir / "_comparison.md"
            comp_gen.generate_comparison(profiles, comp_path)
            paths.append(comp_path)

        if include_health:
            health_path = output_dir / "_health-report.md"
            comp_gen.generate_health_report(profiles, health_path)
            paths.append(health_path)

        return paths

    def _write_status_report(self, profiles: List["ProjectProfile"], output_dir: Path, include: bool) -> List[Path]:
        """Write status report."""
        if not include:
            return []

        from todocs.generators.status_report_gen import StatusReportGenerator

        status_gen = StatusReportGenerator(org_name=self.org_name, org_url=self.org_url)
        status_path = output_dir / "_status-report.md"
        status_gen.generate(profiles, status_path)
        return [status_path]
