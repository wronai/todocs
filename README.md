# todocs

[![Version](https://img.shields.io/badge/version-0.1.11-blue)](https://github.com/wronai/todocs)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB)](https://python.org)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/badge/tests-63%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-88%25-green)](tests/)

Static-analysis documentation generator for project portfolios — WordPress-ready markdown articles **without LLM**.

## What it does

`todocs` scans a directory of projects and for each one produces a detailed status article by:

1. **Extracting metadata** from `pyproject.toml`, `setup.py`, `setup.cfg`, `package.json`
2. **Analyzing code** using Python AST + radon for cyclomatic complexity, maintainability index, and hotspot detection
3. **Building import graphs** — module dependency analysis, cycle detection, fan-in/fan-out hub identification
4. **Detecting API surface** — CLI commands (Click/Typer), REST endpoints (FastAPI/Flask), public classes/functions
5. **Parsing README** sections (description, installation, usage, features, architecture)
6. **Parsing CHANGELOG** for recent version entries with category extraction
7. **Parsing .toon files** — code maps, analysis data, flow pipelines (wronai ecosystem)
8. **Extracting build targets** from Makefile and Taskfile.yml with descriptions
9. **Analyzing Docker** infrastructure — Dockerfile base images, docker-compose services, ports, dependencies
10. **Detecting tech stack** — languages, frameworks, build tools, CI/CD, test frameworks
11. **Scoring maturity** (0-100, A+ to F grade) based on 16 quality indicators
12. **Generating WordPress-compatible markdown** with YAML frontmatter, badges, tables, and metrics
13. **Generating cross-project** comparison, category summaries, and health reports

No API keys. No LLM calls. Pure static analysis + AST + NLP regex parsing.

## Installation

```bash
pip install todocs
```

Or from source:

```bash
git clone https://github.com/wronai/todocs.git
cd todocs
pip install -e ".[dev]"
```

## CLI Usage

### Generate articles for all projects

```bash
todocs generate /path/to/organization --output articles/ --org-name WronAI
```

### Inspect a single project

```bash
todocs inspect /path/to/project
todocs inspect /path/to/project --format json
todocs inspect /path/to/project --format markdown -o report.md
```

### Cross-project comparison

```bash
todocs compare /path/to/org -o comparison.md
```

### Organization health report

```bash
todocs health /path/to/org -o health-report.md
```

### Full options

```bash
todocs generate /path/to/org \
  --output articles/ \
  --org-name "WronAI" \
  --org-url "https://github.com/wronai" \
  --exclude venv --exclude node_modules \
  --json-report report.json \
  --verbose
```

### Controlling Scan Depth (max_depth)

By default, todocs scans **3 levels deep** into project directories. This prevents scanning deep dependency folders while capturing all relevant source code.

#### Adjusting Depth via Python API

```python
from todocs import scan_project, scan_organization

# Scan only top-level files (depth = 1)
profile = scan_project("/path/to/project", max_depth=1)

# Scan deeper (depth = 5) for large monorepos
profile = scan_project("/path/to/project", max_depth=5)

# Apply to organization scan
profiles = scan_organization("/path/to/org", max_depth=4)
```

#### How Depth Works

```
project_root/          # depth 0 (always scanned)
├── src/               # depth 1 (always scanned)
│   ├── core/          # depth 2 (scanned with default max_depth=3)
│   │   ├── models.py  # depth 3 (scanned with default)
│   │   └── utils/     # depth 3 (scanned with default)
│   │       └── helper.py  # depth 4 (skipped with default, scanned with max_depth=4+)
│   └── api/           # depth 2
├── tests/             # depth 1
└── vendor/            # depth 1 (skipped — in skip list)
    └── deep_lib/      # depth 2 (skipped — in skip list)
```

#### What Gets Skipped Automatically

Regardless of depth, these are always excluded:
- `.git/`, `__pycache__/`, `.venv/`, `venv/`, `node_modules/`
- `dist/`, `build/`, `target/`, `.eggs/`
- Paths matching your `.gitignore` patterns
- Hidden directories (starting with `.`)

#### CLI Depth Control

Coming in v0.2.0: `--max-depth` CLI flag
```bash
todocs generate /path/to/org --max-depth 5
```

## Output Structure

```
articles/
├── _index.md                        # Portfolio overview
├── _comparison.md                   # Cross-project comparison tables
├── _health-report.md                # Organization health report
├── _category-llm-and-ai-agents.md   # Per-category summaries
├── allama.md                        # Individual project articles
├── broxeen.md
├── weekly.md
└── ...
```

## Python API

```python
from todocs import scan_organization, generate_articles

profiles = scan_organization("/path/to/org")
articles = generate_articles(profiles, "articles/", org_name="WronAI")
```

### Using individual analyzers

```python
from todocs.analyzers.import_graph import ImportGraphAnalyzer
from todocs.analyzers.api_surface import APISurfaceAnalyzer
from todocs.extractors.toon_parser import ToonParser

ig = ImportGraphAnalyzer("/path/to/project")
graph = ig.build_graph()
hubs = ig.get_hub_modules(top_n=5)

api = APISurfaceAnalyzer("/path/to/project")
surface = api.analyze()

toon = ToonParser("/path/to/project")
data = toon.parse_all()
```

## Architecture

```
todocs/
├── analyzers/           # AST + radon: structure, metrics, imports, API, maturity
│   ├── api_surface.py   # APISurfaceAnalyzer with extracted symbol scanners
│   ├── code_metrics.py  # CodeMetricsAnalyzer with radon integration
│   ├── dependencies.py  # DependencyAnalyzer for runtime/dev deps
│   ├── import_graph.py  # ImportGraphAnalyzer with cycle detection
│   ├── maturity.py      # MaturityScorer with 16 quality indicators
│   └── structure.py     # StructureAnalyzer with tech stack detection
├── extractors/          # Parsers: metadata, README, CHANGELOG, TOON, Makefile, Docker
│   ├── changelog_parser.py
│   ├── docker_parser.py
│   ├── makefile_parser.py
│   ├── metadata.py
│   ├── readme_parser.py
│   └── toon_parser.py   # TOON file parser (refactored into section parsers)
├── generators/          # Article + comparison/category/health generators
│   ├── article.py              # Main ArticleGenerator (146L, refactored)
│   ├── article_sections.py     # 13 section rendering functions
│   └── comparison.py           # ComparisonGenerator for cross-project analysis
├── cli.py               # Click CLI: generate/inspect/compare/health
├── core.py              # Data models + orchestration pipeline
examples/                # Usage examples (see below)
tests/                   # 63 tests, 88% coverage
```

## Project Status (v0.1.3)

After refactoring (2026-03-08):

| Metric | Value |
|--------|-------|
| Source files | 24 (+1 new: article_sections.py) |
| Source lines | ~4,100 |
| Test files | 5 |
| Test lines | 1,560 |
| Test coverage | 88% (63 tests passing) |
| High-CC functions (≥15) | Reduced from 15 to 7 |
| Maturity Grade | B+ (71/100) |

**Refactoring highlights:**
- `article.py`: 560L → 146L (split into `article_sections.py`)
- `custom_analysis.py` main(): CC 33 → 8 (extracted 6 helpers)
- `_scan_public_symbols`: CC 27 → 8 (extracted 4 helpers)
- `parse_analysis` & `parse_map`: CC 25/24 → ~6 (section parsers)
- `detect_tech_stack`: CC 19 → 6 (6 detection methods)
- `_parse_makefile`: CC 19 → 8 (extracted 4 helpers)
- `_parse_sections`: CC 22 → 8 (description + heading extractors)

## Examples

### Basic: Scan single project
```python
from todocs.core import scan_project

profile = scan_project("/path/to/project")
print(f"{profile.name}: {profile.maturity.grade} ({profile.code_stats.source_lines} lines)")
```

### Using refactored article sections directly
```python
from todocs.generators.article_sections import (
    render_metrics, render_tech_stack, render_maturity
)
from todocs.core import scan_project

profile = scan_project("/path/to/project")

# Generate individual sections
metrics_md = render_metrics(profile)
tech_md = render_tech_stack(profile)
maturity_md = render_maturity(profile)

print(metrics_md)
```

### Custom API surface analysis (using refactored helpers)
```python
from todocs.analyzers.api_surface import APISurfaceAnalyzer

api = APISurfaceAnalyzer("/path/to/project")
surface = api.analyze()

# Access specific components
print(f"CLI commands: {len(surface['cli_commands'])}")
print(f"Public classes: {len(surface['public_classes'])}")
print(f"REST endpoints: {len(surface['rest_endpoints'])}")
print(f"Entry points: {surface['entry_points']}")
```

### Organization health report
```python
from todocs import scan_organization
from todocs.generators.comparison import ComparisonGenerator
from pathlib import Path

# Scan organization
profiles = scan_organization("/path/to/org")

# Generate health report
gen = ComparisonGenerator()
report_path = Path("health-report.md")
report_path.write_text(gen.generate_health_report(profiles, org_name="WronAI"))
```

### Category-based analysis
```python
from todocs import scan_organization
from todocs.generators.comparison import ComparisonGenerator

profiles = scan_organization("/path/to/org")
gen = ComparisonGenerator()

# Generate articles grouped by category
category_articles = gen.generate_category_articles(
    profiles,
    output_dir="articles/",
    org_name="WronAI"
)

for path in category_articles:
    print(f"Generated: {path}")
```

### See also: `examples/` directory
- `scan_single.py` — Basic single project scan
- `scan_org.py` — Organization-wide scan  
- `custom_analysis.py` — Using individual analyzers (refactored with 6 helpers)
- `article_sections_demo.py` — New: Direct section rendering
- `api_surface_deep.py` — New: Deep API analysis with refactored helpers

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Author

Created by **Tom Sapletta** - [tom@sapletta.com](mailto:tom@sapletta.com)
