# todocs — Configuration Reference

> All options for `code2docs.yaml`

## Top-level

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `project_name` | `str` | "" | Name of the project (used in headings and badges) |
| `source` | `str` | ./ | Root directory to analyze |
| `output` | `str` | ./docs/ | Output directory for generated docs |
| `readme_output` | `str` | ./README.md | Path for the generated README file |
| `repo_url` | `str` | "" |  |
| `readme` | `ReadmeConfig` | *see `readme` section* |  |
| `docs` | `DocsConfig` | *see `docs` section* |  |
| `examples` | `ExamplesConfig` | *see `examples` section* |  |
| `sync` | `SyncConfig` | *see `sync` section* |  |
| `llm` | `LLMConfig` | *see `llm` section* |  |
| `code2llm` | `Code2LlmConfig` | *see `code2llm` section* |  |
| `verbose` | `bool` | false | Print detailed analysis info during generation |
| `exclude_tests` | `bool` | true | Exclude test files from analysis |
| `skip_private` | `bool` | false | Skip private functions/classes in output |

## `readme`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `sections` | `List` | overview, install, quickstart, generated_output, config, sync_markers, architecture, api, structure, requirements, contributing, docs_nav | README sections to include |
| `badges` | `List` | version, python, coverage, complexity | Badge types to show in README header |
| `sync_markers` | `bool` | true | Wrap generated content in `<!-- code2docs:start/end -->` markers |

## `docs`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_reference` | `bool` | true | Generate per-module API reference docs |
| `module_docs` | `bool` | true | Generate detailed module documentation |
| `architecture` | `bool` | true | Generate architecture overview with Mermaid diagrams |
| `changelog` | `bool` | true | Generate changelog from git history |

## `examples`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_generate` | `bool` | true | Auto-generate usage example files |
| `from_entry_points` | `bool` | true | Generate examples from detected entry points |

## `sync`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `strategy` | `str` | markers | Sync strategy: `markers`, `full`, or `git-diff` |
| `watch` | `bool` | false | Enable file watcher for auto-resync |
| `ignore` | `List` | tests/, __pycache__ | Glob patterns to ignore during sync |

## `llm`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | `bool` | false | Enable LLM-assisted documentation generation |
| `model` | `str` | "" | LLM model identifier (litellm format, e.g. `openai/gpt-4o-mini`, `ollama/llama3`) |
| `api_key` | `str` | "" | API key for the LLM provider (use `.env` or env var `CODE2DOCS_LLM_API_KEY`) |
| `api_base` | `str` | "" | Custom API base URL (for self-hosted or proxy endpoints) |
| `max_tokens` | `int` | 1024 | Maximum tokens per LLM call |
| `temperature` | `float` | 0.3 | Sampling temperature (low = factual, high = creative) |

## `code2llm`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | `bool` | true | Enable LLM-assisted documentation generation |
| `formats` | `List` | all |  |
| `strategy` | `str` | standard | Sync strategy: `markers`, `full`, or `git-diff` |
| `output_dir` | `str` | project |  |
| `chunk` | `bool` | false |  |
| `no_png` | `bool` | true |  |
| `max_depth` | `int` | 3 |  |
| `exclude_patterns` | `List` | venv, .venv, env, .env, node_modules, bower_components, __pycache__, .pytest_cache, .mypy_cache, .git, .hg, .svn, dist, build, target, out, .tox, .eggs, *.egg-info, vendor, third_party, third-party, site-packages, lib/python* |  |

## Example `code2docs.yaml`

```yaml
project_name: todocs
source: ./
output: ../docs/
readme_output: ./README.md
verbose: false

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  sync_markers: true

docs:
  api_reference: True
  module_docs: True
  architecture: True

examples:
  auto_generate: True
```