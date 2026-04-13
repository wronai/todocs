"""CLI interface for todocs — generate project documentation articles."""

from __future__ import annotations

import sys

try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click", file=sys.stderr)
    sys.exit(1)

from .utils import HAS_RICH
from .commands import (
    generate,
    inspect,
    compare,
    health,
    readme,
    status,
    cards,
    index,
    export_cmd,
)

__version__ = "0.1.7"


@click.group()
@click.version_option(version=__version__, prog_name="todocs")
def main():
    """todocs — Static-analysis documentation generator for project portfolios.

    Generates WordPress-ready markdown articles from source code analysis.
    No LLM required.
    """
    pass


# Register all commands
main.add_command(generate)
main.add_command(inspect)
main.add_command(compare)
main.add_command(health)
main.add_command(readme)
main.add_command(status)
main.add_command(cards)
main.add_command(index)
main.add_command(export_cmd, name="export")


if __name__ == "__main__":
    main()
