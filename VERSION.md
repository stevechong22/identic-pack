# Version

**Current:** 0.4.1 — **"The Muscle"** · **Last updated:** 2026-08-21

## Changelog

### 0.4.1 — 2026-08-21
- Reranker guidance fix: ZeroEntropy sunset (Notion acquisition) — no reranker
  configured is fine (pure vector, $0); free-first local upgrade via the
  `llama-server-reranker` recipe (Qwen3-Reranker, Apache 2.0); hosted voyage is
  a paid fallback, not the default. Corrected in `gbrain-operations`.

### 0.4.0 — 2026-08-21
- Added `goodnight-routine` — the four-step end-of-session loop (reflect, ingest,
  cross-link, dream cycle) with the five-section learning reflection delivered as text.
- Added `gbrain-operations` — install/config/health/automation for the retrieval brain
  (Postgres engine, isolation rules, dream cycle, pitfalls). Genericized.
- Added `hindsight-install` — persistent-memory daemon setup (local mode, DeepSeek),
  genericized to per-agent ports and banks.
- Bootstrap docs (playbook, build spec, BotFather guide) now install via
  `/update identic` — the full setup curriculum ships with the machine.

### 0.3.0 — 2026-08-17
- Added `foundational-stories` skill — the three-story grounding layer
  (birth / creation / ultimate). Pattern ships; owner writes their own stories.
- First release with the grounding layer.

### 0.2.0 — 2026-08-17
- First core batch: silence-discipline, loop-keeper, context-watchdog-ingest,
  stacking-principle, update-identic + loops.py, context_monitor.py,
  topic_dump.py, update-identic.sh. All genericized.

### 0.1.0 — 2026-08-17
- Repo scaffolded. Nothing promoted to `core` yet.
- `install/` carries the three setup docs (playbook, build spec, BotFather guide).
- `MANIFEST.json` empty — awaiting first "roll it out" decisions.
