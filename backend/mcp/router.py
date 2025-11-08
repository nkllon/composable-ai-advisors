from __future__ import annotations

from fastapi import APIRouter
from .manager import MCPConfigManager

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

_manager = MCPConfigManager()

async def _ensure_loaded() -> None:
	"""Ensure MCP config is loaded and domain models preloaded at first access."""
	try:
		if not _manager.config.servers:
			await _manager.load()
		# Ensure domain models are loaded at least once
		if not _manager.framework.registry.list_all():
			await _manager.preload_domain_models()
			# As a fallback, if still empty and a sample exists, load it explicitly
			if not _manager.framework.registry.list_all():
				candidate = _manager.framework.loader.base_dir / "sample.ttl"
				if candidate.exists():
					try:
						await _manager.framework.load_domain_model("sample.ttl")
					except Exception:
						pass
	except Exception:
		# Best-effort; endpoints remain functional with empty config
		pass

# Initialization is handled by application lifespan; endpoints also lazy-load.


@router.get("/servers")
async def list_servers() -> list:
	"""List registered MCP servers."""
	await _ensure_loaded()
	return [server.model_dump() for server in _manager.config.servers]


@router.get("/health")
async def health() -> dict:
	"""MCP health summary."""
	await _ensure_loaded()
	framework = _manager.framework
	cache_stats = framework.get_cache_statistics()
	return {
		"status": "ok",
		"servers": len(_manager.config.servers),
		"domain_models_registered": len(framework.registry.models),
		"cache": {
			"hits": cache_stats.hits,
			"misses": cache_stats.misses,
			"size": cache_stats.size,
			"hit_rate": cache_stats.hit_rate(),
		},
	}


@router.get("/metrics")
async def metrics() -> dict:
	"""MCP and domain-model metrics."""
	await _ensure_loaded()
	framework = _manager.framework
	cache_stats = framework.get_cache_statistics()
	return {
		"mcp_context_exchanges_total": 0,
		"domain_model": {
			"load_count": framework.get_metrics().get("load_count", 0),
			"parse_error_count": framework.get_metrics().get("parse_error_count", 0),
			"validation_error_count": framework.get_metrics().get("validation_error_count", 0),
			"cache": {
				"hits": cache_stats.hits,
				"misses": cache_stats.misses,
				"size": cache_stats.size,
				"hit_rate": cache_stats.hit_rate(),
			},
		},
		"servers_configured": len(_manager.config.servers),
	}


@router.get("/domain-models")
async def list_domain_models() -> list:
	"""List registered domain models' metadata."""
	await _ensure_loaded()
	return [meta.model_dump() for meta in _manager.framework.registry.list_all()]


@router.post("/reload")
async def reload_config() -> dict:
	"""Reload MCP config and optionally preload domain models."""
	return await _manager.reload_and_preload()


