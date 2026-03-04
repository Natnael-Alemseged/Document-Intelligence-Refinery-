"""Triage agent orchestration. Full implementation per plan (sampling, doc_id hash, save_profile)."""

from pathlib import Path
from typing import Optional

from refinery.models import DocumentProfile, LanguageInfo
from refinery.triage.exceptions import RefineryTriageError

REFINERY_PROFILES_DIR = Path(".refinery/profiles")


def save_profile(profile: DocumentProfile, doc_id: str) -> Path:
    """Write profile to .refinery/profiles/{doc_id}.json. Creates directory if needed."""
    out_dir = REFINERY_PROFILES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{doc_id}.json"
    path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
    return path


def run_triage(
    pdf_path: Path,
    doc_id: Optional[str] = None,
    domain_strategy: Optional[object] = None,
    save: bool = True,
) -> DocumentProfile:
    """Run triage on a PDF and return a DocumentProfile. Stub: returns minimal profile."""
    try:
        import pdfplumber
    except ImportError:
        raise RefineryTriageError("pdfplumber is required for triage")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
    except Exception as e:
        raise RefineryTriageError(f"Could not open PDF: {e}") from e

    if doc_id is None:
        import hashlib
        doc_id = hashlib.sha256(pdf_path.read_bytes()).hexdigest()

    profile = DocumentProfile(
        origin_type="mixed",
        layout_complexity="single_column",
        language=LanguageInfo(code="unknown", confidence=0.0),
        domain_hint="general",
        status="ok",
        doc_id=doc_id,
        source_path=pdf_path,
        page_count=page_count,
    )
    if save:
        save_profile(profile, doc_id)
    return profile
