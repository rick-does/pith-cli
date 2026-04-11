from __future__ import annotations
import json
import re
from pathlib import Path
import textstat
from rich.console import Console
from rich.table import Table

console = Console()


def run(file: Path, output: str = "text") -> None:
    text = file.read_text(encoding="utf-8")
    plain = strip_markdown(text)

    data = {
        "file": str(file),
        "word_count": textstat.lexicon_count(plain, removepunct=True),
        "sentence_count": textstat.sentence_count(plain),
        "paragraph_count": _count_paragraphs(plain),
        "avg_sentence_length": textstat.avg_sentence_length(plain),
        "avg_syllables_per_word": textstat.avg_syllables_per_word(plain),
        "flesch_reading_ease": textstat.flesch_reading_ease(plain),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(plain),
        "gunning_fog": textstat.gunning_fog(plain),
        "automated_readability_index": textstat.automated_readability_index(plain),
        "coleman_liau_index": textstat.coleman_liau_index(plain),
    }

    if output == "json":
        print(json.dumps(data, indent=2))
    else:
        _print_text(data)


def _count_paragraphs(text: str) -> int:
    return len([p for p in text.split("\n\n") if p.strip()])


def strip_markdown(text: str) -> str:
    """Remove markdown syntax for cleaner prose analysis."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    # Remove tables (lines containing | characters)
    text = re.sub(r"^[|\s].*\|.*$", "", text, flags=re.MULTILINE)
    # Remove heading lines entirely (don't leave bare heading text as prose)
    text = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    text = re.sub(r"\*{1,3}([^\*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_]+)_{1,3}", r"\1", text)
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def _print_text(data: dict) -> None:
    console.print(f"\n[bold]Stats:[/bold] {data['file']}\n")

    counts = Table(show_header=False, box=None, padding=(0, 2))
    counts.add_column("Metric", style="dim")
    counts.add_column("Value", justify="right")
    counts.add_row("Words", str(data["word_count"]))
    counts.add_row("Sentences", str(data["sentence_count"]))
    counts.add_row("Paragraphs", str(data["paragraph_count"]))
    counts.add_row("Avg sentence length", f"{data['avg_sentence_length']:.1f} words")
    counts.add_row("Avg syllables/word", f"{data['avg_syllables_per_word']:.2f}")
    console.print(counts)
    console.print()

    scores = Table(title="Readability Scores", header_style="bold")
    scores.add_column("Score")
    scores.add_column("Value", justify="right")
    scores.add_column("Note", style="dim")

    fre = data["flesch_reading_ease"]
    scores.add_row("Flesch Reading Ease", f"{fre:.1f}", _flesch_label(fre))
    scores.add_row("Flesch-Kincaid Grade", f"{data['flesch_kincaid_grade']:.1f}", "US grade level")
    scores.add_row("Gunning Fog", f"{data['gunning_fog']:.1f}", "Years of education needed")
    scores.add_row("Automated Readability", f"{data['automated_readability_index']:.1f}", "US grade level")
    scores.add_row("Coleman-Liau", f"{data['coleman_liau_index']:.1f}", "US grade level")
    console.print(scores)
    console.print()


def _flesch_label(score: float) -> str:
    if score >= 90: return "Very easy"
    if score >= 80: return "Easy"
    if score >= 70: return "Fairly easy"
    if score >= 60: return "Standard"
    if score >= 50: return "Fairly difficult"
    if score >= 30: return "Difficult"
    return "Very difficult"
