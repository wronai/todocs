"""Shared test fixtures for todocs."""

import pytest


@pytest.fixture
def sample_project(tmp_path):
    """Create a realistic Python project for testing."""
    proj = tmp_path / "sample-project"
    proj.mkdir()

    (proj / "pyproject.toml").write_text("""
[project]
name = "sample-project"
version = "1.2.3"
description = "A sample project for testing todocs"
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = ["click>=8.0", "rich>=13.0", "pyyaml>=6.0"]
keywords = ["sample", "test"]

[project.optional-dependencies]
dev = ["pytest>=7.0", "black", "ruff"]

[project.scripts]
sample = "sample.cli:main"

[project.urls]
Homepage = "https://example.com"
Repository = "https://github.com/example/sample"
""")

    (proj / "README.md").write_text("""# Sample Project

A sample project for testing documentation generation.

## Installation

```bash
pip install sample-project
```

## Usage

```python
from sample import hello
hello()
```

## Features

- Feature one
- Feature two

## Architecture

The project uses a modular architecture.

## License

MIT
""")

    (proj / "CHANGELOG.md").write_text("""# Changelog

## [1.2.3] - 2025-03-01

### Added
- New feature X
- Improved Y

### Fixed
- Bug in Z

## [1.2.0] - 2025-02-15

### Added
- Initial release

## [1.0.0] - 2025-01-01

### Added
- Project created
""")

    # Source code
    src = proj / "sample"
    src.mkdir()
    (src / "__init__.py").write_text(
        '"""Sample package."""\n'
        '__version__ = "1.2.3"\n'
        '__all__ = ["Processor", "helper_function"]\n'
        'from sample.core import Processor, helper_function\n'
    )
    (src / "cli.py").write_text('''"""CLI module."""
import click

@click.group()
def main():
    """Run the sample CLI."""
    pass

@main.command()
@click.argument("name")
def greet(name):
    """Greet a user."""
    click.echo(f"Hello {name}!")

@main.command()
def version():
    """Show version."""
    click.echo("1.2.3")

if __name__ == "__main__":
    main()
''')
    (src / "core.py").write_text('''"""Core module with business logic."""

class Processor:
    """Main processor class for data transformation."""

    def __init__(self, config: dict):
        self.config = config
        self._cache = {}

    def process(self, data: list) -> dict:
        """Process input data and return results."""
        results = {}
        for item in data:
            if isinstance(item, str):
                results[item] = len(item)
            elif isinstance(item, (int, float)):
                results[str(item)] = item * 2
        return results

    def validate(self, data: list) -> bool:
        """Validate input data."""
        return all(isinstance(i, (str, int, float)) for i in data)

    def transform(self, data: dict) -> dict:
        """Transform data using config rules."""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = value.upper()
            else:
                result[key] = value
        return result


class DataLoader:
    """Load data from various sources."""

    def __init__(self, source_path: str):
        self.source_path = source_path

    def load_json(self):
        """Load from JSON file."""
        import json
        with open(self.source_path) as f:
            return json.load(f)

    def load_yaml(self):
        """Load from YAML file."""
        import yaml
        with open(self.source_path) as f:
            return yaml.safe_load(f)


def helper_function(x, y):
    """A helper function."""
    if x > y:
        return x - y
    elif x < y:
        return y - x
    else:
        return 0


def complex_function(data, threshold=10, mode="strict"):
    """A more complex function for testing CC detection."""
    result = []
    for item in data:
        if isinstance(item, dict):
            if "value" in item:
                val = item["value"]
                if val > threshold:
                    if mode == "strict":
                        result.append(val * 2)
                    elif mode == "lenient":
                        result.append(val)
                    else:
                        result.append(0)
                else:
                    result.append(val)
            elif "data" in item:
                result.extend(complex_function(item["data"], threshold, mode))
        elif isinstance(item, (int, float)):
            if item > threshold:
                result.append(item)
        elif isinstance(item, str):
            try:
                num = float(item)
                if num > threshold:
                    result.append(num)
            except ValueError:
                pass
    return result
''')
    (src / "utils.py").write_text('''"""Utility functions."""

import re
from pathlib import Path
from typing import List, Optional


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def find_files(root: Path, pattern: str = "*.py") -> List[Path]:
    """Find files matching pattern."""
    return sorted(root.rglob(pattern))


def read_safe(path: Path, encoding: str = "utf-8") -> Optional[str]:
    """Safely read a file, returning None on error."""
    try:
        return path.read_text(encoding=encoding)
    except Exception:
        return None
''')

    # Tests
    tests = proj / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    (tests / "test_core.py").write_text('''"""Tests for core module."""
import pytest
from sample.core import Processor, helper_function, complex_function

def test_processor_init():
    p = Processor({})
    assert p.config == {}

def test_process_strings():
    p = Processor({})
    result = p.process(["hello", "world"])
    assert result == {"hello": 5, "world": 5}

def test_process_numbers():
    p = Processor({})
    result = p.process([1, 2, 3])
    assert result == {"1": 2, "2": 4, "3": 6}

def test_validate():
    p = Processor({})
    assert p.validate(["a", 1, 2.0])
    assert not p.validate([None])

def test_helper():
    assert helper_function(5, 3) == 2
    assert helper_function(3, 5) == 2
    assert helper_function(3, 3) == 0

def test_complex_function():
    data = [{"value": 20}, {"value": 5}, 15, "25"]
    result = complex_function(data, threshold=10)
    assert 40 in result  # 20 * 2 in strict mode
    assert 5 in result
''')
    (tests / "test_utils.py").write_text('''"""Tests for utils module."""
from sample.utils import slugify, find_files

def test_slugify():
    assert slugify("Hello World") == "hello-world"
    assert slugify("  Foo  Bar  ") == "foo-bar"
''')

    # Infrastructure files
    (proj / "LICENSE").write_text("MIT License")
    (proj / "Makefile").write_text(""".PHONY: help test lint format clean

help:  ## Show this help
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort

test:  ## Run tests
\tpytest tests/ -v

lint:  ## Run linters
\truff check .

format:  ## Format code
\tblack .

clean:  ## Clean artifacts
\trm -rf dist/ build/ *.egg-info
""")
    (proj / "VERSION").write_text("1.2.3\n")
    (proj / ".gitignore").write_text("__pycache__/\n*.pyc\ndist/\n")
    (proj / "Dockerfile").write_text("""FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["sample", "greet", "World"]
""")
    (proj / "docker-compose.yml").write_text("""version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
volumes:
  data:
""")

    # Docs
    docs = proj / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Documentation\n\nWelcome.\n")

    # Examples
    examples = proj / "examples"
    examples.mkdir()
    (examples / "basic.py").write_text("from sample import Processor\np = Processor({})\n")

    # CI
    gh = proj / ".github" / "workflows"
    gh.mkdir(parents=True)
    (gh / "ci.yml").write_text("name: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n")

    return proj


