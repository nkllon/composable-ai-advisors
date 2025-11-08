from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.mcp.router import router


def _create_app() -> FastAPI:
	app = FastAPI()
	app.include_router(router)
	return app


def test_mcp_servers_endpoint_lists_configured_servers() -> None:
	app = _create_app()
	with TestClient(app) as client:
		response = client.get("/api/mcp/servers")
		assert response.status_code == 200
		data = response.json()
		assert isinstance(data, list)
		assert len(data) >= 1
		assert "id" in data[0]
		assert "name" in data[0]


def test_mcp_health_reports_status_and_cache_stats() -> None:
	app = _create_app()
	with TestClient(app) as client:
		response = client.get("/api/mcp/health")
		assert response.status_code == 200
		payload = response.json()
		assert payload.get("status") == "ok"
		assert payload.get("servers", 0) >= 1
		cache = payload.get("cache", {})
		# Basic keys expected from CacheStatistics
		for key in ("hits", "misses", "size", "hit_rate"):
			assert key in cache


def test_mcp_metrics_reports_basic_counters() -> None:
	app = _create_app()
	with TestClient(app) as client:
		response = client.get("/api/mcp/metrics")
		assert response.status_code == 200
		metrics = response.json()
		assert metrics.get("servers_configured", 0) >= 1
		domain_section = metrics.get("domain_model", {})
		assert "load_count" in domain_section
		assert "parse_error_count" in domain_section
		assert "validation_error_count" in domain_section
		cache = domain_section.get("cache", {})
		for key in ("hits", "misses", "size", "hit_rate"):
			assert key in cache


def test_mcp_domain_models_lists_registered_models_after_startup() -> None:
	app = _create_app()
	with TestClient(app) as client:
		response = client.get("/api/mcp/domain-models")
		assert response.status_code == 200
		models = response.json()
		assert isinstance(models, list)
		# Preload is enabled in .mcp/config.json, so we expect at least one model
		assert len(models) >= 1
		assert "domain_id" in models[0].get("metadata", {})


def test_mcp_reload_endpoint_reload_and_preload() -> None:
	app = _create_app()
	with TestClient(app) as client:
		response = client.post("/api/mcp/reload")
		assert response.status_code == 200
		body = response.json()
		assert body.get("config_loaded") is True


