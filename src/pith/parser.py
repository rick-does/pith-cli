"""Shared markdown parsing utilities."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from markdown_it import MarkdownIt

_md = MarkdownIt()


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


def parse(path: Path) -> ParsedDocument:
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
