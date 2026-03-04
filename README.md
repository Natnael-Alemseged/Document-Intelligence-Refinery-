# Document Intelligence Refinery

Triage and multi-strategy extraction for PDFs: origin/layout/domain detection and confidence-gated extraction (FastText → Layout → Vision).

## Setup

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

This creates a virtual environment (`.venv`) and installs dependencies. Locked dependencies are in `uv.lock`.

## Run tests

```bash
uv run pytest tests/ -v
```

Unit tests cover Triage Agent classification (origin, layout, domain) and extraction confidence scoring.

## Project layout

- **`src/refinery/models/`** — Pydantic schemas: `DocumentProfile`, `ExtractedDocument`, `LDU`, `PageIndex`, `ProvenanceChain`, extraction schema (Bbox, TextBlock, ExtractedTable, etc.).
- **`src/refinery/agents/`** — **Triage Agent** (`triage.py`): origin_type, layout_complexity, domain_hint. **Extractor** (`extractor.py`): ExtractionRouter with confidence-gated escalation.
- **`src/refinery/strategies/`** — Extraction strategies with shared interface: `FastTextExtractor`, `LayoutExtractor`, `VisionExtractor`.
- **`rubric/extraction_rules.yaml`** — Chunking constitution and extraction thresholds (fallback: `configs/extraction_rules.yaml`).
- **`.refinery/profiles/`** — DocumentProfile JSON outputs (at least 12 corpus documents recommended; minimum 3 per class).
- **`.refinery/extraction_ledger.jsonl`** — Ledger entries with strategy selection, confidence scores, and cost estimates.

## Triage a PDF (CLI)

```bash
uv run python -m refinery path/to/document.pdf
```

Or the console script (after `uv sync`):

```bash
uv run refinery-triage path/to/document.pdf
```

Options: `--no-save`, `--json`, `--doc-id ID`.

## Extraction

Run extraction after triage (profile is loaded from `.refinery/profiles/{doc_id}.json` if not passed):

```python
from pathlib import Path
from refinery import run_triage, run_extraction, load_profile

# Triage (saves profile to .refinery/profiles/)
profile = run_triage(Path("document.pdf"))

# Extract (uses strategy from profile; escalates on low confidence)
doc = run_extraction(Path("document.pdf"), profile=profile)
# Result saved to .refinery/extractions/{doc_id}.json and logged to extraction_ledger.jsonl
```

Or with an existing profile:

```python
profile = load_profile("existing_doc_id")
doc = run_extraction(Path("document.pdf"), profile=profile)
```

## Usage from Python

```python
from pathlib import Path
from refinery import run_triage, DocumentProfile, run_extraction

profile: DocumentProfile = run_triage(Path("document.pdf"))
# Profile is also saved to .refinery/profiles/{doc_id}.json when doc_id is set or derived

doc = run_extraction(Path("document.pdf"), profile=profile)
```

## Configuration

- **Triage**: `configs/triage_rules.yaml` (char density, image/table/figure ratios, OCR font indicators).
- **Extraction**: `rubric/extraction_rules.yaml` (fast_text thresholds, confidence_escalation_threshold, vision budget and models). See `DOMAIN_NOTES.md` for rationale.

## Vision API keys

Set at least one in `.env` (or environment) for VisionExtractor and fallbacks:

- `OPENROUTER_API_KEY` or `OPENROUTER_KEY`
- `GROQ_API_KEY`
- `GOOGLE_API_KEY` or `GEMINI_API_KEY`
- `SAMBANOVA_KEY`

Default vision model is free-tier (`google/gemini-2.0-flash-exp:free`). Provider fallback order: OpenRouter → Groq → Google → SambaNova.
