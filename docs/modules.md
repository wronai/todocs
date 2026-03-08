# todocs — Module Reference

> 22 modules | 162 functions | 20 classes

## Module Overview

| Module | Lines | Functions | Classes | CC avg | Description | Source |
|--------|-------|-----------|---------|--------|-------------|--------|
| `analyzers.api_surface` | 290 | 0 | 1 | 6.5 | Detect public API surface: CLI commands, exported classes, f | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/api_surface.py) |
| `analyzers.code_metrics` | 240 | 0 | 1 | 6.4 | Code metrics analyzer using Python AST and radon for cycloma | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/code_metrics.py) |
| `analyzers.dependencies` | 151 | 0 | 1 | 9.0 | Dependency extraction from pyproject.toml, setup.py, require | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/dependencies.py) |
| `analyzers.import_graph` | 201 | 0 | 1 | 5.6 | Build import dependency graph between project modules using  | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/import_graph.py) |
| `analyzers.maturity` | 103 | 0 | 1 | 7.5 | Score project maturity based on structural and metric indica | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/maturity.py) |
| `analyzers.structure` | 234 | 0 | 1 | 3.9 | Analyze project directory structure and detect technology st | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/structure.py) |
| `cli` | 307 | 11 | 0 | 2.9 | CLI interface for todocs — generate project documentation ar | [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py) |
| `core` | 387 | 6 | 5 | 5.9 | Core data models and orchestration for todocs. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py) |
| `extractors.changelog_parser` | 103 | 0 | 1 | 4.4 | Parse CHANGELOG.md to extract recent version entries. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/changelog_parser.py) |
| `extractors.docker_parser` | 174 | 0 | 1 | 6.3 | Parse Docker files to extract service topology and base imag | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/docker_parser.py) |
| `extractors.makefile_parser` | 153 | 0 | 1 | 4.3 | Parse Makefile / Taskfile.yml to extract build targets and c | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/makefile_parser.py) |
| `extractors.metadata` | 211 | 0 | 1 | 6.2 | Extract project metadata from pyproject.toml, setup.py, setu | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/metadata.py) |
| `extractors.readme_parser` | 153 | 0 | 1 | 3.9 | Parse README.md into structured sections using regex-based m | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/readme_parser.py) |
| `extractors.toon_parser` | 343 | 0 | 1 | 5.4 | Parse .toon (Token-Oriented Object Notation) files. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/toon_parser.py) |
| `generators.article` | 145 | 0 | 1 | 3.8 | Generate WordPress-ready markdown articles from ProjectProfi | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article.py) |
| `generators.article_sections` | 431 | 14 | 0 | 7.3 | Section renderer helpers for ArticleGenerator. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py) |
| `generators.comparison` | 380 | 0 | 1 | 5.9 | Generate cross-project comparison and category summary artic | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/comparison.py) |
| `utils` | 150 | 1 | 1 | 4.7 | Gitignore pattern matching utility for todocs. | [source](https://github.com/wronai/todocs/blob/main/todocs/utils/__init__.py) |

## Core

### `cli` [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py)

CLI interface for todocs — generate project documentation articles.

- `compare(root_dir, output_path, org_name, exclude)` — Generate cross-project comparison report. [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L264)
- `generate(root_dir, output_dir, org_name, org_url, exclude, json_report, verbose)` — Scan projects and generate WordPress markdown articles. [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L47)
- `health(root_dir, output_path, org_name, exclude)` — Generate organization health report. [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L290)
- `inspect(project_dir, output, fmt)` — Inspect a single project and show its profile. [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L234)
- `main()` — todocs — Static-analysis documentation generator for project portfolios. [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L28)

### `core` [source](https://github.com/wronai/todocs/blob/main/todocs/core.py)

Core data models and orchestration for todocs.

**`CodeStats`** [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L40)
: Aggregated code statistics.

**`MaturityProfile`** [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L70)
: Project maturity assessment.

**`ProjectMetadata`** [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L55)
: Extracted project metadata.

**`ProjectProfile`** [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L88)
: Complete project profile for article generation.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `to_dict` | `` | `—` | 1 |
| `to_json` | `indent` | `—` | 1 |

**`TechStack`** [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L28)
: Detected technology stack.

- `generate_articles(profiles, output_dir, org_name, org_url, include_comparison, include_categories, include_health)` — Generate WordPress-ready markdown articles for each project. [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L279)
- `scan_organization(root_path, exclude, max_depth, progress_callback)` — Scan all projects under root_path and return profiles. [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L227)
- `scan_project(project_path, max_depth)` — Analyze a single project and return its profile. [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L121)

### `utils` [source](https://github.com/wronai/todocs/blob/main/todocs/utils/__init__.py)

Gitignore pattern matching utility for todocs.

**`GitignoreParser`** [source](https://github.com/wronai/todocs/blob/main/todocs/utils/__init__.py#L14)
: Parse and match .gitignore patterns.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `is_ignored` | `relative_path, is_dir` | `—` | 7 |

- `create_scan_filter(project_path, max_depth, extra_excludes)` — Create a filter function for scanning with depth and gitignore support. [source](https://github.com/wronai/todocs/blob/main/todocs/utils/__init__.py#L105)

## analyzers

### `analyzers.api_surface` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/api_surface.py)

Detect public API surface: CLI commands, exported classes, functions, REST endpoints.

**`APISurfaceAnalyzer`** [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/api_surface.py#L16)
: Detect public API surface of a project.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `analyze` | `` | `—` | 1 |

### `analyzers.code_metrics` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/code_metrics.py)

Code metrics analyzer using Python AST and radon for cyclomatic complexity.

**`CodeMetricsAnalyzer`** [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/code_metrics.py#L29)
: Analyze code metrics: lines, complexity, maintainability.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `analyze` | `` | `—` | 16 |
| `get_key_modules` | `top_n` | `—` | 3 |

### `analyzers.dependencies` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/dependencies.py)

Dependency extraction from pyproject.toml, setup.py, requirements.txt, package.json.

**`DependencyAnalyzer`** [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/dependencies.py#L19)
: Extract project dependencies without executing anything.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `get_runtime_deps` | `` | `—` | 17 |
| `get_dev_deps` | `` | `—` | 18 |

### `analyzers.import_graph` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/import_graph.py)

Build import dependency graph between project modules using AST.

**`ImportGraphAnalyzer`** [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/import_graph.py#L17)
: Analyze import relationships between project modules.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `build_graph` | `` | `—` | 15 |
| `get_hub_modules` | `top_n` | `—` | 2 |

### `analyzers.maturity` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/maturity.py)

Score project maturity based on structural and metric indicators.

**`MaturityScorer`** [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/maturity.py#L18)
: Compute a maturity score (0-100) for a project.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `score` | `` | `—` | 14 |

### `analyzers.structure` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/structure.py)

Analyze project directory structure and detect technology stack.

**`StructureAnalyzer`** [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/structure.py#L90)
: Analyze project directory structure.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `analyze` | `` | `—` | 7 |
| `detect_tech_stack` | `` | `—` | 2 |

## extractors

### `extractors.changelog_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/changelog_parser.py)

Parse CHANGELOG.md to extract recent version entries.

**`ChangelogParser`** [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/changelog_parser.py#L10)
: Extract structured entries from CHANGELOG.md.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `parse` | `max_entries` | `—` | 3 |

### `extractors.docker_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/docker_parser.py)

Parse Docker files to extract service topology and base images.

**`DockerParser`** [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/docker_parser.py#L16)
: Extract Docker infrastructure from Dockerfile and docker-compose.yml.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `parse` | `` | `—` | 3 |

### `extractors.makefile_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/makefile_parser.py)

Parse Makefile / Taskfile.yml to extract build targets and commands.

**`MakefileParser`** [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/makefile_parser.py#L16)
: Extract targets and structure from Makefile or Taskfile.yml.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `parse` | `` | `—` | 3 |
| `get_target_names` | `` | `—` | 2 |

### `extractors.metadata` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/metadata.py)

Extract project metadata from pyproject.toml, setup.py, setup.cfg, package.json.

**`MetadataExtractor`** [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/metadata.py#L21)
: Extract structured metadata from project config files.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `extract` | `` | `—` | 9 |

### `extractors.readme_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/readme_parser.py)

Parse README.md into structured sections using regex-based markdown parsing.

**`ReadmeParser`** [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/readme_parser.py#L44)
: Extract structured sections from a README.md file.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `parse` | `` | `—` | 3 |
| `get_first_paragraph` | `` | `—` | 3 |

### `extractors.toon_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/toon_parser.py)

Parse .toon (Token-Oriented Object Notation) files.

**`ToonParser`** [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/toon_parser.py#L20)
: Parse .toon files into structured data.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `find_toon_files` | `` | `—` | 6 |
| `parse_all` | `` | `—` | 5 |
| `parse_map` | `path` | `—` | 2 |
| `parse_analysis` | `path` | `—` | 2 |
| `parse_flow` | `path` | `—` | 11 |
| `parse_functions` | `path` | `—` | 7 |

## generators

### `generators.article` [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article.py)

Generate WordPress-ready markdown articles from ProjectProfile data.

**`ArticleGenerator`** [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article.py#L30)
: Generate markdown articles for WordPress from analyzed project profiles.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `generate` | `profile, output_path` | `—` | 1 |
| `generate_index` | `profiles, output_path` | `—` | 1 |

### `generators.article_sections` [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py)

Section renderer helpers for ArticleGenerator.

- `render_api_surface(p)` — Render API surface section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L247)
- `render_architecture(p)` — Render architecture and key modules section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L118)
- `render_build_targets(p)` — Render build targets section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L300)
- `render_changelog(p)` — Render recent changes section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L358)
- `render_dependencies(p)` — Render dependencies section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L225)
- `render_docker(p)` — Render Docker infrastructure section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L326)
- `render_footer(generated_at)` — Render article footer. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L423)
- `render_frontmatter(p, org_name, generated_at)` — Render WordPress YAML frontmatter. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L15)
- `render_header(p, org_url)` — Render title and badges section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L45)
- `render_maturity(p)` — Render maturity assessment section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L195)
- `render_metrics(p)` — Render code metrics section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L163)
- `render_overview(p, org_name)` — Render overview/description section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L69)
- `render_tech_stack(p)` — Render technology stack section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L89)
- `render_usage(p)` — Render installation/usage section. [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L382)

### `generators.comparison` [source](https://github.com/wronai/todocs/blob/main/todocs/generators/comparison.py)

Generate cross-project comparison and category summary articles.

**`ComparisonGenerator`** [source](https://github.com/wronai/todocs/blob/main/todocs/generators/comparison.py#L13)
: Generate comparative analysis articles across projects.

| Method | Args | Returns | CC |
|--------|------|---------|----|
| `generate_comparison` | `profiles, output_path, title` | `—` | 1 |
| `generate_category_articles` | `profiles, output_dir` | `—` | 3 |
| `generate_health_report` | `profiles, output_path` | `—` | 1 |
