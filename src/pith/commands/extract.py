from __future__ import annotations
import json
from pathlib import Path
from rich.table import Table
from .. import parser
from ..output import get_console


def run(file: Path, output: str = "json") -> None:
    doc = parser.parse(file)

    data = {
        "file": str(file),
        "headings": [{"level": h.level, "text": h.text, "line": h.line} for h in doc.headings],
        "links": [{"text": lnk.text, "url": lnk.url, "line": lnk.line} for lnk in doc.links],
        "code_blocks": [
            {"language": cb.language, "line": cb.line, "lines": len(cb.content.splitlines())}
            for cb in doc.code_blocks
        ],
        "images": [{"alt": img.alt, "url": img.url, "line": img.line} for img in doc.images],
    }

    if output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data)


def _print_text(data: dict) -> None:
    get_console().print(f"\n[bold]Extract:[/bold] {data['file']}\n")

    if data["headings"]:
        t = Table(title="Headings", header_style="bold")
        t.add_column("Level")
        t.add_column("Text")
        t.add_column("Line", justify="right")
        for h in data["headings"]:
            t.add_row(f"H{h['level']}", h["text"], str(h["line"]))
        get_console().print(t)
        get_console().print()

    if data["links"]:
        t = Table(title="Links", header_style="bold")
        t.add_column("Text")
        t.add_column("URL")
        t.add_column("Line", justify="right")
        for lnk in data["links"]:
            t.add_row(lnk["text"] or "[dim]--[/dim]", lnk["url"], str(lnk["line"]))
        get_console().print(t)
        get_console().print()

    if data["code_blocks"]:
        t = Table(title="Code Blocks", header_style="bold")
        t.add_column("Language")
        t.add_column("Lines", justify="right")
        t.add_column("At line", justify="right")
        for cb in data["code_blocks"]:
            t.add_row(cb["language"] or "[dim]none[/dim]", str(cb["lines"]), str(cb["line"]))
        get_console().print(t)
        get_console().print()

    if data["images"]:
        t = Table(title="Images", header_style="bold")
        t.add_column("Alt text")
        t.add_column("URL")
        t.add_column("Line", justify="right")
        for img in data["images"]:
            t.add_row(img["alt"] or "[dim]no alt[/dim]", img["url"], str(img["line"]))
        get_console().print(t)
        get_console().print()
