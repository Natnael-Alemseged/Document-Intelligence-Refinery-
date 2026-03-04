# Document Intelligence Refinery

Phase 1: Triage Agent and Document Profiling.

## Setup

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

This creates a virtual environment (`.venv`) and installs dependencies including dev tools.

## Run tests

```bash
uv run pytest tests/ -v
```

Or:

```bash
uv run python -m pytest tests/ -v
```

## Triage a PDF (CLI)

Using the module (recommended):

```bash
uv run python -m refinery path/to/document.pdf
```

Or the console script (after `uv sync`):

```bash
uv run refinery-triage path/to/document.pdf
```

Options:

- `--no-save` — do not write profile to `.refinery/profiles/`
- `--json` — print profile as JSON to stdout
- `--doc-id ID` — use this doc_id instead of content hash

## Usage from Python

```python
from pathlib import Path
from refinery import run_triage, DocumentProfile

profile: DocumentProfile = run_triage(Path("document.pdf"))
# Profile is also saved to .refinery/profiles/{doc_id}.json when doc_id is set or derived from content hash
```

## Project layout

- `src/refinery/` – main package (models, triage agent)
- `.refinery/profiles/` – created at runtime when saving profiles
- `tests/` – unit and integration tests
