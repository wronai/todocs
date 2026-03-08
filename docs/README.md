<!-- code2docs:start --># todocs

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.9-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-165-green)
> **165** functions | **20** classes | **24** files | CC̄ = 5.5

> Auto-generated project documentation from source code analysis.

**Author:** Softreck  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/wronai/todocs](https://github.com/wronai/todocs)

## Installation

### From PyPI

```bash
pip install todocs
```

### From Source

```bash
git clone https://github.com/wronai/todocs
cd todocs
pip install -e .
```


## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
todocs ./my-project

# Only regenerate README
todocs ./my-project --readme-only

# Preview what would be generated (no file writes)
todocs ./my-project --dry-run

# Check documentation health
todocs check ./my-project

# Sync — regenerate only changed modules
todocs sync ./my-project
```

### Python API

```python
from todocs import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```

## Generated Output

When you run `todocs`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `todocs.yaml` in your project root (or run `todocs init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

todocs can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- todocs:start -->
# Project Title
... auto-generated content ...
<!-- todocs:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

todocs is organized into modular components:

- **CLI** — Command-line interface with Click
- **Core** — Project scanning and profile generation
- **Analyzers** — Code analysis (structure, metrics, imports, API surface, maturity)
- **Extractors** — Parse config files (Makefile, Docker, README, CHANGELOG, TOON)
- **Generators** — Article and documentation generators
- **Utils** — Gitignore parsing and scanning utilities

### Directory Structure

```
todocs/
├── todocs/
│   ├── cli.py              # CLI entry points
│   ├── core.py             # Project/organization scanning
│   ├── analyzers/          # Analysis modules
│   │   ├── api_surface.py
│   │   ├── code_metrics.py
│   │   ├── dependencies.py
│   │   ├── import_graph.py
│   │   ├── maturity.py
│   │   └── structure.py
│   ├── extractors/         # File parsers
│   │   ├── changelog_parser.py
│   │   ├── docker_parser.py
│   │   ├── makefile_parser.py
│   │   ├── metadata.py
│   │   ├── readme_parser.py
│   │   └── toon_parser.py
│   ├── generators/         # Documentation generators
│   │   ├── article.py
│   │   ├── article_sections.py
│   │   └── comparison.py
│   └── utils/              # Utilities
│       └── __init__.py
├── tests/                  # Test suite
├── examples/               # Usage examples
└── docs/                   # Generated documentation
```

## API Overview

### Classes

- **`MakefileParser`** — Extract targets and structure from Makefile or Taskfile.yml.
- **`ToonParser`** — Parse .toon files into structured data.
- **`ReadmeParser`** — Extract structured sections from a README.md file.
- **`ChangelogParser`** — Extract structured entries from CHANGELOG.md.
- **`DockerParser`** — Extract Docker infrastructure from Dockerfile and docker-compose.yml.
- **`ArticleGenerator`** — Generate markdown articles for WordPress from analyzed project profiles.
- **`GitignoreParser`** — Parse and match .gitignore patterns.
- **`ComparisonGenerator`** — Generate comparative analysis articles across projects.
- **`StructureAnalyzer`** — Analyze project directory structure.
- **`MaturityScorer`** — Compute a maturity score (0-100) for a project.
- **`DependencyAnalyzer`** — Extract project dependencies without executing anything.
- **`ImportGraphAnalyzer`** — Analyze import relationships between project modules.
- **`CodeMetricsAnalyzer`** — Analyze code metrics: lines, complexity, maintainability.
- **`APISurfaceAnalyzer`** — Detect public API surface of a project.
- **`TechStack`** — Detected technology stack.
- **`CodeStats`** — Aggregated code statistics.
- **`ProjectMetadata`** — Extracted project metadata.
- **`MaturityProfile`** — Project maturity assessment.
- **`ProjectProfile`** — Complete project profile for article generation.
- **`MetadataExtractor`** — Extract structured metadata from project config files.

### Functions

- `main()` — todocs — Static-analysis documentation generator for project portfolios.
- `generate(root_dir, output_dir, org_name, org_url)` — Scan projects and generate WordPress markdown articles.
- `inspect(project_dir, output, fmt)` — Inspect a single project and show its profile.
- `compare(root_dir, output_path, org_name, exclude)` — Generate cross-project comparison report.
- `health(root_dir, output_path, org_name, exclude)` — Generate organization health report.
- `readme(root_dir, output_path, org_name, exclude)` — Generate a single README.md with project list and 5-line descriptions.
- `render_frontmatter(p, org_name, generated_at)` — Render WordPress YAML frontmatter.
- `render_header(p, org_url)` — Render title and badges section.
- `render_overview(p, org_name)` — Render overview/description section.
- `render_tech_stack(p)` — Render technology stack section.
- `render_architecture(p)` — Render architecture and key modules section.
- `render_metrics(p)` — Render code metrics section.
- `render_maturity(p)` — Render maturity assessment section.
- `render_dependencies(p)` — Render dependencies section.
- `render_api_surface(p)` — Render API surface section.
- `render_build_targets(p)` — Render build targets section.
- `render_docker(p)` — Render Docker infrastructure section.
- `render_changelog(p)` — Render recent changes section.
- `render_usage(p)` — Render installation/usage section.
- `render_footer(generated_at)` — Render article footer.
- `create_scan_filter(project_path, max_depth, extra_excludes)` — Create a filter function for scanning with depth and gitignore support.
- `scan_project(project_path, max_depth)` — Analyze a single project and return its profile.
- `scan_organization(root_path, exclude, max_depth, progress_callback)` — Scan all projects under root_path and return profiles.
- `generate_articles(profiles, output_dir, org_name, org_url)` — Generate WordPress-ready markdown articles for each project.


## Project Structure

📦 `analyzers`
📄 `analyzers.api_surface` (13 functions, 1 classes)
📄 `analyzers.code_metrics` (10 functions, 1 classes)
📄 `analyzers.dependencies` (5 functions, 1 classes)
📄 `analyzers.import_graph` (8 functions, 1 classes)
📄 `analyzers.maturity` (2 functions, 1 classes)
📄 `analyzers.structure` (12 functions, 1 classes)
📄 `cli` (12 functions)
📄 `core` (8 functions, 5 classes)
📄 `examples.advanced_usage`
📄 `examples.quickstart`
📦 `extractors`
📄 `extractors.changelog_parser` (5 functions, 1 classes)
📄 `extractors.docker_parser` (6 functions, 1 classes)
📄 `extractors.makefile_parser` (9 functions, 1 classes)
📄 `extractors.metadata` (9 functions, 1 classes)
📄 `extractors.readme_parser` (9 functions, 1 classes)
📄 `extractors.toon_parser` (17 functions, 1 classes)
📦 `generators`
📄 `generators.article` (5 functions, 1 classes)
📄 `generators.article_sections` (14 functions)
📄 `generators.comparison` (15 functions, 1 classes)
📦 `todocs`
📦 `utils` (6 functions, 1 classes)

## Requirements



## Contributing

**Contributors:**
- Tom Sapletta

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/wronai/todocs
cd todocs

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 📖 [Full Documentation](https://github.com/wronai/todocs/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/wronai/todocs/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/wronai/todocs/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/wronai/todocs/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](./docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](./docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](./docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](./docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](./docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](./docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](./docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](./docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](./CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->