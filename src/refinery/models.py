"""Pydantic models for DocumentProfile. Full implementation per plan."""

from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from pydantic import computed_field
from pydantic import BaseModel, Field


class LanguageInfo(BaseModel):
    """Detected language code and confidence."""

    code: str = "unknown"
    confidence: float = 0.0


class DocumentProfile(BaseModel):
    """Classification profile produced by the Triage Agent."""

    origin_type: Literal[
        "native_digital", "scanned_image", "searchable_scan", "mixed", "form_fillable"
    ] = "mixed"
    layout_complexity: Literal[
        "single_column", "multi_column", "table_heavy", "figure_heavy", "mixed"
    ] = "single_column"
    language: LanguageInfo = Field(default_factory=LanguageInfo)
    domain_hint: Literal["financial", "legal", "technical", "medical", "general"] = "general"
    status: Literal["ok", "unsupported"] = "ok"
    doc_id: Optional[str] = None
    source_path: Optional[Path] = None
    page_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def estimated_extraction_cost(self) -> Literal[
        "fast_text_sufficient", "needs_layout_model", "needs_vision_model"
    ]:
        if self.origin_type == "scanned_image":
            return "needs_vision_model"
        if self.origin_type in ("searchable_scan", "mixed"):
            return "needs_layout_model"
        if self.layout_complexity in ("table_heavy", "figure_heavy"):
            return "needs_layout_model"
        if self.language.code == "unknown" and self.language.confidence == 0:
            return "needs_vision_model"
        return "fast_text_sufficient"
