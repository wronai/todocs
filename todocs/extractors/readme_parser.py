"""Parse README.md into structured sections using regex-based markdown parsing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional


_SECTION_ALIASES = {
    "install": "installation",
    "installing": "installation",
    "setup": "installation",
    "getting started": "installation",
    "quick start": "usage",
    "quickstart": "usage",
    "how to use": "usage",
    "examples": "usage",
    "example": "usage",
    "usage": "usage",
    "features": "features",
    "api": "api",
    "api reference": "api",
    "configuration": "configuration",
    "config": "configuration",
    "contributing": "contributing",
    "contribute": "contributing",
    "license": "license",
    "licence": "license",
    "architecture": "architecture",
    "design": "architecture",
    "roadmap": "roadmap",
    "todo": "roadmap",
    "changelog": "changelog",
    "changes": "changelog",
    "description": "description",
    "overview": "description",
    "about": "description",
    "introduction": "description",
    "what is": "description",
}


class ReadmeParser:
    """Extract structured sections from a README.md file."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

    def parse(self) -> Dict[str, str]:
        """Parse README and return section_name -> content dict."""
        readme_path = self._find_readme()
        if not readme_path:
            return {}

        try:
            text = readme_path.read_text(errors="replace")
        except Exception:
            return {}

        return self._parse_sections(text)

    def _find_readme(self) -> Optional[Path]:
        for name in ["README.md", "readme.md", "Readme.md", "README.rst", "README.txt", "README"]:
            fp = self.root / name
            if fp.exists():
                return fp
        return None

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Split markdown by headings into sections."""
        sections: Dict[str, str] = {}

        # Extract description: text before first heading, OR text between h1 and first h2
        lines = text.split("\n")

        # Strategy 1: text before any heading
        preamble = []
        for line in lines:
            if re.match(r"^#{1,3}\s", line):
                break
            if line.strip() and not line.strip().startswith("[![") and not line.strip().startswith("[!"):
                preamble.append(line)

        # Strategy 2: text between first h1 and first h2/h3
        post_h1 = []
        found_h1 = False
        for line in lines:
            if re.match(r"^#\s", line) and not found_h1:
                found_h1 = True
                continue
            if found_h1:
                if re.match(r"^#{1,3}\s", line):
                    break
                if line.strip() and not line.strip().startswith("[![") and not line.strip().startswith("[!"):
                    post_h1.append(line)

        # Use whichever has more content
        desc_lines = preamble if len(preamble) >= len(post_h1) else post_h1
        desc_text = "\n".join(desc_lines).strip()
        if desc_text:
            desc_text = re.sub(r"\*\*(.+?)\*\*", r"\1", desc_text)
            desc_text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", desc_text)
            sections["description"] = desc_text[:500]

        # Now parse heading-based sections
        heading_pattern = re.compile(r"^(#{1,3})\s+(.+)", re.MULTILINE)
        matches = list(heading_pattern.finditer(text))

        for i, m in enumerate(matches):
            level = len(m.group(1))
            title = m.group(2).strip()
            title_lower = re.sub(r"[^a-z0-9\s]", "", title.lower()).strip()

            # Map to canonical section name
            canonical = _SECTION_ALIASES.get(title_lower, title_lower)

            # Get content until next heading of same or higher level
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()

            # Limit content size
            if len(content) > 1000:
                content = content[:1000] + "..."

            if canonical and content:
                # Don't overwrite if we already have a shorter section name
                if canonical not in sections:
                    sections[canonical] = content

        return sections

    def get_first_paragraph(self) -> str:
        """Get the first meaningful paragraph from README."""
        sections = self.parse()
        desc = sections.get("description", "")
        if desc:
            # Return first paragraph
            paras = desc.split("\n\n")
            return paras[0].strip() if paras else ""
        return ""
