"""Core data models and orchestration for todocs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from todocs.analyzers.structure import StructureAnalyzer
from todocs.analyzers.code_metrics import CodeMetricsAnalyzer
from todocs.analyzers.dependencies import DependencyAnalyzer
from todocs.analyzers.maturity import MaturityScorer
from todocs.analyzers.import_graph import ImportGraphAnalyzer
from todocs.analyzers.api_surface import APISurfaceAnalyzer
from todocs.extractors.metadata import MetadataExtractor
from todocs.extractors.readme_parser import ReadmeParser
from todocs.extractors.changelog_parser import ChangelogParser
from todocs.extractors.toon_parser import ToonParser
from todocs.extractors.makefile_parser import MakefileParser
from todocs.extractors.docker_parser import DockerParser
from todocs.generators.article import ArticleGenerator
from todocs.utils import create_scan_filter


@dataclass
class TechStack:
    """Detected technology stack."""
    primary_language: str = "unknown"
    languages: Dict[str, int] = field(default_factory=dict)  # lang -> file count
    frameworks: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    test_frameworks: List[str] = field(default_factory=list)
    ci_cd: List[str] = field(default_factory=list)
    containerization: List[str] = field(default_factory=list)


@dataclass
class CodeStats:
    """Aggregated code statistics."""
    total_files: int = 0
    total_lines: int = 0
    source_files: int = 0
    source_lines: int = 0
    test_files: int = 0
    test_lines: int = 0
    avg_complexity: float = 0.0
    max_complexity: float = 0.0
    hotspots: List[Dict[str, Any]] = field(default_factory=list)  # high-CC functions
    maintainability_index: float = 0.0


@dataclass
class ProjectMetadata:
    """Extracted project metadata."""
    name: str = ""
    version: str = ""
    description: str = ""
    license: str = ""
    authors: List[str] = field(default_factory=list)
    homepage: str = ""
    repository: str = ""
    keywords: List[str] = field(default_factory=list)
    python_requires: str = ""
    entry_points: Dict[str, str] = field(default_factory=dict)


@dataclass
class MaturityProfile:
    """Project maturity assessment."""
    score: float = 0.0  # 0-100
    grade: str = "F"
    has_tests: bool = False
    has_ci: bool = False
    has_docs: bool = False
    has_changelog: bool = False
    has_license: bool = False
    has_examples: bool = False
    has_docker: bool = False
    has_makefile: bool = False
    has_version_file: bool = False
    test_ratio: float = 0.0  # test_lines / source_lines
    doc_completeness: float = 0.0  # 0-1


@dataclass
class ProjectProfile:
    """Complete project profile for article generation."""
    path: Path = field(default_factory=Path)
    name: str = ""
    metadata: ProjectMetadata = field(default_factory=ProjectMetadata)
    tech_stack: TechStack = field(default_factory=TechStack)
    code_stats: CodeStats = field(default_factory=CodeStats)
    maturity: MaturityProfile = field(default_factory=MaturityProfile)
    structure: Dict[str, Any] = field(default_factory=dict)
    readme_sections: Dict[str, str] = field(default_factory=dict)
    changelog_entries: List[Dict[str, str]] = field(default_factory=list)
    key_modules: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)
    category: str = "uncategorized"
    summary: str = ""
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # New v0.2 fields
    toon_data: Dict[str, Any] = field(default_factory=dict)
    makefile_targets: List[Dict[str, str]] = field(default_factory=list)
    docker_info: Dict[str, Any] = field(default_factory=dict)
    import_graph: Dict[str, Any] = field(default_factory=dict)
    api_surface: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["path"] = str(self.path)
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def scan_project(project_path: Path, max_depth: int = 3) -> ProjectProfile:
    """Analyze a single project and return its profile.

    Args:
        project_path: Path to the project directory
        max_depth: Maximum directory depth to scan (default: 3)
    """
    profile = ProjectProfile(path=project_path, name=project_path.name)

    # Create scan filter with depth limit and gitignore support
    scan_filter = create_scan_filter(project_path, max_depth=max_depth)

    # 1. Extract metadata from pyproject.toml / setup.py / setup.cfg
    meta_ext = MetadataExtractor(project_path)
    profile.metadata = meta_ext.extract()

    # 2. Analyze directory structure (with filter)
    struct_analyzer = StructureAnalyzer(project_path, filter_func=scan_filter)
    profile.structure = struct_analyzer.analyze()
    profile.tech_stack = struct_analyzer.detect_tech_stack()

    # 3. Code metrics (AST + radon) (with filter)
    metrics_analyzer = CodeMetricsAnalyzer(project_path, filter_func=scan_filter)
    profile.code_stats = metrics_analyzer.analyze()
    profile.key_modules = metrics_analyzer.get_key_modules(top_n=10)

    # 4. Dependencies
    dep_analyzer = DependencyAnalyzer(project_path)
    profile.dependencies = dep_analyzer.get_runtime_deps()
    profile.dev_dependencies = dep_analyzer.get_dev_deps()

    # 5. Parse README for sections
    readme_parser = ReadmeParser(project_path)
    profile.readme_sections = readme_parser.parse()

    # 6. Parse CHANGELOG
    cl_parser = ChangelogParser(project_path)
    profile.changelog_entries = cl_parser.parse(max_entries=5)

    # 7. Parse .toon files (if present)
    toon_parser = ToonParser(project_path)
    toon_files = toon_parser.find_toon_files()
    if toon_files:
        profile.toon_data = toon_parser.parse_all()

    # 8. Parse Makefile / Taskfile
    mk_parser = MakefileParser(project_path)
    mk_data = mk_parser.parse()
    profile.makefile_targets = mk_data.get("targets", [])

    # 9. Parse Docker infrastructure
    docker_parser = DockerParser(project_path)
    profile.docker_info = docker_parser.parse()

    # 10. Import graph (Python projects only) (with filter)
    if profile.tech_stack.primary_language == "python":
        ig = ImportGraphAnalyzer(project_path, filter_func=scan_filter)
        profile.import_graph = ig.build_graph()

    # 11. API surface detection (with filter)
    api_analyzer = APISurfaceAnalyzer(project_path, filter_func=scan_filter)
    profile.api_surface = api_analyzer.analyze()

    # 12. Maturity scoring (after all data collected)
    scorer = MaturityScorer(project_path, profile)
    profile.maturity = scorer.score()

    # 13. Auto-categorize
    profile.category = _categorize(profile)

    # 14. Generate summary sentence
    profile.summary = _generate_summary(profile)

    return profile


def _discover_projects(root_path: Path, exclude: Optional[List[str]] = None) -> List[Path]:
    """Discover project directories without scanning them.

    Returns a list of project directory paths that look like valid projects
    (have README.md, pyproject.toml, etc.)
    """
    exclude = set(exclude or [])
    exclude.update({
        "venv", ".venv", "node_modules", "__pycache__", ".git",
        "sandbox", "comparison_output", "recordings",
    })

    project_dirs = []
    root = Path(root_path)

    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name in exclude:
            continue
        # Heuristic: a project directory has README.md or pyproject.toml or Makefile
        markers = {"README.md", "pyproject.toml", "setup.py", "Makefile", "package.json", "Cargo.toml"}
        if not any((child / m).exists() for m in markers):
            continue

        project_dirs.append(child)

    return project_dirs


def scan_organization(
    root_path: Path,
    exclude: Optional[List[str]] = None,
    max_depth: int = 3,
    progress_callback = None
) -> List[ProjectProfile]:
    """Scan all projects under root_path and return profiles.

    Args:
        root_path: Root directory containing project subdirectories
        exclude: Additional directory names to exclude
        max_depth: Maximum directory depth to scan within each project
        progress_callback: Optional callback(project_name, index, total) called for each project
    """
    exclude = set(exclude or [])
    exclude.update({
        "venv", ".venv", "node_modules", "__pycache__", ".git",
        "sandbox", "comparison_output", "recordings",
    })

    profiles = []
    root = Path(root_path)

    # Collect project directories first
    project_dirs = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name in exclude:
            continue
        # Heuristic: a project directory has README.md or pyproject.toml or Makefile
        markers = {"README.md", "pyproject.toml", "setup.py", "Makefile", "package.json", "Cargo.toml"}
        if not any((child / m).exists() for m in markers):
            continue

        project_dirs.append(child)

    # Scan each project with progress callback
    total = len(project_dirs)
    for idx, child in enumerate(project_dirs, 1):
        if progress_callback:
            progress_callback(child.name, idx, total)

        try:
            profile = scan_project(child, max_depth=max_depth)
            profiles.append(profile)
        except Exception as e:
            print(f"[WARN] Failed to analyze {child.name}: {e}")

    return profiles


def generate_articles(
    profiles: List[ProjectProfile],
    output_dir: Path,
    org_name: str = "WronAI",
    org_url: str = "https://github.com/wronai",
    include_comparison: bool = True,
    include_categories: bool = True,
    include_health: bool = True,
) -> List[Path]:
    """Generate WordPress-ready markdown articles for each project."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = ArticleGenerator(org_name=org_name, org_url=org_url)
    paths = []

    for profile in profiles:
        article_path = output_dir / f"{profile.name}.md"
        generator.generate(profile, article_path)
        paths.append(article_path)

    # Index article
    index_path = output_dir / "_index.md"
    generator.generate_index(profiles, index_path)
    paths.insert(0, index_path)

    # Comparison, category, and health articles
    if len(profiles) >= 2:
        from todocs.generators.comparison import ComparisonGenerator
        comp_gen = ComparisonGenerator(org_name=org_name, org_url=org_url)

        if include_comparison:
            comp_path = output_dir / "_comparison.md"
            comp_gen.generate_comparison(profiles, comp_path)
            paths.append(comp_path)

        if include_categories:
            cat_paths = comp_gen.generate_category_articles(profiles, output_dir)
            paths.extend(cat_paths)

        if include_health:
            health_path = output_dir / "_health-report.md"
            comp_gen.generate_health_report(profiles, health_path)
            paths.append(health_path)

    return paths


