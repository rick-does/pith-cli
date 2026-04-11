# pith

[![CI](https://github.com/rick-does/pith/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/rick-does/pith/actions/workflows/ci.yml)

CLI prose analysis for developers and technical writers.

`pth` analyzes text files -- READMEs, documentation, markdown -- and reports on structure, quality, readability, and style. Fully local, no hosted backend, no API keys required.

---

## Install

```bash
pip install pith-cli
```

For the `pth check` command, you also need a spaCy model:

```bash
python -m spacy download en_core_web_sm
```

---

## Commands

All commands remember the last file used. If you run `pth scan README.md` and then `pth stats`, it will reuse `README.md`.

### `pth scan <file>`
5-second triage. How long is it? What kind of document is it? What's the rough shape? Any obvious red flags -- no headings in a 2000-word file, images missing alt text, bare links.

```bash
pth scan README.md
```

### `pth stats <file>`
Pure numbers. Word count, sentence count, paragraph count, average sentence length, readability scores (Flesch-Kincaid, Gunning Fog, and more). No judgment -- just quantitative data.

```bash
pth stats README.md
```

### `pth structure <file>`
The skeleton. Heading hierarchy, section nesting, section word counts. Like a table of contents with metadata -- how deep does nesting go, are sections balanced, are there orphaned subsections.

```bash
pth structure README.md
pth structure README.md --depth 2
```

### `pth check <file>`
The quality pass. Passive voice, overly long sentences, style issues. Flags problems with explanations. Requires spaCy.

```bash
pth check README.md
```

### `pth compare <file1> <file2>`
Structural diff. Not just what lines changed -- what sections were added, removed, or significantly rewritten between two versions of a document.

```bash
pth compare v1.md v2.md
```

### `pth extract <file>`
Data pull. Extracts headings, links, code blocks, and images as structured output. JSON by default, pipeable into other tools.

```bash
pth extract README.md
pth extract README.md --output text
```

### `pth lint <file>`
Fast, CI-friendly pass. Flags structure issues, long sentences, missing alt text, and bare links. No spaCy required. Exits 1 if problems found.

```bash
pth lint README.md
pth lint README.md --quiet   # exit code only, no output
```

### `pth batch <dir>`
Aggregate analysis across all markdown files in a directory. Average readability scores, total word count, per-file breakdown, most complex and largest files.

```bash
pth batch ./docs
pth batch ./docs --output json
```

---

## Flags

```
--output json|text      Output format (default varies by command)
--depth <n>             Max heading depth (structure command)
--quiet                 Exit code only, no output (lint command, CI use)
--pattern               Glob pattern for batch (default: **/*.md)
--help                  Help for any command
```

---

## Part of PiTH

`pth` is the CLI component of **PiTH** -- a markdown development environment. Fully local. No hosted backend.
