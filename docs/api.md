# todocs — API Reference

> 24 modules | 162 functions | 20 classes

## Contents

- [Core](#core) (6 modules)
- [analyzers](#analyzers) (6 modules)
- [extractors](#extractors) (6 modules)
- [generators](#generators) (3 modules)

## Core

### `analyzers` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/__init__.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `APISurfaceAnalyzer` | 1 | Detect public API surface of a project. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/api_surface.py#L16) |
| `CodeMetricsAnalyzer` | 2 | Analyze code metrics: lines, complexity, maintainability. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/code_metrics.py#L29) |
| `DependencyAnalyzer` | 2 | Extract project dependencies without executing anything. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/dependencies.py#L19) |
| `ImportGraphAnalyzer` | 2 | Analyze import relationships between project modules. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/import_graph.py#L17) |
| `MaturityScorer` | 1 | Compute a maturity score (0-100) for a project. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/maturity.py#L18) |
| `StructureAnalyzer` | 2 | Analyze project directory structure. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/structure.py#L90) |

**`CodeMetricsAnalyzer` methods:**

- `analyze()` — Return CodeStats dataclass.
- `get_key_modules(top_n)` — Return the top N most significant Python modules by size and complexity.

**`DependencyAnalyzer` methods:**

- `get_runtime_deps()` — Get runtime dependencies.
- `get_dev_deps()` — Get development dependencies.

**`ImportGraphAnalyzer` methods:**

- `build_graph()` — Build the import dependency graph.
- `get_hub_modules(top_n)` — Identify hub modules (high fan-in or fan-out).

**`StructureAnalyzer` methods:**

- `analyze()` — Return structure summary.
- `detect_tech_stack()` — Detect technology stack from files and markers.

### `cli` [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py)

| Function | Signature | CC | Description | Source |
|----------|-----------|----|-----------  |--------|
| `compare` | `compare(root_dir, output_path, org_name, exclude)` | 2 | Generate cross-project comparison report. | [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L264) |
| `generate` | `generate(root_dir, output_dir, org_name, org_url, ...)` | 5 | Scan projects and generate WordPress markdown articles. | [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L47) |
| `health` | `health(root_dir, output_path, org_name, exclude)` | 1 | Generate organization health report. | [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L290) |
| `inspect` | `inspect(project_dir, output, fmt)` | 3 | Inspect a single project and show its profile. | [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L234) |
| `main` | `main()` | 1 | todocs — Static-analysis documentation generator for project portfolios. | [source](https://github.com/wronai/todocs/blob/main/todocs/cli.py#L28) |

### `core` [source](https://github.com/wronai/todocs/blob/main/todocs/core.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `CodeStats` | 0 | Aggregated code statistics. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L40) |
| `MaturityProfile` | 0 | Project maturity assessment. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L70) |
| `ProjectMetadata` | 0 | Extracted project metadata. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L55) |
| `ProjectProfile` | 2 | Complete project profile for article generation. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L88) |
| `TechStack` | 0 | Detected technology stack. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L28) |

**`ProjectProfile` methods:**

- `to_dict()`
- `to_json(indent)`

| Function | Signature | CC | Description | Source |
|----------|-----------|----|-----------  |--------|
| `generate_articles` | `generate_articles(profiles, output_dir, org_name, org_url, ...)` | 6 | Generate WordPress-ready markdown articles for each project. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L279) |
| `scan_organization` | `scan_organization(root_path, exclude, max_depth, progress_callback)` | 11 ⚠️ | Scan all projects under root_path and return profiles. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L227) |
| `scan_project` | `scan_project(project_path, max_depth)` | 3 | Analyze a single project and return its profile. | [source](https://github.com/wronai/todocs/blob/main/todocs/core.py#L121) |

### `extractors` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/__init__.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ChangelogParser` | 1 | Extract structured entries from CHANGELOG.md. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/changelog_parser.py#L10) |
| `DockerParser` | 1 | Extract Docker infrastructure from Dockerfile and docker-compose.yml. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/docker_parser.py#L16) |
| `MakefileParser` | 2 | Extract targets and structure from Makefile or Taskfile.yml. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/makefile_parser.py#L16) |
| `MetadataExtractor` | 1 | Extract structured metadata from project config files. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/metadata.py#L21) |
| `ReadmeParser` | 2 | Extract structured sections from a README.md file. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/readme_parser.py#L44) |
| `ToonParser` | 6 | Parse .toon files into structured data. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/toon_parser.py#L20) |

**`MakefileParser` methods:**

- `parse()` — Parse build file and return targets with descriptions.
- `get_target_names()` — Quick access to just target names.

**`ReadmeParser` methods:**

- `parse()` — Parse README and return section_name -> content dict.
- `get_first_paragraph()` — Get the first meaningful paragraph from README.

**`ToonParser` methods:**

- `find_toon_files()` — Discover .toon files in the project root.
- `parse_all()` — Parse all discovered .toon files and return unified summary.
- `parse_map(path)` — Parse project.toon / map.toon — module listing with metadata.
- `parse_analysis(path)` — Parse analysis.toon — health, coupling, layers.
- `parse_flow(path)` — Parse flow.toon — pipeline and data-flow analysis.
- `parse_functions(path)` — Parse *.functions.toon — exported function signatures.

### `generators` [source](https://github.com/wronai/todocs/blob/main/todocs/generators/__init__.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ArticleGenerator` | 2 | Generate markdown articles for WordPress from analyzed project profiles. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article.py#L30) |
| `ComparisonGenerator` | 3 | Generate comparative analysis articles across projects. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/comparison.py#L13) |

**`ArticleGenerator` methods:**

- `generate(profile, output_path)` — Generate a single project article.
- `generate_index(profiles, output_path)` — Generate an index/overview article listing all projects.

**`ComparisonGenerator` methods:**

- `generate_comparison(profiles, output_path, title)` — Generate a comparison table article for a set of projects.
- `generate_category_articles(profiles, output_dir)` — Generate one article per category.
- `generate_health_report(profiles, output_path)` — Generate a health/quality overview report.

| Function | Signature | CC | Description | Source |
|----------|-----------|----|-----------  |--------|
| `render_api_surface` | `render_api_surface(p)` | 17 ⚠️ | Render API surface section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L247) |
| `render_architecture` | `render_architecture(p)` | 8 | Render architecture and key modules section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L118) |
| `render_build_targets` | `render_build_targets(p)` | 6 | Render build targets section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L300) |
| `render_changelog` | `render_changelog(p)` | 5 | Render recent changes section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L358) |
| `render_dependencies` | `render_dependencies(p)` | 8 | Render dependencies section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L225) |
| `render_docker` | `render_docker(p)` | 12 ⚠️ | Render Docker infrastructure section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L326) |
| `render_footer` | `render_footer(generated_at)` | 1 | Render article footer. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L423) |
| `render_frontmatter` | `render_frontmatter(p, org_name, generated_at)` | 6 | Render WordPress YAML frontmatter. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L15) |
| `render_header` | `render_header(p, org_url)` | 7 | Render title and badges section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L45) |
| `render_maturity` | `render_maturity(p)` | 3 | Render maturity assessment section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L195) |
| `render_metrics` | `render_metrics(p)` | 4 | Render code metrics section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L163) |
| `render_overview` | `render_overview(p, org_name)` | 6 | Render overview/description section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L69) |
| `render_tech_stack` | `render_tech_stack(p)` | 8 | Render technology stack section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L89) |
| `render_usage` | `render_usage(p)` | 11 ⚠️ | Render installation/usage section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L382) |

