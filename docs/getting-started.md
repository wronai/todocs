# Getting Started with todocs

## Prerequisites

- Python >=3.9
- pip (or your preferred package manager)

## Installation

```bash
pip install .
```

To install from source:

```bash
git clone <repository-url>
cd todocs
pip install -e .
```

## Quick Start

### Command Line

```bash
# Generate full documentation for your project
todocs ./path/to/your/project

# Preview what would be generated (no file writes)
todocs ./path/to/your/project --dry-run

# Only regenerate README
todocs ./path/to/your/project --readme-only
```

### Python API

```python
from utils import create_scan_filter

# Create a filter function for scanning with depth and gitignore support.
result = create_scan_filter("project_path", max_depth=..., extra_excludes=...)
```

## What's Next

- 📖 [API Reference](api.md) — Full function and class documentation
- 🏗️ [Architecture](architecture.md) — System design and module relationships
- 📊 [Coverage Report](coverage.md) — Docstring coverage analysis
- 🔗 [Dependency Graph](dependency-graph.md) — Module dependency visualization
