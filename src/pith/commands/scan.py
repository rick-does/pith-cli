from __future__ import annotations
import json
from pathlib import Path
import textstat
from rich.console import Console
from rich.table import Table
from .. import parser
from .stats import strip_markdown

console = Console()


def run(file: Path, output: str = "text") -> None:
    text = file.read_text(encoding="utf-8")
    doc = parser.parse(file)
    plain = strip_markdown(text)

    word_count = len(plain.split())
    sentence_count = textstat.sentence_count(plain)
    flags = _check_flags(doc, word_count)
    doc_type = _guess_type(file, doc)

    data = {
        "file": str(file),
        "size_bytes": file.stat().st_size,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "heading_count": len(doc.headings),
        "link_count": len(doc.links),
        "code_block_count": len(doc.code_blocks),
        "image_count": len(doc.images),
        "document_type": doc_type,
        "flags": flags,
    }

    if output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data)


def _guess_type(file: Path, doc) -> str:
    name = file.name.lower()
    if name in ("readme.md", "readme.txt", "readme.rst"):
        return "README"
    if "changelog" in name or "history" in name:
        return "Changelog"
    if "contributing" in name:
        return "Contributing guide"
    if "license" in name:
        return "License"
    if len(doc.code_blocks) >= 3:
        return "Technical documentation"
    if len(doc.headings) >= 5:
        return "Structured document"
    if not doc.headings:
        return "Prose document"
    return "Document"


def _check_flags(doc, word_count: int) -> list[str]:
    flags = []
    if word_count > 2000 and not doc.headings:
        flags.append(f"Long document ({word_count} words) with no headings")
    elif not doc.headings:
        flags.append("No headings found")
    elif doc.headings[0].level != 1:
        flags.append(f"No H1 — first heading is H{doc.headings[0].level}")
    if word_count < 50:
        flags.append(f"Very short document ({word_count} words)")
    bare_links = [lnk for lnk in doc.links if not lnk.text]
    if bare_links:
        flags.append(f"{len(bare_links)} link(s) with no anchor text")
    no_alt = [img for img in doc.images if not img.alt]
    if no_alt:
        flags.append(f"{len(no_alt)} image(s) missing alt text")
    return flags


def _print_text(data: dict) -> None:
    console.print(f"\n[bold]Scan:[/bold] {data['file']}\n")
    console.print(f"  [dim]Type:[/dim]  {data['document_type']}")
    console.print(f"  [dim]Size:[/dim]  {data['size_bytes']:,} bytes\n")

    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column("", style="dim")
    t.add_column("", justify="right")
    t.add_row("Words", str(data["word_count"]))
    t.add_row("Sentences", str(data["sentence_count"]))
    t.add_row("Headings", str(data["heading_count"]))
    t.add_row("Links", str(data["link_count"]))
    t.add_row("Code blocks", str(data["code_block_count"]))
    t.add_row("Images", str(data["image_count"]))
    console.print(t)
    console.print()

    if data["flags"]:
        console.print("[bold yellow]Flags:[/bold yellow]")
        for flag in data["flags"]:
            console.print(f"  [yellow]![/yellow] {flag}")
    else:
        console.print("[green]No flags.[/green]")
    console.print()
