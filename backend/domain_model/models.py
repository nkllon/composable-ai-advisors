from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List

from pydantic import BaseModel


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
	capabilities: List[str] = []
	tools: List[str] = []
	rule_sets: List[str] = []
	expertise_keywords: List[str] = []


class DomainModel(BaseModel):
	"""Parsed domain model"""
	metadata: DomainModelMetadata
	content: Any  # RDF Graph, dict, or structured text
	raw_content: str  # Original file content

	class Config:
		arbitrary_types_allowed = True


class ValidationIssue(BaseModel):
	"""Domain model validation issue"""
	field: str
	message: str
	severity: str  # "error", "warning"


class ValidationResult(BaseModel):
	"""Result of domain model validation"""
	is_valid: bool
	errors: List[ValidationIssue] = []


