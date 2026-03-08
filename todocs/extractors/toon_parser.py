"""Parse .toon (Token-Oriented Object Notation) files.

TOON files in the wronai ecosystem come in several flavors:
  - project.toon / map.toon   → module map with classes, functions, imports
  - analysis.toon              → code health: complexity layers, coupling, refactoring hints
  - flow.toon                  → data-flow pipelines with purity/bottleneck info
  - *.functions.toon           → exported function signatures

This parser extracts structured data from all flavors without requiring
the toonic SDK, using regex-based line parsing.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class ToonParser:
    """Parse .toon files into structured data."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

    def find_toon_files(self) -> Dict[str, Path]:
        """Discover .toon files in the project root."""
        found: Dict[str, Path] = {}
        for p in self.root.glob("*.toon"):
            name = p.stem
            # Classify by name pattern
            if "analysis" in name:
                found["analysis"] = p
            elif "flow" in name:
                found["flow"] = p
            elif "function" in name.lower():
                found.setdefault("functions", p)
            elif name in ("project", "map"):
                found.setdefault("map", p)
            else:
                found[name] = p
        return found

    def parse_all(self) -> Dict[str, Any]:
        """Parse all discovered .toon files and return unified summary."""
        files = self.find_toon_files()
        result: Dict[str, Any] = {"toon_files": list(files.keys())}

        if "map" in files:
            result["map"] = self.parse_map(files["map"])
        if "analysis" in files:
            result["analysis"] = self.parse_analysis(files["analysis"])
        if "flow" in files:
            result["flow"] = self.parse_flow(files["flow"])
        if "functions" in files:
            result["functions"] = self.parse_functions(files["functions"])

        return result

    def parse_map(self, path: Path) -> Dict[str, Any]:
        """Parse project.toon / map.toon — module listing with metadata."""
        text = self._read(path)
        if not text:
            return {}

        result: Dict[str, Any] = {}
        result.update(self._parse_map_header(text))
        result["modules"] = self._parse_modules_section(text)
        classes, functions = self._parse_details_section(text)
        result["classes"] = classes
        result["top_functions"] = functions
        return result

    def _parse_map_header(self, text: str) -> Dict[str, Any]:
        """Parse header from map.toon: # project_name | Nf NL | lang:N."""
        result: Dict[str, Any] = {}
        header_m = re.match(r"^#\s+(\S+)\s*\|\s*(\d+)f\s+(\d+)L", text)
        if header_m:
            result["project"] = header_m.group(1)
            result["total_functions"] = int(header_m.group(2))
            result["total_lines"] = int(header_m.group(3))
        return result

    def _parse_modules_section(self, text: str) -> List[Dict[str, Any]]:
        """Parse M[] section from map.toon."""
        modules = []
        in_modules = False
        for line in text.splitlines():
            if line.strip().startswith("M["):
                in_modules = True
                continue
            if in_modules:
                if line.startswith("D:") or line.startswith("HEALTH") or not line.strip():
                    if line.startswith("D:"):
                        in_modules = False
                    if not line.strip():
                        continue
                    break
                m = re.match(r"\s+(\S+),(\d+)", line)
                if m:
                    modules.append({"path": m.group(1), "lines": int(m.group(2))})
        return modules

    def _parse_details_section(self, text: str) -> tuple:
        """Parse D: section from map.toon — classes and functions."""
        classes = []
        functions_list = []
        current_file = ""
        in_details = False

        for line in text.splitlines():
            if line.strip() == "D:":
                in_details = True
                continue
            if not in_details:
                continue

            file_m = re.match(r"\s+(\S+\.py):", line)
            if file_m:
                current_file = file_m.group(1)
                continue

            cls = self._parse_class_line(line, current_file)
            if cls:
                classes.append(cls)

            func = self._parse_function_line(line, current_file)
            if func:
                functions_list.append(func)

        return classes, functions_list[:30]

    def _parse_class_line(self, line: str, current_file: str) -> Dict[str, Any] | None:
        """Parse a class definition line from map.toon details."""
        cls_m = re.match(r"\s+(\w+)(?:\([\w.,\s]+\))?:\s*(.+)", line)
        if cls_m and not line.strip().startswith(("e:", "i:")):
            name = cls_m.group(1)
            rest = cls_m.group(2).strip()
            if name[0].isupper():
                method_count = rest.count("(")
                doc = ""
                if "#" in rest:
                    doc = rest.split("#", 1)[1].strip().rstrip(".")
                return {
                    "name": name,
                    "file": current_file,
                    "methods": method_count,
                    "description": doc[:120],
                }
        return None

    def _parse_function_line(self, line: str, current_file: str) -> Dict[str, Any] | None:
        """Parse a function definition line from map.toon details."""
        func_m = re.match(r"\s+(\w+)\(([^)]*)\)", line)
        if func_m and not line.strip().startswith(("e:", "i:", "c:")):
            fname = func_m.group(1)
            if fname[0].islower() and fname not in ("e", "i", "c", "m", "f"):
                return {"name": fname, "file": current_file}
        return None

    def parse_analysis(self, path: Path) -> Dict[str, Any]:
        """Parse analysis.toon — health, coupling, layers."""
        text = self._read(path)
        if not text:
            return {}

        result: Dict[str, Any] = {}
        result.update(self._parse_analysis_header(text))
        result["health_warnings"] = self._parse_health_section(text)
        result["refactor_suggestions"] = self._parse_refactor_section(text)
        result["layers"] = self._parse_layers_section(text)
        return result

    def _parse_analysis_header(self, text: str) -> Dict[str, Any]:
        """Parse header metrics from analysis.toon."""
        result: Dict[str, Any] = {}

        header2 = re.search(r"CC̄=([0-9.]+)", text)
        if header2:
            result["avg_complexity"] = float(header2.group(1))

        crit_m = re.search(r"critical:(\d+)/(\d+)", text)
        if crit_m:
            result["critical_functions"] = int(crit_m.group(1))
            result["total_functions_analyzed"] = int(crit_m.group(2))

        dups_m = re.search(r"dups:(\d+)", text)
        if dups_m:
            result["duplicate_blocks"] = int(dups_m.group(1))

        cycles_m = re.search(r"cycles:(\d+)", text)
        if cycles_m:
            result["dependency_cycles"] = int(cycles_m.group(1))

        return result

    def _parse_health_section(self, text: str) -> List[Dict[str, Any]]:
        """Parse HEALTH section from analysis.toon."""
        health_items = []
        in_health = False
        for line in text.splitlines():
            if line.strip().startswith("HEALTH"):
                in_health = True
                continue
            if in_health:
                if line.strip() and not line.startswith(" "):
                    break
                hm = re.match(r"\s+[🟡🔴🟢⚠️]\s+CC\s+(\w+)\s+CC=(\d+)", line)
                if hm:
                    health_items.append({
                        "function": hm.group(1),
                        "complexity": int(hm.group(2)),
                    })
        return health_items

    def _parse_refactor_section(self, text: str) -> List[str]:
        """Parse REFACTOR section from analysis.toon."""
        refactor_items = []
        in_refactor = False
        for line in text.splitlines():
            if line.strip().startswith("REFACTOR"):
                in_refactor = True
                continue
            if in_refactor:
                if line.strip() and not line.startswith(" "):
                    break
                rm = re.match(r"\s+\d+\.\s+(.+)", line)
                if rm:
                    refactor_items.append(rm.group(1).strip())
        return refactor_items

    def _parse_layers_section(self, text: str) -> List[Dict[str, Any]]:
        """Parse LAYERS section from analysis.toon."""
        layers = []
        in_layers = False
        for line in text.splitlines():
            if line.strip().startswith("LAYERS"):
                in_layers = True
                continue
            if in_layers:
                if line.strip() and not line.startswith(" ") and not line.startswith("│"):
                    break
                lm = re.match(
                    r"\s*│?\s*[!]*\s*(\w+)\s+(\d+)L\s+(\d+)C\s+(\d+)m\s+CC=([0-9.]+)",
                    line,
                )
                if lm:
                    layers.append({
                        "module": lm.group(1),
                        "lines": int(lm.group(2)),
                        "classes": int(lm.group(3)),
                        "methods": int(lm.group(4)),
                        "complexity": float(lm.group(5)),
                    })
        return layers

    def parse_flow(self, path: Path) -> Dict[str, Any]:
        """Parse flow.toon — pipeline and data-flow analysis."""
        text = self._read(path)
        if not text:
            return {}

        result: Dict[str, Any] = {}

        # Header: # project/flow | N func | M pipelines | K hub-types
        hm = re.match(r"#\s+\S+\s*\|\s*(\d+)\s+func\s*\|\s*(\d+)\s+pipelines?", text)
        if hm:
            result["total_functions"] = int(hm.group(1))
            result["total_pipelines"] = int(hm.group(2))

        # Parse PIPELINES section
        pipelines = []
        current_pipe: Optional[Dict] = None
        for line in text.splitlines():
            # Pipeline header: ProjectName [Category]: InputType → OutputType
            pipe_m = re.match(r"\s+\w+\s+\[(\w+)\]:\s+(.+)", line)
            if pipe_m:
                if current_pipe:
                    pipelines.append(current_pipe)
                current_pipe = {
                    "category": pipe_m.group(1),
                    "signature": pipe_m.group(2).strip(),
                    "steps": [],
                    "bottleneck": "",
                    "purity": "",
                }
                continue

            if current_pipe:
                # Step: → function_name(args) → ReturnType  CC=N  IO/pure/mutation
                step_m = re.match(
                    r"\s+→\s+(\w+)\([^)]*\)\s*→?\s*\S*\s*CC=(\d+)\s+(\w+)",
                    line,
                )
                if step_m:
                    current_pipe["steps"].append({
                        "function": step_m.group(1),
                        "complexity": int(step_m.group(2)),
                        "kind": step_m.group(3),
                    })

                # BOTTLENECK line
                bn_m = re.search(r"BOTTLENECK:\s+(\w+)\(CC=(\d+)\)", line)
                if bn_m:
                    current_pipe["bottleneck"] = bn_m.group(1)

                # PURITY line
                pur_m = re.search(r"PURITY:\s+(\d+/\d+)\s+pure", line)
                if pur_m:
                    current_pipe["purity"] = pur_m.group(1)

        if current_pipe:
            pipelines.append(current_pipe)

        result["pipelines"] = pipelines
        return result

    def parse_functions(self, path: Path) -> Dict[str, Any]:
        """Parse *.functions.toon — exported function signatures."""
        text = self._read(path)
        if not text:
            return {}

        functions = []
        for line in text.splitlines():
            # function_name(arg1:Type, arg2:Type) -> ReturnType
            fm = re.match(r"\s*(\w+)\(([^)]*)\)(?:\s*->\s*(\S+))?", line)
            if fm:
                name = fm.group(1)
                if name[0].islower() and name not in ("e", "i", "c", "m"):
                    functions.append({
                        "name": name,
                        "args": fm.group(2).strip(),
                        "returns": fm.group(3) or "",
                    })

        return {"exported_functions": functions}

    def _read(self, path: Path) -> str:
        try:
            return path.read_text(errors="replace")
        except Exception:
            return ""
