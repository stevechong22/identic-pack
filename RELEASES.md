# Version & Releases

**Current:** 0.4.1 — **"The Muscle"** · **Last updated:** 2026-08-21

## Releases

### 0.4.1 — "The Muscle" patch (2026-08-21)

Reranker guidance corrected: ZeroEntropy (gbrain's original hosted reranker
default) was acquired by Notion and its API sunsets 2026-09-04. Finding from
investigation: **an unconfigured reranker is fine** — pure vector search on
local embeddings, $0. Free-first upgrade path: local Qwen3-Reranker via the
`llama-server-reranker` recipe (Apache 2.0, data stays local). Hosted voyage is
documented as the paid fallback, not the default.

### 0.4.0 — "The Muscle" (2026-08-21)

The operational layer: what makes an identic agent *run*, not just *be*.
Promoted from the working fleet after the Yusephra build surfaced the gap —
the pack shipped identity but not the nervous system.

**New core skills (auto-install):**
- `goodnight-routine` — the four-step end-of-session loop (reflect → ingest →
  cross-link → dream) with the five-section learning reflection delivered as text.
  Includes the coverage-window rule (work since last run, all surfaces,
  midnight boundary) and the never-a-file-link delivery rule.
- `gbrain-operations` — install, configure, health-check, and automate the
  retrieval brain: Postgres engine, per-agent isolation via env vars, the
  `DATABASE_URL` trap, one-serve-only rule, nightly dream cycle, reranker
  migration (ZeroEntropy → voyage), and the universal pitfalls. Genericized.
- `hindsight-install` — persistent-memory daemon for a Hermes agent: local mode
  with DeepSeek, per-agent port/bank isolation, post-update health check, the
  `API_LLM_` vs `LLM_` env trap, and the Gemini fallback. Genericized.

**Bootstrap docs now install via `/update identic`:**
- `steve-chongs-hermes-identic-ai-setup-playbook.md`
- `steve-chongs-hermes-identic-ai-setup-build-spec.md`
- `steve-chongs-hermes-identic-ai-setup-botfather.md`

The three setup docs land in `<HERMES_HOME>/docs/identic/` so any fresh agent
can step through the full curriculum — install, gateway, vault, buckets,
gbrain, Hindsight, nightly pipeline, goodnight ritual — and then make it their
own owner's.

### 0.3.0 — "The Anchor" (2026-08-17)

Adds the grounding layer every identic agent needs.

**New core skill:**
- `foundational-stories` — the three-story architecture (birth / creation /
  ultimate) that forms the lens of the twin. The *pattern* ships; the owner
  writes their own stories into the ✍️ placeholders. Protected pages, read at
  session start, never summarised.

### 0.2.0 — "The Compass" (2026-08-17)

The first core release: the reusable machine, genericized.

**Core skills (auto-install):**
- `silence-discipline` — group-chat presence without narration
- `loop-keeper` — the "nothing gets lost" per-topic card system
- `context-watchdog-ingest` — the lossless auto-dump/context pipeline
- `stacking-principle` — the one-move-hits-three-buckets operating rule
- `update-identic` — the pull command itself

**Core scripts (auto-install):**
- `loops.py` — the loop store (env-configured)
- `context_monitor.py` + `topic_dump.py` — the auto-dump pair (env-configured)
