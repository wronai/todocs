# Refactoring Plan: code2docs ↔ todocs

> Status: In Progress | Created: 2026-03-08 | Updated: 2026-03-08

## Current State

Both scopes live in one `code2docs` package (64 files, 9010 lines).
`todocs` has been extracted as a standalone package (Phase 3 ✅).

## Responsibility Split

### code2docs — single-project documentation
> "Generate full documentation for THIS repository"

| Module | Role |
|--------|------|
| readme_gen | README.md from analysis |
| api_reference_gen | docs/api.md |
| module_docs_gen | docs/modules.md |
| architecture_gen | docs/architecture.md + Mermaid |
| examples_gen | examples/ from API signatures |
| getting_started_gen | docs/getting-started.md |
| contributing_gen | CONTRIBUTING.md |
| coverage_gen | docs/coverage.md |
| depgraph_gen | docs/dependency-graph.md |
| changelog_gen | CHANGELOG.md from git log |
| api_changelog_gen | API changelog from diffs |
| config_docs_gen | docs/configuration.md |
| code2llm_gen | code2llm analysis → project/ |
| mkdocs_gen | mkdocs.yml |

**Infrastructure**: analyzers/, formatters/, sync/, config.py, registry.py, cli.py, llm_helper.py

### todocs — multi-project organization overview
> "Summarize all projects in THIS folder/organization"

| Module | Role | Status |
|--------|------|--------|
| article.py | WordPress-ready project articles | ✅ |
| article_sections.py | Section renderers | ✅ |
| comparison.py | Cross-project comparison | ✅ |
| project_card_gen.py | Single project card (WordPress) | ✅ |
| org_index_gen.py | Organization index.md/catalog | ✅ |
| status_report_gen.py | Organization status report | ✅ |
| formatters/table_formatter.py | Comparative project tables | ✅ |
| outputs/markdown.py | WordPress-ready Markdown output | ✅ |
| outputs/html.py | HTML output | ✅ |
| outputs/json.py | JSON output (API/dashboards) | ✅ |

## Overlaps & Duplicates

### 2.1 Shared code2llm dependency
Both use `code2llm.api.analyze()` / `AnalysisResult`:
- **code2docs**: via ProjectScanner → full single-project analysis
- **todocs** (formerly org_readme_gen): via `_analyze_project()` → simplified multi-project analysis

**Current todocs status**: No code2llm dependency — uses own static analysis pipeline.

### 2.2 Project description extraction
`_extract_description()` (CC=17) duplicated fragments from ReadmeGenerator._extract_project_metadata() (CC=29).

**Current todocs status**: Uses own `MetadataExtractor` — independent implementation.

### 2.3 Shared formatters
Both use MarkdownFormatter, badges, toc — todocs needs only a subset.

### 2.4 Config
`Code2DocsConfig` contains config for both single-project and org-level. `org_name` in CLI switches mode.

### 2.5 CLI
`generate --org-name` activates OrgReadmeAdapter — mixing two modes.

## Refactoring Phases

### Phase 1: Extract shared core → code2docs-core ❌ Blocked (needs code2docs repo)

```
code2docs-core/
├── project_metadata.py    ← shared description/version/URL extraction
├── analysis_bridge.py     ← quick_analyze + full_analyze
├── formatters/
│   ├── markdown.py
│   └── badges.py
└── llm_helper.py
```

### Phase 2: Clean up code2docs ❌ Blocked (needs code2docs repo)

- ReadmeGenerator → delegates to core.extract_project_info()
- Remove OrgReadmeGenerator, OrgReadmeAdapter
- Remove --org-name from CLI
- Remove org-level config fields

### Phase 3: todocs as standalone package ✅ DONE

Current todocs structure:
```
todocs/
├── analyzers/          (6 modules)
├── extractors/         (6 modules)
├── generators/         (6 modules: article, article_sections, comparison,
│                        project_card_gen, status_report_gen, org_index_gen)
├── formatters/         (table_formatter)
├── outputs/            (markdown, html, json)
├── utils/              (gitignore parser)
├── core.py             (data models + orchestration)
└── cli.py              (9 commands: generate, inspect, compare, health,
                         readme, status, cards, index, export)
```

Completed work:
- [x] Add project_card_gen, status_report_gen, org_index_gen
- [x] Add table_formatter
- [x] Add output format modules (markdown, html, json)
- [x] Wire into CLI (status, cards, index, export commands)

### Phase 4: Reduce high CC ✅ DONE

