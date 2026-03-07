"""PageIndex tree builder: traverse section hierarchy and generate LLM summaries."""

import logging
from pathlib import Path
from typing import List, Optional

from refinery.models import LDU
from refinery.strategies.base import load_extraction_rules
from refinery.strategies.config_models import ExtractionRules, PageIndexConfig

from refinery.pageindex.models import SectionNode

logger = logging.getLogger(__name__)

# Lazy token count for truncation
_tiktoken_enc = None


def _token_count_approx(text: str) -> int:
    try:
        import tiktoken
        global _tiktoken_enc
        if _tiktoken_enc is None:
            _tiktoken_enc = tiktoken.get_encoding("cl100k_base")
        return len(_tiktoken_enc.encode(text))
    except Exception:
        return len(text) // 4


def _truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximately max_tokens."""
    if _token_count_approx(text) <= max_tokens:
        return text
    # Binary search by character length
    low, high = 0, len(text)
    while low < high - 1:
        mid = (low + high) // 2
        if _token_count_approx(text[:mid]) <= max_tokens:
            low = mid
        else:
            high = mid
    return text[:low] + " [...]"


def _summarize_with_llm(text: str, model_id: str, max_tokens: int) -> Optional[str]:
    """Call cheap LLM to summarize section text. Returns summary or None on failure."""
    prompt = f"Summarize this section in 2-3 sentences. Section text:\n\n{_truncate_to_tokens(text, max_tokens)}"
    messages = [{"role": "user", "content": prompt}]
    api_key = __import__("os").environ.get("OPENROUTER_API_KEY") or __import__("os").environ.get("OPENROUTER_KEY")
    if not api_key:
        logger.warning("No OPENROUTER_API_KEY; skipping LLM summary")
        return None
    try:
        import httpx
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_id, "messages": messages, "max_tokens": 150},
            )
        r.raise_for_status()
        data = r.json()
        choice = (data.get("choices") or [None])[0]
        if not choice:
            return None
        return (choice.get("message") or {}).get("content", "").strip()
    except Exception as e:
        logger.debug("LLM summary failed: %s", e)
        return None


def _ldu_content_text(ldu: LDU) -> str:
    """Extract string content from LDU for section text."""
    if ldu.content is None:
        return ""
    if isinstance(ldu.content, str):
        return ldu.content
    if isinstance(ldu.content, list):
        return " ".join(str(cell) for row in ldu.content for cell in (row if isinstance(row, (list, tuple)) else [row]))
    return str(ldu.content)


def build_page_index_tree(
    ldus: List[LDU],
    doc_id: str,
    rules: Optional[ExtractionRules] = None,
    persist_path: Optional[Path] = None,
) -> List[SectionNode]:
    """
    Build section tree from LDUs: group by parent_section, generate LLM summary per section.
    Returns flat list of SectionNode (one per section). Optionally persists to .refinery/page_index/{doc_id}.json.
    """
    rules = rules or load_extraction_rules()
    pageindex_cfg: PageIndexConfig = rules.pageindex
    vision = rules.vision
    model_id = pageindex_cfg.summary_model_id or vision.model_cheap
    max_input = pageindex_cfg.max_input_tokens
    batch_size = pageindex_cfg.batch_size

    # Group LDUs by parent_section
    section_to_indices: dict[Optional[str], List[int]] = {}
    for i, ldu in enumerate(ldus):
        sec = ldu.parent_section or "(root)"
        section_to_indices.setdefault(sec, []).append(i)

    nodes: List[SectionNode] = []
    section_labels = sorted(section_to_indices.keys(), key=lambda s: (min(section_to_indices[s]), s))
    for batch_start in range(0, len(section_labels), batch_size):
        batch = section_labels[batch_start : batch_start + batch_size]
        for section_label in batch:
            indices = section_to_indices[section_label]
            if not indices:
                continue
            text_parts = [_ldu_content_text(ldus[i]) for i in indices]
            section_text = "\n\n".join(p for p in text_parts if p.strip())
            summary = _summarize_with_llm(section_text, model_id, max_input) if section_text.strip() else None
            page_refs = []
            for i in indices:
                page_refs.extend(ldus[i].page_refs or [])
            page_range = (min(page_refs), max(page_refs)) if page_refs else None
            nodes.append(
                SectionNode(
                    section_label=section_label,
                    summary=summary,
                    ldu_range=[min(indices), max(indices) + 1],
                    page_range=list(page_range) if page_range else None,
                    children=[],
                )
            )

    if persist_path is not None:
        persist_path.parent.mkdir(parents=True, exist_ok=True)
        persist_path.write_text(
            __import__("json").dumps([n.model_dump() for n in nodes], indent=2),
            encoding="utf-8",
        )
    elif doc_id:
        out_dir = Path(".refinery/page_index")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{doc_id}.json"
        out_path.write_text(
            __import__("json").dumps([n.model_dump() for n in nodes], indent=2),
            encoding="utf-8",
        )
        logger.info("PageIndex tree saved to %s", out_path)

    return nodes
