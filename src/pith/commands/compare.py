from __future__ import annotations
import json
import difflib
from pathlib import Path
from rich.table import Table
from .. import parser
from ..output import get_console


def run(file1: Path, file2: Path, output: str = "text") -> None:
    doc1 = parser.parse(file1)
    doc2 = parser.parse(file2)
    sections1 = _get_sections(doc1, doc1.text)
    sections2 = _get_sections(doc2, doc2.text)
    changes = _diff_structure(sections1, sections2)

    data = {
        "file1": str(file1),
        "file2": str(file2),
        "summary": {
            "headings_before": len(doc1.headings),
            "headings_after": len(doc2.headings),
            "sections_added": sum(1 for c in changes if c["status"] == "added"),
            "sections_removed": sum(1 for c in changes if c["status"] == "removed"),
            "sections_changed": sum(1 for c in changes if c["status"] == "changed"),
            "sections_unchanged": sum(1 for c in changes if c["status"] == "unchanged"),
        },
        "changes": changes,
    }

    if output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data)


def _get_sections(doc, text: str) -> dict[str, dict]:
    lines = text.splitlines()
    sections: dict[str, dict] = {}
    for i, heading in enumerate(doc.headings):
        end_line = len(lines)
        for j in range(i + 1, len(doc.headings)):
            if doc.headings[j].level <= heading.level:
                end_line = doc.headings[j].line - 1
                break
        content = "\n".join(lines[heading.line:end_line])
        sections[heading.text] = {
            "level": heading.level,
            "word_count": len(content.split()),
            "content": content,
        }
    return sections


def _diff_structure(sections1: dict, sections2: dict) -> list[dict]:
    all_keys = list(dict.fromkeys(list(sections1) + list(sections2)))
    changes = []
    for key in all_keys:
        if key in sections1 and key in sections2:
            s1, s2 = sections1[key], sections2[key]
            ratio = difflib.SequenceMatcher(None, s1["content"], s2["content"]).ratio()
            changes.append({
                "status": "unchanged" if ratio >= 0.95 else "changed",
                "title": key,
                "level": s2["level"],
                "word_count_before": s1["word_count"],
                "word_count_after": s2["word_count"],
                "similarity": round(ratio, 2),
            })
        elif key in sections1:
            changes.append({
                "status": "removed",
                "title": key,
                "level": sections1[key]["level"],
                "word_count_before": sections1[key]["word_count"],
                "word_count_after": 0,
                "similarity": 0.0,
            })
        else:
            changes.append({
                "status": "added",
                "title": key,
                "level": sections2[key]["level"],
                "word_count_before": 0,
                "word_count_after": sections2[key]["word_count"],
                "similarity": 0.0,
            })
    return changes


def _print_text(data: dict) -> None:
    get_console().print(f"\n[bold]Compare:[/bold]")
    get_console().print(f"  [dim]Before:[/dim] {data['file1']}")
    get_console().print(f"  [dim]After:[/dim]  {data['file2']}\n")

    s = data["summary"]
    get_console().print(
        f"  {s['headings_before']} -> {s['headings_after']} headings  |  "
        f"[green]+{s['sections_added']} added[/green]  "
        f"[red]-{s['sections_removed']} removed[/red]  "
        f"[yellow]~{s['sections_changed']} changed[/yellow]  "
        f"[dim]{s['sections_unchanged']} unchanged[/dim]\n"
    )

    visible = [c for c in data["changes"] if c["status"] != "unchanged"]
    if not visible:
        get_console().print("[green]No structural changes.[/green]\n")
        return

    t = Table(header_style="bold")
    t.add_column("")
    t.add_column("Section")
    t.add_column("Words before", justify="right")
    t.add_column("Words after", justify="right")
    t.add_column("Similarity", justify="right")

    icons = {"added": "[green]+[/green]", "removed": "[red]-[/red]", "changed": "[yellow]~[/yellow]"}

    for change in visible:
        indent = "  " * (change["level"] - 1)
        t.add_row(
            icons[change["status"]],
            f"{indent}{'#' * change['level']} {change['title']}",
            str(change["word_count_before"]) if change["word_count_before"] else "--",
            str(change["word_count_after"]) if change["word_count_after"] else "--",
            f"{change['similarity']:.0%}" if change["status"] == "changed" else "--",
        )

    get_console().print(t)
    get_console().print()
