"""Tests for new analyzers: import_graph, api_surface."""

import pytest
from pathlib import Path

from todocs.analyzers.import_graph import ImportGraphAnalyzer
from todocs.analyzers.api_surface import APISurfaceAnalyzer


class TestImportGraphAnalyzer:
    def test_build_graph(self, sample_project):
        ig = ImportGraphAnalyzer(sample_project)
        graph = ig.build_graph()

        assert "nodes" in graph
        assert "edges" in graph
        assert "external_imports" in graph
        assert "cycles" in graph
        assert "fan_in" in graph
        assert "fan_out" in graph

        # Should find some Python modules
        assert len(graph["nodes"]) > 0

        # Check node structure
        node = graph["nodes"][0]
        assert "name" in node
        assert "lines" in node
        assert "is_test" in node
        assert "path" in node

        # Should detect external imports
        ext = graph["external_imports"]
        assert isinstance(ext, dict)

    def test_graph_separates_tests(self, sample_project):
        ig = ImportGraphAnalyzer(sample_project)
        graph = ig.build_graph()

        test_nodes = [n for n in graph["nodes"] if n["is_test"]]
        src_nodes = [n for n in graph["nodes"] if not n["is_test"]]

        assert len(test_nodes) > 0, "Should have test nodes"
        assert len(src_nodes) > 0, "Should have source nodes"

    def test_hub_modules(self, sample_project):
        ig = ImportGraphAnalyzer(sample_project)
        hubs = ig.get_hub_modules(top_n=3)

        assert isinstance(hubs, list)
        if hubs:
            assert "module" in hubs[0]
            assert "fan_in" in hubs[0]
            assert "fan_out" in hubs[0]
            assert "hub_score" in hubs[0]

    def test_empty_project(self, tmp_path):
        proj = tmp_path / "empty"
        proj.mkdir()
        ig = ImportGraphAnalyzer(proj)
        graph = ig.build_graph()
        assert graph["nodes"] == []
        assert graph["edges"] == []

    def test_cycle_detection(self, tmp_path):
        """Test that mutual imports are detected as cycles."""
        proj = tmp_path / "cyclic"
        proj.mkdir()
        pkg = proj / "mypkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "a.py").write_text("from mypkg.b import something\n")
        (pkg / "b.py").write_text("from mypkg.a import other\n")

        ig = ImportGraphAnalyzer(proj)
        graph = ig.build_graph()

        # The edge targets resolve to mypkg.b and mypkg.a respectively,
        # so a mutual import cycle is detected
        assert len(graph["cycles"]) > 0, "Should detect the a ↔ b cycle"

    def test_internal_package_detection(self, sample_project):
        ig = ImportGraphAnalyzer(sample_project)
        pkgs = ig._detect_internal_packages()
        assert "sample" in pkgs


class TestAPISurfaceAnalyzer:
    def test_analyze(self, sample_project):
        api = APISurfaceAnalyzer(sample_project)
        result = api.analyze()

        assert "cli_commands" in result
        assert "public_classes" in result
        assert "public_functions" in result
        assert "entry_points" in result
        assert "rest_endpoints" in result

    def test_detect_cli_commands(self, sample_project):
        api = APISurfaceAnalyzer(sample_project)
        result = api.analyze()

        cli_cmds = result["cli_commands"]
        assert len(cli_cmds) > 0, "Should detect Click commands"

        cmd_names = [c["name"] for c in cli_cmds]
        # Should find greet and version commands from sample/cli.py
        assert "greet" in cmd_names or "main" in cmd_names

        for cmd in cli_cmds:
            assert "name" in cmd
            assert "file" in cmd
            assert "framework" in cmd

    def test_detect_entry_points(self, sample_project):
        api = APISurfaceAnalyzer(sample_project)
        result = api.analyze()

        eps = result["entry_points"]
        assert "sample" in eps
        assert eps["sample"] == "sample.cli:main"

    def test_detect_public_classes(self, sample_project):
        api = APISurfaceAnalyzer(sample_project)
        result = api.analyze()

        classes = result["public_classes"]
        class_names = [c["name"] for c in classes]

        assert "Processor" in class_names
        assert "DataLoader" in class_names

        proc = next(c for c in classes if c["name"] == "Processor")
        assert proc["method_count"] > 0
        assert "process" in proc["methods"]
        assert "validate" in proc["methods"]

    def test_detect_public_functions(self, sample_project):
        api = APISurfaceAnalyzer(sample_project)
        result = api.analyze()

        funcs = result["public_functions"]
        func_names = [f["name"] for f in funcs]

        assert "helper_function" in func_names or "slugify" in func_names

    def test_detect_rest_endpoints(self, tmp_path):
        """Test FastAPI endpoint detection."""
        proj = tmp_path / "fastapi-app"
        proj.mkdir()
        pkg = proj / "app"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "main.py").write_text('''
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/items")
def create_item(data: dict):
    return data

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"id": item_id}
''')
        (proj / "pyproject.toml").write_text('[project]\nname = "fastapi-app"\n')

        api = APISurfaceAnalyzer(proj)
        result = api.analyze()

        endpoints = result["rest_endpoints"]
        assert len(endpoints) == 3

        methods = {ep["method"] for ep in endpoints}
        assert "GET" in methods
        assert "POST" in methods

        paths = {ep["path"] for ep in endpoints}
        assert "/health" in paths
        assert "/items" in paths
        assert "/items/{item_id}" in paths

    def test_empty_project(self, empty_project):
        api = APISurfaceAnalyzer(empty_project)
        result = api.analyze()

        assert result["cli_commands"] == []
        assert result["public_classes"] == []
        assert result["entry_points"] == {}

    def test_extract_all(self, tmp_path):
        """Test __all__ extraction."""
        proj = tmp_path / "all_test"
        proj.mkdir()
        pkg = proj / "mypkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text(
            '__all__ = ["Foo", "bar"]\n\n'
            'class Foo:\n    pass\n\n'
            'class _Private:\n    pass\n\n'
            'def bar():\n    pass\n\n'
            'def _internal():\n    pass\n'
        )

        api = APISurfaceAnalyzer(proj)
        result = api.analyze()

        class_names = [c["name"] for c in result["public_classes"]]
        assert "Foo" in class_names
        assert "_Private" not in class_names

        func_names = [f["name"] for f in result["public_functions"]]
        assert "bar" in func_names
        assert "_internal" not in func_names
