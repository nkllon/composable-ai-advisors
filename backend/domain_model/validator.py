from __future__ import annotations

import re
from typing import List, Optional

from .models import DomainModel, DomainModelMetadata, ValidationIssue, ValidationResult


class ModelValidator:
        """Validates domain model structure and content."""

        VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

        def __init__(self, framework_version: str = "1.0.0"):
                self.framework_version = framework_version

        def validate(self, model: DomainModel) -> ValidationResult:
                """Validate a parsed domain model and return aggregated results."""

                issues: List[ValidationIssue] = []
                issues.extend(self._validate_required_fields(model.metadata))

                version_format_issue = self._validate_version_format(model.metadata.version)
                if version_format_issue:
                        issues.append(version_format_issue)
                else:
                        compatibility_issue = self._validate_version_compatibility(model.metadata.version)
                        if compatibility_issue:
                                issues.append(compatibility_issue)

                return ValidationResult(is_valid=not issues, errors=issues)

        def _validate_required_fields(self, metadata: DomainModelMetadata) -> List[ValidationIssue]:
                """Validate required metadata fields are populated."""

                required_fields = {
                        "domain_id": metadata.domain_id,
                        "domain_name": metadata.domain_name,
                        "description": metadata.description,
                        "version": metadata.version,
                }

                issues: List[ValidationIssue] = []
                for field_name, value in required_fields.items():
                        if not str(value).strip():
                                issues.append(
                                        ValidationIssue(
                                                field=field_name,
                                                message="Field is required",
                                                severity="error",
                                        )
                                )

                return issues

        def _validate_version_format(self, version: str) -> Optional[ValidationIssue]:
                """Validate semantic versioning format."""

                if not self.VERSION_PATTERN.match(version):
                        return ValidationIssue(
                                field="version",
                                message="Version must follow semantic versioning MAJOR.MINOR.PATCH",
                                severity="error",
                        )
                return None

        def _validate_version_compatibility(self, version: str) -> Optional[ValidationIssue]:
                """Validate domain model version compatibility with framework."""

                model_major = int(version.split(".")[0])
                framework_major = int(self.framework_version.split(".")[0])
                if model_major > framework_major:
                        return ValidationIssue(
                                field="version",
                                message=(
                                        "Domain model requires a newer framework major version "
                                        f"({version} vs framework {self.framework_version})"
                                ),
                                severity="error",
                        )
                return None


