<!-- code2docs:start --># todocs

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-279-green)
> **279** functions | **27** classes | **42** files | CC̄ = 4.6

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

### Optional Extras

```bash
pip install todocs[dev]    # development tools
pip install todocs[nlp]    # nlp features
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

```
todocs/
├── project        ├── advanced_usage    ├── article_sections_demo        ├── quickstart    ├── scan_org    ├── custom_analysis    ├── scan_single├── todocs/    ├── organization_health_report    ├── api_surface_deep        ├── makefile_parser    ├── cli    ├── extractors/        ├── toon_parser        ├── readme_parser        ├── docker_parser        ├── quickstart        ├── advanced_usage    ├── formatters/        ├── changelog_parser        ├── markdown        ├── table_formatter    ├── outputs/        ├── json        ├── html    ├── generators/        ├── org_index_gen        ├── article        ├── project_card_gen        ├── article_sections        ├── status_report_gen    ├── utils/        ├── structure    ├── analyzers/        ├── comparison        ├── dependencies        ├── maturity        ├── import_graph        ├── code_metrics        ├── api_surface    ├── core        ├── metadata```

## API Overview

### Classes

- **`MakefileParser`** — Extract targets and structure from Makefile or Taskfile.yml.
- **`ToonParser`** — Parse .toon files into structured data.
- **`ReadmeParser`** — Extract structured sections from a README.md file.
- **`DockerParser`** — Extract Docker infrastructure from Dockerfile and docker-compose.yml.
- **`ChangelogParser`** — Extract structured entries from CHANGELOG.md.
- **`MarkdownOutput`** — Write project profiles as markdown files (WordPress-ready).
- **`TableFormatter`** — Generate markdown comparison tables from project profiles.
- **`JSONOutput`** — Write project profiles as structured JSON for APIs and dashboards.
- **`HTMLOutput`** — Write project profiles as a standalone HTML report.
- **`OrgIndexGenerator`** — Generate an index.md catalog page for all projects in an organization.
- **`ArticleGenerator`** — Generate markdown articles for WordPress from analyzed project profiles.
- **`ProjectCardGenerator`** — Generate a compact project card suitable for WordPress embedding.
- **`StatusReportGenerator`** — Generate a comprehensive organization status report.
- **`GitignoreParser`** — Parse and match .gitignore patterns.
- **`StructureAnalyzer`** — Analyze project directory structure.
- **`ComparisonGenerator`** — Generate comparative analysis articles across projects.
- **`DependencyAnalyzer`** — Extract project dependencies without executing anything.
- **`MaturityScorer`** — Compute a maturity score (0-100) for a project.
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

- `main()` — —
- `main()` — —
- `main()` — —
- `main()` — —
- `analyze_maturity_distribution(profiles)` — Analyze maturity grade distribution across projects.
- `analyze_code_metrics(profiles)` — Aggregate code metrics across all projects.
- `analyze_tech_stacks(profiles)` — Analyze technology distribution across projects.
- `find_critical_projects(profiles, threshold)` — Find projects with low maturity scores.
- `print_health_summary(profiles, org_name)` — Print a formatted health summary to console.
- `main()` — —
- `print_section(title)` — Print a formatted section header.
- `analyze_entry_points(analyzer)` — Analyze and display entry points.
- `analyze_cli_commands(analyzer)` — Analyze and display CLI commands.
- `analyze_public_symbols(analyzer)` — Analyze and display public classes and functions.
- `analyze_rest_endpoints(analyzer)` — Analyze and display REST API endpoints.
- `analyze_symbol_sources(analyzer)` — Show which files contribute public symbols.
- `main()` — —
- `main()` — todocs — Static-analysis documentation generator for project portfolios.
- `generate(root_dir, output_dir, org_name, org_url)` — Scan projects and generate WordPress markdown articles.
- `inspect(project_dir, output, fmt)` — Inspect a single project and show its profile.
- `compare(root_dir, output_path, org_name, exclude)` — Generate cross-project comparison report.
- `health(root_dir, output_path, org_name, exclude)` — Generate organization health report.
- `readme(root_dir, output_path, org_name, exclude)` — Generate a single README.md with project list and 5-line descriptions.
- `status(root_dir, output_path, org_name, exclude)` — Generate organization status report with KPIs and recommendations.
- `cards(root_dir, output_dir, org_name, exclude)` — Generate project cards (compact single-project summaries).
- `index(root_dir, output_path, org_name, exclude)` — Generate organization project index / catalog page.
- `export_cmd(root_dir, output_path, fmt, org_name)` — Export organization report in HTML or JSON format.
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

📄 `docs.examples.advanced_usage`
📄 `docs.examples.quickstart`
📄 `examples.api_surface_deep` (7 functions)
📄 `examples.article_sections_demo` (1 functions)
📄 `examples.custom_analysis` (8 functions)
📄 `examples.organization_health_report` (6 functions)
📄 `examples.scan_org` (1 functions)
📄 `examples.scan_single` (1 functions)
📄 `project`
📦 `todocs`
📦 `todocs.analyzers`
📄 `todocs.analyzers.api_surface` (13 functions, 1 classes)
📄 `todocs.analyzers.code_metrics` (15 functions, 1 classes)
📄 `todocs.analyzers.dependencies` (10 functions, 1 classes)
📄 `todocs.analyzers.import_graph` (13 functions, 1 classes)
📄 `todocs.analyzers.maturity` (2 functions, 1 classes)
📄 `todocs.analyzers.structure` (12 functions, 1 classes)
📄 `todocs.cli` (18 functions)
📄 `todocs.core` (11 functions, 5 classes)
📄 `todocs.examples.advanced_usage`
📄 `todocs.examples.quickstart`
📦 `todocs.extractors`
📄 `todocs.extractors.changelog_parser` (5 functions, 1 classes)
📄 `todocs.extractors.docker_parser` (6 functions, 1 classes)
📄 `todocs.extractors.makefile_parser` (9 functions, 1 classes)
📄 `todocs.extractors.metadata` (9 functions, 1 classes)
📄 `todocs.extractors.readme_parser` (9 functions, 1 classes)
📄 `todocs.extractors.toon_parser` (17 functions, 1 classes)
📦 `todocs.formatters`
📄 `todocs.formatters.table_formatter` (7 functions, 1 classes)
📦 `todocs.generators`
📄 `todocs.generators.article` (5 functions, 1 classes)
📄 `todocs.generators.article_sections` (18 functions)
📄 `todocs.generators.comparison` (23 functions, 1 classes)
📄 `todocs.generators.org_index_gen` (9 functions, 1 classes)
📄 `todocs.generators.project_card_gen` (11 functions, 1 classes)
📄 `todocs.generators.status_report_gen` (14 functions, 1 classes)
📦 `todocs.outputs`
📄 `todocs.outputs.html` (5 functions, 1 classes)
📄 `todocs.outputs.json` (6 functions, 1 classes)
📄 `todocs.outputs.markdown` (2 functions, 1 classes)
📦 `todocs.utils` (6 functions, 1 classes)

## Requirements

- Python >= >=3.10
- tomli >=2.0; python_version<'3.11'- pyyaml >=6.0- jinja2 >=3.1- radon >=6.0- rich >=13.0- click >=8.1

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