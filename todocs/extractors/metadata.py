"""Extract project metadata from pyproject.toml, setup.py, setup.cfg, package.json."""

from __future__ import annotations

import ast
import configparser
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    import tomli
except ImportError:
    try:
        import tomllib as tomli  # type: ignore
    except ImportError:
        tomli = None  # type: ignore


class MetadataExtractor:
    """Extract structured metadata from project config files."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

    def extract(self):
        from todocs.core import ProjectMetadata

        meta = ProjectMetadata(name=self.root.name)

        # Priority: pyproject.toml > setup.cfg > setup.py > package.json
        pyp = self._from_pyproject()
        if pyp:
            self._merge(meta, pyp)

        cfg = self._from_setup_cfg()
        if cfg:
            self._merge(meta, cfg)

        spy = self._from_setup_py()
        if spy:
            self._merge(meta, spy)

        pkg = self._from_package_json()
        if pkg:
            self._merge(meta, pkg)

        # Read VERSION file if present
        if not meta.version:
            vfile = self.root / "VERSION"
            if vfile.exists():
                try:
                    meta.version = vfile.read_text().strip()
                except Exception:
                    pass

        # Infer repo URL from project name if not set
        if not meta.repository:
            meta.repository = f"https://github.com/wronai/{meta.name}"

        return meta

    def _merge(self, target, source: Dict):
        """Merge source dict into target ProjectMetadata, only filling blanks."""
        for key, val in source.items():
            if val and hasattr(target, key):
                current = getattr(target, key)
                if not current or (isinstance(current, list) and len(current) == 0):
                    setattr(target, key, val)

    def _from_pyproject(self) -> Optional[Dict]:
        fp = self.root / "pyproject.toml"
        if not fp.exists() or tomli is None:
            return None
        try:
            data = tomli.loads(fp.read_text(errors="replace"))
        except Exception:
            return None

        proj = data.get("project", {})
        poetry = data.get("tool", {}).get("poetry", {})

        # Merge poetry into proj as fallback
        combined = {**poetry, **proj}

        meta = {}
        meta["name"] = combined.get("name", "")
        meta["version"] = combined.get("version", "")
        meta["description"] = combined.get("description", "")
        meta["license"] = self._extract_license(combined.get("license"))
        meta["keywords"] = combined.get("keywords", [])
        meta["python_requires"] = combined.get("requires-python", "")

        # Authors
        authors_raw = combined.get("authors", [])
        authors = []
        for a in authors_raw:
            if isinstance(a, dict):
                authors.append(a.get("name", ""))
            elif isinstance(a, str):
                authors.append(a)
        meta["authors"] = [a for a in authors if a]

        # URLs
        urls = combined.get("urls", {})
        meta["homepage"] = urls.get("Homepage", urls.get("homepage", ""))
        meta["repository"] = urls.get("Repository", urls.get("repository", ""))

        # Entry points
        scripts = combined.get("scripts", proj.get("scripts", {}))
        if isinstance(scripts, dict):
            meta["entry_points"] = scripts

        return meta

    def _from_setup_cfg(self) -> Optional[Dict]:
        fp = self.root / "setup.cfg"
        if not fp.exists():
            return None
        try:
            cfg = configparser.ConfigParser()
            cfg.read(str(fp))
        except Exception:
            return None

        if not cfg.has_section("metadata"):
            return None

        return {
            "name": cfg.get("metadata", "name", fallback=""),
            "version": cfg.get("metadata", "version", fallback=""),
            "description": cfg.get("metadata", "description", fallback=""),
            "license": cfg.get("metadata", "license", fallback=""),
            "authors": [cfg.get("metadata", "author", fallback="")] if cfg.get("metadata", "author", fallback="") else [],
        }

    def _from_setup_py(self) -> Optional[Dict]:
        fp = self.root / "setup.py"
        if not fp.exists():
            return None
        try:
            code = fp.read_text(errors="replace")
            tree = ast.parse(code)
        except Exception:
            return None

        # Find setup() call and extract keyword args
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = ""
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name == "setup":
                    return self._extract_setup_kwargs(node)
        return None

    def _extract_setup_kwargs(self, call_node: ast.Call) -> Dict:
        meta = {}
        for kw in call_node.keywords:
            if kw.arg in ("name", "version", "description", "license", "author"):
                if isinstance(kw.value, ast.Constant):
                    val = kw.value.value
                    if kw.arg == "author":
                        meta["authors"] = [str(val)]
                    else:
                        meta[kw.arg] = str(val)
        return meta

    def _from_package_json(self) -> Optional[Dict]:
        fp = self.root / "package.json"
        if not fp.exists():
            return None
        try:
            data = json.loads(fp.read_text(errors="replace"))
        except Exception:
            return None

        meta = {
            "name": data.get("name", ""),
            "version": data.get("version", ""),
            "description": data.get("description", ""),
            "license": data.get("license", ""),
            "homepage": data.get("homepage", ""),
            "repository": "",
            "keywords": data.get("keywords", []),
        }

        repo = data.get("repository", "")
        if isinstance(repo, dict):
            meta["repository"] = repo.get("url", "")
        elif isinstance(repo, str):
            meta["repository"] = repo

        author = data.get("author", "")
        if isinstance(author, str) and author:
            meta["authors"] = [author]
        elif isinstance(author, dict):
            meta["authors"] = [author.get("name", "")]

        return meta

    def _extract_license(self, lic_val) -> str:
        if isinstance(lic_val, str):
            return lic_val
        if isinstance(lic_val, dict):
            return lic_val.get("text", lic_val.get("id", ""))
        return ""