# --- Internal helpers ---

_CATEGORY_KEYWORDS = {
    "llm": (["llm", "ai", "agent", "model", "benchmark", "ollama", "rag", "intent", "ellma"], "LLM & AI Agents"),
    "devops": (["docker", "dockfra", "clonebox", "deploy", "infra", "mcp", "pactown", "projektor"], "DevOps & Infrastructure"),
    "nlp": (["nlp", "voice", "stts", "speech", "text2", "stt", "tts"], "NLP & Voice Interfaces"),
    "analysis": (["code2", "devix", "weekly", "ats", "ocr", "pactfix", "nfo"], "Code Analysis & Processing"),
    "repair": (["fix", "heal", "xnv"], "System & Repair Tools"),
    "framework": (["markpact", "marksync", "streamware", "toonic", "contract"], "Frameworks & DSL"),
    "devtool": (["devmentor", "getv", "goal", "clickmd", "domd"], "Developer Tools"),
    "platform": (["pactown-com", "docs-pactown", "blog-pactown"], "Pactown Platform"),
}


def _categorize(profile: ProjectProfile) -> str:
    name_lower = profile.name.lower()
    desc_lower = (profile.metadata.description or "").lower()
    combined = f"{name_lower} {desc_lower}"

    for _key, (keywords, category) in _CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return category

    # Fallback: inspect dependencies
    all_deps = " ".join(profile.dependencies).lower()
    if any(k in all_deps for k in ["torch", "transformers", "ollama", "litellm"]):
        return "LLM & AI Agents"
    if any(k in all_deps for k in ["docker", "kubernetes", "ansible"]):
        return "DevOps & Infrastructure"

    return "Uncategorized"


def _generate_summary(profile: ProjectProfile) -> str:
    """Generate a summary sentence from available data without LLM."""
    meta = profile.metadata
    stats = profile.code_stats
    mat = profile.maturity

    name = meta.name or profile.name
    desc = meta.description or ""
    lang = profile.tech_stack.primary_language.capitalize()

    if desc:
        base = f"{name} — {desc}"
    else:
        base = f"{name} is a {lang} project"

    parts = [base]

    if stats.source_files > 0:
        parts.append(f"comprising {stats.source_files} source files ({stats.source_lines:,} lines)")

    if mat.has_tests and stats.test_files > 0:
        parts.append(f"with {stats.test_files} test files")

    if mat.grade:
        parts.append(f"at maturity grade {mat.grade}")

    return ", ".join(parts) + "."
