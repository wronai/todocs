"""Parse Docker files to extract service topology and base images."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class DockerParser:
    """Extract Docker infrastructure from Dockerfile and docker-compose.yml."""

    def __init__(self, project_path: Path):
        self.root = Path(project_path)

    def parse(self) -> Dict[str, Any]:
        """Parse all Docker-related files."""
        result: Dict[str, Any] = {
            "has_dockerfile": False,
            "has_compose": False,
            "base_images": [],
            "services": [],
            "exposed_ports": [],
            "volumes": [],
        }

        # Parse Dockerfile(s)
        for df in self._find_dockerfiles():
            result["has_dockerfile"] = True
            df_data = self._parse_dockerfile(df)
            result["base_images"].extend(df_data.get("base_images", []))
            result["exposed_ports"].extend(df_data.get("ports", []))

        # Parse docker-compose
        for cf in self._find_compose_files():
            result["has_compose"] = True
            compose_data = self._parse_compose(cf)
            result["services"].extend(compose_data.get("services", []))
            result["volumes"].extend(compose_data.get("volumes", []))

        # Deduplicate
        result["base_images"] = list(dict.fromkeys(result["base_images"]))
        result["exposed_ports"] = list(dict.fromkeys(result["exposed_ports"]))

        return result

    def _find_dockerfiles(self) -> List[Path]:
        """Find all Dockerfiles in project root."""
        found = []
        for p in self.root.iterdir():
            if p.is_file() and p.name.startswith("Dockerfile"):
                found.append(p)
        # Also check docker/ subdirectory
        docker_dir = self.root / "docker"
        if docker_dir.is_dir():
            for p in docker_dir.iterdir():
                if p.is_file() and p.name.startswith("Dockerfile"):
                    found.append(p)
        return found

    def _find_compose_files(self) -> List[Path]:
        """Find docker-compose files."""
        names = [
            "docker-compose.yml", "docker-compose.yaml",
            "docker-compose.dev.yml", "docker-compose.test.yml",
            "docker-compose.prod.yml",
        ]
        return [self.root / n for n in names if (self.root / n).exists()]

    def _parse_dockerfile(self, path: Path) -> Dict[str, Any]:
        """Extract FROM images, EXPOSE ports, ENTRYPOINT from Dockerfile."""
        text = self._read_dockerfile(path)
        if text is None:
            return {}

        result = self._extract_from_images(text)
        result["ports"] = self._extract_exposed_ports(text)
        result["entrypoint"] = self._extract_entrypoint(text)
        result["cmd"] = self._extract_cmd(text)
        result["dockerfile"] = path.name

        return result

    def _read_dockerfile(self, path: Path) -> str | None:
        """Read Dockerfile content, returning None on error."""
        try:
            return path.read_text(errors="replace")
        except Exception:
            return None

    def _extract_from_images(self, text: str) -> Dict[str, List[str]]:
        """Extract base images from FROM instructions."""
        images = []
        for line in self._iter_instructions(text):
            from_m = re.match(r"FROM\s+(\S+)", line, re.IGNORECASE)
            if from_m:
                img = self._clean_image_name(from_m.group(1))
                images.append(img)
        return {"base_images": images}

    def _clean_image_name(self, raw: str) -> str:
        """Strip --platform flags and AS aliases from image name."""
        cleaned = re.sub(r"--platform=\S+\s+", "", raw)
        return cleaned.split(" AS ")[0].split(" as ")[0].strip()

    def _extract_exposed_ports(self, text: str) -> List[str]:
        """Extract exposed ports from EXPOSE instructions."""
        ports = []
        for line in self._iter_instructions(text):
            expose_m = re.match(r"EXPOSE\s+(.+)", line, re.IGNORECASE)
            if expose_m:
                for port in expose_m.group(1).split():
                    ports.append(port.split("/")[0])
        return ports

    def _extract_entrypoint(self, text: str) -> str:
        """Extract ENTRYPOINT command."""
        for line in self._iter_instructions(text):
            entry_m = re.match(r"ENTRYPOINT\s+(.+)", line, re.IGNORECASE)
            if entry_m:
                return entry_m.group(1).strip()
        return ""

    def _extract_cmd(self, text: str) -> str:
        """Extract CMD command."""
        for line in self._iter_instructions(text):
            cmd_m = re.match(r"CMD\s+(.+)", line, re.IGNORECASE)
            if cmd_m:
                return cmd_m.group(1).strip()
        return ""

    def _iter_instructions(self, text: str):
        """Yield non-empty, non-comment lines from Dockerfile."""
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                yield line

    def _parse_compose(self, path: Path) -> Dict[str, Any]:
        """Extract services, ports, volumes from docker-compose.yml."""
        if not HAS_YAML:
            return {"services": [], "volumes": []}

        try:
            data = yaml.safe_load(path.read_text(errors="replace"))
        except Exception:
            return {"services": [], "volumes": []}

        if not isinstance(data, dict):
            return {"services": [], "volumes": []}

        services = []
        raw_services = data.get("services", {})

        for name, svc in raw_services.items():
            if not isinstance(svc, dict):
                continue

            svc_info: Dict[str, Any] = {"name": name}
            svc_info["image"] = svc.get("image", "")
            svc_info["build"] = bool(svc.get("build"))

            # Ports
            ports_raw = svc.get("ports", [])
            svc_info["ports"] = [str(p) for p in ports_raw[:5]]

            # Environment variables (just count, don't expose values)
            env = svc.get("environment", {})
            if isinstance(env, list):
                svc_info["env_count"] = len(env)
            elif isinstance(env, dict):
                svc_info["env_count"] = len(env)
            else:
                svc_info["env_count"] = 0

            # Depends on
            svc_info["depends_on"] = []
            deps = svc.get("depends_on", [])
            if isinstance(deps, list):
                svc_info["depends_on"] = deps
            elif isinstance(deps, dict):
                svc_info["depends_on"] = list(deps.keys())

            # Volumes
            svc_info["volumes"] = [str(v).split(":")[0] for v in svc.get("volumes", [])[:5]]

            services.append(svc_info)

        # Top-level volumes
        volumes = list((data.get("volumes") or {}).keys())

        return {"services": services, "volumes": volumes, "source": path.name}
