# Lazyday Vault

Lazyday Vault is a Claude Code and Codex compatible plugin for personal
knowledge management workflows in Chinese.

It is designed for a local-first personal vault where any input can become a
traceable knowledge asset: a sentence, chat note, log file, image, video,
archive, ebook, transcript, project document, or research source.

## Core Model

Lazyday Vault keeps seven layers separate:

- Inbox layer: temporary drop zone for unprocessed material.
- Raw source layer: immutable original files and source manifests.
- Extract layer: OCR, transcripts, text extracts, chunks, and source maps.
- Index layer: source, tag, entity, timeline, asset, claim, conflict, and
  citation indexes.
- Wiki layer: LLM-maintained markdown pages for projects, areas, entities,
  concepts, timelines, questions, decisions, and syntheses.
- Answer layer: durable question answers and research outputs that can later be
  merged back into the wiki.
- Log layer: append-only ingest, process, query, research, maintenance logs, and
  a JSONL event ledger for rebuild and sync-conflict recovery.

This follows the useful part of PARA, LLM wiki, NotebookLM-like source grounding,
and Obsidian-style linked notes: preserve the source of truth, compile reusable
knowledge once, maintain links, and cite evidence when answering.

## Skills

- `route-vault-task`: choose the right Lazyday Vault skill for capture,
  processing, retrieval, research, retrospectives, or maintenance.
- `initialize-vault`: idempotently create or repair the base vault structure,
  indexes, logs, wiki index, and event ledger in the current project root.
- `capture-source`: preserve arbitrary incoming content in the raw source layer
  and create source manifests.
- `extract-source`: turn raw sources into extracts, chunks, media derivatives,
  and source maps.
- `integrate-knowledge`: tag, link, classify, update indexes, and maintain the
  LLM wiki.
- `process-source`: coordinate extraction and integration when the user asks to
  generally process a source without naming a stage.
- `record-vault-interaction`: save user questions, assistant answers,
  corrections, feedback, and decisions as traceable interaction sources with
  claim-level conflict handling.
- `answer-vault-question`: answer questions from the vault with evidence,
  citations, uncertainty labels, and original source references.
- `vault-deep-research`: run multi-step research over vault sources, optionally
  using external research when requested, and file durable research outputs.
- `review-life-log`: produce daily, weekly, monthly, yearly, project, mood, and
  reflection summaries from timeline evidence.
- `maintain-vault`: lint and repair the vault structure, indexes, links,
  citation coverage, stale claims, and orphan pages.

## Default Vault Path

Lazyday Vault is meant to run inside the vault data project. By default, the
current project root is the vault root, so it can be placed directly in iCloud
Drive or another file-sync folder.

```text
<vault-project>/
├── raw/
├── processed/
├── wiki/
├── indexes/
├── answers/
└── logs/
```

Optional agent workflow artifacts, if needed, should use:

```text
.lazyday/vault/requirements/
```

The raw source layer is append-only by default. Generated summaries, tags,
indexes, and wiki pages must link back to source IDs and original file paths.

For iCloud sync, keep all durable knowledge files as portable markdown, JSONL,
or original media files. Local-only caches, vector indexes, or temporary
transcoding outputs should be treated as rebuildable and kept out of the source
of truth.

Critical long-term invariants:

- Every durable fact should trace to `source_id + locator + raw path`.
- Old assistant answers are historical records unless their `parent_sources`
  support the claim.
- User corrections and decisions should create claim-level relationships instead
  of overwriting old sources.
- iCloud conflict copies and cloud placeholders must be marked explicitly before
  processing or rebuilding indexes.

## Target Vault Rules

Copy the bundled target-vault rule file into the root of the vault data project:

```bash
cp plugins/lazyday-vault/rules/AGENTS.md <vault-project>/AGENTS.md
```

That `AGENTS.md` is intentionally stricter than a normal project rule file. It
requires all knowledge-base operations to route through `route-vault-task` or an
explicit Lazyday Vault skill, protects raw sources, enforces source citations,
prevents assistant-answer self-reinforcement, and defines confirmation gates for
iCloud conflicts, external services, batch rewrites, and raw-source changes.

## References

The shared protocol lives in:

- `rules/AGENTS.md`
- `skills/route-vault-task/references/vault-protocol.md`
- `skills/route-vault-task/references/architecture.md`
- `skills/route-vault-task/references/source-types.md`
- `skills/route-vault-task/references/retrieval-protocol.md`
- `skills/route-vault-task/references/interaction-conflict-protocol.md`
- `skills/route-vault-task/references/industry-patterns.md`
