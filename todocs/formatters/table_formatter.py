"""Comparative table formatter for multi-project data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from todocs.core import ProjectProfile


class TableFormatter:
    """Generate markdown comparison tables from project profiles."""

    def format_comparison(
        self,
        profiles: List["ProjectProfile"],
        columns: Optional[List[Dict[str, Any]]] = None,
        sort_by: str = "name",
        ascending: bool = True,
        limit: int = 50,
    ) -> str:
        """Render a configurable comparison table.

        Args:
            profiles: List of project profiles.
            columns: Column definitions, each a dict with:
                - header: column header text
                - getter: callable(profile) -> str
                - align: "left" | "right" | "center" (default "left")
            sort_by: Profile attribute name to sort by.
            ascending: Sort direction.
            limit: Max rows.
        """
        if columns is None:
            columns = self._default_columns()

        sorted_profiles = self._sort_profiles(profiles, sort_by, ascending)[:limit]
        return self._render_table(sorted_profiles, columns)

    def format_matrix(
        self,
        profiles: List["ProjectProfile"],
        features: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Render a feature presence matrix (✅/❌ grid).

        Args:
            features: Feature definitions, each a dict with:
                - header: column header
                - check: callable(profile) -> bool
        """
        if features is None:
            features = self._default_features()

        lines = []
        headers = ["Project"] + [f["header"] for f in features]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join(":-----:" if i > 0 else "-------" for i in range(len(headers))) + "|")

        for p in sorted(profiles, key=lambda x: x.name):
            cells = [p.name]
            for f in features:
                cells.append("✅" if f["check"](p) else "❌")
            lines.append("| " + " | ".join(cells) + " |")

        return "\n".join(lines)

    def format_ranking(
        self,
        profiles: List["ProjectProfile"],
        key: Callable[["ProjectProfile"], float] = lambda p: p.maturity.score,
        header: str = "Score",
        descending: bool = True,
        limit: int = 20,
    ) -> str:
        """Render a ranked leaderboard table."""
        ranked = sorted(profiles, key=key, reverse=descending)[:limit]
        lines = [
            f"| # | Project | {header} | Grade |",
            "|--:|---------|------:|:-----:|",
        ]
        for i, p in enumerate(ranked, 1):
            val = key(p)
            fmt_val = f"{val:,.0f}" if isinstance(val, (int, float)) else str(val)
            lines.append(f"| {i} | {p.name} | {fmt_val} | {p.maturity.grade} |")
        return "\n".join(lines)

    # ── Internal helpers ───────────────────────────────────────────

    @staticmethod
    def _default_columns() -> List[Dict[str, Any]]:
        return [
            {"header": "Project", "getter": lambda p: p.name, "align": "left"},
            {"header": "Version", "getter": lambda p: p.metadata.version or "—", "align": "left"},
            {"header": "Language", "getter": lambda p: p.tech_stack.primary_language, "align": "left"},
            {"header": "SLOC", "getter": lambda p: f"{p.code_stats.source_lines:,}", "align": "right"},
            {"header": "Grade", "getter": lambda p: p.maturity.grade, "align": "center"},
            {"header": "Tests", "getter": lambda p: "✓" if p.maturity.has_tests else "✗", "align": "center"},
        ]

    @staticmethod
    def _default_features() -> List[Dict[str, Any]]:
        return [
            {"header": "Tests", "check": lambda p: p.maturity.has_tests},
            {"header": "CI/CD", "check": lambda p: p.maturity.has_ci},
            {"header": "Docs", "check": lambda p: p.maturity.has_docs},
            {"header": "Docker", "check": lambda p: p.maturity.has_docker},
            {"header": "Changelog", "check": lambda p: p.maturity.has_changelog},
            {"header": "License", "check": lambda p: p.maturity.has_license},
            {"header": "Examples", "check": lambda p: p.maturity.has_examples},
        ]

    @staticmethod
    def _sort_profiles(
        profiles: List["ProjectProfile"], sort_by: str, ascending: bool
    ) -> List["ProjectProfile"]:
        def _get_sort_key(p: "ProjectProfile"):
            if sort_by == "name":
                return p.name.lower()
            if sort_by == "sloc":
                return p.code_stats.source_lines
            if sort_by == "maturity":
                return p.maturity.score
            if sort_by == "complexity":
                return p.code_stats.avg_complexity
            return p.name.lower()
        return sorted(profiles, key=_get_sort_key, reverse=not ascending)

    @staticmethod
    def _render_table(
        profiles: List["ProjectProfile"], columns: List[Dict[str, Any]]
    ) -> str:
        align_map = {"left": "------", "right": "-----:", "center": ":----:"}

        headers = [c["header"] for c in columns]
        aligns = [align_map.get(c.get("align", "left"), "------") for c in columns]

        lines = [
            "| " + " | ".join(headers) + " |",
            "|" + "|".join(aligns) + "|",
        ]
        for p in profiles:
            cells = [str(c["getter"](p)) for c in columns]
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)
