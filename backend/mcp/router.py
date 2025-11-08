from __future__ import annotations

from fastapi import APIRouter
from .manager import MCPConfigManager

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

_manager = MCPConfigManager()

@router.on_event("startup")
async def _startup() -> None:
	"""Load MCP config and optionally preload domain models on startup."""
	await _manager.load()
	await _manager.preload_domain_models()


@router.get("/servers")
async def list_servers() -> list:
	"""List registered MCP servers."""
	return [server.model_dump() for server in _manager.config.servers]


@router.get("/health")
async def health() -> dict:
	"""MCP health summary."""
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
	return [meta.model_dump() for meta in _manager.framework.registry.list_all()]


@router.post("/reload")
async def reload_config() -> dict:
	"""Reload MCP config and optionally preload domain models."""
	return await _manager.reload_and_preload()


