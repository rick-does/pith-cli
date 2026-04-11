# CLAUDE.md — pith-cli (pth)

## PiTH — Umbrella Brand

**PiTH** is the umbrella brand for a markdown development environment. This repo (`pith`) contains the CLI component (`pth`).

PiTH is not for monetizing. If others find it useful, fine.

`pth` is a CLI prose analysis tool for developers and technical writers. It analyzes text files — READMEs, documentation, markdown — and reports on structure, quality, readability, and style. Fully local, pip-installable, no hosted backend.

---

## Name

- **Tool name:** `pth` (the command users type)
- **Package name:** `pith-cli` (on PyPI, to avoid conflict with dormant `pth` package)
- **Origin:** Derived from "pith" — the essential substance of something. "Pithy" means brief and forceful. Fits a tool that analyzes whether writing gets to the point. Three letters, easy to type, no `ctl` suffix.
- **PyPI/npm conflicts:** Dormant packages exist for `pth` but are unused. `pth-cli` or `pith-cli` is clean.

---

## Architecture

Fully local. No hosted backend. No Lightsail. No ongoing cost.

- Python CLI package (pip-installable)
- File processing via parsing libraries
- NLP via spaCy (local)
- Optional Claude API integration for qualitative commands (user provides their own API key)
- File watching via watchdog

---

## Commands

### Core commands (start here)

**`pth scan <file>`** — First impression. The lightest touch. You've just opened a file you haven't seen before and want to know what you're looking at in 5 seconds. How long is it? What kind of document is it? What's the rough shape? Any obvious red flags (e.g., no headings in a 2000-word file, or a README with no code blocks)? Think of scanning a document with your eyes before you start reading. Not deep analysis — triage.

**`pth stats <file>`** — Pure numbers. Word count, sentence count, paragraph count, average sentence length, readability scores (Flesch-Kincaid, Gunning Fog). No judgment, no opinions — just quantitative data. You'd use this when you need to answer "how complex is this document?" with a number.

**`pth structure <file>`** — The skeleton. Heading hierarchy, section nesting, section sizes. Like a table of contents with metadata — how deep does the nesting go, how balanced are the sections, are there orphaned subsections under missing parents. You'd use this to understand the architecture of a document without reading it.

**`pth check <file>`** — The quality pass. This is where judgment lives. Passive voice, overly long sentences, muddled agents, style rule violations. Flags problems with locations and explanations. This is the command closest to a linter — it tells you what's wrong and where.

**`pth compare <f1> <f2>`** — Structural diff. Not just "what lines changed" (that's regular diff) but "what sections were added, removed, restructured, or significantly rewritten." You'd use this to understand how a document evolved between versions at a meaningful level, not a line level.

**`pth extract <file>`** — Data pull. Extract specific elements as structured output: all headings, all links, all code blocks, all images. Output is JSON, meant for piping into other tools or scripts. You'd use this when you need to answer "what links are in this doc?" or "show me every code example."

---

**Key distinction:** `scan` is 5-second triage, not "run everything." Each command answers a fundamentally different question about the document.

```
pth scan <file>
pth stats <file>
pth structure <file>
pth check <file>
pth compare <f1> <f2>
pth extract <file>
```

### Additional commands (build after core is solid)

```
pth lint <file>          # quick pass, just problems, no detail
pth summary <file>       # one-paragraph summary (uses Claude API)
pth watch <file>         # live re-analysis as you edit
pth batch <dir>          # run analysis across a directory
pth report <file>        # full HTML or JSON report
pth init                 # create a .pth config file for the project
```

---

## Common Flags

```
--output json|text|html
--format markdown|rst|txt
--depth <n>              # how deep into structure
--rules <file>           # custom style rules
--min / --max            # thresholds for metrics
--verbose
--quiet                  # just exit code, for CI use
```

---

## Library Stack

| Command | Library | Notes |
|---------|---------|-------|
| `pth structure`, `pth extract` | `mistune` or `markdown-it-py` | Parses markdown into AST |
| `pth stats` | `textstat` | Readability scores, sentence metrics |
| `pth check`, `pth lint` | `spaCy` | NLP, passive voice, dependency parsing, agent/action identification |
| `pth compare` | `difflib` + structural AST diff | Text diff + structural diff |
| `pth summary` | Claude API | User provides API key |
| `pth watch` | `watchdog` | File system watcher |

---

## What Each Command Does

**`pth stats`** — word count, sentence length, paragraph count, readability scores (Flesch-Kincaid, Gunning Fog, etc.)

**`pth structure`** — heading hierarchy, document shape, section lengths, depth analysis

**`pth extract`** — pull headings, code blocks, links, lists as structured output (JSON-pipeable)

**`pth check`** — passive voice detection, sentence complexity, long sentences, style rule violations from `.pth` config

**`pth compare`** — structural diff between two versions of a document. Not just line diff — what sections changed, what was added/removed at the structural level

**`pth summary`** — Claude API call, returns one-paragraph summary of the document

**`pth watch`** — runs analysis on every save, live feedback while writing

**`pth batch`** — iterates over a directory, produces aggregate report

**`pth lint`** — fast, CI-friendly, just flags problems with exit code

**`pth init`** — creates `.pth` config file for project-level style rules

---

## Existing Tools (context)

- **vale** — established prose linter, style rule enforcement. Does not do structural analysis, readability metrics beyond basic, or semantic comparison. `pth` is not trying to replace vale — different emphasis.
- **textstat** — readability metrics library, used internally by `pth`
- **Grammarly** — cloud, GUI. Not comparable.

---

## Notes

- `pth check` is where a Natural Sentence Analysis methodology could live — spaCy identifies grammatical relationships (agent, main verb, dependents) to flag structural prose issues. This is genuinely unique and not covered by vale.
- `--quiet` flag makes `pth lint` useful in CI pipelines — just returns exit code, no output.
- `pth batch` + `--output json` makes it pipeable into other tools.
