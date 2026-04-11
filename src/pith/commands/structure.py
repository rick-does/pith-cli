from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.tree import Tree
from .. import parser

console = Console()


def run(file: Path, output: str = "text", depth: Optional[int] = None) -> None:
    doc = parser.parse(file)
    lines = doc.text.splitlines()

    filtered = [h for h in doc.headings if depth is None or h.level <= depth]
    sections = _build_sections(filtered, lines)
    issues = _find_issues(doc.headings)

    data = {
        "file": str(file),
        "heading_count": len(doc.headings),
        "max_depth": max((h.level for h in doc.headings), default=0),
        "issues": issues,
        "sections": sections,
    }

    if output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data, filtered)


def _build_sections(headings: list, lines: list[str]) -> list[dict]:
    sections = []
    for i, heading in enumerate(headings):
        end_line = len(lines)
        for j in range(i + 1, len(headings)):
            if headings[j].level <= heading.level:
                end_line = headings[j].line - 1
                break
        section_text = "\n".join(lines[heading.line:end_line])
        sections.append({
            "level": heading.level,
            "title": heading.text,
            "line": heading.line,
            "word_count": len(section_text.split()),
        })
    return sections


def _find_issues(headings: list) -> list[str]:
    issues = []
    if not headings:
        issues.append("No headings found")
        return issues
    if headings[0].level != 1:
        issues.append(f"Document does not start with H1 (first heading is H{headings[0].level})")
    h1_count = sum(1 for h in headings if h.level == 1)
    if h1_count > 1:
        issues.append(f"Multiple H1 headings ({h1_count})")
    for i in range(1, len(headings)):
        prev, curr = headings[i - 1], headings[i]
        if curr.level > prev.level + 1:
            issues.append(f"Line {curr.line}: H{curr.level} follows H{prev.level} (skipped level)")
    return issues


def _print_text(data: dict, headings: list) -> None:
    console.print(f"\n[bold]Structure:[/bold] {data['file']}\n")

    if not headings:
        console.print("[yellow]No headings found.[/yellow]\n")
        return

    tree = Tree(f"[bold]{data['file']}[/bold]")
    stack: list[tuple[int, Tree]] = [(0, tree)]

    for section in data["sections"]:
        level = section["level"]
        label = (
            f"[bold]{'#' * level}[/bold] {section['title']}  "
            f"[dim](line {section['line']}, ~{section['word_count']} words)[/dim]"
        )
        while len(stack) > 1 and stack[-1][0] >= level:
            stack.pop()
        node = stack[-1][1].add(label)
        stack.append((level, node))

    console.print(tree)
    console.print()

    if data["issues"]:
        console.print("[bold yellow]Issues:[/bold yellow]")
        for issue in data["issues"]:
            console.print(f"  [yellow]![/yellow] {issue}")
        console.print()
