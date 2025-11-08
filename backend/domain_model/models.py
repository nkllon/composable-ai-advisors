from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field


class DomainModelFormat(str, Enum):
	"""Supported domain model formats"""
	TURTLE = "turtle"
	JSON = "json"
	MARKDOWN = "markdown"


class DomainModelMetadata(BaseModel):
        """Metadata for a domain model"""

        domain_id: str
        domain_name: str
        description: str
        version: str
        format: DomainModelFormat
        file_path: str
        loaded_at: datetime
        capabilities: List[str] = Field(default_factory=list)
        tools: List[str] = Field(default_factory=list)
        rule_sets: List[str] = Field(default_factory=list)
        expertise_keywords: List[str] = Field(default_factory=list)


class DomainModel(BaseModel):
        """Parsed domain model"""
        metadata: DomainModelMetadata
        content: Any  # RDF Graph, dict, or structured text
        raw_content: str  # Original file content

        model_config = ConfigDict(arbitrary_types_allowed=True)


class ValidationIssue(BaseModel):
	"""Domain model validation issue"""
	field: str
	message: str
	severity: str  # "error", "warning"


class ValidationResult(BaseModel):
        """Result of domain model validation"""

        is_valid: bool
        errors: List[ValidationIssue] = Field(default_factory=list)


