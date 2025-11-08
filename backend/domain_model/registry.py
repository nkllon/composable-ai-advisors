from __future__ import annotations

from typing import Dict, List, Optional

from .models import DomainModel, DomainModelMetadata


class ModelRegistry:
	"""Registry of loaded domain models (skeleton)."""

	def __init__(self):
		self.models: Dict[str, DomainModel] = {}
		self.version_history: Dict[str, Dict[str, DomainModel]] = {}

	def register(self, model: DomainModel) -> None:
		"""Register a domain model (skeleton)."""
		raise NotImplementedError

	def get(self, domain_id: str, version: Optional[str] = None) -> Optional[DomainModel]:
		"""Get a domain model by ID and optional version (skeleton)."""
		raise NotImplementedError

	def list_all(self) -> List[DomainModelMetadata]:
		"""List all registered domain models (skeleton)."""
		raise NotImplementedError

	def get_versions(self, domain_id: str) -> List[str]:
		"""Get all versions of a domain model (skeleton)."""
		raise NotImplementedError


