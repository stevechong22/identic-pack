---
name: hindsight-install
description: "Install and configure Hindsight persistent memory on a Hermes agent (local mode, DeepSeek)."
triggers:
  - "install hindsight"
  - "set up hindsight"
  - "hindsight isn't working"
  - "memory provider setup"
version: 1.0.0
category: devops
---

# Hindsight Install — Hermes Agent (generic)

Complete install pattern for Hindsight local mode on a Hermes agent. Encodes every pitfall
discovered during the first sibling-agent install session.

## Prerequisites

- Hermes v0.18.2+ (PR #2823 or later for lifecycle hooks)
- DeepSeek API key (or Gemini as fallback)
- `uvx` available (for hindsight-embed daemon)
- Python 3.11+

## Install Steps

### 1. Install the plugin

```bash
pip install hindsight-hermes
```

Verify registration: `python3 -c "import importlib.metadata; print([ep.name for ep in importlib.metadata.entry_points(group='hermes_agent.plugins')])"` — must show `hindsight`.

### 2. Set memory provider

```bash
HERMES_HOME=/path/to/agent hermes config set memory.provider hindsight
```

### 3. Create Hindsight config

`<HERMES_HOME>/hindsight/config.json`:

```json
{
  "mode": "local",
  "api_url": "http://localhost:<PORT>",
  "bank_id": "<agent-name>",
  "bankMission": "<one-line agent identity>",
  "recallBudget": "medium",
  "recallMaxTokens": 4096,
  "autoRecall": true,
  "autoRetain": true,
  "retainEveryNTurns": 1,
  "retainOverlapTurns": 2,
  "memory_mode": "hybrid",
  "prefetch_method": "recall"
}
```

**Port rule: pick your own port — never another agent's.** Each agent gets its own daemon port,
its own bank, its own embedded Postgres data dir.

### 4. Set env vars in `.env`

```bash
HINDSIGHT_MODE=local
HINDSIGHT_API_URL=http://localhost:<PORT>
HINDSIGHT_API_KEY=local-mode          # required even in local mode!
HINDSIGHT_LLM_API_KEY=<deepseek-api-key>
HINDSIGHT_BANK_ID=<agent-name>
HINDSIGHT_RECALL_BUDGET=medium
HINDSIGHT_BANK_MISSION="<agent identity>"
```

### 5. Start the daemon

```bash
# Create profile (one-time, per-agent)
uvx hindsight-embed profile create <agent-name> --port <PORT> \
  --env HINDSIGHT_API_LLM_PROVIDER=deepseek \
  --env HINDSIGHT_API_LLM_API_KEY=<deepseek-key> \
  --env HINDSIGHT_API_LLM_MODEL=deepseek-v4-flash

# Start daemon (survives gateway restarts)
uvx hindsight-embed -p <agent-name> daemon start
```

**Note:** First start takes 60-120s — embedded PostgreSQL initialization + dependency downloads.
Subsequent starts are instant.

### 6. Disable built-in memory tool

```bash
HERMES_HOME=/path/to/agent hermes tools disable memory
```

### 7. Restart gateway + start fresh session

```bash
systemctl --user restart hermes-gateway-<agent>
# Then /new from the messaging app
```

### 8. Verify

```bash
curl http://localhost:<PORT>/health           # → {"status":"healthy"}
HERMES_HOME=/path/to/agent hermes memory status  # → Provider: hindsight, Status: available ✓
```

## Pitfalls

### ❌ `ERROR: HINDSIGHT_API_LLM_API_KEY environment variable required`
The daemon uses `HINDSIGHT_API_LLM_*` (with `API_` prefix). The plugin uses `HINDSIGHT_LLM_*` (no
`API_`). **BOTH must be set.**

### ❌ DeepSeek native provider (not OpenAI compatible)
Use `HINDSIGHT_API_LLM_PROVIDER=deepseek` + `HINDSIGHT_API_LLM_MODEL=deepseek-v4-flash` — do NOT use
`provider: openai` with `OPENAI_BASE_URL`.

### ❌ `OPENAI_BASE_URL` in the agent `.env`
NEVER set `OPENAI_BASE_URL` in the agent's `.env` — it redirects Hermes's internal DeepSeek routing
and breaks the primary model. Keep it in the Hindsight daemon profile only.

### ❌ Hindsight tools not registering
The plugin silently skips tool registration when unconfigured. Check:
1. `HINDSIGHT_API_KEY=local-mode` in agent `.env` (required even in local mode)
2. `HINDSIGHT_API_URL=http://localhost:<PORT>` in agent `.env`
3. Restart gateway after adding env vars — the plugin checks at startup

### ❌ Daemon dies after `hermes update`
The daemon does NOT auto-restart after an update (gateway restart kills it). After EVERY update:
`curl -s localhost:<PORT>/health` → if down, `uvx hindsight-embed -p <agent-name> daemon start`.

### ❌ Cross-agent contamination
Never connect one daemon to another agent's bank or data dir. One daemon = one bank = one data dir.
Verify bank fact counts after any ingest (`<agent> Hindsight bank empty` → something is wrong).

### ❌ `auto-fastest` / ModelRelay proxy interference
Remove any `auto-fastest` custom provider from config.yaml. The proxy (port 7352) can intercept
model routing. Check: `grep auto-fastest config.yaml`.

## Gemini Fallback

If DeepSeek runs out of credits, switch the daemon to Gemini:

```bash
uvx hindsight-embed profile set-env <agent> HINDSIGHT_API_LLM_PROVIDER gemini
uvx hindsight-embed profile set-env <agent> HINDSIGHT_API_LLM_API_KEY "<gemini-key>"
uvx hindsight-embed profile set-env <agent> HINDSIGHT_API_LLM_MODEL gemini-flash-latest
uvx hindsight-embed -p <agent> daemon restart
```

## Health probe (for nightly checks)

```bash
# Hindsight health probe
curl -s http://localhost:<PORT>/health | grep -q "healthy" || echo "HINDSIGHT_DOWN"
# Test recall
uvx hindsight-embed -p <agent> memory recall <agent> "health probe" 2>&1 | grep -q "Result" || echo "HINDSIGHT_RECALL_FAIL"
```
