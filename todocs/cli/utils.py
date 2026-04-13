"""CLI utilities and shared constants."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

TIMEOUT_5 = 5
CONSTANT_40 = 40
CONSTANT_70 = 70


try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def detect_org_from_git(root_dir: Path) -> tuple[str, str]:
    """Detect organization name and URL from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_5,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Parse github.com/user/repo or git@github.com:user/repo
            match = re.search(r"github\.com[/:]([^/]+)", url)
            if match:
                org = match.group(1)
                return org, f"https://github.com/{org}"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fallback: use parent directory name
    org = root_dir.parent.name if root_dir.parent.name else root_dir.name
    return org, f"https://github.com/{org}"


def write_json_report(profiles: list, json_report: Optional[str], console, has_rich: bool):
    """Write optional JSON report."""
    if not json_report:
        return

    report_data = [p.to_dict() for p in profiles]
    Path(json_report).write_text(
        json.dumps(report_data, indent=2, default=str), encoding="utf-8"
    )
    if has_rich and console:
        console.print(f"[green]✓[/green] JSON report written to [cyan]{json_report}[/cyan]")
    else:
        print(f"JSON report written to {json_report}")
