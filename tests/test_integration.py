"""Tests for comparison generator, CLI, and integration tests."""

import json
from click.testing import CliRunner

from todocs.core import scan_project, scan_organization, generate_articles
from todocs.generators.comparison import ComparisonGenerator
from todocs.cli import main

CONSTANT_3 = 3
PORT_4 = 4
CONSTANT_6 = 6
CONSTANT_50 = 50


# ── ComparisonGenerator ─────────────────────────────────────


class TestComparisonGenerator:
    def test_generate_comparison(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        assert len(profiles) >= 2

        out = tmp_path / "comparison.md"
        gen = ComparisonGenerator(org_name="TestOrg")
        gen.generate_comparison(profiles, out)

        content = out.read_text()
        assert "Cross-Project Comparison" in content
        assert "Size Comparison" in content
        assert "Maturity Leaderboard" in content
        assert "Technology Stack Overview" in content

    def test_generate_category_articles(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "cats"
        out.mkdir()

        gen = ComparisonGenerator()
        paths = gen.generate_category_articles(profiles, out)

        assert len(paths) >= 1
        for p in paths:
            assert p.exists()
            content = p.read_text()
            assert "Category Overview" in content

    def test_generate_health_report(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "health.md"

        gen = ComparisonGenerator(org_name="TestOrg")
        gen.generate_health_report(profiles, out)

        content = out.read_text()
        assert "Health Report" in content
        assert "Executive Summary" in content
        assert "Grade Distribution" in content
        assert "Projects Needing Attention" in content
        assert "Top Performers" in content

    def test_shared_dependencies(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "comp.md"

        gen = ComparisonGenerator()
        gen.generate_comparison(profiles, out)

        content = out.read_text()
        # click is a shared dependency between tool-alpha and lib-beta
        assert "Shared Dependencies" in content or "click" in content


# ── CLI Tests ───────────────────────────────────────────────


class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "todocs" in result.output
        assert "generate" in result.output
        assert "inspect" in result.output
        assert "compare" in result.output
        assert "health" in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.7" in result.output

    def test_inspect_json(self, sample_project):
        runner = CliRunner()
        result = runner.invoke(main, ["inspect", str(sample_project), "--format", "json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["name"] == "sample-project"
        assert data["metadata"]["version"] == "1.2.3"

    def test_inspect_markdown(self, sample_project):
        runner = CliRunner()
        result = runner.invoke(main, ["inspect", str(sample_project), "--format", "markdown"])
        assert result.exit_code == 0
        assert "# sample-project" in result.output
        assert "## Technology Stack" in result.output

    def test_inspect_to_file(self, sample_project, tmp_path):
        out = tmp_path / "output.md"
        runner = CliRunner()
        result = runner.invoke(main, ["inspect", str(sample_project), "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        assert "sample-project" in out.read_text()

    def test_generate(self, multi_org, tmp_path):
        out = tmp_path / "articles"
        runner = CliRunner()
        result = runner.invoke(main, ["generate", str(multi_org), "-o", str(out)])
        assert result.exit_code == 0
        assert out.is_dir()
        # Index + per-project articles + comparison + categories + health
        files = list(out.glob("*.md"))
        assert len(files) >= PORT_4  # at least index + 3 projects

    def test_generate_with_json_report(self, multi_org, tmp_path):
        out = tmp_path / "articles"
        report = tmp_path / "report.json"
        runner = CliRunner()
        result = runner.invoke(main, [
            "generate", str(multi_org),
            "-o", str(out),
            "--json-report", str(report),
        ])
        assert result.exit_code == 0
        assert report.exists()

        data = json.loads(report.read_text())
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_compare(self, multi_org, tmp_path):
        out = tmp_path / "comparison.md"
        runner = CliRunner()
        result = runner.invoke(main, ["compare", str(multi_org), "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()

    def test_health(self, multi_org, tmp_path):
        out = tmp_path / "health.md"
        runner = CliRunner()
        result = runner.invoke(main, ["health", str(multi_org), "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        assert "Health Report" in out.read_text()


# ── Integration Tests ───────────────────────────────────────


class TestIntegration:
    def test_full_pipeline_python(self, sample_project, tmp_path):
        """End-to-end: scan a Python project, generate article, verify content."""
        profile = scan_project(sample_project)

        # Verify all profile fields are populated
        assert profile.name == "sample-project"
        assert profile.metadata.version == "1.2.3"
        assert profile.metadata.description
        assert profile.tech_stack.primary_language == "python"
        assert profile.code_stats.source_files > 0
        assert profile.code_stats.source_lines > 0
        assert profile.code_stats.test_files > 0
        assert profile.maturity.score > 0
        assert profile.maturity.has_tests
        assert profile.maturity.has_license
        assert profile.maturity.has_ci
        assert profile.maturity.has_docs
        assert profile.maturity.has_changelog
        assert profile.maturity.has_docker
        assert profile.maturity.has_makefile
        assert len(profile.dependencies) > 0
        assert len(profile.dev_dependencies) > 0
        assert len(profile.changelog_entries) >= 2
        assert len(profile.key_modules) > 0
        assert len(profile.readme_sections) > 0

        # New v0.2 fields
        assert len(profile.makefile_targets) > 0
        assert profile.docker_info.get("has_dockerfile")
        assert profile.docker_info.get("has_compose")
        assert len(profile.import_graph.get("nodes", [])) > 0
        assert "cli_commands" in profile.api_surface

        # Generate article and verify
        out = tmp_path / "articles"
        paths = generate_articles([profile], out)
        article = (out / "sample-project.md").read_text()

        # Verify frontmatter
        assert "---" in article
        assert 'title: "sample-project' in article
        assert 'version: "1.2.3"' in article

        # Verify sections exist
        assert "## Overview" in article
        assert "## Technology Stack" in article
        assert "## Architecture & Key Modules" in article
        assert "## Code Metrics" in article
        assert "## Maturity Assessment" in article
        assert "## Dependencies" in article
        assert "## Recent Changes" in article
        assert "## Build Targets" in article
        assert "## Docker Infrastructure" in article

    def test_full_pipeline_js(self, js_project, tmp_path):
        """End-to-end: scan a JS project."""
        profile = scan_project(js_project)

        assert profile.name == "js-app"
        assert profile.metadata.version == "2.0.0"
        assert profile.tech_stack.primary_language == "javascript"
        assert "express" in profile.dependencies
        assert "jest" in profile.dev_dependencies

        out = tmp_path / "articles"
        paths = generate_articles([profile], out)
        assert (out / "js-app.md").exists()

    def test_full_pipeline_empty(self, empty_project, tmp_path):
        """End-to-end: minimal project still produces valid article."""
        profile = scan_project(empty_project)

        assert profile.name == "empty-proj"
        assert profile.maturity.score < CONSTANT_50  # Low maturity for empty project
        assert profile.code_stats.source_files == 0

        out = tmp_path / "articles"
        paths = generate_articles([profile], out)
        article = (out / "empty-proj.md").read_text()
        assert "## Maturity Assessment" in article

    def test_organization_scan(self, multi_org, tmp_path):
        """End-to-end: scan org with mixed Python/JS projects."""
        profiles = scan_organization(multi_org)

        assert len(profiles) == CONSTANT_3

        names = {p.name for p in profiles}
        assert "tool-alpha" in names
        assert "lib-beta" in names
        assert "web-gamma" in names

        # Verify categorization works
        categories = {p.category for p in profiles}
        assert len(categories) >= 1  # At least one category

        # Generate all articles
        out = tmp_path / "articles"
        paths = generate_articles(profiles, out)

        # Should have: index + 3 projects + comparison + health + category articles
        md_files = list(out.glob("*.md"))
        assert len(md_files) >= CONSTANT_6

        # Index should list all projects
        index = (out / "_index.md").read_text()
        assert "tool-alpha" in index
        assert "lib-beta" in index
        assert "web-gamma" in index

        # Comparison should exist
        comp = out / "_comparison.md"
        assert comp.exists()
        assert "Cross-Project Comparison" in comp.read_text()

        # Health report should exist
        health = out / "_health-report.md"
        assert health.exists()
        assert "Health Report" in health.read_text()

    def test_profile_serialization_roundtrip(self, sample_project):
        """Verify JSON serialization/deserialization."""
        profile = scan_project(sample_project)

        json_str = profile.to_json()
        data = json.loads(json_str)

        # All fields present
        assert data["name"] == "sample-project"
        assert data["metadata"]["version"] == "1.2.3"
        assert isinstance(data["tech_stack"]["languages"], dict)
        assert isinstance(data["code_stats"]["hotspots"], list)
        assert isinstance(data["makefile_targets"], list)
        assert isinstance(data["docker_info"], dict)
        assert isinstance(data["import_graph"], dict)
        assert isinstance(data["api_surface"], dict)

    def test_exclude_directories(self, multi_org):
        """Test that exclude parameter works."""
        all_profiles = scan_organization(multi_org)
        filtered = scan_organization(multi_org, exclude=["web-gamma"])

        assert len(filtered) == len(all_profiles) - 1
        assert all(p.name != "web-gamma" for p in filtered)

    def test_article_frontmatter_valid(self, sample_project, tmp_path):
        """Verify YAML frontmatter is parseable."""
        import yaml

        profile = scan_project(sample_project)
        out = tmp_path / "articles"
        generate_articles([profile], out)

        content = (out / "sample-project.md").read_text()

        # Extract frontmatter between --- markers
        parts = content.split("---")
        assert len(parts) >= CONSTANT_3, "Should have YAML frontmatter"

        frontmatter = parts[1].strip()
        data = yaml.safe_load(frontmatter)

        assert data["title"]
        assert data["slug"]
        assert data["date"]
        assert data["category"]
        assert data["version"]
        assert data["maturity_grade"]
        assert isinstance(data["maturity_score"], (int, float))
        assert data["generated_by"] == "todocs v0.1.0"
