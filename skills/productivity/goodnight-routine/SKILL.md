---
name: goodnight-routine
description: "Four-step end-of-session routine: reflect, ingest, cross-link, dream cycle."
triggers:
  - Owner says "goodnight"
  - End of session / daily wrap
version: 1.0.0
category: productivity
---

# Goodnight Routine (generic)

When the owner says "goodnight" (or any close-of-session signal), run these four steps in order.
Steps 3 and 4 can be delegated to background subagents and run in parallel.

The vault pipeline (raw → wiki → cross-link → gbrain) handles preservation. Goodnight is
**reflection + vault maintenance** — not a compression-salvage ritual.

---

## Step 0: Session Close (before reflection — silent)

1. Flip the model back to the agent's default if an auto-upgrade ran during the session.
2. Check the memory daemon health (silent — the owner doesn't need to see this).

---

## Step 1: Reflect, Record, and Deliver to the Owner

**Goal:** capture what you learned and deliver it as part of the goodnight message.

### Coverage window — CRITICAL

Reflect on the **work since the last goodnight run**, NOT the current calendar day and NOT just the
current session.

- **Midnight boundary rule:** owners often work past midnight. A goodnight triggered at 1:30am wraps
  up the *previous* day's work. Reflect on the work, not the date.
- **All surfaces:** a day of work spans the DM AND every group topic. Before writing anything,
  enumerate ALL sessions with activity since the last goodnight (query the session store; read the
  significant user↔assistant exchanges, not just titles).
- **A thin-looking day is never an excuse for a thin reflection.** If this session has two messages,
  the reflection is about the *other* sessions. Short session ≠ short reflection.

### Write the learnings file

Write `02_MEMORY/<agent-name>-learnings-YYYY-MM-DD.md` with exactly these sections:

1. **About the Owner** — corrections, preferences, patterns, what they care about
2. **About Me — What I Need to Fix** — what you did wrong, what you improved, hard rules to lock
3. **About Peers** — cross-agent and family interactions worth noting
4. **About the System** — config changes, new commands, architecture lessons
5. **The Human Pattern** — the single most important relational observation of the day

### Deliver as text — never as a file link

After writing the file, paste the reflection **as text in the goodnight reply**. The owner gets to
read the agent's inner life — this is the closing of the day. Never skip it, never link to it.

---

## Step 2: Ingest the Session and Update Wikis

**Goal:** preserve the session's output and wire it into the vault's index.

1. Preserve concrete artifacts (commands, config changes) into `01_RAW/` — source, unedited.
2. Wire new files into `03_WIKI/`: add `[[wikilinks]]`, `tags:`, and dated subheadings on the
   relevant project or concept pages.
3. Update `STACKING.md` if a new active thread started.
4. Add any newly verified commands to `00_SYSTEM/VERIFIED_COMMANDS.md`.

---

## Step 3: Cross-Link the Vault

**Goal:** eliminate orphans (zero backlinks) and stubs (zero forward links).

1. Walk every `.md` file in `03_WIKI/`.
2. For each page: extract `[[wikilinks]]` and frontmatter `tags:`.
3. Find backlinks by grepping for `[[page-name]]` across `03_WIKI/`.
4. For any orphan or stub, add 2–3 meaningful cross-links (shared themes/people/projects — never
   mechanical bulk).

**Rules:** never modify `00_SYSTEM/`, `01_RAW/`, or `04_TOOLS/`. Back up before editing. Delegate
to a parallel subagent for vaults with 50+ pages.

---

## Step 4: Run the Dream Cycle + Memory Health

**Goal:** refresh embeddings so the vault is searchable tomorrow, and verify memory is alive.

1. Dream cycle (try in order):
   - `gbrain dream cycle --vault <vault-path>`
   - or the agent's local dream-cycle script
   - or manual: walk `03_WIKI/` and run `gbrain refresh <file>` for every markdown file
2. Memory health probe: `curl -s localhost:<port>/health` — if down, alert the owner.

The dream cycle can take minutes on a large vault — delegate to a background subagent.

---

## Execution Order

```
Step 1 (reflect) — do immediately, owner is waiting
Step 2 (ingest)  — do immediately, files are fresh
Step 3 (cross-link) — delegate to background subagent
Step 4 (dream)   — delegate to background subagent
```

Steps 3 and 4 run in parallel after 1 and 2 are done.

---

## Pitfalls

- Don't skip reflection just because the session was short — short sessions often yield the
  sharpest learnings.
- Cross-linking must back up files before modifying — a bad regex can corrupt YAML frontmatter.
- Never deliver the reflection as a file link — the owner explicitly wants the text itself.
- If the owner stops reading the reflections, drop the ritual or change the delivery — a ritual
  nobody reads becomes noise.
