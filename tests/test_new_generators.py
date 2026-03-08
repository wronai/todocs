"""Tests for new generators: project_card_gen, status_report_gen, org_index_gen."""

import pytest
from pathlib import Path

from todocs.core import scan_project, scan_organization
from todocs.generators.project_card_gen import ProjectCardGenerator
from todocs.generators.status_report_gen import StatusReportGenerator
from todocs.generators.org_index_gen import OrgIndexGenerator


class TestProjectCardGenerator:
    def test_generate_single_card(self, sample_project, tmp_path):
        profile = scan_project(sample_project)
        out = tmp_path / "card.md"

        gen = ProjectCardGenerator(org_name="TestOrg")
        gen.generate(profile, out)

        content = out.read_text()
        assert "Project Card" in content
        assert "sample-project" in content
        assert "| Metric | Value |" in content
        assert "**Features:**" in content
        assert "**Dependencies:**" in content

    def test_generate_all_cards(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "cards"

        gen = ProjectCardGenerator()
        paths = gen.generate_all(profiles, out)

        assert len(paths) == len(profiles)
        for p in paths:
            assert p.exists()
            assert p.suffix == ".md"
            assert "-card.md" in p.name

    def test_card_frontmatter(self, sample_project, tmp_path):
        profile = scan_project(sample_project)
        out = tmp_path / "card.md"

        gen = ProjectCardGenerator()
        gen.generate(profile, out)

        content = out.read_text()
        assert "---" in content
        assert 'card_type: "project"' in content
        assert 'generated_by: "todocs"' in content

    def test_card_badges(self, sample_project):
        profile = scan_project(sample_project)
        gen = ProjectCardGenerator()
        card = gen.render_card(profile)

        assert "img.shields.io" in card
        assert "version-1.2.3" in card

    def test_card_features(self, sample_project):
        profile = scan_project(sample_project)
        gen = ProjectCardGenerator()
        card = gen.render_card(profile)

        # sample_project has tests, CI, Docker, docs
        assert "✅ tests" in card
        assert "✅ CI" in card
        assert "✅ Docker" in card

    def test_card_empty_project(self, empty_project, tmp_path):
        profile = scan_project(empty_project)
        out = tmp_path / "card.md"

        gen = ProjectCardGenerator()
        gen.generate(profile, out)

        content = out.read_text()
        assert "empty-proj" in content
        assert "❌" in content  # missing features


class TestStatusReportGenerator:
    def test_generate_report(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "status.md"

        gen = StatusReportGenerator(org_name="TestOrg")
        gen.generate(profiles, out)

        content = out.read_text()
        assert "Status Report" in content
        assert "KPI Dashboard" in content
        assert "Grade Breakdown" in content
        assert "Language Distribution" in content
        assert "Quality Gaps" in content
        assert "Largest Projects" in content

    def test_report_frontmatter(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "status.md"

        gen = StatusReportGenerator()
        gen.generate(profiles, out)

        content = out.read_text()
        assert "---" in content
        assert 'category: "Status"' in content
        assert f'project_count: {len(profiles)}' in content

    def test_kpi_values(self, multi_org):
        profiles = scan_organization(multi_org)
        gen = StatusReportGenerator(org_name="TestOrg")
        md = gen.render(profiles)

        assert "Total projects" in md
        assert "Total source lines" in md
        assert "Average maturity" in md
        assert "Projects with tests" in md

    def test_recommendations(self, multi_org):
        profiles = scan_organization(multi_org)
        gen = StatusReportGenerator()
        md = gen.render(profiles)

        # web-gamma has no tests, so we should get a recommendation
        if any(not p.maturity.has_tests for p in profiles):
            assert "Recommendations" in md
            assert "Add tests" in md

    def test_empty_profiles(self, tmp_path):
        out = tmp_path / "status.md"
        gen = StatusReportGenerator()
        gen.generate([], out)

        content = out.read_text()
        assert "Status Report" in content

    def test_recent_activity(self, multi_org):
        profiles = scan_organization(multi_org)
        gen = StatusReportGenerator()
        md = gen.render(profiles)

        # tool-alpha has a changelog
        active = [p for p in profiles if p.changelog_entries]
        if active:
            assert "Recent Activity" in md


class TestOrgIndexGenerator:
    def test_generate_index(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "index.md"

        gen = OrgIndexGenerator(org_name="TestOrg")
        gen.generate(profiles, out)

        content = out.read_text()
        assert "Project Index" in content
        assert "At a Glance" in content
        assert "Projects by Category" in content
        assert "Alphabetical Index" in content

    def test_index_frontmatter(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "index.md"

        gen = OrgIndexGenerator()
        gen.generate(profiles, out)

        content = out.read_text()
        assert "---" in content
        assert 'category: "Index"' in content

    def test_index_lists_all_projects(self, multi_org, tmp_path):
        profiles = scan_organization(multi_org)
        out = tmp_path / "index.md"

        gen = OrgIndexGenerator()
        gen.generate(profiles, out)

        content = out.read_text()
        for p in profiles:
            assert p.name in content

    def test_index_category_tables(self, multi_org):
        profiles = scan_organization(multi_org)
        gen = OrgIndexGenerator()
        md = gen.render(profiles)

        assert "| Project | Version | Language | SLOC | Grade |" in md

    def test_index_quick_stats(self, multi_org):
        profiles = scan_organization(multi_org)
        gen = OrgIndexGenerator()
        md = gen.render(profiles)

        assert f"**{len(profiles)}** projects" in md

    def test_index_empty(self, tmp_path):
        out = tmp_path / "index.md"
        gen = OrgIndexGenerator()
        gen.generate([], out)

        content = out.read_text()
        assert "**0** projects" in content
