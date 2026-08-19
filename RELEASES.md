# Version & Releases

**Current:** 0.2.0 — **"The Compass"** · **Last updated:** 2026-08-17

## Releases

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
- `update-identic.sh` — the pull mechanism

**Also:** `install/` carries the three setup docs (playbook, build spec,
BotFather guide).

### 0.1.0 — Scaffold (2026-08-17)

Repo structure, README, VERSION, MANIFEST, empty skill/script/workflow dirs.

---

## Promotion log

- 2026-08-17 — First core batch promoted (owner: "roll it out" on the goal).
  Every item passed the genericize test: no owner name, identity, voice,
  family, or secrets; all paths/ports env-parameterized.
