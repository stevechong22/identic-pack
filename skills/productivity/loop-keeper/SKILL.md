---
name: loop-keeper
description: "Loop kanban: per-topic cards, one-word closes, daily digest."
version: 1.0.0
category: productivity
metadata:
  hermes:
    exportable: true
    tags: [kanban, adhd, telegram, topics, loops, daily-briefing]
---

# Loop Keeper

A human's brain runs many parallel lanes (Telegram topics). Loops get opened and
buried, and the topic interface shows no badges so they can't tell what's
waiting. Loop Keeper gives every loop a durable card that survives topic
context resets, and closes loops with one-word replies. **Designed to add
structure without squashing multi-lane speed.**

## Core Design (do not break these)

1. **Every topic is a lane.** Card's `topic` = the Telegram thread id where the
   loop lives. One topic per loop.
2. **The store is the single source of truth.** `<IDENTIC_VAULT>/02_MEMORY/kanban/loops.json`
   (agent-owned, vault-backed nightly → Drive + NVMe). NEVER keep kanban state
   only in session context — that was the old pattern's failure mode.
3. **Silent capture — zero-effort, no trigger.** Capture is triggered by EVERY
   owner message, never by them announcing a task. The words `missed` and
   `board` are for VIEWING only. Every actionable in any message becomes a card
   before the reply lands — mid-flurry messages, voice notes (after
   transcription), throwaway thoughts. **If in doubt, card it:** dropping costs
   one word; losing an ask costs weeks. No ceremony, no "I've added that to the
   kanban" announcements.
4. **Append-only.** Done/dropped cards stay in the store forever — they're the
   owner's stepping-stone trail. Never delete.
5. **Close with one word.** Numbered replies: `2 done` / `3 drop` / `5 do it`.
   Voice-typing tolerant: also accept "number two is done", "drop 4", "do it".
6. **Pull by default, one push a day.** The ONLY push is the morning digest.
   Never reintroduce pushes without explicit opt-in — interruptions break
   hyperfocus.

## The Reminder Tail (the core need)

The owner can't see what's waiting — topic notifications vanish, and they won't
remember to type `board` or `missed`. So on EVERY substantive reply in any
topic, append the tail line. **It leads with what's open in THIS topic, listed
by number** — that's what they can act on right now:

`📋 This topic: 2 open — 1. Voice replies repeat everything I said 2. Agent X memory cleanup — reply N done/drop`

- Open here: list the current topic's actual open loops (summaries only, no
  next-actions — those live in the full `board` view). Numbers map to the
  displayed list; "N done/drop" closes them.
- No open loops here but loops elsewhere: `📋 Nothing open here — elsewhere:
  Work(2) · Family(1)` (max 3 topics).
- Nothing open anywhere: no tail line at all.
- Skip on one-word acknowledgements.
- **Never schedule a cron to fire loops into topics** — the owner is only in a
  topic while typing; a cron fires when they're absent = ghost noise. The tail
  fires exactly when they're engaged. The morning digest is the one scheduled
  view.
- Killable: "stop the tail".
- Never fabricate counts — always read from the store via `loops.py digest`.

## TABLE RULE

Every task list the owner sees — loops view, kanban posts, digest task sections
— renders as a TABLE. Always. Telegram does NOT render markdown pipe tables;
raw `|` pipes are unreadable on a phone. The readable table = a monospace
**code block** with aligned columns. Minimal columns: `# | Task | Topic |
Est/Age`. No prose around the table — the table IS the message.

## Compression Rule

The loops response must never become a distraction. Terse: one header line with
the count, topic group lines, one line per loop (globally numbered), one
reply-guidance line. No prose around the table, no blank-line padding, no
section headers, no essays. **A summary that needs scrolling is a failed
response.** The morning digest is the one place with sections — capped at 25
lines.

## Desktop Kanban Mirror (one board)

If the owner wants ONE board — their loops and the agent work visible together
in the Hermes desktop kanban — `loops.py` mirrors loops.json → the ACTIVE
kanban.db board one-way:
- Every open loop becomes an UNASSIGNED `ready` card (title =
  `[TopicName] <plain-English summary>`, project_id = TopicName, body =
  `Owner loop L<id> | topic: X | next: ...`). The worker dispatcher only claims
  cards WITH an assignee, so the owner's loops are never dispatched to agents —
  never assign them.
- Pitfall: the ACTIVE board's DB lives at `~/.hermes/kanban/boards/<slug>/kanban.db`,
  NOT `~/.hermes/kanban.db` (legacy, empty). Direct sqlite writes to the active
  board DB are blocked by the gateway guard — run mutations through the hermes
  CLI (which loops.py does).
- Idempotency key `loop-<card_id>` prevents duplicates; card's kanban task id
  is stored in the loop's `kb_id` field.
