# Steve Chong Identic Pack

> The reusable layer that sits on top of any Hermes install to make it an *identic*
> agent — one that remembers its owner, tracks their life buckets, and works like a
> twin, not a chatbot.

**This is the machine, not the man.** Everything here is generic scaffolding. It is
deliberately free of one person's identity, voice, memory, and secrets. Each person who
installs it fills it with themselves.

## What's in here

| Directory | What it holds |
|---|---|
| `skills/` | Exportable skills — the reusable procedures (silence discipline, context watchdog, loop keeper, stacking) |
| `scripts/` | Parameterized scripts — no hardcoded paths, ports, or owner identity |
| `workflows/` | Generic pipeline docs — the auto-dump/context pipeline, goodnight ritual, nightly maintenance |
| `install/` | The setup docs — playbook, build spec, BotFather guide |
| `extras/` | Optional extras — a curated list of links, NOT auto-installed |
| `MANIFEST.json` | The gate — `core` (auto-install) vs `optional` (links only) |

## The gate

Nothing enters this repo unless the owner says **"roll it out."** Promotion is:

1. Owner tests the thing live on their own agent.
2. Owner says roll it out.
3. The thing is committed here with a version bump in `VERSION.md`.
4. Downstream agents run the update command to pull it.

**Core = auto-installed. Optional = a list of links.** Be ruthless about what earns the
`core` label: only things every identic agent should have. Everything else is optional.

## Install / update (on any agent)

An agent pulls the latest with the update command (see `workflows/update-identic.md`):

```
/update identic
```

This does a `git pull` from this repo into the agent's own `skills/` and `scripts/` —
box-independent, because it's just git.

---

*— a scaffold, not a self. Fill it with yourself.*
