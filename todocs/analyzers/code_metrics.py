"""Code metrics analyzer using Python AST and radon for cyclomatic complexity."""

from __future__ import annotations

import ast
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from radon.complexity import cc_visit, cc_rank
    from radon.metrics import mi_visit

    HAS_RADON = True
except ImportError:
    HAS_RADON = False

_SKIP_DIRS = {
    "venv", ".venv", "env", "node_modules", "__pycache__", ".git",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".eggs", "htmlcov", "site", ".idea", ".vscode",
}

_SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".rs", ".go", ".php", ".java", ".c", ".cpp", ".rb"}
_TEST_PATTERNS = {"test_", "_test.py", "tests/", "test/", "spec/"}


class CodeMetricsAnalyzer:
    """Analyze code metrics: lines, complexity, maintainability."""

    def __init__(self, project_path: Path, filter_func=None):
        self.root = Path(project_path)
        self._filter = filter_func
        self._py_files: List[Path] = []
        self._all_source: List[Path] = []
        self._test_files: List[Path] = []
        self._modules: List[Dict[str, Any]] = []
        self._scanned = False

    def _should_skip(self, path: Path) -> bool:
        for part in path.parts:
            if part in _SKIP_DIRS or part.endswith(".egg-info"):
                return True
        return False

    def _is_test(self, path: Path) -> bool:
        rel = str(path.relative_to(self.root))
        return any(pat in rel for pat in _TEST_PATTERNS)

    def _scan(self):
        if self._scanned:
            return
        for p in self.root.rglob("*"):
            if not p.is_file():
                continue
            if self._should_skip(p.relative_to(self.root)):
                continue
            if self._filter and not self._filter(p):
                continue
            ext = p.suffix.lower()
            if ext in _SOURCE_EXTENSIONS:
                self._all_source.append(p)
                if self._is_test(p):
                    self._test_files.append(p)
                if ext == ".py":
                    self._py_files.append(p)
        self._scanned = True

    def _count_lines(self, path: Path) -> int:
        try:
            return sum(1 for _ in path.open("r", errors="replace"))
        except Exception:
            return 0

    def analyze(self):
        """Return CodeStats dataclass."""
        from todocs.core import CodeStats

        self._scan()

        total_files = len(self._all_source)
        test_files = len(self._test_files)
        source_files = total_files - test_files

        source_lines = sum(self._count_lines(f) for f in self._all_source if f not in set(self._test_files))
        test_lines = sum(self._count_lines(f) for f in self._test_files)
        total_lines = source_lines + test_lines

        # Complexity via radon (Python files only)
        complexities = []
        hotspots = []
        mi_scores = []

        for pyf in self._py_files:
            if self._is_test(pyf):
                continue
            try:
                code = pyf.read_text(errors="replace")
            except Exception:
                continue

            if HAS_RADON:
                try:
                    blocks = cc_visit(code)
                    for block in blocks:
                        complexities.append(block.complexity)
                        if block.complexity > 10:
                            hotspots.append({
                                "file": str(pyf.relative_to(self.root)),
                                "name": block.name,
                                "type": block.letter,
                                "complexity": block.complexity,
                                "rank": cc_rank(block.complexity),
                                "line": block.lineno,
                            })
                except Exception:
                    pass

                try:
                    mi = mi_visit(code, multi=True)
                    mi_scores.append(mi)
                except Exception:
                    pass
            else:
                # Fallback: count branches via AST
                try:
                    tree = ast.parse(code)
                    cc = self._ast_complexity(tree)
                    complexities.append(cc)
                except Exception:
                    pass

        avg_cc = sum(complexities) / len(complexities) if complexities else 0.0
        max_cc = max(complexities) if complexities else 0.0
        avg_mi = sum(mi_scores) / len(mi_scores) if mi_scores else 0.0

        hotspots.sort(key=lambda h: h.get("complexity", 0), reverse=True)

        return CodeStats(
            total_files=total_files,
            total_lines=total_lines,
            source_files=source_files,
            source_lines=source_lines,
            test_files=test_files,
            test_lines=test_lines,
            avg_complexity=round(avg_cc, 2),
            max_complexity=max_cc,
            hotspots=hotspots[:10],
            maintainability_index=round(avg_mi, 2),
        )

    def _ast_complexity(self, tree: ast.AST) -> int:
        """Simple cyclomatic complexity estimate via AST node counting."""
        cc = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                  ast.With, ast.Assert, ast.comprehension)):
                cc += 1
            elif isinstance(node, ast.BoolOp):
                cc += len(node.values) - 1
        return cc

    def _parse_module_ast(self, code: str) -> tuple:
        """Parse AST and extract classes, functions, imports, and docstring.

        Returns: (classes, functions, imports, docstring)
        """
        classes = []
        functions = []
        imports = []
        docstring = ""

        try:
            tree = ast.parse(code)

            # Module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant)):
                val = tree.body[0].value
                docstring = str(getattr(val, "value", ""))

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    classes.append({"name": node.name, "methods": methods, "line": node.lineno})
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Only top-level functions
                    if hasattr(node, "col_offset") and node.col_offset == 0:
                        functions.append({"name": node.name, "line": node.lineno})
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
        except SyntaxError:
            pass

        return classes, functions, imports, docstring

    def _extract_module_info(self, pyf: Path) -> Dict[str, Any] | None:
        """Extract information from a single Python file.

        Returns module dict or None if extraction fails.
        """
        if self._is_test(pyf):
            return None

        try:
            code = pyf.read_text(errors="replace")
            lines = code.count("\n") + 1
        except Exception:
            return None

        classes, functions, imports, docstring = self._parse_module_ast(code)

        rel_path = str(pyf.relative_to(self.root))
        return {
            "path": rel_path,
            "lines": lines,
            "classes": classes,
            "functions": functions,
            "imports": imports[:20],
            "docstring": (docstring[:200] + "...") if len(docstring) > 200 else docstring,
        }

    def get_key_modules(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Return the top N most significant Python modules by size and complexity."""
        self._scan()
        modules = []

        for pyf in self._py_files:
            module_info = self._extract_module_info(pyf)
            if module_info:
                modules.append(module_info)

        # Sort by lines descending
        modules.sort(key=lambda m: m["lines"], reverse=True)
        return modules[:top_n]
