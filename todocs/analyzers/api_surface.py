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

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

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

        # Focus on __init__.py files and non-test modules
        target_files = []
        for pyf in self.root.rglob("__init__.py"):
            if not self._should_skip(pyf.relative_to(self.root)):
                target_files.append(pyf)

        # Also scan top-level source modules (not tests)
        for pyf in self.root.rglob("*.py"):
            if self._should_skip(pyf.relative_to(self.root)):
                continue
            if "test" in pyf.name.lower():
                continue
            rel = pyf.relative_to(self.root)
            # Only 1-2 level deep files
            if len(rel.parts) <= 3:
                target_files.append(pyf)

        seen_classes = set()
        seen_funcs = set()

        for pyf in target_files:
            try:
                code = pyf.read_text(errors="replace")
                tree = ast.parse(code)
            except Exception:
                continue

            rel = str(pyf.relative_to(self.root))

            # Check __all__ for explicit exports
            all_names = self._extract_all(tree)

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    name = node.name
                    if name.startswith("_") and name not in (all_names or []):
                        continue
                    if name in seen_classes:
                        continue
                    seen_classes.add(name)

                    doc = ast.get_docstring(node) or ""
                    methods = [
                        n.name for n in node.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and not n.name.startswith("_")
                    ]

                    classes.append({
                        "name": name,
                        "file": rel,
                        "methods": methods[:10],
                        "method_count": len(methods),
                        "description": doc[:120],
                        "is_exported": name in (all_names or set()),
                    })

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = node.name
                    if name.startswith("_"):
                        continue
                    if name in seen_funcs:
                        continue
                    seen_funcs.add(name)

                    doc = ast.get_docstring(node) or ""
                    args = [
                        a.arg for a in node.args.args
                        if a.arg != "self"
                    ]

                    functions.append({
                        "name": name,
                        "file": rel,
                        "args": args[:8],
                        "description": doc[:120],
                        "is_exported": name in (all_names or set()),
                    })

        return classes[:20], functions[:20]

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
