from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import textstat
from rich.console import Console
from rich.table import Table
from .. import parser
from .stats import strip_markdown
from .structure import _find_issues as structure_issues

console = Console()

EXTENSIONS = {".md", ".txt", ".rst"}


def run(directory: Path, output: str = "text", pattern: Optional[str] = None) -> None:
    glob = pattern or "**/*"
    files = sorted(
        f for f in directory.glob(glob)
        if f.is_file() and f.suffix.lower() in EXTENSIONS
    )

    if not files:
        console.print(f"[yellow]No markdown/text files found in {directory}[/yellow]")
        return

    results = [_analyze(f) for f in files]

    data = {
        "directory": str(directory),
        "file_count": len(results),
        "aggregate": _aggregate(results),
        "files": results,
    }

    if output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data)


def _analyze(file: Path) -> dict:
    text = file.read_text(encoding="utf-8")
    doc = parser.parse(file)
    plain = strip_markdown(text)

    word_count = len(plain.split())
    sentence_count = textstat.sentence_count(plain) if plain.strip() else 0
    fre = textstat.flesch_reading_ease(plain) if plain.strip() else 0.0
    fkg = textstat.flesch_kincaid_grade(plain) if plain.strip() else 0.0
    issues = structure_issues(doc.headings)

    return {
        "file": str(file),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "heading_count": len(doc.headings),
        "link_count": len(doc.links),
        "code_block_count": len(doc.code_blocks),
        "flesch_reading_ease": round(fre, 1),
        "flesch_kincaid_grade": round(fkg, 1),
        "structure_issues": len(issues),
    }


def _aggregate(results: list[dict]) -> dict:
    n = len(results)
    if n == 0:
        return {}

    total_words = sum(r["word_count"] for r in results)
    avg_fre = sum(r["flesch_reading_ease"] for r in results) / n
    avg_fkg = sum(r["flesch_kincaid_grade"] for r in results) / n
    total_issues = sum(r["structure_issues"] for r in results)

    most_complex = min(results, key=lambda r: r["flesch_reading_ease"])
    most_words = max(results, key=lambda r: r["word_count"])

    return {
        "total_words": total_words,
        "avg_flesch_reading_ease": round(avg_fre, 1),
        "avg_flesch_kincaid_grade": round(avg_fkg, 1),
        "total_structure_issues": total_issues,
        "most_complex_file": most_complex["file"],
        "largest_file": most_words["file"],
    }


def _print_text(data: dict) -> None:
    agg = data["aggregate"]
    console.print(f"\n[bold]Batch:[/bold] {data['directory']}\n")
    console.print(f"  {data['file_count']} files  |  {agg['total_words']:,} total words  |  "
                  f"{agg['total_structure_issues']} structure issue(s)\n")

    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column("", style="dim")
    summary.add_column("", justify="right")
    summary.add_row("Avg Flesch Reading Ease", str(agg["avg_flesch_reading_ease"]))
    summary.add_row("Avg Flesch-Kincaid Grade", str(agg["avg_flesch_kincaid_grade"]))
    summary.add_row("Most complex file", Path(agg["most_complex_file"]).name)
    summary.add_row("Largest file", Path(agg["largest_file"]).name)
    console.print(summary)
    console.print()

    t = Table(header_style="bold")
    t.add_column("File")
    t.add_column("Words", justify="right")
    t.add_column("Headings", justify="right")
    t.add_column("Links", justify="right")
    t.add_column("FRE", justify="right")
    t.add_column("Grade", justify="right")
    t.add_column("Issues", justify="right")

    for r in data["files"]:
        issues_str = f"[yellow]{r['structure_issues']}[/yellow]" if r["structure_issues"] else "[dim]0[/dim]"
        t.add_row(
            Path(r["file"]).name,
            str(r["word_count"]),
            str(r["heading_count"]),
            str(r["link_count"]),
            str(r["flesch_reading_ease"]),
            str(r["flesch_kincaid_grade"]),
            issues_str,
        )

    console.print(t)
    console.print()
