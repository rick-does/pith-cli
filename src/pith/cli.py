import sys
import io
import typer
from pathlib import Path
from typing import Optional
from enum import Enum

# Force UTF-8 output on Windows to avoid CP1252 encoding errors
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

app = typer.Typer(
    name="pth",
    help="Prose analysis for developers and technical writers.",
    no_args_is_help=True,
)

_LAST_FILE = Path.home() / ".pth_last"


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


def _save_last(path: Path) -> None:
    _LAST_FILE.write_text(str(path.resolve()), encoding="utf-8")


def _load_last() -> Optional[Path]:
    if _LAST_FILE.exists():
        p = Path(_LAST_FILE.read_text(encoding="utf-8").strip())
        if p.exists():
            return p
    return None


def _resolve_file(file: Optional[str]) -> Path:
    if file is not None:
        p = Path(file)
        _save_last(p)
        return p
    last = _load_last()
    if last is None:
        typer.echo("No file specified and no previous file found. Pass a filename.")
        raise typer.Exit(1)
    typer.echo(f"Using last file: {last}")
    return last


@app.command("scan")
def cmd_scan(
    file: Optional[str] = typer.Argument(None, help="File to analyze (default: last used file)"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """5-second triage: what is this file, what's its shape, any obvious red flags."""
    from .commands.scan import run
    run(_resolve_file(file), output=output.value)


@app.command("stats")
def cmd_stats(
    file: Optional[str] = typer.Argument(None, help="File to analyze (default: last used file)"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """Quantitative metrics: word count, readability scores, sentence stats."""
    from .commands.stats import run
    run(_resolve_file(file), output=output.value)


@app.command("structure")
def cmd_structure(
    file: Optional[str] = typer.Argument(None, help="File to analyze (default: last used file)"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
    depth: Optional[int] = typer.Option(None, "--depth", help="Max heading depth to show"),
):
    """Document skeleton: heading hierarchy, section sizes, depth analysis."""
    from .commands.structure import run
    run(_resolve_file(file), output=output.value, depth=depth)


@app.command("check")
def cmd_check(
    file: Optional[str] = typer.Argument(None, help="File to analyze (default: last used file)"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """Quality pass: passive voice, long sentences, style issues."""
    from .commands.check import run
    run(_resolve_file(file), output=output.value)


@app.command("compare")
def cmd_compare(
    file1: str = typer.Argument(..., help="First (before) file"),
    file2: str = typer.Argument(..., help="Second (after) file"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
):
    """Structural diff: what sections were added, removed, or restructured."""
    from .commands.compare import run
    run(Path(file1), Path(file2), output=output.value)


@app.command("lint")
def cmd_lint(
    file: Optional[str] = typer.Argument(None, help="File to lint (default: last used file)"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="No output, just exit code (for CI)"),
):
    """Quick pass: flags problems only, exits 1 if any found (CI-friendly)."""
    from .commands.lint import run
    run(_resolve_file(file), output=output.value, quiet=quiet)


@app.command("batch")
def cmd_batch(
    directory: str = typer.Argument(..., help="Directory to analyze"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format"),
    pattern: Optional[str] = typer.Option(None, "--pattern", help="Glob pattern (default: **/*.md)"),
):
    """Aggregate analysis across all files in a directory."""
    from .commands.batch import run
    run(Path(directory), output=output.value, pattern=pattern)


@app.command("extract")
def cmd_extract(
    file: Optional[str] = typer.Argument(None, help="File to analyze (default: last used file)"),
    output: OutputFormat = typer.Option(OutputFormat.json, "--output", "-o", help="Output format"),
):
    """Pull structured elements: headings, links, code blocks, images."""
    from .commands.extract import run
    run(_resolve_file(file), output=output.value)
