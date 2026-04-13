"""Base generator class with common functionality."""

from __future__ import annotations

from datetime import datetime


class BaseGenerator:
    """Base class for all generators with common initialization."""

    def __init__(self, org_name: str = "WronAI", org_url: str = "https://github.com/wronai"):
        self.org_name = org_name
        self.org_url = org_url
        self.generated_at = datetime.now().strftime("%Y-%m-%d")
