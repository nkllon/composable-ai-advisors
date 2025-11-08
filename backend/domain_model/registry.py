from __future__ import annotations

from typing import Dict, List, Optional

from .models import DomainModel, DomainModelMetadata


class ModelRegistry:
    """Registry of loaded domain models."""

    def __init__(self) -> None:
        self.models: Dict[str, DomainModel] = {}
        self.version_history: Dict[str, Dict[str, DomainModel]] = {}

    def register(self, model: DomainModel) -> None:
        """Register a domain model, keeping track of version history."""

        metadata = model.metadata
        domain_id = metadata.domain_id
        version = metadata.version

        history = self.version_history.setdefault(domain_id, {})
        history[version] = model

        current = self.models.get(domain_id)
        if current is None or self._compare_versions(version, current.metadata.version) >= 0:
            self.models[domain_id] = model

    def get(self, domain_id: str, version: Optional[str] = None) -> Optional[DomainModel]:
        """Get a domain model by ID and optional version."""

        if version:
            return self.version_history.get(domain_id, {}).get(version)
        return self.models.get(domain_id)

    def list_all(self) -> List[DomainModelMetadata]:
        """List metadata for all registered domain models."""

        return [model.metadata for model in self.models.values()]

    def get_versions(self, domain_id: str) -> List[str]:
        """Get all known versions of a domain model in descending order."""

        versions = list(self.version_history.get(domain_id, {}).keys())
        versions.sort(key=self._version_key, reverse=True)
        return versions

    @staticmethod
    def _version_key(version: str) -> tuple[int, int, int]:
        parts = [int(part) for part in version.split(".") if part]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    def _compare_versions(self, left: str, right: str) -> int:
        left_key = self._version_key(left)
        right_key = self._version_key(right)
        return (left_key > right_key) - (left_key < right_key)


