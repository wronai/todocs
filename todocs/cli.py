"""CLI interface for todocs — backward compatibility shim.

This module re-exports all CLI functionality from the todocs.cli package.
The actual implementation has been moved to:
  - todocs.cli/__init__.py - main CLI group
  - todocs.cli/commands.py - command implementations
  - todocs.cli/progress.py - Rich progress utilities
  - todocs.cli/utils.py - shared utilities
"""

from __future__ import annotations

# Re-export all public API from the new cli package
from todocs.cli import (
    main,
    __version__,
)
from todocs.cli.commands import (
    generate,
    inspect,
    compare,
    health,
    readme,
    status,
    cards,
    index,
    export_cmd,
)
from todocs.cli.utils import (
    HAS_RICH,
    detect_org_from_git,
    write_json_report,
    TIMEOUT_5,
    CONSTANT_40,
    CONSTANT_70,
)
from todocs.cli.progress import (
    generate_with_rich,
    generate_without_rich,
    discover_and_show_progress,
    scan_with_progress,
    print_project_summary,
    generate_articles_with_progress,
)

# Backward compatibility aliases
_detect_org_from_git = detect_org_from_git
_write_json_report = write_json_report
_generate_with_rich = generate_with_rich
_generate_without_rich = generate_without_rich
_discover_and_show_progress = discover_and_show_progress
_scan_with_progress = scan_with_progress
_print_project_summary = print_project_summary
_generate_articles_with_progress = generate_articles_with_progress

__all__ = [
    "main",
    "generate",
    "inspect",
    "compare",
    "health",
    "readme",
    "status",
    "cards",
    "index",
    "export_cmd",
    "HAS_RICH",
]

if __name__ == "__main__":
    main()
