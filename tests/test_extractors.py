"""Tests for new extractors: toon_parser, makefile_parser, docker_parser."""

import pytest
from pathlib import Path

from todocs.extractors.toon_parser import ToonParser
from todocs.extractors.makefile_parser import MakefileParser
from todocs.extractors.docker_parser import DockerParser


# ── ToonParser ──────────────────────────────────────────────


class TestToonParser:
    def test_find_toon_files_empty(self, tmp_path):
        parser = ToonParser(tmp_path)
        assert parser.find_toon_files() == {}

    def test_find_toon_files(self, tmp_path):
        (tmp_path / "project.toon").write_text("# test")
        (tmp_path / "analysis.toon").write_text("# test")
        (tmp_path / "flow.toon").write_text("# test")
        (tmp_path / "project.functions.toon").write_text("# test")

        parser = ToonParser(tmp_path)
        files = parser.find_toon_files()
        assert "map" in files
        assert "analysis" in files
        assert "flow" in files
        assert "functions" in files

    def test_parse_map_basic(self, tmp_path):
        (tmp_path / "project.toon").write_text("""# myproject | 10f 1200L | python:10
# Keys: M=modules, D=details
M[3]:
  myproject/__init__.py,20
  myproject/core.py,450
  myproject/cli.py,200
D:
  myproject/core.py:
    e: Processor,helper
    Processor(Base): __init__(1),process(1),validate(1)  # Main processor class
    helper(x;y)
""")

        parser = ToonParser(tmp_path)
        result = parser.parse_map(tmp_path / "project.toon")

        assert result["project"] == "myproject"
        assert result["total_functions"] == 10
        assert result["total_lines"] == 1200
        assert len(result["modules"]) == 3
        assert result["modules"][1]["path"] == "myproject/core.py"
        assert result["modules"][1]["lines"] == 450
        assert len(result["classes"]) >= 1
        assert result["classes"][0]["name"] == "Processor"

    def test_parse_analysis(self, tmp_path):
        (tmp_path / "analysis.toon").write_text("""# myproject | 10f 1200L | py:10 | 2026-03-08
# CC̄=4.5 | critical:3/50 | dups:1 | cycles:2

HEALTH[3]:
  🟡 CC    process_data CC=18 (limit:15)
  🟡 CC    validate_input CC=16 (limit:15)
  🔴 CC    complex_handler CC=25 (limit:15)

REFACTOR[2]:
  1. split 3 high-CC methods  (CC>15)
  2. break 2 circular dependencies

LAYERS:
  myproject/                    CC̄=4.5
  │ !! core                     450L  2C   8m  CC=18     ←3
  │ !  cli                      200L  1C   5m  CC=10     ←1
  │ utils                    150L  0C   4m  CC=5      ←2
""")

        parser = ToonParser(tmp_path)
        result = parser.parse_analysis(tmp_path / "analysis.toon")

        assert result["avg_complexity"] == 4.5
        assert result["critical_functions"] == 3
        assert result["total_functions_analyzed"] == 50
        assert result["duplicate_blocks"] == 1
        assert result["dependency_cycles"] == 2
        assert len(result["health_warnings"]) == 3
        assert result["health_warnings"][0]["function"] == "process_data"
        assert result["health_warnings"][0]["complexity"] == 18
        assert len(result["refactor_suggestions"]) == 2
        assert len(result["layers"]) == 3
        assert result["layers"][0]["module"] == "core"
        assert result["layers"][0]["complexity"] == 18.0

    def test_parse_flow(self, tmp_path):
        (tmp_path / "flow.toon").write_text("""# myproject/flow | 20 func | 3 pipelines | 2 hub-types | 2026-03-08

PIPELINES[3] (Core:1, Export:2):
  MyProject [Core]: Input → Output
              → process(data:List) → Dict        CC=8    pure ▶
              → validate(data:List) → bool         CC=3    pure ■
              PURITY: 2/2 pure  BOTTLENECK: process(CC=8)

  MyProject [Export]: Dict → str
              → format(data:Dict) → str            CC=5    pure ▶
              → write(path:str) → None             CC=2    IO ■
              PURITY: 1/2 pure  BOTTLENECK: format(CC=5)
""")

        parser = ToonParser(tmp_path)
        result = parser.parse_flow(tmp_path / "flow.toon")

        assert result["total_functions"] == 20
        assert result["total_pipelines"] == 3
        assert len(result["pipelines"]) == 2
        assert result["pipelines"][0]["category"] == "Core"
        assert result["pipelines"][0]["bottleneck"] == "process"
        assert result["pipelines"][0]["purity"] == "2/2"

    def test_parse_all(self, tmp_path):
        (tmp_path / "project.toon").write_text("# test | 5f 500L | python:5\nM[1]:\n  test.py,500\nD:\n")
        (tmp_path / "analysis.toon").write_text("# test | 5f 500L | py:5\n# CC̄=3.0 | critical:0/10 | dups:0 | cycles:0\n")

        parser = ToonParser(tmp_path)
        result = parser.parse_all()

        assert "map" in result["toon_files"]
        assert "analysis" in result["toon_files"]
        assert "map" in result
        assert "analysis" in result


