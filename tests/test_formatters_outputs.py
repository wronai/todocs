"""Tests for table_formatter and output formats (HTML, JSON)."""

import json
import pytest
from pathlib import Path

from todocs.core import scan_project, scan_organization
from todocs.formatters.table_formatter import TableFormatter
from todocs.outputs.html import HTMLOutput
from todocs.outputs.json import JSONOutput
from todocs.outputs.markdown import MarkdownOutput


class TestTableFormatter:
    def test_format_comparison_default(self, multi_org):
        profiles = scan_organization(multi_org)
        fmt = TableFormatter()
        table = fmt.format_comparison(profiles)

        assert "| Project |" in table
        assert "| Version |" in table
        for p in profiles:
            assert p.name in table

    def test_format_comparison_sort_by_sloc(self, multi_org):
        profiles = scan_organization(multi_org)
        fmt = TableFormatter()
        table = fmt.format_comparison(profiles, sort_by="sloc", ascending=False)

        assert "| Project |" in table

    def test_format_comparison_limit(self, multi_org):
        profiles = scan_organization(multi_org)
        fmt = TableFormatter()
        table = fmt.format_comparison(profiles, limit=1)

        # Header + separator + 1 data row = 3 lines
        lines = [l for l in table.strip().split("\n") if l.startswith("|")]
        assert len(lines) == 3

    def test_format_comparison_custom_columns(self, multi_org):
        profiles = scan_organization(multi_org)
        fmt = TableFormatter()
        columns = [
            {"header": "Name", "getter": lambda p: p.name, "align": "left"},
            {"header": "Score", "getter": lambda p: f"{p.maturity.score:.0f}", "align": "right"},
        ]
        table = fmt.format_comparison(profiles, columns=columns)

        assert "| Name |" in table
        assert "| Score |" in table

    def test_format_matrix(self, multi_org):
        profiles = scan_organization(multi_org)
        fmt = TableFormatter()
        matrix = fmt.format_matrix(profiles)

        assert "| Project |" in matrix
        assert "Tests" in matrix
        assert "CI/CD" in matrix
        # Should contain check marks
        assert "✅" in matrix or "❌" in matrix

    def test_format_ranking(self, multi_org):
        profiles = scan_organization(multi_org)
        fmt = TableFormatter()
        ranking = fmt.format_ranking(profiles)

        assert "| # |" in ranking
        assert "| Project |" in ranking
        assert "| Score |" in ranking
        # First row should be rank 1
        assert "| 1 |" in ranking


class TestHTMLOutput:
    def test_write_html(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.html"

        writer = HTMLOutput(org_name="TestOrg")
        writer.write(profiles, out)

        content = out.read_text()
        assert "<!DOCTYPE html>" in content
        assert "TestOrg" in content
        assert "<table>" in content

    def test_html_contains_all_projects(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.html"

        writer = HTMLOutput()
        writer.write(profiles, out)

        content = out.read_text()
        for p in profiles:
            assert p.name in content

    def test_html_has_cards(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.html"

        writer = HTMLOutput()
        writer.write(profiles, out)

        content = out.read_text()
        assert "class='card'" in content or 'class="card"' in content

    def test_html_has_stats(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.html"

        writer = HTMLOutput()
        writer.write(profiles, out)

        content = out.read_text()
        assert "Projects" in content
        assert "Total SLOC" in content

    def test_html_single_project(self, sample_project, tmp_path):
        profile = scan_project(sample_project)
        out = tmp_path / "report.html"

        writer = HTMLOutput()
        writer.write([profile], out)

        content = out.read_text()
        assert "sample-project" in content


class TestJSONOutput:
    def test_write_json(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.json"

        writer = JSONOutput(org_name="TestOrg")
        writer.write(profiles, out)

        data = json.loads(out.read_text())
        assert "meta" in data
        assert "summary" in data
        assert "projects" in data

    def test_json_meta(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.json"

        writer = JSONOutput(org_name="TestOrg")
        writer.write(profiles, out)

        data = json.loads(out.read_text())
        meta = data["meta"]
        assert meta["org_name"] == "TestOrg"
        assert meta["generator"] == "todocs"
        assert meta["project_count"] == len(profiles)

    def test_json_summary(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.json"

        writer = JSONOutput()
        writer.write(profiles, out)

        data = json.loads(out.read_text())
        summary = data["summary"]
        assert "total_projects" in summary
        assert "total_source_lines" in summary
        assert "avg_maturity_score" in summary
        assert "categories" in summary
        assert "languages" in summary

    def test_json_project_entries(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "report.json"

        writer = JSONOutput()
        writer.write(profiles, out)

        data = json.loads(out.read_text())
        projects = data["projects"]
        assert len(projects) == len(profiles)

        for entry in projects:
            assert "name" in entry
            assert "metrics" in entry
            assert "maturity" in entry
            assert "tech_stack" in entry
            assert "dependencies" in entry

    def test_json_project_metrics(self, sample_project, tmp_path):
        profile = scan_project(sample_project)
        out = tmp_path / "report.json"

        writer = JSONOutput()
        writer.write([profile], out)

        data = json.loads(out.read_text())
        entry = data["projects"][0]
        metrics = entry["metrics"]
        assert "source_lines" in metrics
        assert "source_files" in metrics
        assert "avg_complexity" in metrics

        maturity = entry["maturity"]
        assert "score" in maturity
        assert "grade" in maturity
        assert isinstance(maturity["has_tests"], bool)

    def test_json_empty(self, tmp_path):
        out = tmp_path / "report.json"
        writer = JSONOutput()
        writer.write([], out)

        data = json.loads(out.read_text())
        assert data["meta"]["project_count"] == 0
        assert data["projects"] == []


class TestMarkdownOutput:
    def test_write_all_default(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "md_out"

        writer = MarkdownOutput(org_name="TestOrg")
        paths = writer.write_all(profiles, out)

        assert len(paths) >= len(profiles) + 1  # articles + at least index
        assert (out / "_index.md").exists()

    def test_write_all_with_cards(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "md_out"

        writer = MarkdownOutput()
        paths = writer.write_all(profiles, out, include_cards=True)

        card_files = [p for p in paths if "-card.md" in p.name]
        assert len(card_files) == len(profiles)

    def test_write_all_with_status(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "md_out"

        writer = MarkdownOutput()
        paths = writer.write_all(profiles, out, include_status=True)

        assert (out / "_status-report.md").exists()

    def test_write_all_includes_comparison(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "md_out"

        writer = MarkdownOutput()
        writer.write_all(profiles, out, include_comparison=True)

        assert (out / "_comparison.md").exists()

    def test_write_all_includes_health(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "md_out"

        writer = MarkdownOutput()
        writer.write_all(profiles, out, include_health=True)

        assert (out / "_health-report.md").exists()