- Auto-sync runs inside `loops.py` after every add/done/drop/edit; manual:
  `loops.py sync-kanban`.
- loops.json (Telegram) remains the source of truth; the board is a mirror,
  not the store.

## CLI

Script: `<HERMES_HOME>/scripts/loops.py` (env-configured; see the script header
for `IDENTIC_*` variables)

| Command | Purpose |
|---|---|
| `loops.py add <topic> "<summary>" --next "..." --streams "#3 work,family" [--waiting]` | Open a loop |
| `loops.py list <topic>` | Punchy markdown table for one topic |
| `loops.py all` | Round-the-grounds, one row per topic |
| `loops.py digest` | JSON dump of open loops (for cron / agent composition) |
| `loops.py done <id> --note "..."` | Close a loop |
| `loops.py drop <id> --note "..."` | Abandon a loop |
| `loops.py stats` | Counts |

Card schema: `id` (L{topic}-{seq}), `topic`, `summary`, `next`, `streams[]`,
`lane` (open/done/dropped), `waiting`, `created`, `done`, `note`.

## Commands (word-triggered, in any topic)

| The owner says | The agent does |
|---|---|
| `missed` | **within-topic drop-scan** — scan THIS topic's history for dropped asks (multi-point suggestions where the owner answered only one, flurry drops, parked "read later" items never read, mid-thread topic-jumps) and surface as a table. The owner's primary question: "what did I drop HERE?" |
| `board` / `kb` | **whole-group round-up** (`loops.py all`) — no "all" needed. `board all` / `kb all` / `what's open` are aliases |
| `board in <topic>` | per-topic table (`loops.py list <thread id>`) — usually unnecessary; the pre-flight reminder shows it automatically |
| `board stats` | counts |
| `N done` / `N drop` / `N do it` (reply to a table/digest) | map N → card id, run done/drop. If `do it`: mark note, then do it or schedule it |
| `kill start today` | pause the morning cron (find job id via cronjob list) |
| Any task dropped mid-conversation | capture silently via `loops.py add` before replying |

**Number mapping:** the rendered table numbers cards 1..N in order. When the
owner replies with numbers, resolve against the LAST table rendered in that
topic/session (or re-run `list` and match by position if unsure — verify by
summary before closing, never close on a guess).

**Bare `missed` / `board` / `kb` is ALWAYS the command — never the English
word.** (The old `loops` trigger collided with Nous Research's `/loop` slash
command and was removed. Hindsight per-turn injection carries the trigger rule
into every session regardless of age.)

**Topic id** = `message_thread_id` of the current thread. Map names via the
agent's topic directory (or the `IDENTIC_TOPIC_NAMES` JSON).

## Wait-Detection Signals

The owner's pattern: skims messages and leaves them hanging; asks several
things in one message and replies to only one; changes direction mid-thread.
They often have no idea what's waiting on them.

- **Signal A — the sure tell:** if an agent message ends with a
  recommendation, question, or ask and the owner sends NO reply (or the topic
  goes silent), that ask is waiting on them → it becomes a card. Check at the
  start of every session and in the morning audit.
