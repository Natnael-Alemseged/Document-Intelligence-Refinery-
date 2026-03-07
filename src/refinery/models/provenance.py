"""Provenance and logical document units: PageIndex, LDU, ProvenanceChain."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, computed_field


class PageIndex(BaseModel):
    """Reference to a page or a hierarchical section (0-based index, optional label, optional children)."""

    index: int = 0
    label: Optional[str] = None  # e.g. "1", "i", "Appendix A"
    children: List["PageIndex"] = Field(default_factory=list)  # recursive: sub-pages or subsections


# Allow recursive PageIndex
PageIndex.model_rebuild()


LDUKind = Literal["text", "table", "figure", "heading", "list", "other"]


class LDU(BaseModel):
    """Logical Document Unit: a coherent chunk (text, table, figure) with optional provenance."""

    kind: LDUKind = "text"
    content: Any = None  # text str, or table data, or figure ref
    page_index: Optional[PageIndex] = None
    page_refs: List[int] = Field(default_factory=list)  # page indices the chunk spans (for multi-page chunks)
    token_count: int = 0
    bbox: Optional[Dict[str, float]] = None  # x0, top, x1, bottom
    content_hash: Optional[str] = None
    parent_section: Optional[str] = None  # e.g. "Chapter 3", "Appendix A"
    chunk_id: str = ""  # stable id for dedup, retrieval, referencing
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @computed_field
    @property
    def chunk_type(self) -> LDUKind:
        """Spec-compliant alias for kind (chunk_type in API)."""
        return self.kind


class ProvenanceChain(BaseModel):
    """Chain of content hashes for audit and deduplication, with source and span metadata."""

    hashes: List[str] = Field(default_factory=list)
    source_strategy: Optional[str] = None
    source_document: Optional[str] = None  # doc_id or path for traceability
    bbox: Optional[Dict[str, float]] = None  # overall span (x0, top, x1, bottom) for the chain
