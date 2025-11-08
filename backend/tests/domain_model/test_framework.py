import json
from pathlib import Path

import json
import sys
from pathlib import Path

import asyncio

import pytest

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

from backend.domain_model.framework import DomainModelFramework
from backend.domain_model.loader import ModelLoader
from backend.domain_model.models import DomainModelFormat
from backend.domain_model.parser import ModelParser


def test_model_loader_detects_format_and_resolves_paths():
        loader = ModelLoader()

        ttl_path = Path(".mcp/domain-models/research-analyst.ttl")
        content, fmt, resolved = asyncio.run(loader.load_file(ttl_path.name))

        assert "Research Analyst" in content
        assert fmt is DomainModelFormat.TURTLE
        assert resolved.samefile(ttl_path)

        assert loader.detect_format("example.json") is DomainModelFormat.JSON
        assert loader.detect_format("notes.md") is DomainModelFormat.MARKDOWN


def test_model_parser_extracts_metadata_from_turtle():
        parser = ModelParser()
        ttl_path = Path(".mcp/domain-models/compliance-officer.ttl")
        content = ttl_path.read_text(encoding="utf-8")

        model = parser.parse(content, DomainModelFormat.TURTLE, str(ttl_path))

        metadata = model.metadata
        assert metadata.domain_id == "compliance_officer"
        assert metadata.domain_name == "Compliance Officer"
        assert "regulatory" in metadata.description.lower()
        assert set(metadata.capabilities) == {
                "control_mapping",
                "risk_ranking",
                "exception_logging",
        }
        assert set(metadata.tools) == {"policy_repository", "risk_register"}
        assert set(metadata.rule_sets) == {"escalate_high_risk", "document_decision_rationale"}
        assert "audit_trail" in metadata.expertise_keywords


def test_framework_loads_and_caches_models(tmp_path: Path):
        framework = DomainModelFramework()

        model = asyncio.run(framework.load_domain_model("systems-architect.ttl"))
        assert model.metadata.domain_id == "systems_architect"

        cached = framework.get_domain_model("systems_architect")
        assert cached is model

        metrics = framework.get_metrics()
        assert metrics["load_count"] == 1
        stats = framework.get_cache_statistics()
        assert stats.hits == 1


def test_framework_reports_validation_errors(tmp_path: Path):
        invalid_model = {
                "metadata": {
                        "domain_id": "incomplete",
                        "domain_name": "",
                        "description": "",
                        "version": "1",
                },
                "content": {},
        }
        invalid_path = tmp_path / "invalid-model.json"
        invalid_path.write_text(json.dumps(invalid_model), encoding="utf-8")

        framework = DomainModelFramework(base_dir=tmp_path)

        with pytest.raises(ValueError) as excinfo:
                asyncio.run(framework.load_domain_model(invalid_path.name))

        message = str(excinfo.value)
        assert "Domain model" in message
        assert "domain_name" in message or "description" in message
