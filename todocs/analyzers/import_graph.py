"""Build import dependency graph between project modules using AST."""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

_SKIP_DIRS = {
    "venv", ".venv", "env", "node_modules", "__pycache__", ".git",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".eggs", "htmlcov", "site",
}


class ImportGraphAnalyzer:
    """Analyze import relationships between project modules."""

    def __init__(self, project_path: Path, filter_func=None):
        self.root = Path(project_path)
        self._filter = filter_func

    def _should_skip(self, path: Path) -> bool:
        for part in path.parts:
            if part in _SKIP_DIRS or part.endswith(".egg-info"):
                return True
        return False

    def _iter_py_files(self):
        for p in self.root.rglob("*.py"):
            if self._should_skip(p.relative_to(self.root)):
                continue
            if self._filter and not self._filter(p):
                continue
            yield p

    def _module_name(self, path: Path) -> str:
        """Convert file path to dotted module name."""
        rel = path.relative_to(self.root)
        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].replace(".py", "")
        return ".".join(parts)

    def build_graph(self) -> Dict[str, Any]:
        """Build the import dependency graph.

        Returns:
            {
                "nodes": [{"name": "module.name", "lines": N, "is_test": bool}],
                "edges": [{"from": "a", "to": "b", "count": N}],
                "internal_packages": ["pkg1", "pkg2"],
                "external_imports": {"package": count},
                "cycles": [["a", "b", "a"]],
                "fan_in": {"module": N},   # how many modules import this
                "fan_out": {"module": N},  # how many modules this imports
            }
        """
        internal_pkgs = self._detect_internal_packages()
        modules: Dict[str, Dict[str, Any]] = {}
        edges: Dict[Tuple[str, str], int] = defaultdict(int)
        external_counts: Dict[str, int] = defaultdict(int)

        for pyf in self._iter_py_files():
            mod_name = self._module_name(pyf)
            rel_str = str(pyf.relative_to(self.root))

            try:
                code = pyf.read_text(errors="replace")
                lines = code.count("\n") + 1
            except Exception:
                lines = 0
                code = ""

            modules[mod_name] = {
                "name": mod_name,
                "lines": lines,
                "is_test": "test" in rel_str.lower(),
                "path": rel_str,
            }

            imported = self._parse_file_imports(pyf, code)
            for imp in imported:
                top_pkg = imp.split(".")[0]
                if top_pkg in internal_pkgs:
                    edges[(mod_name, imp)] += 1
                else:
                    external_counts[top_pkg] += 1

        edge_list, fan_in, fan_out = self._build_fan_metrics(edges)
        cycles = self._detect_cycles(edges)

        return {
            "nodes": list(modules.values()),
            "edges": edge_list,
            "internal_packages": sorted(internal_pkgs),
            "external_imports": dict(
                sorted(external_counts.items(), key=lambda x: -x[1])[:20]
            ),
            "cycles": cycles,
            "fan_in": dict(sorted(fan_in.items(), key=lambda x: -x[1])[:10]),
            "fan_out": dict(sorted(fan_out.items(), key=lambda x: -x[1])[:10]),
            "total_internal_edges": len(edge_list),
        }

    def _parse_file_imports(self, pyf: Path, code: str) -> List[str]:
        """Extract all imported module names from a Python source file."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        imported: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.append(node.module)
                elif node.level > 0:
                    imported.extend(self._resolve_relative_import(pyf, node))
        return imported

    def _resolve_relative_import(self, pyf: Path, node: ast.ImportFrom) -> List[str]:
        """Resolve a relative import node to an absolute module name."""
        parts = list(pyf.relative_to(self.root).parent.parts)
        if node.level > len(parts):
            return []
        base = ".".join(parts[: len(parts) - node.level + 1])
        if node.module:
            return [f"{base}.{node.module}"]
        return [base]

    @staticmethod
    def _build_fan_metrics(edges: Dict[Tuple[str, str], int]) -> tuple:
        """Build edge list and fan-in/fan-out dicts from raw edges."""
        fan_in: Dict[str, int] = defaultdict(int)
        fan_out: Dict[str, int] = defaultdict(int)
        edge_list = []
        for (src, dst), count in edges.items():
            fan_out[src] += 1
            fan_in[dst] += 1
            edge_list.append({"from": src, "to": dst, "count": count})
        return edge_list, fan_in, fan_out

    def _detect_internal_packages(self) -> Set[str]:
        """Detect top-level package directories in the project."""
        pkgs = set()
        for child in self.root.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                if child.name not in _SKIP_DIRS:
                    pkgs.add(child.name)
        # Also check for single-file modules in src/
        src = self.root / "src"
        if src.is_dir():
            for child in src.iterdir():
                if child.is_dir() and (child / "__init__.py").exists():
                    pkgs.add(child.name)
        return pkgs

    def _detect_cycles(self, edges: Dict[Tuple[str, str], int]) -> List[List[str]]:
        """Simple cycle detection (2-node mutual imports)."""
        adj: Dict[str, Set[str]] = defaultdict(set)
        for (src, dst) in edges:
            # Normalize: use top-level package for matching
            adj[src].add(dst)

        cycles = []
        seen = set()

        for a in adj:
            for b in adj[a]:
                if b in adj and a in adj[b]:
                    cycle = tuple(sorted([a, b]))
                    if cycle not in seen:
                        seen.add(cycle)
                        cycles.append([a, b, a])

        return cycles[:10]  # limit

    def get_hub_modules(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Identify hub modules (high fan-in or fan-out)."""
        graph = self.build_graph()
        fan_in = graph.get("fan_in", {})
        fan_out = graph.get("fan_out", {})

        all_modules = set(fan_in.keys()) | set(fan_out.keys())
        scored = []
        for mod in all_modules:
            fi = fan_in.get(mod, 0)
            fo = fan_out.get(mod, 0)
            scored.append({
                "module": mod,
                "fan_in": fi,
                "fan_out": fo,
                "hub_score": fi + fo,
            })

        scored.sort(key=lambda x: x["hub_score"], reverse=True)
        return scored[:top_n]
