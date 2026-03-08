"""Tests for new CLI commands: status, cards, index, export."""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner

from todocs.cli import main


class TestCLIStatus:
    def test_status_command(self, multi_org, tmp_path):
        out = tmp_path / "status.md"
        runner = CliRunner()
        result = runner.invoke(main, ["status", str(multi_org), "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        assert "Status Report" in out.read_text()

    def test_status_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["status", "--help"])
        assert result.exit_code == 0
        assert "status report" in result.output.lower()

    def test_status_with_org_name(self, multi_org, tmp_path):
        out = tmp_path / "status.md"
        runner = CliRunner()
        result = runner.invoke(main, [
            "status", str(multi_org), "-o", str(out), "--org-name", "MyOrg"
        ])
        assert result.exit_code == 0
        assert "MyOrg" in out.read_text()


class TestCLICards:
    def test_cards_command(self, multi_org, tmp_path):
        out = tmp_path / "cards"
        runner = CliRunner()
        result = runner.invoke(main, ["cards", str(multi_org), "-o", str(out)])
        assert result.exit_code == 0
        assert out.is_dir()

        card_files = list(out.glob("*-card.md"))
        assert len(card_files) >= 2

    def test_cards_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["cards", "--help"])
        assert result.exit_code == 0
        assert "project cards" in result.output.lower()


class TestCLIIndex:
    def test_index_command(self, multi_org, tmp_path):
        out = tmp_path / "index.md"
        runner = CliRunner()
        result = runner.invoke(main, ["index", str(multi_org), "-o", str(out)])
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text()
        assert "Project Index" in content
        assert "tool-alpha" in content

    def test_index_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["index", "--help"])
        assert result.exit_code == 0
        assert "index" in result.output.lower()

    def test_index_no_projects(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        runner = CliRunner()
        result = runner.invoke(main, ["index", str(empty_dir)])
        assert result.exit_code != 0


class TestCLIExport:
    def test_export_html(self, multi_org, tmp_path):
        out = tmp_path / "report.html"
        runner = CliRunner()
        result = runner.invoke(main, [
            "export", str(multi_org), "--format", "html", "-o", str(out)
        ])
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text()
        assert "<!DOCTYPE html>" in content

    def test_export_json(self, multi_org, tmp_path):
        out = tmp_path / "report.json"
        runner = CliRunner()
        result = runner.invoke(main, [
            "export", str(multi_org), "--format", "json", "-o", str(out)
        ])
        assert result.exit_code == 0
        assert out.exists()

        data = json.loads(out.read_text())
        assert "meta" in data
        assert "projects" in data

    def test_export_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["export", "--help"])
        assert result.exit_code == 0
        assert "html" in result.output.lower()
        assert "json" in result.output.lower()

    def test_export_no_projects(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        out = tmp_path / "report.html"
        runner = CliRunner()
        result = runner.invoke(main, [
            "export", str(empty_dir), "--format", "html", "-o", str(out)
        ])
        assert result.exit_code != 0

    def test_export_json_contains_all_projects(self, multi_org, tmp_path):
        out = tmp_path / "report.json"
        runner = CliRunner()
        result = runner.invoke(main, [
            "export", str(multi_org), "--format", "json", "-o", str(out)
        ])
        assert result.exit_code == 0

        data = json.loads(out.read_text())
        names = {p["name"] for p in data["projects"]}
        assert "tool-alpha" in names
        assert "lib-beta" in names
        assert "web-gamma" in names
