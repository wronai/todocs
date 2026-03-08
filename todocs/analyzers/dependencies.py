"""Dependency extraction from pyproject.toml, setup.py, requirements.txt, package.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional

try:
    import tomli
except ImportError:
    try:
        import tomllib as tomli  # Python 3.11+
    except ImportError:
        tomli = None  # type: ignore


class DependencyAnalyzer:
    """Extract project dependencies without executing anything."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)
        self._pyproject: Optional[dict] = None
        self._loaded = False

    def _load_pyproject(self) -> dict:
        if self._loaded:
            return self._pyproject or {}
        self._loaded = True

        fp = self.root / "pyproject.toml"
        if not fp.exists() or tomli is None:
            return {}

        try:
            self._pyproject = tomli.loads(fp.read_text(errors="replace"))
        except Exception:
            self._pyproject = {}
        return self._pyproject or {}

    def _parse_dep_name(self, dep: str) -> str:
        """Extract package name from a dependency spec like 'foo>=1.0; python_version<3.11'."""
        dep = dep.strip()
        # Handle extras: foo[extra]
        m = re.match(r"^([A-Za-z0-9_.-]+)", dep)
        return m.group(1) if m else dep

    def get_runtime_deps(self) -> List[str]:
        """Get runtime dependencies."""
        deps: List[str] = []

        # From pyproject.toml
        pyp = self._load_pyproject()
        proj_deps = pyp.get("project", {}).get("dependencies", [])
        deps.extend(self._parse_dep_name(d) for d in proj_deps)

        # Poetry format
        poetry_deps = pyp.get("tool", {}).get("poetry", {}).get("dependencies", {})
        for name in poetry_deps:
            if name.lower() != "python":
                deps.append(name)

        # From requirements.txt
        req_file = self.root / "requirements.txt"
        if req_file.exists():
            try:
                for line in req_file.read_text(errors="replace").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        name = self._parse_dep_name(line)
                        if name and name not in deps:
                            deps.append(name)
            except Exception:
                pass

        # From package.json
        pkg_json = self.root / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(errors="replace"))
                for name in data.get("dependencies", {}):
                    deps.append(name)
            except Exception:
                pass

        # Deduplicate preserving order
        seen = set()
        unique = []
        for d in deps:
            dl = d.lower()
            if dl not in seen:
                seen.add(dl)
                unique.append(d)
        return unique

    def get_dev_deps(self) -> List[str]:
        """Get development dependencies."""
        deps: List[str] = []

        pyp = self._load_pyproject()

        # From [project.optional-dependencies] dev/test
        opt = pyp.get("project", {}).get("optional-dependencies", {})
        for group in ["dev", "test", "testing", "development"]:
            for d in opt.get(group, []):
                deps.append(self._parse_dep_name(d))

        # Poetry dev-dependencies
        poetry_dev = pyp.get("tool", {}).get("poetry", {}).get("dev-dependencies", {})
        for name in poetry_dev:
            deps.append(name)

        # Poetry group.dev
        groups = pyp.get("tool", {}).get("poetry", {}).get("group", {})
        dev_group = groups.get("dev", {}).get("dependencies", {})
        for name in dev_group:
            deps.append(name)

        # requirements-dev.txt
        for fname in ["requirements-dev.txt", "requirements-test.txt"]:
            fp = self.root / fname
            if fp.exists():
                try:
                    for line in fp.read_text(errors="replace").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and not line.startswith("-"):
                            name = self._parse_dep_name(line)
                            if name:
                                deps.append(name)
                except Exception:
                    pass

        # package.json devDependencies
        pkg_json = self.root / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(errors="replace"))
                for name in data.get("devDependencies", {}):
                    deps.append(name)
            except Exception:
                pass

        seen = set()
        unique = []
        for d in deps:
            dl = d.lower()
            if dl not in seen:
                seen.add(dl)
                unique.append(d)
        return unique
