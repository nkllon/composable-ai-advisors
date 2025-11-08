from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .models import DomainModelFormat


class ModelLoader:
	"""Loads domain model files from filesystem (skeleton)."""

	def __init__(self, base_dir: Path = Path(".mcp/domain-models")):
		self.base_dir = base_dir

	async def load_file(self, file_path: str) -> Tuple[str, DomainModelFormat]:
		"""Load a domain model file and detect format (skeleton)."""
		raise NotImplementedError

	async def load_multiple(self, file_paths: List[str]) -> List[Tuple[str, DomainModelFormat]]:
		"""Load multiple domain model files concurrently (skeleton)."""
		raise NotImplementedError

	def detect_format(self, file_path: str) -> DomainModelFormat:
		"""Detect format based on file extension (skeleton)."""
		raise NotImplementedError

	def resolve_path(self, file_path: str) -> Path:
		"""Resolve absolute or relative path (skeleton)."""
		raise NotImplementedError


