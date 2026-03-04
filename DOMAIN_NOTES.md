# Domain Notes: Extraction Thresholds and Confidence

This document justifies the thresholds and confidence signals used in the Multi-Strategy Extraction Engine (Phase 2).

## FastText strategy (Strategy A)

FastText is used for **native digital**, **single-column** documents where pdfplumber can reliably extract a character stream. Confidence is multi-signal:

### Signals

1. **Character count per page**  
   Pages with very few characters (< 100) are likely scanned (OCR produced little) or empty. We require at least `min_chars_per_page` (see `configs/extraction_rules.yaml`) so that low-content pages trigger escalation.

2. **Character density** (character area / page area in points)  
   Reuses triage logic: density below `min_char_density` (e.g. 0.02) suggests sparse or image-dominated content. High density with non-OCR fonts supports native digital.

3. **Image-to-page area ratio**  
   If images cover more than `max_image_ratio` (e.g. 50%) of the page, the page is treated as image-dominated; fast text extraction is unreliable, so we escalate.

4. **Readability score**  
   Ratio of alphanumeric word characters to total characters. Low values can indicate scrambled text, bad encoding, or non-text content. Used as a confidence component.

5. **Font mapping**  
   We check that `page.chars` have valid `fontname` and `adv` (advance width). Missing or invalid font metrics suggest incomplete or non-standard extraction; we reduce confidence.

6. **OCR font penalty**  
   If fonts match OCR indicators (e.g. T3, OCR-A, Identity-H), we treat the page as searchable scan and apply a confidence penalty so the router can prefer layout or vision when appropriate.

### Threshold values

Actual values are in **`configs/extraction_rules.yaml`**:

- `fast_text.min_chars_per_page`: 100  
- `fast_text.max_image_ratio`: 0.50  
- `fast_text.min_char_density`: 0.02  
- `fast_text.min_confidence`: 0.5  
- `confidence_escalation_threshold`: 0.5 (global; below this we try the next strategy)

### Escalation

When document-level confidence (minimum over pages) is below `confidence_escalation_threshold`, the router does **not** accept FastText and escalates to Layout (Docling) and then to Vision if needed.

## Layout strategy (Strategy B)

- Used for multi-column, table-heavy, figure-heavy, or mixed layout/origin.  
- **Table-heavy sanity check**: If the profile is `table_heavy` but Docling detects zero tables, we return low confidence so the router escalates to Vision.

## Vision strategy (Strategy C)

- Used for scanned images, when A/B confidence is below threshold, or when `likely_handwritten` is in the triage notes.  
- **Budget**: `vision.budget_per_document_usd` caps spend per document; when the next page would exceed the cap, we stop and return the document with `status="truncated_budget"`.

## Audit

All extraction decisions and outcomes are logged to **`.refinery/extraction_ledger.jsonl`** with `timestamp`, `doc_id`, `strategy`, `confidence`, `cost_usd`, `time_ms`, and `status` for performance and cost auditing.
