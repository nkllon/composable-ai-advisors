from __future__ import annotations

import asyncio
from pathlib import Path
from typing import List, Tuple

import aiofiles

from .models import DomainModelFormat


class ModelLoader:
        """Loads domain model files from the filesystem."""

        def __init__(self, base_dir: Path = Path(".mcp/domain-models")):
                self.base_dir = base_dir

        async def load_file(self, file_path: str) -> Tuple[str, DomainModelFormat, Path]:
                """Load a domain model file and detect its format."""

                resolved_path = self.resolve_path(file_path)
                fmt = self.detect_format(resolved_path.name)

                async with aiofiles.open(resolved_path, "r", encoding="utf-8") as handle:
                        content = await handle.read()

                return content, fmt, resolved_path

        async def load_multiple(self, file_paths: List[str]) -> List[Tuple[str, DomainModelFormat, Path]]:
                """Load multiple domain model files concurrently."""

                tasks = [self.load_file(path) for path in file_paths]
                return await asyncio.gather(*tasks)

        def detect_format(self, file_path: str) -> DomainModelFormat:
                """Detect format based on file extension."""

                suffix = Path(file_path).suffix.lower()
                if suffix in {".ttl", ".turtle"}:
                        return DomainModelFormat.TURTLE
                if suffix == ".json":
                        return DomainModelFormat.JSON
                if suffix in {".md", ".markdown", ".mkd"}:
                        return DomainModelFormat.MARKDOWN
                raise ValueError(f"Unsupported domain model format for file: {file_path}")

        def resolve_path(self, file_path: str) -> Path:
                """Resolve an absolute or relative domain model path."""

                candidate = Path(file_path)
                if not candidate.is_absolute():
                        candidate = (self.base_dir / candidate).resolve()

                if not candidate.exists():
                        raise FileNotFoundError(f"Domain model file not found: {candidate}")

                return candidate


