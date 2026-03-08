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
        phony_targets = self._collect_phony_targets(text)
        lines = text.splitlines()

        for i, line in enumerate(lines):
            target = self._parse_target_line(line, lines, i, phony_targets)
            if target:
                targets.append(target)

        return targets

    def _collect_phony_targets(self, text: str) -> set:
        """Collect .PHONY target declarations from Makefile."""
        phony_targets = set()
        for line in text.splitlines():
            phony_m = re.match(r"\.PHONY:\s*(.+)", line)
            if phony_m:
                phony_targets.update(phony_m.group(1).split())
        return phony_targets

    def _parse_target_line(self, line: str, lines: list, index: int, phony_targets: set) -> Dict[str, Any] | None:
        """Parse a single Makefile target line."""
        target_m = re.match(r"^([a-zA-Z_][\w.-]*)\s*:(?!=)", line)
        if not target_m:
            return None

        name = target_m.group(1)
        if name.startswith("_") or name.startswith("."):
            return None

        help_text = self._extract_help_text(line, lines, index)
        commands = self._collect_commands(lines, index)

        return {
            "name": name,
            "description": help_text,
            "commands": commands[:3],
            "is_phony": name in phony_targets,
        }

    def _extract_help_text(self, line: str, lines: list, index: int) -> str:
        """Extract help text from inline comment or previous line."""
        help_m = re.search(r"##\s*(.+)", line)
        if help_m:
            return help_m.group(1).strip()

        if index > 0:
            prev = lines[index - 1].strip()
            if prev.startswith("#") and not prev.startswith("##"):
                return prev.lstrip("# ").strip()
        return ""

    def _collect_commands(self, lines: list, index: int) -> List[str]:
        """Collect indented command lines after a target."""
        commands = []
        for j in range(index + 1, min(index + 10, len(lines))):
            cmd_line = lines[j]
            if cmd_line.startswith("\t") or cmd_line.startswith("    "):
                cmd = cmd_line.strip()
                if cmd.startswith("@"):
                    cmd = cmd[1:]
                if "MAKEFILE_LIST" in cmd:
                    continue
                commands.append(cmd)
            elif cmd_line.strip():
                break
        return commands

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
