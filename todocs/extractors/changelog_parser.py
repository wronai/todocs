"""Parse CHANGELOG.md to extract recent version entries."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional


class ChangelogParser:
    """Extract structured entries from CHANGELOG.md."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

    def parse(self, max_entries: int = 5) -> List[Dict[str, str]]:
        """Return list of {version, date, content} dicts for recent releases."""
        cl_path = self._find_changelog()
        if not cl_path:
            return []

        try:
            text = cl_path.read_text(errors="replace")
        except Exception:
            return []

        return self._parse_entries(text, max_entries)

    def _find_changelog(self) -> Optional[Path]:
        for name in ["CHANGELOG.md", "changelog.md", "CHANGES.md", "HISTORY.md"]:
            fp = self.root / name
            if fp.exists():
                return fp
        return None

    def _parse_entries(self, text: str, max_entries: int) -> List[Dict[str, str]]:
        """Parse Keep-a-Changelog or similar format."""
        entries = []

        # Pattern matches: ## [1.0.0] - 2025-01-01  or  ## 1.0.0 (2025-01-01)  or  ## v1.0.0
        heading_re = re.compile(
            r"^##\s+\[?v?(\d+\.\d+(?:\.\d+)?(?:-\w+)?)\]?"
            r"(?:\s*[-–]\s*(\d{4}-\d{2}-\d{2}))?"
            r"(?:\s*\((\d{4}-\d{2}-\d{2})\))?",
            re.MULTILINE,
        )

        matches = list(heading_re.finditer(text))

        for i, m in enumerate(matches):
            if len(entries) >= max_entries:
                break

            version = m.group(1)
            date = m.group(2) or m.group(3) or ""

            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()

            # Summarize: extract category headers and first items
            summary = self._summarize_entry(content)

            entries.append({
                "version": version,
                "date": date,
                "content": summary,
            })

        return entries

    def _summarize_entry(self, content: str, max_items: int = 6) -> str:
        """Summarize a changelog entry by extracting key changes."""
        lines = content.split("\n")
        items = []
        current_category = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Category heading: ### Added, ### Fixed, etc.
            cat_match = re.match(r"^###\s+(.+)", line)
            if cat_match:
                current_category = cat_match.group(1).strip()
                continue

            # List item
            if line.startswith(("- ", "* ", "+ ")):
                item_text = line.lstrip("-*+ ").strip()
                # Remove markdown links
                item_text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", item_text)
                if len(item_text) > 120:
                    item_text = item_text[:120] + "..."

                prefix = f"[{current_category}] " if current_category else ""
                items.append(f"{prefix}{item_text}")

                if len(items) >= max_items:
                    break

        return "; ".join(items) if items else content[:300]
