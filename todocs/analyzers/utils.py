"""Shared analyzer utilities."""

from __future__ import annotations

from pathlib import Path


def should_skip(path: Path, skip_dirs: set[str]) -> bool:
    """Check if path should be skipped based on directory names.

    Args:
        path: Path to check
        skip_dirs: Set of directory names to skip

    Returns:
        True if path contains any skip directory or .egg-info
    """
    for part in path.parts:
        if part in skip_dirs or part.endswith(".egg-info"):
            return True
    return False
