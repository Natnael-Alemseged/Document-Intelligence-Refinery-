"""Environment helpers: read .env from project root when process env is missing keys."""

from functools import lru_cache
from pathlib import Path
import os


def _project_root() -> Path:
    # src/refinery/env.py -> project root is two levels up from src/
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def _load_project_env_once() -> None:
    env_path = _project_root() / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            # Respect already exported environment values.
            os.environ.setdefault(key, value)


def get_env_value(*names: str) -> str | None:
    """
    Return the first available env value from names.
    Falls back to loading project-root .env exactly once.
    """
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    _load_project_env_once()
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None
