"""todocs — Static-analysis documentation generator for project portfolios.

Generates WordPress-ready markdown articles from source code analysis,
metadata extraction, and NLP-based summarization — no LLM required.
"""

__version__ = "0.1.8"
__all__ = ["scan_organization", "generate_articles", "ProjectProfile"]

from todocs.core import scan_organization, generate_articles, ProjectProfile
