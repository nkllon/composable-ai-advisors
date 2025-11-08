from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import yaml
from rdflib import Graph, Namespace, RDF

from .models import DomainModel, DomainModelFormat, DomainModelMetadata


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

        model_subject = next(
            graph.subjects(RDF.type, DOMAIN_NS.DomainModel),
            None,
        )
        if model_subject is None:
            raise ValueError("Domain model turtle is missing a DomainModel subject")

        metadata_dict: Dict[str, Any] = {
            "domain_id": self._get_literal(graph, model_subject, DOMAIN_NS.domainId),
            "domain_name": self._get_literal(graph, model_subject, DOMAIN_NS.domainName),
            "description": self._get_literal(graph, model_subject, DOMAIN_NS.description),
            "version": self._get_literal(graph, model_subject, DOMAIN_NS.version),
            "capabilities": self._get_literals(graph, model_subject, DOMAIN_NS.capability),
            "tools": self._get_literals(graph, model_subject, DOMAIN_NS.tool),
            "rule_sets": self._get_literals(graph, model_subject, DOMAIN_NS.ruleSet),
            "expertise_keywords": self._get_literals(graph, model_subject, DOMAIN_NS.expertiseKeyword),
        }

        metadata = self._build_metadata(metadata_dict, DomainModelFormat.TURTLE, file_path)
        return graph, metadata

    def _parse_json(self, content: str, file_path: str) -> Tuple[Dict[str, Any], DomainModelMetadata]:
        data = json.loads(content)
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

    @staticmethod
    def _get_literal(graph: Graph, subject: Any, predicate: Any) -> str:
        value = next(graph.objects(subject, predicate), None)
        if value is None:
            raise ValueError(f"Missing required predicate {predicate} in domain model")
        return str(value)

    @staticmethod
    def _get_literals(graph: Graph, subject: Any, predicate: Any) -> list[str]:
        return sorted(str(value) for value in graph.objects(subject, predicate))


