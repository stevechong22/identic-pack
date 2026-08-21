---
name: gbrain-operations
description: "Install, configure, health-check, and automate gbrain over a local vault (Postgres engine)."
triggers:
  - gbrain install, config, or health issues
  - vault search not returning results
  - setting up the nightly dream cycle
version: 1.0.0
category: devops
---

# gbrain Operations (generic)

The retrieval brain: local Postgres + pgvector + Ollama embeddings over the agent's own vault.
Free, local, no API cost. **Run `gbrain query "<topic>"` before every response** — the vault is the
agent's memory. If results reference raw files (01_RAW/), read those too.

## Install

```bash
git clone https://github.com/garrytan/gbrain.git && cd gbrain && bun install && bun link
```

Do **NOT** use `bun install -g github:...` or `npm install -g gbrain` — the -g path produces a broken
CLI (gbrain #218), and npm has an unrelated package squatting the name.

## Postgres engine (required — PGLite is single-writer and corrupts under concurrency)

```bash
sudo apt install postgresql postgresql-contrib postgresql-16-pgvector   # Debian/Ubuntu
sudo -u postgres psql -c "CREATE USER gbrain WITH PASSWORD 'pick-a-strong-one';"
sudo -u postgres psql -c "CREATE DATABASE gbrain OWNER gbrain;"
sudo -u postgres psql -d gbrain -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -c "ALTER ROLE gbrain BYPASSRLS;"   # grants migrations
# If migration 35 (auto_rls_event_trigger) fails: ALTER ROLE gbrain SUPERUSER;
```

`~/.gbrain/config.json`:
```json
{"engine":"postgres","database_url":"postgresql://gbrain:PASSWORD@localhost:PORT/gbrain"}
```

- Ubuntu PG16 defaults to port **5433**, not 5432 — check `pg_lsclusters`.
- On a shared box, give each agent its own **database** on the shared cluster.
- `gbrain doctor` runs pending schema migrations automatically.

## Isolation (multi-agent boxes) — hard rules

- Each agent sets `GBRAIN_DATABASE_URL` **and** `DATABASE_URL` in its **own** `.env`, pointing at its
  own DB. The env var wins over the shared `~/.gbrain/config.json` — this is the airtight isolation
  lever. (`GBRAIN_HOME` is a dead end — the config code hardcodes `~/.gbrain/config.json`.)
- Keep the shared config.json pointed at the PRIMARY agent's DB. Autopilot scripts must `export
  GBRAIN_DATABASE_URL=<own-db>` explicitly.
- **NEVER run destructive SQL on another agent's database.** Markdown on disk is the source of truth;
  DB pages are derived and re-syncable. When a cross-agent leak is flagged: STOP → check the owning
  agent's vault for legitimately-named files first → confirm with the owner → only then act.

## Health checks

```bash
gbrain doctor
gbrain doctor --fast   # skips DB connection check
```

- **Doctor exit code + score are NOT trustworthy for DB-down.** On a dead DB, doctor can return
  `Overall health score: 95/100` with exit 0 — the only signal is `[WARN] connection`. Treat the
  `connection` WARN as the error trigger, and probe the serve endpoint directly:
  `curl -s localhost:3131/health` → `service_unavailable` when the DB is down.
- **`DATABASE_URL` env trap:** gbrain prefers `env:DATABASE_URL` over config.json. A stale/redacted
  env silently breaks every call. `unset DATABASE_URL` (or set it correctly) before every command,
  cron, hook, and terminal use.

## One serve only

Multiple `gbrain serve` processes on the same database conflict (each maintains its own pool).
One systemd unit, one serve process. The unit's ExecStart **must use the full bun path**
(`/path/to/bun /path/to/gbrain/src/cli.ts serve --http localhost:7391`) — the `~/.local/bin/gbrain`
symlink resolves to a bun script and systemd lacks bun in PATH.

## Nightly dream cycle

```bash
gbrain sync --repo <vault-abs-path> --skip-failed
gbrain embed --stale
gbrain extract all
gbrain extract --stale        # clears links_extraction_lag after dream
gbrain dream --source default
gbrain doctor
```

- The `default` source `local_path` **MUST be absolute** — `'.'` resolves to $HOME, finds no .git,
  and auto-creates one (git bloat on root). Fix via psql or config before first sync.
- **Reranker:** ZeroEntropy's hosted API is sunset (acquired by Notion; stops 2026-09-04).
  **No reranker configured = fine** — pure vector search, $0. Free-first local upgrade:
  the `llama-server-reranker` recipe (v0.40.6.1+) serves Qwen3-Reranker (0.6B/4B/8B, Apache
  2.0) or self-hosted ZeroEntropy weights via llama.cpp `--reranking` — same `gateway.rerank()`
  seam, $0 per call, data never leaves the box. Hosted fallback: `voyage:rerank-2.5`
  (200M free tokens/mo, then paid — needs a key and sends docs off-box).
- **llama-server reranker pitfalls (verified 2026-08-21):**
  - **Default physical batch 512 is too small** — real payloads (query + 25 candidate chunks)
    exceed it → HTTP 500 `input (N tokens) is too large`. Launch with
    `--batch-size 4096 --ubatch-size 4096`.
  - **Default context bloats RSS** (40k ctx × 4 slots ≈ 4.5GB+) → OOM-kills on memory-tight
    boxes mid-request (symptom: `rerank timed out` / `socket connection was closed` in the
    audit). Use `--ctx-size 8192 --parallel 1`.
  - **Verify end-to-end:** `gbrain search "<q>" --json` must show `rerank_score` per row.
    ABSENT = fail-open (reranker not firing or failing); check
    `~/.gbrain/audit/rerank-failures-*.jsonl` for the reason. Reranker scores are raw-logit
    scale (e-15) — ordering is what matters, don't round-check for 0-1.
  - Config keys: `search.reranker.enabled true`, `search.reranker.model
    llama-server-reranker:<alias>`, `provider_base_urls.llama-server-reranker
    http://127.0.0.1:8081/v1`, `search.reranker.top_n_in 8`, `search.reranker.timeout_ms 60000`.
- Sync keys on **committed git state** — commit changed files before `gbrain sync`, or it reports
  "Already up to date" and imports nothing. Use `--no-pull` when the git remote is unreachable.

## Pitfalls

1. **Forgetting `dream --source default`** — basic sync/embed/extract doesn't run synthesis, takes,
   or calibration.
2. **`gbrain pack upgrade` does not exist** — use `gbrain upgrade` + `gbrain onboard --apply --yes`.
3. **`onboard --apply` may only LIST recommendations** in some versions (0.42.59.0–0.42.66.0) —
   verify with `gbrain doctor` and run the auto-eligible fixes manually.
4. **Oversized pages** (> nomic-embed-text context ≈8192 tokens) fail the first embed pass; the
   retry logic splits/truncates and the rows DO get embedded — verify with a NULL-embedding query
   before believing the printed "failed" line.
5. **`gbrain embed --stale` can report 0 while doctor reports stale chunks** — `--stale` keys off
   internal bookkeeping; doctor counts rows with NULL embeddings. When they disagree, embed by slug:
   `gbrain embed --slugs "<slug>"`.
6. **Premium models hallucinate issue numbers** — verify every referenced gbrain issue against the
   actual repo before acting (a fabricated #1340 once derailed a fix session).
7. **Never `bun build --compile`** — bakes env vars (including DB passwords) into compiled binaries.
8. **Never run `gbrain frontmatter validate <source-name> --fix`** — it takes a filesystem path:
   `gbrain frontmatter validate <vault-path> --fix`. It only auto-fixes NULL_BYTES, MISSING_CLOSE,
   NESTED_QUOTES, SLUG_MISMATCH — MISSING_OPEN (raw files, by design) and YAML_PARSE are manual.

## Survive reboot (systemd)

```
[Unit]
Description=gbrain semantic brain
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=<owner>
Environment=HOME=/home/<owner>
ExecStart=<bun-full-path> <gbrain-src>/cli.ts serve --http localhost:7391
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`sudo systemctl enable --now gbrain.service`. Restarting the serve process picks up config changes
(Restart=on-failure respawns it clean reading config.json).
