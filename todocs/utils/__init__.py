"""Gitignore pattern matching utility for todocs.

Parses .gitignore files and provides pattern matching for path exclusion.
"""

from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Optional


class GitignoreParser:
    """Parse and match .gitignore patterns."""

    def __init__(self, root_path: Path, max_depth: int = 3):
        self.root = Path(root_path)
        self.max_depth = max_depth
        self.patterns: List[tuple] = []  # (pattern, is_negation, is_dir_only)
        self._load_gitignore()

    def _load_gitignore(self) -> None:
        """Load patterns from .gitignore file if it exists."""
        gitignore_path = self.root / ".gitignore"
        if gitignore_path.exists():
            try:
                content = gitignore_path.read_text(errors="replace")
                self.patterns = self._parse_patterns(content)
            except Exception:
                pass

    def _parse_patterns(self, content: str) -> List[tuple]:
        """Parse gitignore content into patterns."""
        patterns = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            is_negation = line.startswith("!")
            if is_negation:
                line = line[1:]

            is_dir_only = line.endswith("/")
            if is_dir_only:
                line = line[:-1]

            # Skip empty patterns
            if not line:
                continue

            patterns.append((line, is_negation, is_dir_only))

        return patterns

    def _match_pattern(self, pattern: str, path: str, is_dir: bool) -> bool:
        """Match a single pattern against a path."""
        # Handle directory-only patterns
        if pattern.endswith("/"):
            if not is_dir:
                return False
            pattern = pattern[:-1]

        # Handle patterns with slashes (relative to root)
        if "/" in pattern:
            # Pattern contains path separator - match from root
            if pattern.startswith("/"):
                pattern = pattern[1:]
            return fnmatch(path, pattern) or fnmatch(path, f"*/{pattern}")
        else:
            # No path separator - match any component
            parts = path.split("/")
            for part in parts:
                if fnmatch(part, pattern):
                    return True
            return False

    def is_ignored(self, relative_path: Path, is_dir: bool = False) -> bool:
        """Check if a path should be ignored."""
        path_str = str(relative_path).replace("\\", "/")

        # Check depth limit
        depth = len(relative_path.parts)
        if depth > self.max_depth:
            return True

        # Check gitignore patterns
        ignored = False
        for pattern, is_negation, is_dir_only in self.patterns:
            if is_dir_only and not is_dir:
                continue

            matches = self._match_pattern(pattern, path_str, is_dir)

            if matches:
                if is_negation:
                    ignored = False
                else:
                    ignored = True

        return ignored


def create_scan_filter(project_path: Path, max_depth: int = 3, extra_excludes: Optional[set] = None):
    """Create a filter function for scanning with depth and gitignore support."""
    gitignore = GitignoreParser(project_path, max_depth)
    extra_excludes = extra_excludes or set()

    # Common dependency/package folders to always skip
    skip_dirs = {
        "venv", ".venv", "env", "node_modules", "__pycache__", ".git",
        ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
        ".eggs", ".egg-info", "htmlcov", "coverage",
        "site", ".idea", ".vscode", ".hg", ".svn", "CVS",
        ".next", ".nuxt", ".svelte-kit", ".vercel", ".netlify",
        "vendor", "bower_components", "jspm_packages",
        "target",  # Rust/Cargo
        "bin", "obj",  # .NET
        ".gradle",  # Gradle
    }
    skip_dirs.update(extra_excludes)

    def should_scan(path: Path) -> bool:
        """Check if a path should be scanned."""
        try:
            rel_path = path.relative_to(project_path)
        except ValueError:
            return True

        # Skip dot directories
        if any(part.startswith(".") for part in rel_path.parts):
            return False

        # Skip common dependency/package folders
        if any(part in skip_dirs for part in rel_path.parts):
            return False

        # Check depth
        if len(rel_path.parts) > max_depth:
            return False

        # Check gitignore patterns
        is_dir = path.is_dir()
        if gitignore.is_ignored(rel_path, is_dir):
            return False

        return True

    return should_scan
