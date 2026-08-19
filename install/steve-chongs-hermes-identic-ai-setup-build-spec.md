# Build Spec — Personal Knowledge Vault & Identic Agent

> **Version:** 1.2 · **Last updated:** 2026-08-17
>
> **This is the architecture. For the actual step-by-step build, read the Playbook
> and follow its steps.** This document explains *what* you're building and *why*;
> the playbook tells you *how*, in order.

> **For the agent doing the build (Claude Code, or a fresh Hermes instance).** Read this
> in full before writing anything. Then propose a plan and wait for approval.
>
> This is the *architecture* of the vault and its agent. It is deliberately free of
> anyone's personal data — every personal value is a `[MY …]` placeholder you fill with
> the owner's own answers.
>
> **✍️ = the owner must supply this.** Everything else is scaffolding.

---

## Mission

Build a personal, LLM-maintained knowledge vault, following Karpathy's LLM-wiki pattern,
organised around the owner's **life buckets** (their distinct areas of life), with an
integrated identity layer so the agent anticipates them and, when asked, sounds like them.

The vault is simultaneously:

1. The owner's personal knowledge base
2. A durable record of who they are — for their own reflection, and (if they want) a
   digital-twin project
3. A living archive of everything they capture: writing, voice notes, articles, meetings

This is not a research project. It is the operating system of one person's life.

---

## Architecture

```
[MY VAULT]/                                  [Obsidian opens this · Git versioned]
│
├── 00_SYSTEM/
│   ├── AGENTS.md                            ← the agent's rules of engagement
│   ├── SOUL.md                              ← compact personality card
│   ├── BUCKETS.md                           ← the owner's life areas (the map)
│   ├── STACKING.md                          ← active threads, event-driven
│   ├── IDENTITY.md                          ← digital-twin snapshot, refreshed nightly
│   ├── SCHEMA.md                            ← frontmatter spec (this file, §Frontmatter)
│   ├── TAXONOMY.md                          ← controlled vocabulary of tags
│   ├── INDEX.md                             ← vault catalogue, rebuilt on ingest
│   └── LOG.md                               ← append-only diary
│
├── 01_RAW/                                  [IMMUTABLE. Agent reads only. Never edits.]
│   ├── inbox/                               ← drop zone before triage
│   ├── voice_memos/                         ← highest-trust voice corpus
│   ├── transcripts/
│   ├── articles/                            ← web-clipper output
│   ├── assets/                              ← images
│   ├── meetings/
│   ├── writing/                             ← the owner's own posts, essays, emails
│   ├── resume_cv/
│   └── exports/                             ← material exported from other tools
│
├── 02_MEMORY/                               [Atomic, agent-owned]
│   ├── decisions/   preferences/   patterns/   captures/
│   └── people/                              ← atomic facts about people
│
├── 03_WIKI/                                 [Distilled, frontmatter-required]
│   ├── buckets/                             ← 1 page per life bucket
│   ├── projects/                            ← 1 page per active project
│   ├── people/                              ← family / collaborators / advisors / network
│   ├── concepts/                            ← ideas the owner cares about
│   └── timelines/
│
└── 04_TOOLS/                                [Python scripts. Start dead simple.]
    ├── search_vault.py                      ← SQLite FTS5 full-text search
    ├── triage_ingest.py                     ← quality gate before any write
    ├── update_stacking.py                   ← refresh STACKING.md after ingest
    ├── refresh_identity.py                  ← rebuild IDENTITY.md nightly
    └── lint_vault.py                        ← find contradictions, orphans, drift
```

---

## Frontmatter Schema — CRITICAL, DAY ONE

**This is the most important architectural decision. Get it right at the start.**

Every page in `03_WIKI/` MUST have YAML frontmatter:

```yaml
---
title: "Page title"
created: YYYY-MM-DD
last_verified: YYYY-MM-DD
confidence: high          # high | medium | low
bucket: [primary]         # which life area(s) this belongs to
tags: []                  # from the controlled vocabulary
sources:
  - 01_RAW/…              # where the raw source lives
stale: false              # true if >90 days unverified or superseded
contradicts: null         # link a conflicting page — never overwrite
---
```

For `02_MEMORY/` atomic records, the short form:

```yaml
---
type: decision | preference | pattern | capture | person
created: YYYY-MM-DD
confidence: high | medium | low
bucket: [primary]
sources: []
---
```

