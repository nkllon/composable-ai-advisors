from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


@router.get("/servers")
async def list_servers() -> list:
	"""List registered MCP servers (placeholder)."""
	return []


@router.get("/health")
async def health() -> dict:
	"""MCP health summary (placeholder)."""
	return {"status": "ok"}


@router.get("/metrics")
async def metrics() -> dict:
	"""MCP metrics (placeholder)."""
	return {"mcp_context_exchanges_total": 0}


