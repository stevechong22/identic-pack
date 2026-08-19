---
name: update-identic
description: "Pull the latest identic pack into this agent — /update identic."
version: 1.0.0
category: autonomous-ai-agents
metadata:
  hermes:
    exportable: true
    tags: [identic-pack, update, distribution, multi-agent]
---

# Update Identic

Bring THIS agent to the latest version of the shared identic pack — the
versioned source of truth for every reusable skill and script across the fleet.

**The agent pulls; it never pushes. Only the owner promotes into the repo.**
Pull is downstream; promote is upstream. They never cross.

## When to use

- The owner says **"update identic"** or **"roll it out"** in any topic.
- A new release is announced (`RELEASES.md`) and you want it.
- A fresh agent just installed the base Hermes and needs the pack.

## How it works

1. `update-identic.sh` clones/pulls `<IDENTIC_REPO_URL>` (a git repo — box
   independent, works on a shared box or a standalone machine).
2. It installs everything in the repo's `skills/` and `scripts/` into THIS
   agent's own home:
   - `skills/` → `<HERMES_HOME>/skills/` (new skills load next session)
   - `scripts/` → `<HERMES_HOME>/scripts/` (available immediately)
3. It reports: what changed, from which version, any conflicts.
4. It does **NOT** touch: identity, config, tokens, `.env`, the vault, or
   anything in `extras/OPTIONAL.md`.

## The gate — what rolls and what doesn't

| In the repo | Installed by /update identic |
|---|---|
| `skills/` — exportable, genericized skills | ✅ Yes |
| `scripts/` — parameterized scripts | ✅ Yes |
| `workflows/` — generic pipeline docs | ✅ Yes (into a docs location) |
| `install/` — the setup docs | ✅ (first install only) |
| `extras/OPTIONAL.md` — curated links | ❌ Never auto-installed |
| Anything with identity, voice, memory, family, or secrets | ❌ Must never be in the repo |

The owner says **"roll it out"** to promote something new. That's the only gate.

## Slack command

On the owner's instruction, run:

```bash
IDENTIC_REPO_URL=<repo> bash <HERMES_HOME>/scripts/update-identic.sh
```

Or with `--dry-run` to preview before applying:

```bash
IDENTIC_REPO_URL=<repo> bash <HERMES_HOME>/scripts/update-identic.sh --dry-run
```

## On different boxes

The same command works everywhere because it's just git. A fresh agent on a new
machine needs only: the repo URL + a way to reach it (SSH key or token), then
`/update identic` brings it current. No per-box config, no manual copying.

## Pitfalls

- **Never push to the repo from an agent.** Only the owner promotes. If you
  think something belongs in the pack, tell the owner "this is worth promoting"
  — don't commit it.
- **Version drift:** always check `git pull` output for "Already up to date"
  vs a real change. Report the before → after version.
- **The genericize test before promoting anything:** if it contains the
  owner's name, identity, voice, family, or secrets — it does not belong in the
  pack. If it has a hardcoded path/port/owner — parameterize it first.
