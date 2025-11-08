from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import yaml
from rdflib import Graph, Namespace, RDF, RDFS, URIRef

from .models import DomainModel, DomainModelFormat, DomainModelMetadata


# Canonical project namespaces
CAA = Namespace("http://nkllon.com/ontology/caa#")
DOMAIN_NS = Namespace("https://composable.ai/ontology/domain#")


class ModelParser:
	"""Parses raw domain model files into structured domain model objects."""

	def parse(self, content: str, fmt: DomainModelFormat, file_path: str) -> DomainModel:
		"""Parse domain model content using the appropriate parser."""

		if fmt is DomainModelFormat.TURTLE:
			parsed_content, metadata = self._parse_turtle(content, file_path)
		elif fmt is DomainModelFormat.JSON:
			parsed_content, metadata = self._parse_json(content, file_path)
		elif fmt is DomainModelFormat.MARKDOWN:
			parsed_content, metadata = self._parse_markdown(content, file_path)
		else:
			raise ValueError(f"Unsupported domain model format: {fmt}")

		return DomainModel(metadata=metadata, content=parsed_content, raw_content=content)

	def _parse_turtle(self, content: str, file_path: str) -> Tuple[Graph, DomainModelMetadata]:
		graph = Graph()
		graph.parse(data=content, format="turtle")

		# Locate domain model subject: prefer CAA type, then DOMAIN_NS fallback
		model_subject = next(graph.subjects(RDF.type, CAA.DomainModel), None)
		if model_subject is None:
			model_subject = next(graph.subjects(RDF.type, DOMAIN_NS.DomainModel), None)
		if model_subject is None:
			raise ValueError("Domain model Turtle missing a DomainModel subject")

		# Extract metadata with CAA-first, DOMAIN_NS fallback
		def first_literal(pred_caa: URIRef, pred_alt: URIRef | None = None, required: bool = False) -> str | None:
			val = next(graph.objects(model_subject, pred_caa), None)
			if val is None and pred_alt is not None:
				val = next(graph.objects(model_subject, pred_alt), None)
			if val is None:
				if required:
					raise ValueError(f"Missing required predicate {pred_caa} in domain model")
				return None
			return str(val)

		def all_literals(pred_caa: URIRef, pred_alt: URIRef | None = None) -> list[str]:
			values = list(graph.objects(model_subject, pred_caa))
			if not values and pred_alt is not None:
				values = list(graph.objects(model_subject, pred_alt))
			return sorted(str(v) for v in values)

		domain_id = first_literal(CAA.domainId, DOMAIN_NS.domainId)
		if not domain_id:
			# Derive from subject localname if not explicitly provided
			if isinstance(model_subject, URIRef):
				domain_id = str(model_subject).split("#")[-1].split("/")[-1]
			else:
				domain_id = "unknown_domain"

		domain_name = first_literal(RDFS.label, DOMAIN_NS.domainName, required=True)
		description = first_literal(RDFS.comment, DOMAIN_NS.description, required=True)
		version = first_literal(CAA.version, DOMAIN_NS.version, required=True)
		capabilities = all_literals(CAA.capability, DOMAIN_NS.capability)
		tools = all_literals(CAA.usesTool, DOMAIN_NS.tool)
		rule_sets = all_literals(CAA.appliesRules, DOMAIN_NS.ruleSet)
		expertise_keywords = all_literals(CAA.expertiseKeyword, DOMAIN_NS.expertiseKeyword)

		metadata_dict: Dict[str, Any] = {
			"domain_id": domain_id,
			"domain_name": domain_name,
			"description": description,
			"version": version,
			"capabilities": capabilities,
			"tools": tools,
			"rule_sets": rule_sets,
			"expertise_keywords": expertise_keywords,
		}

		metadata = self._build_metadata(metadata_dict, DomainModelFormat.TURTLE, file_path)
		return graph, metadata

	def _parse_json(self, content: str, file_path: str) -> Tuple[Dict[str, Any], DomainModelMetadata]:
		data = json.loads(content)
		# Prefer top-level fields as per spec; fallback to nested "metadata"
		if any(k in data for k in ("domain_id", "domain_name", "description", "version")):
			metadata_dict = {
				"domain_id": data.get("domain_id"),
				"domain_name": data.get("domain_name"),
				"description": data.get("description"),
				"version": data.get("version"),
				"capabilities": data.get("capabilities", []),
				"tools": data.get("tools", []),
				"rule_sets": data.get("rule_sets", []),
				"expertise_keywords": data.get("expertise_keywords", []),
			}
		else:
			metadata_dict = dict(data.get("metadata", {}))
		metadata = self._build_metadata(metadata_dict, DomainModelFormat.JSON, file_path)
		return data.get("content", {}), metadata

	def _parse_markdown(self, content: str, file_path: str) -> Tuple[str, DomainModelMetadata]:
		front_matter: Dict[str, Any] = {}
		body = content
		if content.startswith("---"):
			segments = content.split("---", 2)
			if len(segments) >= 3:
				_, raw_meta, body = segments
				front_matter = yaml.safe_load(raw_meta) or {}

		metadata = self._build_metadata(front_matter, DomainModelFormat.MARKDOWN, file_path)
		return body.strip(), metadata

	def _build_metadata(
		self,
		metadata_dict: Dict[str, Any],
		fmt: DomainModelFormat,
		file_path: str,
	) -> DomainModelMetadata:
		metadata_dict = {**metadata_dict}
		metadata_dict.setdefault("capabilities", [])
		metadata_dict.setdefault("tools", [])
		metadata_dict.setdefault("rule_sets", [])
		metadata_dict.setdefault("expertise_keywords", [])
		metadata_dict["format"] = fmt
		metadata_dict["file_path"] = file_path
		metadata_dict["loaded_at"] = datetime.now(timezone.utc)

		return DomainModelMetadata.model_validate(metadata_dict)
