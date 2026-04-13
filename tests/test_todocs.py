"""Tests for todocs core functionality."""

import json

import pytest

from todocs.core import scan_project, generate_articles
from todocs.extractors.metadata import MetadataExtractor
from todocs.extractors.readme_parser import ReadmeParser
from todocs.extractors.changelog_parser import ChangelogParser
from todocs.analyzers.structure import StructureAnalyzer
from todocs.analyzers.code_metrics import CodeMetricsAnalyzer
from todocs.analyzers.dependencies import DependencyAnalyzer


@pytest.fixture
def sample_project(tmp_path):
    """Create a minimal sample project for testing."""
    proj = tmp_path / "sample-project"
    proj.mkdir()

    # pyproject.toml
    (proj / "pyproject.toml").write_text("""
[project]
name = "sample-project"
version = "1.2.3"
description = "A sample project for testing todocs"
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = ["click>=8.0", "rich>=13.0"]
keywords = ["sample", "test"]

[project.optional-dependencies]
dev = ["pytest>=7.0"]

[project.scripts]
sample = "sample.cli:main"

[project.urls]
Homepage = "https://example.com"
Repository = "https://github.com/example/sample"
""")

    # README.md
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

## License

MIT
""")

    # CHANGELOG.md
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
""")

    # Source code
    src = proj / "sample"
    src.mkdir()
    (src / "__init__.py").write_text('"""Sample package."""\n__version__ = "1.2.3"\n')
    (src / "cli.py").write_text('''"""CLI module."""
import click

@click.command()
def main():
    """Run the sample CLI."""
    click.echo("Hello!")

if __name__ == "__main__":
    main()
''')
    (src / "core.py").write_text('''"""Core module with business logic."""

class Processor:
    """Main processor class."""

    def __init__(self, config: dict):
        self.config = config

    def process(self, data: list) -> dict:
        """Process input data."""
        results = {}
        for item in data:
            if isinstance(item, str):
                results[item] = len(item)
            elif isinstance(item, (int, float)):
                results[str(item)] = item * 2
        return results

    def validate(self, data: list) -> bool:
        """Validate input."""
        return all(isinstance(i, (str, int, float)) for i in data)

def helper_function(x, y):
    """A helper function."""
    if x > y:
        return x - y
    elif x < y:
        return y - x
    else:
        return 0
''')

    # Tests
    tests = proj / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    (tests / "test_core.py").write_text('''"""Tests for core module."""
import pytest
from sample.core import Processor, helper_function

def test_processor_init():
    p = Processor({})
    assert p.config == {}

def test_process_strings():
    p = Processor({})
    result = p.process(["hello", "world"])
    assert result == {"hello": 5, "world": 5}

def test_helper():
    assert helper_function(5, 3) == 2
    assert helper_function(3, 5) == 2
    assert helper_function(3, 3) == 0
''')

    # Other files
    (proj / "LICENSE").write_text("MIT License")
    (proj / "Makefile").write_text("test:\n\tpytest\n")
    (proj / "VERSION").write_text("1.2.3\n")
    (proj / ".gitignore").write_text("__pycache__/\n*.pyc\n")

    return proj


class TestMetadataExtractor:
    def test_extract_pyproject(self, sample_project):
        ext = MetadataExtractor(sample_project)
        meta = ext.extract()
        assert meta.name == "sample-project"
        assert meta.version == "1.2.3"
        assert meta.description == "A sample project for testing todocs"
        assert meta.license == "MIT"
        assert "sample" in str(meta.entry_points)

    def test_missing_project(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        ext = MetadataExtractor(empty)
        meta = ext.extract()
        assert meta.name == "empty"
        assert meta.version == ""


class TestReadmeParser:
    def test_parse_sections(self, sample_project):
        parser = ReadmeParser(sample_project)
        sections = parser.parse()
        assert "description" in sections
        assert "installation" in sections
        assert "usage" in sections
        assert "license" in sections

    def test_no_readme(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        parser = ReadmeParser(empty)
        assert parser.parse() == {}


class TestChangelogParser:
    def test_parse_entries(self, sample_project):
        parser = ChangelogParser(sample_project)
        entries = parser.parse()
        assert len(entries) == 2
        assert entries[0]["version"] == "1.2.3"
        assert entries[0]["date"] == "2025-03-01"
        assert entries[1]["version"] == "1.2.0"


class TestStructureAnalyzer:
    def test_analyze(self, sample_project):
        analyzer = StructureAnalyzer(sample_project)
        result = analyzer.analyze()
        assert result["total_files"] > 0
        assert result["has_tests"]

    def test_detect_tech_stack(self, sample_project):
        analyzer = StructureAnalyzer(sample_project)
        ts = analyzer.detect_tech_stack()
        assert ts.primary_language == "python"
        assert "pyproject" in ts.build_tools


class TestCodeMetrics:
    def test_analyze(self, sample_project):
        analyzer = CodeMetricsAnalyzer(sample_project)
        stats = analyzer.analyze()
        assert stats.source_files > 0
        assert stats.source_lines > 0
        assert stats.test_files > 0

    def test_key_modules(self, sample_project):
        analyzer = CodeMetricsAnalyzer(sample_project)
        modules = analyzer.get_key_modules(top_n=5)
        assert len(modules) > 0
        assert "path" in modules[0]
        assert "classes" in modules[0]


class TestDependencyAnalyzer:
    def test_runtime_deps(self, sample_project):
        analyzer = DependencyAnalyzer(sample_project)
        deps = analyzer.get_runtime_deps()
        assert "click" in deps
        assert "rich" in deps

    def test_dev_deps(self, sample_project):
        analyzer = DependencyAnalyzer(sample_project)
        deps = analyzer.get_dev_deps()
        assert "pytest" in deps


class TestScanProject:
    def test_full_scan(self, sample_project):
        profile = scan_project(sample_project)
        assert profile.name == "sample-project"
        assert profile.metadata.version == "1.2.3"
        assert profile.maturity.has_tests
        assert profile.maturity.has_license
        assert profile.maturity.has_makefile
        assert profile.code_stats.source_files > 0
        assert len(profile.dependencies) > 0

    def test_profile_serialization(self, sample_project):
        profile = scan_project(sample_project)
        data = profile.to_dict()
        assert "name" in data
        assert "metadata" in data
        json_str = profile.to_json()
        parsed = json.loads(json_str)
        assert parsed["name"] == "sample-project"


class TestGenerateArticles:
    def test_generate(self, sample_project, tmp_path):
        profile = scan_project(sample_project)
        out_dir = tmp_path / "articles"
        paths = generate_articles([profile], out_dir)
        assert len(paths) == 2  # index + 1 article
        assert (out_dir / "_index.md").exists()
        assert (out_dir / "sample-project.md").exists()

        # Check article content
        content = (out_dir / "sample-project.md").read_text()
        assert "---" in content  # frontmatter
        assert "sample-project" in content
        assert "## Technology Stack" in content
        assert "## Code Metrics" in content
        assert "## Maturity Assessment" in content

    def test_index_content(self, sample_project, tmp_path):
        profile = scan_project(sample_project)
        out_dir = tmp_path / "articles"
        generate_articles([profile], out_dir)
        index = (out_dir / "_index.md").read_text()
        assert "Project Portfolio" in index
        assert "sample-project" in index
