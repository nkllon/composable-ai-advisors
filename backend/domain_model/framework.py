from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .cache import ModelCache, CacheStatistics
from .loader import ModelLoader
from .models import DomainModel
from .parser import ModelParser
from .registry import ModelRegistry
from .validator import ModelValidator


class DomainModelFramework:
    """Main interface for domain model management."""

    def __init__(self, base_dir: Path = Path(".mcp/domain-models"), framework_version: str = "1.0.0", cache_ttl: int | None = None):
        self.loader = ModelLoader(base_dir)
        self.parser = ModelParser()
        self.validator = ModelValidator(framework_version)
        self.registry = ModelRegistry()
        self.cache = ModelCache(default_ttl=cache_ttl or 300)
        self.metrics: Dict[str, Any] = {
            "load_count": 0,
            "parse_error_count": 0,
            "validation_error_count": 0,
        }

    async def load_domain_model(self, file_path: str) -> DomainModel:
        """Load, parse, validate, register, and cache a domain model."""

        try:
            raw_content, fmt, resolved_path = await self.loader.load_file(file_path)
            model = self.parser.parse(raw_content, fmt, str(resolved_path))
        except Exception as exc:  # noqa: BLE001 - bubble unexpected parse issues
            self.metrics["parse_error_count"] += 1
            raise ValueError(f"Failed to parse domain model '{file_path}': {exc}") from exc

        validation = self.validator.validate(model)
        if not validation.is_valid:
            self.metrics["validation_error_count"] += 1
            messages = "; ".join(f"{issue.field}: {issue.message}" for issue in validation.errors)
            raise ValueError(f"Domain model '{file_path}' failed validation: {messages}")

        self.registry.register(model)
        self.cache.put(model.metadata.domain_id, model)
        self.metrics["load_count"] += 1

        return model

    def get_domain_model(self, domain_id: str, version: Optional[str] = None) -> Optional[DomainModel]:
        """Get a domain model from cache or registry."""

        cached = self.cache.get(domain_id)
        if cached and version in (None, cached.metadata.version):
            return cached

        model = self.registry.get(domain_id, version)
        if model:
            self.cache.put(domain_id, model)
        return model

    def get_cache_statistics(self) -> CacheStatistics:
        """Get cache statistics."""
        return self.cache.get_statistics()

    def get_metrics(self) -> Dict[str, Any]:
        """Get framework metrics."""
        return dict(self.metrics)


