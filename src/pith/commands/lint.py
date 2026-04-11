from __future__ import annotations
import json
import sys
from pathlib import Path
from .. import parser
from ..output import get_console
from .stats import strip_markdown
from .structure import _find_issues as structure_issues

LONG_SENTENCE_THRESHOLD = 35


def run(file: Path, output: str = "text", quiet: bool = False) -> None:
    doc = parser.parse(file)
    plain = strip_markdown(doc.text)

    issues = []

    # Structure issues
    for msg in structure_issues(doc.headings):
        issues.append({"type": "structure", "detail": msg})

    # Long sentences (no spaCy — keep lint fast)
    # Split on sentence-ending punctuation rather than raw lines
    import re
    sentences = re.split(r'(?<=[.!?])\s+', plain)
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        words = sent.split()
        if len(words) >= LONG_SENTENCE_THRESHOLD:
            issues.append({
                "type": "long_sentence",
                "detail": f"{len(words)} words: {' '.join(words[:8])}...",
            })

    # Images missing alt text
    for img in doc.images:
        if not img.alt:
            issues.append({
                "type": "missing_alt",
                "detail": f"Line {img.line}: image missing alt text ({img.url})",
            })

    # Links with no anchor text
    for lnk in doc.links:
        if not lnk.text:
            issues.append({
                "type": "bare_link",
                "detail": f"Line {lnk.line}: link with no anchor text ({lnk.url})",
            })

    has_issues = len(issues) > 0

    if output == "json":
        print(json.dumps({"file": str(file), "issue_count": len(issues), "issues": issues}, indent=2))
    elif not quiet:
        _print_text(file, issues)

    if has_issues:
        sys.exit(1)


def _print_text(file: Path, issues: list[dict]) -> None:
    if not issues:
        get_console().print(f"[green]OK[/green]  {file}")
        return

    get_console().print(f"{file}  ({len(issues)} issues)")
    for issue in issues:
        get_console().print(f"  ! {issue['detail']}")
