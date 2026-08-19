---
name: context-watchdog-ingest
description: "Monitor per-topic session context — warn at 80%, dump to vault at 90%."
version: 1.3.0
category: productivity
metadata:
  hermes:
    exportable: true
    tags: [context, dump, memory, watchdog, vault]
---

# Context Watchdog & Ingest Pipeline

Prevents data loss as context approaches the LLM window limit by monitoring,
warning, and auto-dumping raw conversation to the vault. This is the lossless
alternative to context compression: the raw words are never thrown away.

**The principle:** compression summarises and *discards* the original. This
pipeline keeps everything — the raw conversation is archived to the vault and
re-read on demand, so an agent becomes a *twin* (never forgets) instead of a
chatbot.

## ⚠️ Context compression is intentionally DISABLED

If the agent runs with context compression on, it replaces conversation with a
lossy summary. For an identic agent this is wrong: the original words are the
audit trail and the identity corpus. Turn compression off and use this pipeline
instead. (Why it was disabled historically: buggy auxiliary model resolution
eroded trust. The lossless approach is the fix, not a workaround.)

## How it works

### The three tiers

1. **Raw dump per topic (the archive).** `topic_dump.py` appends a session's
   full transcript to ONE append-only file per topic:
   `<IDENTIC_VAULT>/01_RAW/sessions/topic-{slug}-dump.md`.
   Lossless, one file per topic, grows forever. Read on demand.
2. **State file (the distilled layer).** A small per-topic summary — decisions,
   open loops, key facts — read at session start so a fresh session has
   continuity without re-reading every raw line.
3. **Memory layer (the every-turn layer).** Hindsight/gbrain recall injects the
   relevant facts each turn automatically.

### The watchdog

`context_monitor.py` runs every ~15 minutes (no_agent cron). It queries the
agent's own state.db for active Telegram sessions, sums tokens per session, and
warns/triggers at thresholds. Silent when healthy.

| Level | Trigger | Action |
|---|---|---|
| < 80% | — | Silent — no output, no delivery |
| ≥ 80% | Per-session first hit | Warn the owner: "Topic X at ~80% — heads up. I'll dump at 90%." |
| ≥ 90% | Per-session auto-fire | **Auto-dump + notify + offer /new** |

### The dump (90% trigger — AUTOMATED, visible, no approval wait)

At 90% the monitor auto-fires and **shows the owner it happened** — it does not
silently wait, and it does not ask.

1. **Auto-dump** — `context_monitor.py` runs `topic_dump.py --session <id>`,
   appending the session's full messages to the topic's archive file.
2. **Post confirmation INTO the topic** — the monitor sends a message into the
   topic's own thread via the Bot API (not just the cron delivery target):
   "Context dump complete — saved to `<path>`. Run `/new` here; the next
   session reads the dump automatically."
3. **Only mark "trigger" if the dump succeeded** — a failed dump keeps the
   previous state so the next tick retries (no silent failure).
4. **Session-start read rule** — any NEW session in a topic (including after
   `/new`) reads the topic's dump file (header + tail) + wiki/state page before
   responding. Continuity survives the reset automatically.

### Manual trigger — `dump` / `snapshot`

The owner can dump ANY topic on demand, not just at 90%: say `dump` (or
`snapshot`) in a topic → the agent dumps the current session immediately,
confirms the path in-topic, and says it's safe to `/new`. Use case: clean slate
before a build.

### Retroactive recovery — `/new` does NOT delete history

`/new` ends the old session and starts a fresh empty one, but the old messages
stay in state.db. `topic_dump.py --thread <id>` dumps the most recent session
with messages (skipping the fresh empty one), so it recovers the just-ended
session after the fact. Saying `dump` first removes the ~15-min gap; it's
insurance, not a requirement.

### Cooldown

One notification per threshold crossing per topic. No spam at 91%.

## ⚠️ The silent-failure warning (memory daemon)

The memory layer runs as a **background daemon**, and it can die without anyone
noticing. When it does, the agent quietly loses its memory — it still answers,
but no longer remembers, and *nothing tells the owner it's down*. Two things
must be built in from day one:

1. **A health watchdog** (every 5–15 minutes) pinging `localhost:<port>/health`
   — if it doesn't respond, **alert the owner loudly**, not silently.
2. **A start-of-session check** — the agent verifies the daemon is alive before
   relying on memory.

## Environment (for the scripts)

Both scripts read config from env, so any agent on any box can install them
with zero edits:

| Env var | What it sets |
|---|---|
| `HERMES_HOME` | Where this agent's state.db + .env live (default `~/.hermes`) |
| `IDENTIC_VAULT` | The agent's vault root (required) |
| `IDENTIC_TOPIC_NAMES` | Optional JSON file mapping thread_id → friendly topic name |
| `IDENTIC_GROUP_CHAT` | The Telegram group chat id the agent lives in |
| `IDENTIC_GROUP_URL` | `t.me/c/` prefix without the `-100` |
| `IDENTIC_CONTEXT_LIMIT` | Context window in tokens (default 1,000,000) |

## Token Estimation

Prefer real API-reported tokens from state.db sessions table (`input_tokens`,
`output_tokens`). Fall back to character estimate only if the db query fails.

## Pitfalls

- **Aggregate DB size is misleading for topic threads.** Always query
  per-session tokens.
- **Compression is intentionally DISABLED** — do NOT re-enable without the
  owner's explicit direction. This pipeline is the replacement.
- **Vault boundary:** session dumps go to `<IDENTIC_VAULT>/01_RAW/sessions/`
  ONLY. Never cross into another agent's vault.
- **Manual pre-restart dump.** The owner sometimes `/new`s a topic BEFORE it
  hits 90% (clean slate for a build). Don't wait for the auto-trigger — dump on
  request.

## Verification

```bash
python3 <HERMES_HOME>/scripts/context_monitor.py   # silent when healthy
python3 <HERMES_HOME>/scripts/topic_dump.py --thread <id>   # manual dump
```
