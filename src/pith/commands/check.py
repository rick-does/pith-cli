from __future__ import annotations
import json
from pathlib import Path
from ..output import get_console
from .stats import strip_markdown

LONG_SENTENCE_THRESHOLD = 35
VERY_LONG_SENTENCE_THRESHOLD = 50


def run(file: Path, output: str = "text") -> None:
    try:
        import spacy
    except ImportError:
        get_console().print("[red]spaCy is required for pth check.[/red]")
        get_console().print("  pip install spacy")
        get_console().print("  python -m spacy download en_core_web_sm")
        raise SystemExit(1)

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        get_console().print("[red]spaCy model not found.[/red]")
        get_console().print("  python -m spacy download en_core_web_sm")
        raise SystemExit(1)

    from .. import parser as _parser
    doc = _parser.parse(file)
    plain = strip_markdown(doc.text)
    doc_nlp = nlp(plain)

    issues = []
    for sent in doc_nlp.sents:
        sent_text = sent.text.strip()
        if not sent_text:
            continue
        word_count = len([t for t in sent if not t.is_punct and not t.is_space])

        if _is_passive(sent):
            issues.append({
                "type": "passive_voice",
                "severity": "warning",
                "sentence": _truncate(sent_text),
                "detail": "Passive voice construction",
            })

        if word_count >= VERY_LONG_SENTENCE_THRESHOLD:
            issues.append({
                "type": "very_long_sentence",
                "severity": "warning",
                "sentence": _truncate(sent_text),
                "detail": f"{word_count} words -- consider splitting",
            })
        elif word_count >= LONG_SENTENCE_THRESHOLD:
            issues.append({
                "type": "long_sentence",
                "severity": "info",
                "sentence": _truncate(sent_text),
                "detail": f"{word_count} words",
            })

    data = {
        "file": str(file),
        "issue_count": len(issues),
        "issues": issues,
    }

    if output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data)


def _is_passive(sent) -> bool:
    for token in sent:
        if token.dep_ in ("nsubjpass", "auxpass"):
            return True
    return False


def _truncate(text: str, limit: int = 100) -> str:
    return text[:limit] + ("..." if len(text) > limit else "")


def _print_text(data: dict) -> None:
    get_console().print(f"\n[bold]Check:[/bold] {data['file']}\n")

    if not data["issues"]:
        get_console().print("[green]No issues found.[/green]\n")
        return

    get_console().print(f"Found [bold]{data['issue_count']}[/bold] issue(s)\n")

    for issue in data["issues"]:
        icon = "[yellow]![/yellow]" if issue["severity"] == "warning" else "[blue]i[/blue]"
        label = issue["type"].replace("_", " ").title()
        get_console().print(f"  {icon} [bold]{label}[/bold] -- {issue['detail']}")
        get_console().print(f"    [dim]{issue['sentence']}[/dim]")
        get_console().print()