# ── MakefileParser ──────────────────────────────────────────


class TestMakefileParser:
    def test_parse_makefile(self, sample_project):
        parser = MakefileParser(sample_project)
        result = parser.parse()

        assert result["type"] == "makefile"
        targets = result["targets"]
        assert len(targets) > 0

        names = [t["name"] for t in targets]
        assert "test" in names
        assert "lint" in names

        # Check that help descriptions are extracted
        test_target = next(t for t in targets if t["name"] == "test")
        assert test_target["description"] == "Run tests"

    def test_parse_empty(self, tmp_path):
        proj = tmp_path / "noproj"
        proj.mkdir()
        parser = MakefileParser(proj)
        result = parser.parse()
        assert result["type"] is None
        assert result["targets"] == []

    def test_parse_taskfile(self, tmp_path):
        proj = tmp_path / "taskproj"
        proj.mkdir()
        (proj / "Taskfile.yml").write_text("""version: "3"
tasks:
  test:
    desc: Run unit tests
    cmds:
      - pytest tests/ -v
  build:
    desc: Build package
    cmds:
      - python -m build
  clean:
    cmds:
      - rm -rf dist/
""")
        parser = MakefileParser(proj)
        result = parser.parse()

        assert result["type"] == "taskfile"
        assert len(result["targets"]) == 3
        names = [t["name"] for t in result["targets"]]
        assert "test" in names
        assert "build" in names

        test_t = next(t for t in result["targets"] if t["name"] == "test")
        assert test_t["description"] == "Run unit tests"
        assert "pytest" in test_t["commands"][0]

    def test_get_target_names(self, sample_project):
        parser = MakefileParser(sample_project)
        names = parser.get_target_names()
        assert isinstance(names, list)
        assert "test" in names


# ── DockerParser ────────────────────────────────────────────


class TestDockerParser:
    def test_parse_full(self, sample_project):
        parser = DockerParser(sample_project)
        result = parser.parse()

        assert result["has_dockerfile"]
        assert result["has_compose"]
        assert "python:3.12-slim" in result["base_images"]
        assert "8000" in result["exposed_ports"]

        # Docker-compose services
        assert len(result["services"]) == 2
        names = [s["name"] for s in result["services"]]
        assert "app" in names
        assert "redis" in names

        app_svc = next(s for s in result["services"] if s["name"] == "app")
        assert app_svc["build"]
        assert "redis" in app_svc["depends_on"]

        redis_svc = next(s for s in result["services"] if s["name"] == "redis")
        assert redis_svc["image"] == "redis:7-alpine"

    def test_parse_no_docker(self, tmp_path):
        proj = tmp_path / "nodocker"
        proj.mkdir()
        parser = DockerParser(proj)
        result = parser.parse()
        assert not result["has_dockerfile"]
        assert not result["has_compose"]
        assert result["services"] == []

    def test_parse_dockerfile_only(self, tmp_path):
        proj = tmp_path / "onlydocker"
        proj.mkdir()
        (proj / "Dockerfile").write_text("FROM node:20-alpine\nEXPOSE 3000\nCMD [\"node\", \"index.js\"]\n")

        parser = DockerParser(proj)
        result = parser.parse()
        assert result["has_dockerfile"]
        assert not result["has_compose"]
        assert "node:20-alpine" in result["base_images"]
        assert "3000" in result["exposed_ports"]

    def test_parse_multistage_dockerfile(self, tmp_path):
        proj = tmp_path / "multistage"
        proj.mkdir()
        (proj / "Dockerfile").write_text("""FROM python:3.12 AS builder
RUN pip install build
FROM python:3.12-slim AS runtime
COPY --from=builder /app /app
EXPOSE 8080
""")
        parser = DockerParser(proj)
        result = parser.parse()
        assert "python:3.12" in result["base_images"]
        assert "python:3.12-slim" in result["base_images"]
        assert "8080" in result["exposed_ports"]
