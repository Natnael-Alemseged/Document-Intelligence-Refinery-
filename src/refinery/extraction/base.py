"""Extractor protocol and extraction config."""

from pathlib import Path
from typing import Protocol, runtime_checkable

from refinery.models import DocumentProfile
from refinery.extraction.config_models import ExtractionRules
from refinery.extraction.schema import ExtractedDocument


@runtime_checkable
class Extractor(Protocol):
    """Protocol for extraction strategies. extract returns document and optional confidence (0-1)."""

    def extract(self, pdf_path: Path, profile: DocumentProfile) -> tuple[ExtractedDocument, float]:
        """Run extraction. Returns (document, confidence). Low confidence triggers escalation."""
        ...


def _default_extraction_config_path() -> Path:
    return Path.cwd() / "configs" / "extraction_rules.yaml"


def load_extraction_rules(path: Path | None = None) -> ExtractionRules:
    """Load extraction rules from YAML. Uses defaults if file missing."""
    try:
        import yaml
    except ImportError:
        return ExtractionRules()

    config_path = path or _default_extraction_config_path()
    if not config_path.exists():
        return ExtractionRules()
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not data:
        return ExtractionRules()
    return ExtractionRules.model_validate(data)
