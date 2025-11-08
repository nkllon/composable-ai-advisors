from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional, List
import os

from pydantic import ValidationError

from backend.domain_model.framework import DomainModelFramework
from .config import MCPConfig, DEFAULT_CONFIG_PATH, ROOT


class MCPConfigManager:
    """Loads and provides access to MCP configuration and domain models."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH) -> None:
        env_config_path = os.getenv("MCP_CONFIG_PATH")
        if env_config_path:
            candidate = Path(env_config_path)
            self.config_path = candidate if candidate.is_absolute() else (ROOT / candidate).resolve()
        else:
            self.config_path = config_path
        self._config: MCPConfig = MCPConfig()
        self._framework: Optional[DomainModelFramework] = None
        self._lock = asyncio.Lock()

    @property
    def config(self) -> MCPConfig:
        return self._config

    @property
    def framework(self) -> DomainModelFramework:
        if self._framework is None:
            cache_ttl = self._config.cache.default_ttl_seconds
            dm_env = os.getenv("MCP_DOMAIN_MODELS_DIR")
            if dm_env:
                dm_candidate = Path(dm_env)
                base_dir = dm_candidate if dm_candidate.is_absolute() else (ROOT / dm_candidate).resolve()
            else:
                base_dir = self._config.domain_models.base_dir
            self._framework = DomainModelFramework(base_dir=base_dir, cache_ttl=cache_ttl)
        return self._framework

    async def load(self) -> MCPConfig:
        async with self._lock:
            if not self.config_path.exists():
                self._config = MCPConfig()  # defaults
                self._framework = None
                return self._config

            try:
                raw_text = self.config_path.read_text(encoding="utf-8")
                data = json.loads(raw_text) if raw_text.strip() else {}
                self._config = MCPConfig.model_validate(data or {})
                self._framework = None
            except (OSError, json.JSONDecodeError, ValidationError):
                self._config = MCPConfig()
                self._framework = None
            # Ensure minimal defaults if config file exists but resulted in empty servers/models
            try:
                if not self._config.servers:
                    # Provide a default local server entry for tests and local usage
                    from .config import MCPServerConfig  # local import to avoid cycles
                    self._config.servers = [MCPServerConfig(id="local-mcp", name="Local MCP", type="local", enabled=True)]
                # If a sample model exists in the default directory and no files configured, use it
                dm_dir = self._config.domain_models.base_dir
                sample = (dm_dir / "sample.ttl")
                if self._config.domain_models.preload and not self._config.domain_models.files and sample.exists():
                    self._config.domain_models.files = ["sample.ttl"]
            except Exception:
                # Non-fatal; leave as-is
                pass
            return self._config

    async def preload_domain_models(self) -> List[str]:
        cfg = self._config
        if not cfg.domain_models.preload or not cfg.domain_models.files:
            return []
        file_paths = list(cfg.domain_models.files)
        tasks = [self.framework.load_domain_model(path) for path in file_paths]
        loaded: List[str] = []
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if hasattr(res, "metadata"):
                loaded.append(getattr(res, "metadata").domain_id)  # type: ignore[attr-defined]
        return loaded

    async def reload_and_preload(self) -> dict:
        await self.load()
        loaded = await self.preload_domain_models()
        return {
            "config_loaded": True,
            "preloaded_domain_models": loaded,
        }


