"""Detect public API surface: CLI commands, exported classes, functions, REST endpoints."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List

_SKIP_DIRS = {
    "venv", ".venv", "env", "node_modules", "__pycache__", ".git",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs",
}


class APISurfaceAnalyzer:
    """Detect public API surface of a project."""

    def __init__(self, project_path: Path, filter_func=None):
        self.root = Path(project_path)
        self._filter = filter_func

    def analyze(self) -> Dict[str, Any]:
        """Return public API surface summary."""
        result: Dict[str, Any] = {
            "cli_commands": self._detect_cli_commands(),
            "public_classes": [],
            "public_functions": [],
            "rest_endpoints": [],
            "entry_points": self._detect_entry_points(),
        }

        # Scan Python source for public classes & functions
        classes, functions = self._scan_public_symbols()
        result["public_classes"] = classes
        result["public_functions"] = functions

        # Detect REST endpoints (FastAPI/Flask patterns)
        result["rest_endpoints"] = self._detect_rest_endpoints()

        return result

    def _should_skip(self, path: Path) -> bool:
        for part in path.parts:
            if part in _SKIP_DIRS or part.endswith(".egg-info"):
                return True
        return False

    def _detect_entry_points(self) -> Dict[str, str]:
        """Extract entry points from pyproject.toml."""
        try:
            import tomli
        except ImportError:
            try:
                import tomllib as tomli  # type: ignore
            except ImportError:
                return {}

        pyp = self.root / "pyproject.toml"
        if not pyp.exists():
            return {}

        try:
            data = tomli.loads(pyp.read_text(errors="replace"))
            scripts = data.get("project", {}).get("scripts", {})
            poetry_scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {})
            return {**poetry_scripts, **scripts}
        except Exception:
            return {}

    def _detect_cli_commands(self) -> List[Dict[str, str]]:
        """Detect CLI commands from Click/Typer/argparse patterns."""
        commands: List[Dict[str, str]] = []

        for pyf in self.root.rglob("*.py"):
            if self._should_skip(pyf.relative_to(self.root)):
                continue
            if self._filter and not self._filter(pyf):
                continue
            if "test" in pyf.name.lower():
                continue

            try:
                code = pyf.read_text(errors="replace")
                tree = ast.parse(code)
            except Exception:
                continue

            rel = str(pyf.relative_to(self.root))

            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                # Check decorators for click.command, click.group, app.command
                for dec in node.decorator_list:
                    dec_name = self._decorator_name(dec)
                    if dec_name in (
                        "click.command", "click.group", "main.command",
                        "app.command", "cli.command", "app.callback",
                    ):
                        # Extract docstring
                        doc = ast.get_docstring(node) or ""
                        commands.append({
                            "name": node.name,
                            "file": rel,
                            "framework": "click" if "click" in dec_name else "typer",
                            "description": doc[:120],
                        })
                        break

        return commands

    def _decorator_name(self, dec_node) -> str:
        """Extract decorator name string from AST node."""
        if isinstance(dec_node, ast.Name):
            return dec_node.id
        elif isinstance(dec_node, ast.Attribute):
            parts = []
            node = dec_node
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
            return ".".join(reversed(parts))
        elif isinstance(dec_node, ast.Call):
            return self._decorator_name(dec_node.func)
        return ""

    def _scan_public_symbols(self):
        """Scan __init__.py and main modules for public classes and functions."""
        classes: List[Dict[str, Any]] = []
        functions: List[Dict[str, Any]] = []
        seen_classes = set()
        seen_funcs = set()

        target_files = self._collect_target_files()

        for pyf in target_files:
            cls, funcs = self._extract_from_file(pyf, seen_classes, seen_funcs)
            classes.extend(cls)
            functions.extend(funcs)

        return classes[:20], functions[:20]

    def _collect_target_files(self) -> List[Path]:
        """Collect target Python files for public symbol scanning."""
        target_files = []
        for pyf in self.root.rglob("__init__.py"):
            if not self._should_skip(pyf.relative_to(self.root)):
                if self._filter and not self._filter(pyf):
                    continue
                target_files.append(pyf)

        for pyf in self.root.rglob("*.py"):
            if self._should_skip(pyf.relative_to(self.root)):
                continue
            if self._filter and not self._filter(pyf):
                continue
            if "test" in pyf.name.lower():
                continue
            rel = pyf.relative_to(self.root)
            if len(rel.parts) <= 3:
                target_files.append(pyf)

        return target_files

    def _extract_from_file(
        self, pyf: Path, seen_classes: set, seen_funcs: set
    ) -> tuple:
        """Extract classes and functions from a single Python file."""
        classes: List[Dict[str, Any]] = []
        functions: List[Dict[str, Any]] = []

        try:
            code = pyf.read_text(errors="replace")
            tree = ast.parse(code)
        except Exception:
            return classes, functions

        rel = str(pyf.relative_to(self.root))
        all_names = self._extract_all(tree)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                cls = self._extract_class(node, rel, all_names, seen_classes)
                if cls:
                    classes.append(cls)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = self._extract_function(node, rel, all_names, seen_funcs)
                if func:
                    functions.append(func)

        return classes, functions

    def _extract_class(
        self, node: ast.ClassDef, rel_path: str, all_names: set, seen: set
    ) -> Dict[str, Any] | None:
        """Extract class information from AST node."""
        name = node.name
        if name.startswith("_") and name not in (all_names or []):
            return None
        if name in seen:
            return None
        seen.add(name)

        doc = ast.get_docstring(node) or ""
        methods = [
            n.name for n in node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not n.name.startswith("_")
        ]

        return {
            "name": name,
            "file": rel_path,
            "methods": methods[:10],
            "method_count": len(methods),
            "description": doc[:120],
            "is_exported": name in (all_names or set()),
        }

    def _extract_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, rel_path: str,
        all_names: set, seen: set
    ) -> Dict[str, Any] | None:
        """Extract function information from AST node."""
        name = node.name
        if name.startswith("_"):
            return None
        if name in seen:
            return None
        seen.add(name)

        doc = ast.get_docstring(node) or ""
        args = [a.arg for a in node.args.args if a.arg != "self"]

        return {
            "name": name,
            "file": rel_path,
            "args": args[:8],
            "description": doc[:120],
            "is_exported": name in (all_names or set()),
        }

    def _extract_all(self, tree: ast.AST) -> set:
        """Extract __all__ = [...] from module."""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            names = set()
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    names.add(elt.value)
                            return names
        return set()

    def _detect_rest_endpoints(self) -> List[Dict[str, str]]:
        """Detect REST API endpoints from FastAPI/Flask decorator patterns."""
        endpoints: List[Dict[str, str]] = []
        http_methods = {"get", "post", "put", "patch", "delete", "head", "options"}

        for pyf in self.root.rglob("*.py"):
            if self._should_skip(pyf.relative_to(self.root)):
                continue
            if self._filter and not self._filter(pyf):
                continue

            try:
                code = pyf.read_text(errors="replace")
            except Exception:
                continue

            # Regex approach for speed — match @app.get("/path") or @router.post("/path")
            for m in re.finditer(
                r"@\w+\.(" + "|".join(http_methods) + r")\s*\(\s*['\"]([^'\"]+)['\"]",
                code,
            ):
                method = m.group(1).upper()
                path = m.group(2)
                endpoints.append({
                    "method": method,
                    "path": path,
                    "file": str(pyf.relative_to(self.root)),
                })

        return endpoints[:30]
