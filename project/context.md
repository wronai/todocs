# System Architecture Analysis

## Overview

- **Project**: todocs
- **Language**: python
- **Files**: 25
- **Lines**: 7967
- **Functions**: 248
- **Classes**: 27
- **Avg CC**: 4.6
- **Critical (CC≥10)**: 25

## Architecture

### root/ (1 files, 18L, 0 functions)

- `project.sh` — 18L, 0 methods, CC↑0

### todocs/ (3 files, 880L, 25 functions)

- `core.py` — 387L, 8 methods, CC↑11
- `cli.py` — 483L, 17 methods, CC↑7
- `__init__.py` — 10L, 0 methods, CC↑0

### todocs/analyzers/ (7 files, 1230L, 63 functions)

- `maturity.py` — 103L, 2 methods, CC↑14
- `api_surface.py` — 290L, 13 methods, CC↑13
- `code_metrics.py` — 265L, 15 methods, CC↑10
- `import_graph.py` — 204L, 11 methods, CC↑9
- `dependencies.py` — 133L, 10 methods, CC↑8
- _2 more files_

### todocs/extractors/ (7 files, 1138L, 55 functions)

- `docker_parser.py` — 174L, 6 methods, CC↑13
- `toon_parser.py` — 343L, 17 methods, CC↑11
- `makefile_parser.py` — 153L, 9 methods, CC↑10
- `metadata.py` — 211L, 9 methods, CC↑10
- `changelog_parser.py` — 103L, 5 methods, CC↑9
- _2 more files_

### todocs/formatters/ (2 files, 146L, 7 functions)

- `table_formatter.py` — 145L, 7 methods, CC↑8
- `__init__.py` — 1L, 0 methods, CC↑0

### todocs/generators/ (7 files, 1536L, 79 functions)

- `status_report_gen.py` — 195L, 13 methods, CC↑16
- `comparison.py` — 482L, 23 methods, CC↑14
- `article.py` — 145L, 5 methods, CC↑13
- `article_sections.py` — 460L, 18 methods, CC↑12
- `org_index_gen.py` — 118L, 9 methods, CC↑6
- _2 more files_

### todocs/outputs/ (4 files, 350L, 13 functions)

- `json.py` — 104L, 6 methods, CC↑14
- `html.py` — 164L, 5 methods, CC↑12
- `markdown.py` — 81L, 2 methods, CC↑8
- `__init__.py` — 1L, 0 methods, CC↑0

### todocs/utils/ (1 files, 150L, 6 functions)

- `__init__.py` — 150L, 6 methods, CC↑8

## Key Exports

- **StatusReportGenerator** (class, CC̄=5.1)
  - `_quality_gaps` CC=16 ⚠ split
  - `_recommendations` CC=15 ⚠ split
- **MaturityScorer** (class, CC̄=7.5)
- **APISurfaceAnalyzer** (class, CC̄=6.5)
- **DockerParser** (class, CC̄=6.3)
- **HTMLOutput** (class, CC̄=5.2)
- **ToonParser** (class, CC̄=5.4)
- **MetadataExtractor** (class, CC̄=6.2)
- **GitignoreParser** (class, CC̄=5.2)

## Hotspots (High Fan-Out)

- **scan_project** — fan-out=33: Analyze a single project and return its profile.

Args:
    project_path: Path t
- **ImportGraphAnalyzer.build_graph** — fan-out=21: Build the import dependency graph.

Returns:
    {
        "nodes": [{"name": "m
- **export_cmd** — fan-out=16: Export with 16 outputs
- **DockerParser._parse_dockerfile** — fan-out=16: Extract FROM images, EXPOSE ports, ENTRYPOINT from Dockerfile.
- **MarkdownOutput.write_all** — fan-out=16: Write all markdown outputs. Returns list of written paths.
- **scan_organization** — fan-out=16: Scan all projects under root_path and return profiles.

Args:
    root_path: Roo
- **generate** — fan-out=15: Scan projects and generate WordPress markdown articles.

ROOT_DIR is the directo

## Refactoring Priorities

| # | Action | Impact | Effort |
|---|--------|--------|--------|
| 1 | Split StatusReportGenerator._quality_gaps (CC=16 → target CC<10) | medium | low |
| 2 | Split StatusReportGenerator._recommendations (CC=15 → target CC<10) | medium | low |
| 3 | Reduce scan_project fan-out (currently 33) | medium | medium |
| 4 | Reduce ImportGraphAnalyzer.build_graph fan-out (currently 21) | medium | medium |
| 5 | Reduce export_cmd fan-out (currently 16) | medium | medium |

## Context for LLM

When suggesting changes:
1. Start from hotspots and high-CC functions
2. Follow refactoring priorities above
3. Maintain public API surface — keep backward compatibility
4. Prefer minimal, incremental changes