- **Signal B — the smoking gun:** if the owner's next message in a topic is
  disjointed — not logically connected to the last exchange — the previous ask
  was dropped. Before following the new direction: card any uncarded ask from
  the last exchange, one line ("parking X: <summary> — reply done/drop
  anytime").
- **Signal C — the flurry:** the owner fires 2-3 messages in a row before the
  agent replies. Each message in the flurry can carry an ask. Capture ALL
  actionables before following the latest; anything the reply won't cover
  becomes a card. Never let the last message win by default.
- **Plain-English rule:** every card summary reads like the owner's own words —
  what they were doing when they asked. No internal jargon. Test: if a stranger
  couldn't tell what the owner was doing from the line, rewrite it. Technical
  detail goes in `note`/`streams`, never in the summary.
- **Recall rule:** a summary is ONLY good if it makes the owner go "ahh yes, I
  remember." They cannot recall tasks from compressed labels — their brain
  needs the human context. ALWAYS include the person/place/situation, not a
  category. Bad: "Wise payment blocked". Good: "Monthly payment bounced from
  the joint Wise account — the one in [partner]'s name". Test: read
  the summary aloud — would YOU remember which task it is? Terse summary =
  failed summary. Applies to ALL renders.
- **Multi-ask rule:** one card per recommendation. If the agent's reply makes 3
  recommendations and the owner answers only 1, the other 2 stay open and
  appear in tables/digests until closed. Never let a partial reply silently
  retire the rest.
- **Every open loop is 'waiting on you' by default** (cards with `waiting:
  true` are blocked on someone else — label those ⏳). Make it unmistakable in
  renders: header "N waiting on you".
- **Morning audit — FULL history:** scan the agent's state.db (read-only)
  across ALL group sessions, not just tails, for patterns:
  - **END-ASK** — a session ends on an agent question/recommendation.
  - **SELF-ASK** — the agent asks, then keeps talking, the owner never replied.
  - **PARTIAL** — a multi-question agent message followed by a short or empty
    owner reply (voice notes land as empty text).
  - **FLURRY** — 2+ consecutive owner messages with no agent between; earlier
    asks in the flurry were likely dropped.
  - Heuristic: agent messages whose last ~500 chars match
    `?|should |which |pick |choose |do you|want me|send me|let me know|your call|you decide`;
    flurry = 2+ `user` role messages in a row.
  - Triage with judgment: card genuine unanswered asks not already in the store
    (check `loops.json` first); skip resolved or stale (>7 days unless
    verifiably still live); never fabricate an ask — only card what the
    messages actually show. Dedup: never two cards for the same ask.

## Start Today (morning cron)

- Job: "Start Today — loop-closing briefing", `0 7 * * *`, deliver to the daily
  topic, attach_to_session=true, skills=[loop-keeper].
- Prompt steps (self-contained): run `loops.py digest` → read STACKING.md
  active threads → compose numbered digest → save copy to
  `02_MEMORY/kanban/start-today-YYYY-MM-DD.md` → output as final response.
- Format — **MANDATORY board style** (≤25 lines, phone-readable; a wall of text
  is a failed briefing):
```
🌅 Start Today — Fri 7 Aug · 13 open
⚡ QUICK WINS — <5-15 min
| # | Task | Topic | Est | Age |
|---|------|-------|-----|-----|
| 3 | Message Dan re Mac | [Tech](https://t.me/c/<group>/17) | 2m | 0d |
🔥 CRITICAL — timing-sensitive
| # | Task | Topic | Est | Age |
|---|------|-------|-----|-----|
| 9 | Jo — agent concerns. Today | [Work](https://t.me/c/<group>/9) | 30m | 0d |
📅 LATER / THIS WEEK
| # | Task | Topic | Est | Age |
|---|------|-------|-----|-----|
| 16 | Project stocktake | [Thesis](https://t.me/c/<group>/13) | 3h | 0d |
⏳ Blocked on others: Person (thing)
💡 Stacking shot: ...
Reply "N done / N drop / N do it"
```
- Every row: number + plain-English summary, hyperlinked topic, est time, age.
- Age computed from the card's `created` (or the kanban state file's `added`
  field if the task lives there).
- ⚡ Quick wins: 2-3 loops doable in <5-15 min (message replies, approvals,
  small decisions).
- ⏳ Blocked on others: cards with `waiting: true`.
- 💡 Stacking shot: 1-2 suggestions cross-referencing STACKING.md active
  threads against open loops.
- If zero open loops: send a 3-line "nothing open 🎉" message — never pad.
- **watch-item (first week):** confirm attach_to_session posts into the daily
  topic rather than creating a new topic per day; if it creates topics, switch
  to plain `:<topic_id>` delivery without attach_to_session.
- Other agents' groups are NOT in this store (agent isolation). The digest
  never invents counts for lanes it doesn't own.

## Fabric Rule

Every session in any topic ends with its actionables recorded. Concretely:
1. Identify actionables in the owner's message(s) — tasks, decisions pending on
   them, waiting-on items.
2. Before your reply lands, run `loops.py add` (new) or update the card
   (`done`/`drop`/`--next` refresh) silently.
3. If a loop is already closed or the owner says "forget it", drop the card —
   don't keep zombie loops.
4. Stacking cross-check on close: when a loop closes, check STACKING.md — does
   a done loop open a follow-up in another stream? Suggest it (one line).

## Pitfalls

- **Never close on a guessed number** — if the mapping is ambiguous, re-render
  the table and ask.
- **Don't spam confirmations** — closing a loop gets a one-liner, not a table
  re-render, unless asked.
- **Store path is vault, not the agent home** — the vault gets backed up
  nightly. If `02_MEMORY/kanban/` doesn't exist, the script creates it.
- **Concurrent writes** — single agent, low risk; the script writes atomically
  (tmp+rename).
- **Do not confuse with `kanban.db`** (Hermes worker-dispatch kanban,
  `hermes kanban ...`). That's for agents doing work. Loop Keeper is for the
  owner-facing life loops. Never create dispatcher cards for the owner's
  personal loops.

## Verification

```bash
python3 <HERMES_HOME>/scripts/loops.py stats
python3 <HERMES_HOME>/scripts/loops.py list 29
python3 <HERMES_HOME>/scripts/loops.py digest
```
Round-trip test: add → done → confirm lane flip → store persists across
sessions (it's on disk, vault-backed).
