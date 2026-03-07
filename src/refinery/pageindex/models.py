"""Section tree node with optional LLM summary. Persisted as .refinery/page_index/{doc_id}.json."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SectionNode(BaseModel):
    """A node in the PageIndex section tree: label, span of LDUs, optional summary, children."""

    section_label: str = ""
    summary: Optional[str] = None
    ldu_range: Optional[List[int]] = None  # [start_idx, end_idx] into List[LDU]
    page_range: Optional[List[int]] = None  # [min_page, max_page] for display
    children: List["SectionNode"] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


SectionNode.model_rebuild()
