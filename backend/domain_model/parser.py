from __future__ import annotations

from typing import Any, Tuple

from .models import DomainModel, DomainModelFormat, DomainModelMetadata


class BaseParser:
	"""Base class for domain model parsers (skeleton)."""

	def parse(self, content: str, file_path: str) -> Tuple[Any, DomainModelMetadata]:
		"""Parse domain model content and extract metadata (skeleton)."""
		raise NotImplementedError


class ModelParser:
	"""Main parser dispatcher (skeleton)."""

	def parse(self, content: str, fmt: DomainModelFormat, file_path: str) -> DomainModel:
		"""Parse domain model content using appropriate parser (skeleton)."""
		raise NotImplementedError


