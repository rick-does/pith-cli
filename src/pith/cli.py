import typer
from pathlib import Path
from typing import Optional
from enum import Enum

app = typer.Typer(
    name="pth",
    help="Prose analysis for developers and technical writers.",
    no_args_is_help=True,
)


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


@app.command("scan")
def cmd_scan(
    file: Path = typer.Argument(..., exists=True, readable=True, help="File to analyze"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """5-second triage: what is this file, what's its shape, any obvious red flags."""
    from .commands.scan import run
    run(file, output=output.value)


@app.command("stats")
def cmd_stats(
    file: Path = typer.Argument(..., exists=True, readable=True, help="File to analyze"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """Quantitative metrics: word count, readability scores, sentence stats."""
    from .commands.stats import run
    run(file, output=output.value)


@app.command("structure")
def cmd_structure(
    file: Path = typer.Argument(..., exists=True, readable=True, help="File to analyze"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
    depth: Optional[int] = typer.Option(None, "--depth", help="Max heading depth to show"),
):
    """Document skeleton: heading hierarchy, section sizes, depth analysis."""
    from .commands.structure import run
    run(file, output=output.value, depth=depth)


@app.command("check")
def cmd_check(
    file: Path = typer.Argument(..., exists=True, readable=True, help="File to analyze"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """Quality pass: passive voice, long sentences, style issues."""
    from .commands.check import run
    run(file, output=output.value)


@app.command("compare")
def cmd_compare(
    file1: Path = typer.Argument(..., exists=True, readable=True, help="First (before) file"),
    file2: Path = typer.Argument(..., exists=True, readable=True, help="Second (after) file"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """Structural diff: what sections were added, removed, or restructured."""
    from .commands.compare import run
    run(file1, file2, output=output.value)


@app.command("extract")
def cmd_extract(
    file: Path = typer.Argument(..., exists=True, readable=True, help="File to analyze"),
    output: OutputFormat = typer.Option(OutputFormat.json, "--output", "-o", help="Output format"),
):
    """Pull structured elements: headings, links, code blocks, images."""
    from .commands.extract import run
    run(file, output=output.value)
