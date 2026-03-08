"""Parse Makefile / Taskfile.yml to extract build targets and commands."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class MakefileParser:
    """Extract targets and structure from Makefile or Taskfile.yml."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

    def parse(self) -> Dict[str, Any]:
        """Parse build file and return targets with descriptions."""
        # Try Makefile first, then Taskfile.yml
        makefile = self.root / "Makefile"
        taskfile = self.root / "Taskfile.yml"

        result: Dict[str, Any] = {"type": None, "targets": []}

        if makefile.exists():
            result["type"] = "makefile"
            result["targets"] = self._parse_makefile(makefile)
        elif taskfile.exists():
            result["type"] = "taskfile"
            result["targets"] = self._parse_taskfile(taskfile)

        return result

    def _parse_makefile(self, path: Path) -> List[Dict[str, str]]:
        """Parse GNU Makefile targets."""
        try:
            text = path.read_text(errors="replace")
        except Exception:
            return []

        targets = []
        phony_targets = set()

        # Collect .PHONY declarations
        for line in text.splitlines():
            phony_m = re.match(r"\.PHONY:\s*(.+)", line)
            if phony_m:
                phony_targets.update(phony_m.group(1).split())

        lines = text.splitlines()
        for i, line in enumerate(lines):
            # Target pattern: target_name: [dependencies]  ## optional help text
            target_m = re.match(r"^([a-zA-Z_][\w.-]*)\s*:(?!=)", line)
            if target_m:
                name = target_m.group(1)

                # Skip internal targets
                if name.startswith("_") or name.startswith("."):
                    continue

                # Help comment: ## description
                help_text = ""
                help_m = re.search(r"##\s*(.+)", line)
                if help_m:
                    help_text = help_m.group(1).strip()

                # If no inline help, check line above for comment
                if not help_text and i > 0:
                    prev = lines[i - 1].strip()
                    if prev.startswith("#") and not prev.startswith("##"):
                        help_text = prev.lstrip("# ").strip()

                # Collect commands (indented lines after target)
                commands = []
                for j in range(i + 1, min(i + 10, len(lines))):
                    cmd_line = lines[j]
                    if cmd_line.startswith("\t") or cmd_line.startswith("    "):
                        cmd = cmd_line.strip()
                        # Strip @ prefix
                        if cmd.startswith("@"):
                            cmd = cmd[1:]
                        # Skip internal grep/awk help generators
                        if "MAKEFILE_LIST" in cmd:
                            continue
                        commands.append(cmd)
                    elif cmd_line.strip():
                        break

                targets.append({
                    "name": name,
                    "description": help_text,
                    "commands": commands[:3],  # first 3 commands
                    "is_phony": name in phony_targets,
                })

        return targets

    def _parse_taskfile(self, path: Path) -> List[Dict[str, str]]:
        """Parse Taskfile.yml (go-task format)."""
        if not HAS_YAML:
            return []

        try:
            data = yaml.safe_load(path.read_text(errors="replace"))
        except Exception:
            return []

        if not isinstance(data, dict):
            return []

        targets = []
        tasks = data.get("tasks", {})

        for name, task_def in tasks.items():
            if isinstance(task_def, dict):
                desc = task_def.get("desc", task_def.get("summary", ""))
                cmds = task_def.get("cmds", [])
                cmd_strs = []
                for c in cmds[:3]:
                    if isinstance(c, str):
                        cmd_strs.append(c)
                    elif isinstance(c, dict) and "cmd" in c:
                        cmd_strs.append(c["cmd"])

                targets.append({
                    "name": name,
                    "description": str(desc),
                    "commands": cmd_strs,
                    "is_phony": True,
                })

        return targets

    def get_target_names(self) -> List[str]:
        """Quick access to just target names."""
        data = self.parse()
        return [t["name"] for t in data.get("targets", [])]
