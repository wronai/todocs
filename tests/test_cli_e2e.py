"""E2E shell tests for CLI commands.

These tests run the actual CLI commands using subprocess to verify
they work end-to-end with real project structures.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def sample_project(tmp_path):
    """Create a minimal sample project structure."""
    project_dir = tmp_path / "sample_project"
    project_dir.mkdir()

    # Create pyproject.toml
    (project_dir / "pyproject.toml").write_text("""
[project]
name = "sample-project"
version = "1.0.0"
description = "A sample project for testing"
readme = "README.md"

[project.optional-dependencies]
dev = ["pytest"]
""")

    # Create README.md
    (project_dir / "README.md").write_text("""# Sample Project

This is a sample project for testing.

## Installation

pip install sample-project

## Usage

python -m sample_project
""")

    # Create a Python file
    src_dir = project_dir / "src" / "sample_project"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text('"""Sample project module."""\n__version__ = "1.0.0"\n')
    (src_dir / "main.py").write_text('"""Main module."""\ndef main():\n    print("Hello")\n')

    # Create a test file
    test_dir = project_dir / "tests"
    test_dir.mkdir()
    (test_dir / "test_main.py").write_text('"""Tests for main module."""\ndef test_main():\n    pass\n')

    return project_dir


@pytest.fixture
def sample_organization(tmp_path, sample_project):
    """Create a minimal organization with multiple projects."""
    org_dir = tmp_path / "organization"
    org_dir.mkdir()

    # Copy sample project as project1
    import shutil
    proj1 = org_dir / "project1"
    shutil.copytree(sample_project, proj1)
    (proj1 / "pyproject.toml").write_text("""
[project]
name = "project1"
version = "1.0.0"
description = "First test project"
""")

    # Create project2
    proj2 = org_dir / "project2"
    proj2.mkdir()
    (proj2 / "README.md").write_text("# Project 2\n\nSecond test project.")
    (proj2 / "package.json").write_text('{"name": "project2", "version": "2.0.0"}')

    return org_dir


class TestCLIInspect:
    """E2E tests for 'todocs inspect' command."""

    def test_inspect_markdown_output(self, sample_project, tmp_path):
        """Test inspect command with markdown output."""
        output_file = tmp_path / "output.md"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "inspect", str(sample_project),
                "--output", str(output_file),
                "--format", "markdown"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()
        content = output_file.read_text()
        assert "sample-project" in content or "Sample Project" in content

    def test_inspect_json_output(self, sample_project, tmp_path):
        """Test inspect command with JSON output."""
        output_file = tmp_path / "output.json"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "inspect", str(sample_project),
                "--output", str(output_file),
                "--format", "json"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()
        import json
        data = json.loads(output_file.read_text())
        assert "name" in data

    def test_inspect_stdout(self, sample_project):
        """Test inspect command writing to stdout."""
        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "inspect", str(sample_project),
                "--format", "markdown"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0
        assert "sample-project" in result.stdout or "Sample Project" in result.stdout


class TestCLIGenerate:
    """E2E tests for 'todocs generate' command."""

    def test_generate_articles(self, sample_organization, tmp_path):
        """Test generate command creates articles."""
        output_dir = tmp_path / "articles"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "generate", str(sample_organization),
                "--output", str(output_dir),
                "--org-name", "TestOrg"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_dir.exists()

        # Check for index file
        assert (output_dir / "_index.md").exists()

        # Check for project articles
        assert (output_dir / "project1.md").exists()

    def test_generate_with_json_report(self, sample_organization, tmp_path):
        """Test generate command with JSON report option."""
        output_dir = tmp_path / "articles"
        json_report = tmp_path / "report.json"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "generate", str(sample_organization),
                "--output", str(output_dir),
                "--json-report", str(json_report)
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert json_report.exists()
        import json
        data = json.loads(json_report.read_text())
        assert isinstance(data, list)
        assert len(data) >= 1


class TestCLICompare:
    """E2E tests for 'todocs compare' command."""

    def test_compare_multiple_projects(self, sample_organization, tmp_path):
        """Test compare command with multiple projects."""
        output_file = tmp_path / "comparison.md"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "compare", str(sample_organization),
                "--output", str(output_file),
                "--org-name", "TestOrg"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()
        content = output_file.read_text()
        assert "Comparison" in content or "comparison" in content.lower()

    def test_compare_insufficient_projects(self, sample_project, tmp_path):
        """Test compare command fails with single project."""
        output_file = tmp_path / "comparison.md"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "compare", str(sample_project.parent),
                "--output", str(output_file)
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode != 0 or "Need at least 2 projects" in result.stderr


class TestCLIHealth:
    """E2E tests for 'todocs health' command."""

    def test_health_report(self, sample_organization, tmp_path):
        """Test health command generates report."""
        output_file = tmp_path / "health.md"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "health", str(sample_organization),
                "--output", str(output_file),
                "--org-name", "TestOrg"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()
        content = output_file.read_text()
        assert "Health" in content or "health" in content.lower()


class TestCLIReadme:
    """E2E tests for 'todocs readme' command."""

    def test_readme_generation(self, sample_organization, tmp_path):
        """Test readme command generates single README."""
        output_file = tmp_path / "README.md"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "readme", str(sample_organization),
                "--output", str(output_file),
                "--org-name", "TestOrg",
                "--title", "Test Portfolio"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()
        content = output_file.read_text()
        assert "Test Portfolio" in content
        assert "project1" in content.lower()
        assert "## Summary" in content
        assert "## Projects" in content

    def test_readme_no_projects(self, tmp_path):
        """Test readme command with empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        output_file = tmp_path / "README.md"

        result = subprocess.run(
            [
                sys.executable, "-m", "todocs.cli",
                "readme", str(empty_dir),
                "--output", str(output_file)
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode != 0
        assert "No projects found" in result.stderr or "No projects found" in result.stdout


class TestCLIHelp:
    """E2E tests for CLI help commands."""

    def test_main_help(self):
        """Test main CLI help."""
        result = subprocess.run(
            [sys.executable, "-m", "todocs.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )

        assert result.returncode == 0
        assert "todocs" in result.stdout
        assert "generate" in result.stdout
        assert "inspect" in result.stdout
        assert "compare" in result.stdout
        assert "health" in result.stdout
        assert "readme" in result.stdout

    def test_subcommand_help(self):
        """Test subcommand help works for all commands."""
        commands = ["generate", "inspect", "compare", "health", "readme"]

        for cmd in commands:
            result = subprocess.run(
                [sys.executable, "-m", "todocs.cli", cmd, "--help"],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )
            assert result.returncode == 0, f"Help failed for {cmd}: {result.stderr}"
            assert "Usage:" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
