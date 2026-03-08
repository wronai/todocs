"""Analyze project directory structure and detect technology stack."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

# Import locally to handle the TechStack dataclass from core
# We'll do a lazy import to avoid circular deps


_LANG_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".php": "php",
    ".rb": "ruby",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".sh": "shell",
    ".bash": "shell",
}

_SKIP_DIRS = {
    "venv", ".venv", "env", "node_modules", "__pycache__", ".git",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".eggs", "*.egg-info", "htmlcov", "coverage",
    "site", ".idea", ".vscode",
}

_FRAMEWORK_MARKERS = {
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],
    "click": ["click"],
    "typer": ["typer"],
    "tauri": ["src-tauri"],
    "react": ["react"],
    "vue": ["vue"],
    "express": ["express"],
    "nextjs": ["next.config.js", "next.config.ts"],
}

_BUILD_TOOL_FILES = {
    "Makefile": "make",
    "Taskfile.yml": "taskfile",
    "pyproject.toml": "pyproject",
    "setup.py": "setuptools",
    "setup.cfg": "setuptools",
    "poetry.lock": "poetry",
    "Cargo.toml": "cargo",
    "package.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "composer.json": "composer",
}

_TEST_FRAMEWORK_FILES = {
    "pytest.ini": "pytest",
    "conftest.py": "pytest",
    "jest.config.js": "jest",
    "jest.config.ts": "jest",
    "playwright.config.ts": "playwright",
    "playwright.config.js": "playwright",
    "tox.ini": "tox",
}

_CI_FILES = {
    ".github/workflows": "github-actions",
    ".gitlab-ci.yml": "gitlab-ci",
    ".travis.yml": "travis-ci",
    "Jenkinsfile": "jenkins",
    ".circleci": "circleci",
}

_DOCKER_FILES = {
    "Dockerfile": "docker",
    "docker-compose.yml": "docker-compose",
    "docker-compose.yaml": "docker-compose",
}


class StructureAnalyzer:
    """Analyze project directory structure."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

    def _should_skip(self, path: Path) -> bool:
        for part in path.parts:
            if part in _SKIP_DIRS or part.endswith(".egg-info"):
                return True
        return False

    def _iter_files(self):
        for p in self.root.rglob("*"):
            if p.is_file() and not self._should_skip(p.relative_to(self.root)):
                yield p

    def analyze(self) -> Dict[str, Any]:
        """Return structure summary."""
        dirs = set()
        files_by_type: Dict[str, int] = Counter()
        total_files = 0

        for p in self._iter_files():
            total_files += 1
            ext = p.suffix.lower()
            files_by_type[ext] += 1
            rel = p.relative_to(self.root)
            if len(rel.parts) > 1:
                dirs.add(rel.parts[0])

        top_dirs = sorted(dirs)
        has_src = any(d in top_dirs for d in ["src", self.root.name])
        has_tests = "tests" in top_dirs or "test" in top_dirs
        has_docs = "docs" in top_dirs or "doc" in top_dirs
        has_examples = "examples" in top_dirs or "example" in top_dirs

        return {
            "total_files": total_files,
            "top_dirs": top_dirs,
            "file_types": dict(files_by_type.most_common(20)),
            "has_src_dir": has_src,
            "has_tests": has_tests,
            "has_docs": has_docs,
            "has_examples": has_examples,
        }

    def detect_tech_stack(self):
        """Detect technology stack from files and markers."""
        from todocs.core import TechStack

        lang_counts: Counter = Counter()
        frameworks: List[str] = []
        build_tools: List[str] = []
        test_fws: List[str] = []
        ci_cd: List[str] = []
        containers: List[str] = []

        for p in self._iter_files():
            ext = p.suffix.lower()
            if ext in _LANG_EXTENSIONS:
                lang_counts[_LANG_EXTENSIONS[ext]] += 1

        # Build tools
        for fname, tool in _BUILD_TOOL_FILES.items():
            if (self.root / fname).exists():
                build_tools.append(tool)

        # Test frameworks
        for fname, fw in _TEST_FRAMEWORK_FILES.items():
            if (self.root / fname).exists():
                test_fws.append(fw)
        # Also check for tests/ with pytest convention
        tests_dir = self.root / "tests"
        if tests_dir.is_dir() and any(tests_dir.glob("test_*.py")):
            if "pytest" not in test_fws:
                test_fws.append("pytest")

        # CI/CD
        for path_str, ci in _CI_FILES.items():
            if (self.root / path_str).exists():
                ci_cd.append(ci)

        # Docker
        for fname, dock in _DOCKER_FILES.items():
            if (self.root / fname).exists():
                containers.append(dock)

        # Frameworks (check pyproject.toml deps + directory markers)
        dep_text = self._read_deps_text()
        for fw_name, markers in _FRAMEWORK_MARKERS.items():
            for marker in markers:
                if (self.root / marker).exists() or marker in dep_text:
                    frameworks.append(fw_name)
                    break

        primary = lang_counts.most_common(1)[0][0] if lang_counts else "unknown"

        return TechStack(
            primary_language=primary,
            languages=dict(lang_counts),
            frameworks=list(set(frameworks)),
            build_tools=list(set(build_tools)),
            test_frameworks=list(set(test_fws)),
            ci_cd=list(set(ci_cd)),
            containerization=list(set(containers)),
        )

    def _read_deps_text(self) -> str:
        """Read dependency names from pyproject.toml/requirements.txt as raw text."""
        texts = []
        for fname in ["pyproject.toml", "requirements.txt", "package.json"]:
            fp = self.root / fname
            if fp.exists():
                try:
                    texts.append(fp.read_text(errors="replace"))
                except Exception:
                    pass
        return "\n".join(texts).lower()