All 8 methods with CC≥15 refactored below 15. Results:

| Method | Before | After | Strategy |
|--------|--------|-------|----------|
| DependencyAnalyzer.get_dev_deps | 18 | 4 | Extract _deduplicate, _deps_from_requirements, _deps_from_package_json, _pyproject_dev_deps |
| ComparisonGenerator._render_health_report | 18 | 7 | Extract _health_executive_summary, _health_grade_distribution, _health_projects_needing_attention, _health_top_performers |
| render_api_surface | 17 | 7 | Extract _render_entry_points, _render_cli_commands, _render_rest_endpoints, _render_public_classes |
| CodeMetricsAnalyzer._parse_module_ast | 17 | 8 | Extract _extract_module_docstring, _extract_imports |
| DependencyAnalyzer.get_runtime_deps | 17 | 4 | Shared helpers with get_dev_deps |
| CodeMetricsAnalyzer.analyze | 16 | 8 | Extract _collect_complexity_data, _collect_radon_metrics, _collect_ast_fallback |
| ComparisonGenerator._render_readme_list | 16 | 5 | Extract _readme_summary_table, _project_features, _readme_project_section |
| ImportGraphAnalyzer.build_graph | 15 | 9 | Extract _parse_file_imports, _resolve_relative_import, _build_fan_metrics |

Max CC remaining: 14 (ComparisonGenerator._render_category, MaturityScorer.score)

### Phase 5: Break dependency cycles ❌ Pertains to code2docs

### Phase 1/2 Feasibility Assessment (code2docs repo found)

**code2docs repo**: `/home/tom/github/wronai/code2docs` (v3.0.9)

**Architecture**: code2docs depends on `code2llm` for analysis, uses a `BaseGenerator` + `GeneratorRegistry` pattern. 14 generators, formatters, sync/watcher, LLM helper.

**Overlap analysis**:

| Area | code2docs | todocs | Shared potential |
|------|-----------|--------|------------------|
| Dependency scanning | `DependencyScanner` (richer, returns `DependencyInfo` dataclass) | `DependencyAnalyzer` (simpler, returns `List[str]`) | Medium — different granularity |
| Project metadata | Via `code2llm.api.AnalysisResult` | Own `MetadataExtractor` | Low — different data sources |
| Markdown formatting | `formatters/markdown.py`, `badges.py`, `toc.py` | Inline in generators | Low — todocs is simpler |
| Config | `Code2DocsConfig` dataclass | Minimal (CLI args only) | None |
| CLI | `click`-based, single `generate` + sub-modes | `click`-based, 9 commands | None — distinct UIs |

**Assessment**:
- **Phase 1 (shared core)**: Low priority. The overlap is limited to dependency scanning and some formatting utilities. The packages use different analysis backends (`code2llm` vs todocs' own AST-based pipeline). Extracting a shared core would add coupling for minimal dedup (~100 LOC).
- **Phase 2 (clean code2docs)**: Independent of todocs. The `OrgReadmeGenerator`/`OrgReadmeAdapter` in code2docs can be deprecated in favor of todocs, but this is a code2docs-side change.
- **Recommendation**: Keep packages independent. Phase 1 is not cost-effective. Phase 2 can proceed as a code2docs cleanup task (remove org-level code, point users to todocs for multi-project docs).

## Complementarity Matrix (post-refactoring)

| Function | code2docs-core | code2docs | todocs |
|----------|---------------|-----------|--------|
| Project metadata extraction | ✅ | — | — |
| MarkdownFormatter | ✅ | — | — |
| LLM Helper | ✅ | — | — |
| code2llm bridge | ✅ | — | — |
| Single-project README | — | ✅ | — |
| API reference | — | ✅ | — |
| Module/architecture docs | — | ✅ | — |
| Sync/Watch | — | ✅ | — |
| Multi-project discovery | — | — | ✅ |
| Multi-project analysis | — | — | ✅ |
| Organization README | — | — | ✅ |
| Project cards (WP) | — | — | ✅ |
| Status reports | — | — | ✅ |
| Comparative tables | — | — | ✅ |

## Impact Estimates

| Metric | Before | After |
|--------|--------|-------|
| CC̄ code2docs | 4.2 | ~3.0 |
| Methods CC>15 | 10 | 0 |
| Dependency cycles | 1 | 0 |
| Duplicated logic | ~200 LOC | 0 |
| Packages | 1 (monolith) | 2 (code2docs + todocs) — shared core not justified |
