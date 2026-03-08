# todocs

[![Version](https://img.shields.io/badge/version-0.1.3-blue)](https://github.com/wronai/todocs)
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
├── extractors/          # Parsers: metadata, README, CHANGELOG, TOON, Makefile, Docker
├── generators/          # Article + comparison/category/health generators
├── cli.py               # Click CLI: generate/inspect/compare/health
├── core.py              # Data models + orchestration pipeline
examples/                # scan_single, scan_org, custom_analysis
tests/                   # 63 tests, 88% coverage
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Author

Created by **Tom Sapletta** - [tom@sapletta.com](mailto:tom@sapletta.com)
