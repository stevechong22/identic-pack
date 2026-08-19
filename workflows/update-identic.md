# Update Identic — the pull command

Every agent gets one command to bring itself to the latest identic pack version:

```
/update identic
```

## What it does

1. `git pull` this repo (the identic pack) to the latest tag.
2. Install everything in `MANIFEST.json` → `core` into the agent's own `skills/` and `scripts/`.
3. Report: version before → after, what changed, any conflicts.
4. Does **not** touch anything `optional`, and does **not** touch identity, config, tokens, or the vault.

## Why git

Because it's box-independent. The same command works today on one shared box and later
on separate machines — a fresh agent just needs the repo URL and a token, then `/update
identic` does the rest.

## The gate reminder

An agent pulls; it never pushes. Only the owner promotes into the repo. Pull is
downstream; promote is upstream. They never cross.
