from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, HttpUrl


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = ROOT / ".mcp/config.json"
DEFAULT_DOMAIN_MODELS_DIR = ROOT / ".mcp/domain-models"


class CacheConfig(BaseModel):
    default_ttl_seconds: int = Field(default=300, ge=0)


class DomainModelsConfig(BaseModel):
    base_dir: Path = Field(default=DEFAULT_DOMAIN_MODELS_DIR)
    files: List[str] = Field(default_factory=list)
    preload: bool = False


class MCPServerConfig(BaseModel):
    id: str
    name: str
    type: str = Field(description="e.g., http, grpc, local")
    endpoint: Optional[HttpUrl] = None
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolAdapterConfig(BaseModel):
    name: str
    type: str
    endpoint: Optional[str] = None
    api_key_env: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)


class MCPConfig(BaseModel):
    version: str = "1.0"
    cache: CacheConfig = Field(default_factory=CacheConfig)
    domain_models: DomainModelsConfig = Field(default_factory=DomainModelsConfig)
    servers: List[MCPServerConfig] = Field(default_factory=list)
    tools: List[ToolAdapterConfig] = Field(default_factory=list)