For `01_RAW/`, minimal (it's immutable):

```yaml
---
type: voice_memo | transcript | article | meeting | writing | export
captured: YYYY-MM-DDTHH:MM:SS+TZ
source_hash: sha256:…
title: "…"
---
```

### Field rules

| Field | Rule |
|---|---|
| `confidence` | `high` = direct source in 01_RAW/. `medium` = inferred. `low` = recollection. |
| `sources` | Required for `high`. Empty = `low`. |
| `stale` | Flip `true` when unverified >90 days. `lint_vault.py` surfaces these. |
| `contradicts` | New claim vs old claim → mark both pages, keep both. The owner decides the winner. Never overwrite. |

---

## Typed Wikilinks

Plain `[[page]]` is too flat. Use typed wikilinks where the relationship matters:

- `[[page]] (uses)` · `(alternative-to)` · `(supersedes)` · `(contradicts)` · `(extends)` · `(cites)`

Use the Obsidian community plugin `obsidian-wikilink-types` (penfieldlabs). This turns the
vault from "X connects to Y" into a queryable graph: *"show me everything that
contradicts my current plan."*

---

## The Karpathy 4 Principles (Build Discipline)

1. **Think Before Coding.** State assumptions. Surface tradeoffs. Ask rather than guess.
2. **Simplicity First.** Minimum code. No speculative features.
3. **Surgical Changes.** Touch only what's needed. Every changed line traces to the request.
4. **Goal-Driven Execution.** Define success, loop until verified.

---

## Recency Weighting (voice notes)

The owner's thinking evolves. The most recent note on a topic is the canonical version of
their current position.

**Rule:** voice-note-sourced pages are recency-weighted. When a new note overlaps an old
one, the new becomes canonical, the old is marked `superseded_by:` (kept, not deleted),
and the wiki page updates to the new position.

---

## Privacy Sandbox

**✍️ YOUR INPUT** — the owner decides what is private vs shareable.

Every page carries a `shareable: true|false` field. **Default = `false`.** Only content the
owner explicitly flags `shareable: true` may ever be exposed to an external audience, if
they ever build a public-facing layer.

Pattern default-private:
- Family details, financials, health, personal struggles
- Private messages, email, journals

Pattern default-shareable (owner's call):
- Public writing, talks, professional bio

Get the metadata right from day one; turning the feature on later is trivial.

---

## Identity Layer

**✍️ YOUR INPUT** — who the owner is.

The agent maintains `00_SYSTEM/IDENTITY.md`, a ~1-page snapshot of who the owner is,
refreshed nightly. At session start the agent reads, in order:

1. `AGENTS.md` (rules)
2. `STACKING.md` (active threads)
3. `IDENTITY.md` (who they are today)
4. `VOICE_PROFILE.md` (how they sound — built from their own writing, see the playbook Step 8)

Cheap, always-on, means the agent opens every conversation already knowing the landscape
and today's version of the owner.

---

## Voice Profile

**✍️ YOUR INPUT** — the owner's own writing.

The agent builds a `VOICE_PROFILE.md` from the owner's own words — their posts, emails,
messages — so it can write *as them* when asked. Source priority: voice notes and
informal messages first (closest to natural voice), polished writing second. The owner
corrects it over the first days; the correction is the magic.

---

## Build Order

| # | Step | Acceptance criterion |
|---|---|---|
| 0 | Install Obsidian. Set attachment folder = `01_RAW/assets`. Install Dataview, obsidian-wikilink-types, Web Clipper, Templater. Init Git in the vault. | `git log` runs in vault dir |
| 1 | Scaffold the full directory tree. Create empty system files; populate SCHEMA.md from this spec. | All dirs exist |
| 2 | Define the agent's personality (SOUL.md / personality config), from the owner's answers. | `/personality` returns the owner's voice |
| 3 | Hand-seed bucket pages + key people pages with full frontmatter, from the owner's intake answers. | Pages pass frontmatter check |
| 4 | Build `search_vault.py` (FTS5) + `triage_ingest.py`. Test with real ingests. | Nothing lands in wiki without frontmatter |
| 5 | Wire the identity layer + nightly refresh cron. | IDENTITY.md regenerates on schedule |
| 6 | Build `update_stacking.py` + `lint_vault.py`. | Scripts return clean exit codes |
| 7 | Build the voice profile from the owner's writing. | Returns owner-voice output on a test prompt |
| 8 | Wire the Telegram gateway + the loop-keeper + nightly pipeline (see the playbook). | Talk to it from a phone |

---

## What NOT to Do

- ❌ Don't build a vector database on day one. Plain markdown + FTS5 is enough until ~500 pages.
- ❌ Don't silo knowledge by bucket. Buckets are tags, not folders.
- ❌ Don't overwrite contradicting claims. Mark with `contradicts:`. The owner decides.
- ❌ Don't touch `01_RAW/`. Immutable. Always.
- ❌ Don't default `shareable` to `true`. Default false.
- ❌ Don't build speculative features. The owner will ask when ready.

---

## What Success Looks Like (8 weeks in)

- 30–50 wiki pages, all with consistent frontmatter
- The owner asks a question and gets a grounded, cited answer in seconds
- The graph view shows clear clusters for each life area
- `IDENTITY.md` reads like a useful, current snapshot of "them today"
- They have not had to repeat themselves to the agent in weeks
- The task board (kanban + loop keeper) is part of daily habit — they check it, not their chat scroll

---

## The 2-Week Gate (before you clone yourself)

Before doing anything more ambitious — like building a *second* agent for a family member,
or scaling this into a multi-agent setup — **use this agent intensely for at least 2 weeks
first.** Two weeks of real daily use is enough to:

- Find what's genuinely useful vs what sounded good in theory
- Let the vault fill with real content, so a clone has something to inherit
- Let the voice profile sharpen from actual corrections, not guesses

**Rule: minimum 2 weeks of intense use before cloning the setup for another person or
building a family agent.** A clone of an empty vault is just an empty vault twice. A clone
of a two-week-old vault that actually knows you is a foundation.

*(A separate document covers the cloning/family-agent process itself — when you reach the
2-week gate, ask for that one.)*

---

*— a scaffold, not a self. Fill it with yourself.*
