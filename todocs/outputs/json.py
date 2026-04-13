"""JSON output — structured JSON serializer for API/dashboard consumption."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from todocs.generators.base import BaseGenerator

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


class JSONOutput(BaseGenerator):
    """Write project profiles as structured JSON for APIs and dashboards."""

    def write(self, profiles: List["ProjectProfile"], output_path: Path) -> None:
        """Write the JSON report to a file."""
        data = self.render(profiles)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, default=str, ensure_ascii=False),
            encoding="utf-8",
        )

    def render(self, profiles: List["ProjectProfile"]) -> Dict[str, Any]:
        """Render the full JSON report as a dict."""
        return {
            "meta": self._meta(len(profiles)),
            "summary": self._summary(profiles),
            "projects": [self._project_entry(p) for p in sorted(profiles, key=lambda x: x.name)],
        }

    def _meta(self, count: int) -> Dict[str, Any]:
        return {
            "org_name": self.org_name,
            "org_url": self.org_url,
            "generated_at": self.generated_at,
            "generator": "todocs",
            "project_count": count,
        }

    def _summary(self, profiles: List["ProjectProfile"]) -> Dict[str, Any]:
        total = len(profiles)
        if not total:
            return {}
        return {
            "total_projects": total,
            "total_source_lines": sum(p.code_stats.source_lines for p in profiles),
            "total_source_files": sum(p.code_stats.source_files for p in profiles),
            "total_test_files": sum(p.code_stats.test_files for p in profiles),
            "avg_maturity_score": round(sum(p.maturity.score for p in profiles) / total, 1),
            "pct_with_tests": round(sum(1 for p in profiles if p.maturity.has_tests) / total * 100, 1),
            "pct_with_ci": round(sum(1 for p in profiles if p.maturity.has_ci) / total * 100, 1),
            "pct_with_docker": round(sum(1 for p in profiles if p.maturity.has_docker) / total * 100, 1),
            "categories": list(sorted(set(p.category for p in profiles))),
            "languages": list(sorted(set(p.tech_stack.primary_language for p in profiles))),
        }

    @staticmethod
    def _project_entry(p: "ProjectProfile") -> Dict[str, Any]:
        return {
            "name": p.name,
            "version": p.metadata.version or None,
            "description": p.metadata.description or None,
            "category": p.category,
            "language": p.tech_stack.primary_language,
            "repository": p.metadata.repository or None,
            "metrics": {
                "source_lines": p.code_stats.source_lines,
                "source_files": p.code_stats.source_files,
                "test_files": p.code_stats.test_files,
                "test_lines": p.code_stats.test_lines,
                "avg_complexity": p.code_stats.avg_complexity,
                "max_complexity": p.code_stats.max_complexity,
                "maintainability_index": p.code_stats.maintainability_index,
            },
            "maturity": {
                "score": p.maturity.score,
                "grade": p.maturity.grade,
                "has_tests": p.maturity.has_tests,
                "has_ci": p.maturity.has_ci,
                "has_docs": p.maturity.has_docs,
                "has_changelog": p.maturity.has_changelog,
                "has_license": p.maturity.has_license,
                "has_docker": p.maturity.has_docker,
                "has_examples": p.maturity.has_examples,
                "test_ratio": round(p.maturity.test_ratio, 3),
            },
            "tech_stack": {
                "primary_language": p.tech_stack.primary_language,
                "languages": p.tech_stack.languages,
                "frameworks": p.tech_stack.frameworks,
                "build_tools": p.tech_stack.build_tools,
                "ci_cd": p.tech_stack.ci_cd,
            },
            "dependencies": p.dependencies,
            "dev_dependencies": p.dev_dependencies,
        }