### `utils` [source](https://github.com/wronai/todocs/blob/main/todocs/utils/__init__.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `GitignoreParser` | 1 | Parse and match .gitignore patterns. | [source](https://github.com/wronai/todocs/blob/main/todocs/utils/__init__.py#L14) |

| Function | Signature | CC | Description | Source |
|----------|-----------|----|-----------  |--------|
| `create_scan_filter` | `create_scan_filter(project_path, max_depth, extra_excludes)` | 2 | Create a filter function for scanning with depth and gitignore support. | [source](https://github.com/wronai/todocs/blob/main/todocs/utils/__init__.py#L105) |

## analyzers

### `analyzers.api_surface` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/api_surface.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `APISurfaceAnalyzer` | 1 | Detect public API surface of a project. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/api_surface.py#L16) |

### `analyzers.code_metrics` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/code_metrics.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `CodeMetricsAnalyzer` | 2 | Analyze code metrics: lines, complexity, maintainability. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/code_metrics.py#L29) |

**`CodeMetricsAnalyzer` methods:**

- `analyze()` — Return CodeStats dataclass.
- `get_key_modules(top_n)` — Return the top N most significant Python modules by size and complexity.

### `analyzers.dependencies` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/dependencies.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `DependencyAnalyzer` | 2 | Extract project dependencies without executing anything. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/dependencies.py#L19) |

**`DependencyAnalyzer` methods:**

- `get_runtime_deps()` — Get runtime dependencies.
- `get_dev_deps()` — Get development dependencies.

### `analyzers.import_graph` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/import_graph.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ImportGraphAnalyzer` | 2 | Analyze import relationships between project modules. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/import_graph.py#L17) |

**`ImportGraphAnalyzer` methods:**

- `build_graph()` — Build the import dependency graph.
- `get_hub_modules(top_n)` — Identify hub modules (high fan-in or fan-out).

### `analyzers.maturity` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/maturity.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `MaturityScorer` | 1 | Compute a maturity score (0-100) for a project. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/maturity.py#L18) |

### `analyzers.structure` [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/structure.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `StructureAnalyzer` | 2 | Analyze project directory structure. | [source](https://github.com/wronai/todocs/blob/main/todocs/analyzers/structure.py#L90) |

**`StructureAnalyzer` methods:**

- `analyze()` — Return structure summary.
- `detect_tech_stack()` — Detect technology stack from files and markers.

## extractors

### `extractors.changelog_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/changelog_parser.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ChangelogParser` | 1 | Extract structured entries from CHANGELOG.md. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/changelog_parser.py#L10) |

### `extractors.docker_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/docker_parser.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `DockerParser` | 1 | Extract Docker infrastructure from Dockerfile and docker-compose.yml. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/docker_parser.py#L16) |

### `extractors.makefile_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/makefile_parser.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `MakefileParser` | 2 | Extract targets and structure from Makefile or Taskfile.yml. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/makefile_parser.py#L16) |

**`MakefileParser` methods:**

- `parse()` — Parse build file and return targets with descriptions.
- `get_target_names()` — Quick access to just target names.

### `extractors.metadata` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/metadata.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `MetadataExtractor` | 1 | Extract structured metadata from project config files. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/metadata.py#L21) |

### `extractors.readme_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/readme_parser.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ReadmeParser` | 2 | Extract structured sections from a README.md file. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/readme_parser.py#L44) |

**`ReadmeParser` methods:**

- `parse()` — Parse README and return section_name -> content dict.
- `get_first_paragraph()` — Get the first meaningful paragraph from README.

### `extractors.toon_parser` [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/toon_parser.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ToonParser` | 6 | Parse .toon files into structured data. | [source](https://github.com/wronai/todocs/blob/main/todocs/extractors/toon_parser.py#L20) |

**`ToonParser` methods:**

- `find_toon_files()` — Discover .toon files in the project root.
- `parse_all()` — Parse all discovered .toon files and return unified summary.
- `parse_map(path)` — Parse project.toon / map.toon — module listing with metadata.
- `parse_analysis(path)` — Parse analysis.toon — health, coupling, layers.
- `parse_flow(path)` — Parse flow.toon — pipeline and data-flow analysis.
- `parse_functions(path)` — Parse *.functions.toon — exported function signatures.

## generators

### `generators.article` [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ArticleGenerator` | 2 | Generate markdown articles for WordPress from analyzed project profiles. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article.py#L30) |

**`ArticleGenerator` methods:**

- `generate(profile, output_path)` — Generate a single project article.
- `generate_index(profiles, output_path)` — Generate an index/overview article listing all projects.

### `generators.article_sections` [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py)

| Function | Signature | CC | Description | Source |
|----------|-----------|----|-----------  |--------|
| `render_api_surface` | `render_api_surface(p)` | 17 ⚠️ | Render API surface section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L247) |
| `render_architecture` | `render_architecture(p)` | 8 | Render architecture and key modules section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L118) |
| `render_build_targets` | `render_build_targets(p)` | 6 | Render build targets section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L300) |
| `render_changelog` | `render_changelog(p)` | 5 | Render recent changes section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L358) |
| `render_dependencies` | `render_dependencies(p)` | 8 | Render dependencies section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L225) |
| `render_docker` | `render_docker(p)` | 12 ⚠️ | Render Docker infrastructure section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L326) |
| `render_footer` | `render_footer(generated_at)` | 1 | Render article footer. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L423) |
| `render_frontmatter` | `render_frontmatter(p, org_name, generated_at)` | 6 | Render WordPress YAML frontmatter. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L15) |
| `render_header` | `render_header(p, org_url)` | 7 | Render title and badges section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L45) |
| `render_maturity` | `render_maturity(p)` | 3 | Render maturity assessment section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L195) |
| `render_metrics` | `render_metrics(p)` | 4 | Render code metrics section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L163) |
| `render_overview` | `render_overview(p, org_name)` | 6 | Render overview/description section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L69) |
| `render_tech_stack` | `render_tech_stack(p)` | 8 | Render technology stack section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L89) |
| `render_usage` | `render_usage(p)` | 11 ⚠️ | Render installation/usage section. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/article_sections.py#L382) |

### `generators.comparison` [source](https://github.com/wronai/todocs/blob/main/todocs/generators/comparison.py)

| Class | Methods | Description | Source |
|-------|---------|-------------|--------|
| `ComparisonGenerator` | 3 | Generate comparative analysis articles across projects. | [source](https://github.com/wronai/todocs/blob/main/todocs/generators/comparison.py#L13) |

**`ComparisonGenerator` methods:**

- `generate_comparison(profiles, output_path, title)` — Generate a comparison table article for a set of projects.
- `generate_category_articles(profiles, output_dir)` — Generate one article per category.
- `generate_health_report(profiles, output_path)` — Generate a health/quality overview report.
