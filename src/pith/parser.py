"""Shared parsing utilities for markdown and PDF files."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from markdown_it import MarkdownIt

_md = MarkdownIt()

PDF_EXTENSIONS = {".pdf"}
TEXT_EXTENSIONS = {".md", ".txt", ".rst"}


@dataclass
class Heading:
    level: int
    text: str
    line: int


@dataclass
class Link:
    text: str
    url: str
    line: int


@dataclass
class CodeBlock:
    language: str
    content: str
    line: int


@dataclass
class Image:
    alt: str
    url: str
    line: int


@dataclass
class ParsedDocument:
    text: str
    tokens: list
    headings: list[Heading] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    is_pdf: bool = False


def parse(path: Path) -> ParsedDocument:
    if path.suffix.lower() in PDF_EXTENSIONS:
        return _parse_pdf(path)
    return _parse_markdown(path)


# --- Markdown ---

def _parse_markdown(path: Path) -> ParsedDocument:
    text = path.read_text(encoding="utf-8")
    tokens = _md.parse(text)
    doc = ParsedDocument(text=text, tokens=tokens)
    _extract_headings(tokens, doc)
    _extract_inline_elements(tokens, doc)
    _extract_code_blocks(tokens, doc)
    return doc


def _extract_headings(tokens: list, doc: ParsedDocument) -> None:
    i = 0
    while i < len(tokens):
        if tokens[i].type == "heading_open":
            level = int(tokens[i].tag[1])
            line = (tokens[i].map[0] + 1) if tokens[i].map else 0
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                text = tokens[i + 1].content
                doc.headings.append(Heading(level=level, text=text, line=line))
            i += 2
        else:
            i += 1


def _extract_inline_elements(tokens: list, doc: ParsedDocument) -> None:
    for token in tokens:
        if token.type == "inline" and token.children:
            children = token.children
            i = 0
            while i < len(children):
                child = children[i]
                if child.type == "link_open":
                    attrs = dict(child.attrs) if child.attrs else {}
                    href = attrs.get("href", "")
                    text = ""
                    if i + 1 < len(children) and children[i + 1].type == "text":
                        text = children[i + 1].content
                    line = (child.map[0] + 1) if child.map else 0
                    doc.links.append(Link(text=text, url=href, line=line))
                elif child.type == "image":
                    attrs = dict(child.attrs) if child.attrs else {}
                    src = attrs.get("src", "")
                    alt = attrs.get("alt", "")
                    line = (child.map[0] + 1) if child.map else 0
                    doc.images.append(Image(alt=alt, url=src, line=line))
                i += 1


def _extract_code_blocks(tokens: list, doc: ParsedDocument) -> None:
    for token in tokens:
        if token.type == "fence":
            lang = token.info.strip() if token.info else ""
            line = (token.map[0] + 1) if token.map else 0
            doc.code_blocks.append(CodeBlock(language=lang, content=token.content, line=line))
        elif token.type == "code_block":
            line = (token.map[0] + 1) if token.map else 0
            doc.code_blocks.append(CodeBlock(language="", content=token.content, line=line))


# --- PDF ---

def _parse_pdf(path: Path) -> ParsedDocument:
    try:
        import fitz
    except ImportError:
        raise ImportError(
            "pymupdf is required to read PDF files.\n"
            "Install it: pip install pymupdf"
        )

    pdf = fitz.open(str(path.resolve()))
    lines: list[str] = []
    links: list[Link] = []
    images: list[Image] = []

    # Collect font sizes to identify headings heuristically
    size_counts: dict[int, int] = {}
    for page in pdf:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = round(span["size"])
                    size_counts[size] = size_counts.get(size, 0) + 1

    # Body size = most frequent; heading sizes = anything meaningfully larger
    body_size = max(size_counts, key=size_counts.get) if size_counts else 12
    heading_sizes = sorted(
        {s for s in size_counts if s > body_size * 1.12},
        reverse=True,
    )
    size_to_level = {s: i + 1 for i, s in enumerate(heading_sizes[:6])}

    # Prefer bookmarks (outline/TOC) over font-size heuristics when available
    toc = pdf.get_toc(simple=True)  # [[level, title, page], ...]
    use_bookmarks = len(toc) > 0

    if use_bookmarks:
        bookmark_headings: list[Heading] = [
            Heading(level=min(entry[0], 6), text=entry[1], line=entry[2])
            for entry in toc
            if entry[1].strip()
        ]

    headings: list[Heading] = []
    line_no = 0

    for page_no, page in enumerate(pdf):
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for raw_line in block["lines"]:
                line_no += 1
                span_text = "".join(s["text"] for s in raw_line["spans"]).strip()
                if not span_text:
                    continue
                lines.append(span_text)

                # Font-size heading detection (only used when no bookmarks)
                if not use_bookmarks:
                    max_size = max(round(s["size"]) for s in raw_line["spans"])
                    if max_size in size_to_level:
                        headings.append(Heading(
                            level=size_to_level[max_size],
                            text=span_text,
                            line=line_no,
                        ))

        # Links from annotations
        for link in page.get_links():
            if "uri" in link:
                links.append(Link(text="", url=link["uri"], line=0))

        # Images
        for img in page.get_images():
            images.append(Image(
                alt="",
                url=f"[embedded image, page {page_no + 1}]",
                line=0,
            ))

    text = "\n".join(lines)
    doc = ParsedDocument(text=text, tokens=[], is_pdf=True)
    doc.headings = bookmark_headings if use_bookmarks else headings
    doc.links = links
    doc.images = images
    return doc