@pytest.fixture
def js_project(tmp_path):
    """Create a JavaScript/Node.js project for testing."""
    proj = tmp_path / "js-app"
    proj.mkdir()

    (proj / "package.json").write_text("""{
  "name": "js-app",
  "version": "2.0.0",
  "description": "A JavaScript application",
  "license": "MIT",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}""")

    (proj / "README.md").write_text("# JS App\n\nA JavaScript application.\n\n## Usage\n\n```bash\nnpm start\n```\n")

    src = proj / "src"
    src.mkdir()
    (src / "index.js").write_text("const express = require('express');\nconst app = express();\napp.listen(3000);\n")
    (src / "routes.js").write_text("module.exports = { hello: (req, res) => res.send('hello') };\n")

    (proj / "Makefile").write_text("test:\n\tnpm test\n")

    return proj


@pytest.fixture
def empty_project(tmp_path):
    """Create a minimal empty project."""
    proj = tmp_path / "empty-proj"
    proj.mkdir()
    (proj / "README.md").write_text("# Empty\n\nNothing here yet.\n")
    return proj


@pytest.fixture
def multi_org(tmp_path):
    """Create a mini organization with 3 projects."""
    org = tmp_path / "org"
    org.mkdir()

    # Project A: Python CLI tool
    a = org / "tool-alpha"
    a.mkdir()
    (a / "pyproject.toml").write_text("""
[project]
name = "tool-alpha"
version = "0.5.0"
description = "Alpha CLI tool"
dependencies = ["click>=8.0"]

[project.scripts]
alpha = "alpha.cli:main"
""")
    (a / "README.md").write_text("# Tool Alpha\n\nA CLI tool.\n\n## Installation\n\n```bash\npip install tool-alpha\n```\n")
    (a / "CHANGELOG.md").write_text("# Changelog\n\n## [0.5.0] - 2025-06-01\n\n### Added\n- Feature one\n")
    (a / "LICENSE").write_text("MIT")
    (a / "Makefile").write_text("test:\n\tpytest\n")
    src_a = a / "alpha"
    src_a.mkdir()
    (src_a / "__init__.py").write_text('__version__ = "0.5.0"\n')
    (src_a / "cli.py").write_text('import click\n\n@click.command()\ndef main():\n    """Run alpha."""\n    pass\n')
    tests_a = a / "tests"
    tests_a.mkdir()
    (tests_a / "__init__.py").write_text("")
    (tests_a / "test_cli.py").write_text("def test_placeholder():\n    assert True\n")

    # Project B: Python library
    b = org / "lib-beta"
    b.mkdir()
    (b / "pyproject.toml").write_text("""
[project]
name = "lib-beta"
version = "1.0.0"
description = "Beta utility library"
dependencies = ["pyyaml>=6.0", "click>=8.0"]
""")
    (b / "README.md").write_text("# Lib Beta\n\nA utility library.\n\n## Features\n\n- Parsing\n- Formatting\n")
    (b / "LICENSE").write_text("Apache-2.0")
    src_b = b / "beta"
    src_b.mkdir()
    (src_b / "__init__.py").write_text('"""Beta library."""\n__version__ = "1.0.0"\n')
    (src_b / "parser.py").write_text('"""Parser module."""\n\nclass YAMLParser:\n    def parse(self, text):\n        pass\n\nclass JSONParser:\n    def parse(self, text):\n        pass\n')

    # Project C: Node.js app (no Python)
    c = org / "web-gamma"
    c.mkdir()
    (c / "package.json").write_text('{"name":"web-gamma","version":"3.1.0","description":"Gamma web app","dependencies":{"react":"^18.0"}}')
    (c / "README.md").write_text("# Web Gamma\n\nA React web application.\n")
    src_c = c / "src"
    src_c.mkdir()
    (src_c / "App.tsx").write_text("export default function App() { return <div>Hello</div>; }\n")

    return org
