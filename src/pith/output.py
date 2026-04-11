"""Centralized console for all output. Handles Windows encoding."""
import sys
from functools import lru_cache
from rich.console import Console


def _fix_encoding() -> None:
    """Ensure stdout/stderr use UTF-8 on Windows."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


@lru_cache(maxsize=1)
def get_console() -> Console:
    """Return a Console with UTF-8 encoding guaranteed."""
    _fix_encoding()
    return Console()
