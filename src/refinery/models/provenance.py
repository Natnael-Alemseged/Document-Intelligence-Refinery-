"""Provenance and logical document units: PageIndex, LDU, ProvenanceChain."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class PageIndex(BaseModel):
    """Reference to a page (0-based index and optional label)."""

    index: int = 0
    label: Optional[str] = None  # e.g. "1", "i", "Appendix A"


LDUKind = Literal["text", "table", "figure", "heading", "list", "other"]


class LDU(BaseModel):
    """Logical Document Unit: a coherent chunk (text, table, figure) with optional provenance."""

    kind: LDUKind = "text"
    content: Any = None  # text str, or table data, or figure ref
    page_index: Optional[PageIndex] = None
    bbox: Optional[Dict[str, float]] = None  # x0, top, x1, bottom
    content_hash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProvenanceChain(BaseModel):
    """Chain of content hashes for audit and deduplication."""

    hashes: List[str] = Field(default_factory=list)
    source_strategy: Optional[str] = None
