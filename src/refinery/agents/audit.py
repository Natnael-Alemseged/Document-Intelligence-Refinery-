"""
Audit Mode: verify a claim against the corpus.
Returns verified (with citation), not_found, or unverifiable (e.g. conflicting evidence).
"""

import logging
from typing import Any, Literal, Optional

from refinery.models import ProvenanceChain, SourceCitation
from refinery.agents.query_agent import run_query

logger = logging.getLogger(__name__)


def verify_claim(
    claim: str,
    doc_id: Optional[str] = None,
) -> dict:
    """
    Verify a claim against the document(s). Returns structured result:
    - verified: bool
    - citation: ProvenanceChain or None (when verified)
    - status: "verified" | "not_found" | "unverifiable"
    - evidence: list of nearest chunks (with bbox, content_hash) for inspection
    """
    result = run_query(claim, doc_id=doc_id)
    citations: list = result.get("citations", [])
    answer = result.get("answer", "")
    provenance_chain: Optional[ProvenanceChain] = result.get("provenance_chain")

    # Build evidence list from citations (nearest chunks)
    evidence = []
    for c in citations:
        if isinstance(c, SourceCitation):
            evidence.append({
                "document_name": c.document_name,
                "page_number": c.page_number,
                "page_numbers": getattr(c, "page_numbers", []),
                "bbox": c.bbox,
                "content_hash": c.content_hash,
            })
        elif isinstance(c, dict):
            evidence.append(c)

    # Heuristic: no citations -> not_found
    if not citations:
        return {
            "verified": False,
            "citation": None,
            "status": "not_found",
            "evidence": evidence,
        }

    # If answer says "No matching content" treat as not_found
    if "No matching content found" in (answer or ""):
        return {
            "verified": False,
            "citation": None,
            "status": "not_found",
            "evidence": evidence,
        }

    # Single supporting citation -> verified
    if len(citations) == 1:
        return {
            "verified": True,
            "citation": provenance_chain,
            "status": "verified",
            "evidence": evidence,
        }

    # Multiple citations: could be supporting or conflicting -> unverifiable unless single source
    return {
        "verified": False,
        "citation": provenance_chain,
        "status": "unverifiable",
        "evidence": evidence,
    }


def verify_claim_with_judge(
    claim: str,
    doc_id: Optional[str] = None,
) -> dict:
    """
    Same as verify_claim but with optional LLM judge step when evidence is present but
    conflicting: call LLM to decide if claim is supported or unverifiable.
    """
    base = verify_claim(claim, doc_id=doc_id)
    if base["status"] != "verified" or len(base.get("evidence", [])) < 2:
        return base
    # Optional: call LLM to check if evidence conflicts
    # For now return as verified; can add OPENROUTER call to judge "do these sources support the claim?"
    return base
