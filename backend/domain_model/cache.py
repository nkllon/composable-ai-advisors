from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, Optional

from .models import DomainModel


@dataclass
class CacheEntry:
	model: DomainModel
	cached_at: datetime
	ttl: int

	def is_expired(self) -> bool:
		return datetime.utcnow() > self.cached_at + timedelta(seconds=self.ttl)


@dataclass
class CacheStatistics:
	hits: int = 0
	misses: int = 0
	size: int = 0

	def hit_rate(self) -> float:
		total = self.hits + self.misses
		return self.hits / total if total > 0 else 0.0


class ModelCache:
	"""In-memory cache for domain models (skeleton)."""

	def __init__(self, default_ttl: int = 300):
		self.cache: Dict[str, CacheEntry] = {}
		self.default_ttl = default_ttl
	self.stats = CacheStatistics()
		self.lock = Lock()

	def get(self, domain_id: str) -> Optional[DomainModel]:
		"""Get a domain model from cache (skeleton)."""
		with self.lock:
			entry = self.cache.get(domain_id)
			if not entry:
				self.stats.misses += 1
				return None
			if entry.is_expired():
				self.cache.pop(domain_id, None)
				self.stats.misses += 1
				return None
			self.stats.hits += 1
			return entry.model

	def put(self, domain_id: str, model: DomainModel, ttl: Optional[int] = None) -> None:
		"""Put a domain model in cache (skeleton)."""
		with self.lock:
			self.cache[domain_id] = CacheEntry(model=model, cached_at=datetime.utcnow(), ttl=ttl or self.default_ttl)
			self.stats.size = len(self.cache)

	def invalidate(self, domain_id: str) -> None:
		"""Invalidate a cache entry (skeleton)."""
		with self.lock:
			self.cache.pop(domain_id, None)
			self.stats.size = len(self.cache)

	def invalidate_all(self) -> None:
		"""Invalidate all cache entries (skeleton)."""
		with self.lock:
			self.cache.clear()
			self.stats.size = 0

	def get_statistics(self) -> CacheStatistics:
		"""Get cache statistics (skeleton)."""
		return self.stats


