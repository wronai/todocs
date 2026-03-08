"""Score project maturity based on structural and metric indicators."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from todocs.core import ProjectProfile, MaturityProfile


_GRADE_THRESHOLDS = [
    (90, "A+"), (80, "A"), (70, "B+"), (60, "B"),
    (50, "C+"), (40, "C"), (30, "D"), (20, "D-"), (0, "F"),
]


class MaturityScorer:
    """Compute a maturity score (0-100) for a project."""

    def __init__(self, project_path: Path, profile: "ProjectProfile"):
        self.root = Path(project_path)
        self.profile = profile

    def score(self) -> "MaturityProfile":
        from todocs.core import MaturityProfile

        p = self.profile
        root = self.root

        has_tests = (root / "tests").is_dir() or (root / "test").is_dir()
        has_ci = (root / ".github" / "workflows").is_dir() or (root / ".gitlab-ci.yml").exists()
        has_docs = (root / "docs").is_dir()
        has_changelog = (root / "CHANGELOG.md").exists() or (root / "changelog.md").exists()
        has_license = (root / "LICENSE").exists() or (root / "LICENSE.md").exists()
        has_examples = (root / "examples").is_dir() or (root / "example").is_dir()
        has_docker = (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists()
        has_makefile = (root / "Makefile").exists() or (root / "Taskfile.yml").exists()
        has_version = (root / "VERSION").exists()
        has_readme = (root / "README.md").exists()
        has_pyproject = (root / "pyproject.toml").exists()
        has_gitignore = (root / ".gitignore").exists()

        # Test ratio
        src_lines = max(p.code_stats.source_lines, 1)
        test_ratio = p.code_stats.test_lines / src_lines

        # Doc completeness (0-1): based on readme sections
        readme_keys = set(p.readme_sections.keys())
        expected_sections = {"description", "installation", "usage", "license"}
        found = len(readme_keys & expected_sections)
        doc_completeness = found / len(expected_sections) if expected_sections else 0

        # Scoring
        points = 0.0
        max_points = 0.0

        checks = [
            (has_readme, 10, "README"),
            (has_tests, 12, "Tests"),
            (has_ci, 8, "CI/CD"),
            (has_docs, 6, "Docs dir"),
            (has_changelog, 7, "Changelog"),
            (has_license, 6, "License"),
            (has_examples, 5, "Examples"),
            (has_docker, 5, "Docker"),
            (has_makefile, 5, "Makefile"),
            (has_version, 3, "Version file"),
            (has_pyproject, 5, "pyproject.toml"),
            (has_gitignore, 3, "gitignore"),
            (test_ratio >= 0.1, 8, "Test ratio >= 10%"),
            (test_ratio >= 0.3, 5, "Test ratio >= 30%"),
            (doc_completeness >= 0.5, 6, "Doc completeness >= 50%"),
            (p.code_stats.avg_complexity <= 10, 6, "Low avg complexity"),
        ]

        for passed, weight, _label in checks:
            max_points += weight
            if passed:
                points += weight

        raw_score = (points / max_points * 100) if max_points > 0 else 0
        grade = "F"
        for threshold, g in _GRADE_THRESHOLDS:
            if raw_score >= threshold:
                grade = g
                break

        return MaturityProfile(
            score=round(raw_score, 1),
            grade=grade,
            has_tests=has_tests,
            has_ci=has_ci,
            has_docs=has_docs,
            has_changelog=has_changelog,
            has_license=has_license,
            has_examples=has_examples,
            has_docker=has_docker,
            has_makefile=has_makefile,
            has_version_file=has_version,
            test_ratio=round(test_ratio, 3),
            doc_completeness=round(doc_completeness, 2),
        )
