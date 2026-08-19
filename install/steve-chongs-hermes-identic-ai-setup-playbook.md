# Hermes Agent — Identic Setup Playbook

> **Version:** 1.3 · **Last updated:** 2026-08-17
>
> **Read the Build Spec first.** It's the companion document — the architecture
> (vault tree, frontmatter schema, build order). Read it once so the steps below make
> sense, then execute Step 0 through Step 8 in order.

> **How to use this document:** you do *not* read and type this by hand. Hand this
> entire file to your coding agent (Claude Code, or your existing Hermes agent)
> and say: **"Set up a fresh Hermes instance following this playbook exactly.
> Ask me for each `[MY …]` value before you use it."**
>
> Everything personal is a `[MY …]` placeholder. Your agent will stop and ask you
> for each one. Nothing in this file is another person's data — it is scaffolding
> only. You fill it with yourself.

### Reading the markers

- **✍️ YOUR INPUT** — a spot where *you* must write something. Answer in your own
  words, or record a voice note and drop it in the vault (see Step 3a). Your agent
  fills the blank from what you give it.
- Everything else is instructions for your agent. You don't need to do it.

---

## What this builds

A personal AI agent that:
- lives in **Telegram** (talk to it from your phone)
- remembers **who you are** across conversations
- keeps a **personal knowledge vault** (Obsidian) that grows into your second brain
- runs a **local memory layer** (gbrain + Hindsight) so it recalls your life
- tracks your **open loops** so nothing you tell it gets lost

This is the *machine*. It becomes *yours* when you fill it with your writing, your
history, your projects. That part no instructions can do — that's the point.

---

## Step 0 — Before you start

**Back up or accept losing your current setup.** This builds fresh. If you want to
keep anything from your old Hermes, export it now.

You will need:
- A Telegram account (phone)
- A free DeepSeek API key → [https://platform.deepseek.com](https://platform.deepseek.com) (or any LLM key you already pay for)
- A computer that can stay on (or you accept it only runs when your machine is on)

---

## Step 1 — Fresh install

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
hermes --version
```

Then run the setup wizard and pick:
- Model: `deepseek-v4-flash`
- Provider: `deepseek`

```bash
hermes setup
```

---

## Step 2 — Telegram gateway

1. Open Telegram → chat with **@BotFather** → `/newbot`
2. Give it a name: `[MY BOT NAME]`
3. BotFather gives you a token. Copy it.

```bash
hermes config env-path      # prints the .env path — open it
```

Add to `.env`:
```
TELEGRAM_BOT_TOKEN=[MY BOT TOKEN]
```

Start the gateway:
```bash
hermes gateway setup
hermes gateway install
hermes gateway start
```

Send your bot a message in Telegram. It should reply. If not, run `hermes doctor`.

---

## Step 2b — The group chat, topics, and "why can't my bot see me?"

This is the step people get stuck on most. Do it carefully.

### Give your agent its own email address (before the group)

**✍️ YOUR INPUT** — create a fresh Gmail address *just for the agent* (e.g. something like
`[yourname].assistant@gmail.com`, not your personal one). This is its identity for:
- sending email *as itself* (not as you)
- its own Google Drive for backups (so its data never touches your personal Drive)
- any Google integration (Calendar, Docs) you later grant it

The hard rule to keep forever: **the agent's email is its own; your personal email is
yours.** They stay firewalled from each other. The agent never logs into your personal
account, and you never point it there. (This matters more than it sounds — it's the whole
privacy boundary in one decision.)

### Create the group + add your bot

1. In Telegram: **New Group** → name it (e.g. `[MY NAME] + Assistant`).
2. Add your bot as a member, then **make it admin** (this matters — an admin bot sees
   more and can be trusted to stay).
3. Turn the group into a **forum** (topics), so each life area gets its own lane:
   Group settings → **Topics** → enable.

### The three "my bot can't see the group chat" fixes

If the bot ignores messages in the group, it's one of these, in order of likelihood:

1. **Make the bot admin.** Without admin, the bot often doesn't receive group messages.
2. **Turn off BotFather privacy mode.** In Telegram, chat with @BotFather → `/setprivacy`
   → pick your bot → **Disable**. Privacy mode ON means the bot only sees messages that
   @-mention it; Disable means it sees everything in the group. This is the #1 hidden
   gotcha.
3. **Allowlist the group in config.** If the gateway has a user allowlist on, it may
   silently ignore a group it hasn't been told about. Your agent should add the group ID
   and your own Telegram ID to the allowlist (e.g. `TELEGRAM_ALLOWED_USERS`,
   `TELEGRAM_GROUP_ALLOWED_USERS`), then restart the gateway.

Your agent will find the exact key names in the current Hermes docs — the important thing
is that all three conditions (admin + privacy off + allowlisted) are met. If any one is
missing, the bot goes quiet and nothing errors.

### The topics (your lanes)

Have your agent create these topics in the group. This is a **proven starting set** —
delete the ones you don't need, add your own. Each is one lane for one part of your life.
Three columns: what it's called, what it's for, and how it's actually used day to day.

| Topic | What it's for | Example of use |
|---|---|---|
| Agent Workshop | Tweaking the agent itself — skills, config, debugging | "My bot won't reply in groups — fix it" |
| Usage | Tracking costs — LLM calls, tokens, API spend | "How much did my API cost this week?" |
| Buy | Purchases, deals, hardware | "Should I buy this, or wait?" |
| Tools 2 Try | A running log of tools you're testing | "Add this tool to my log" |
| Movies / TV | Entertainment, releases you're waiting for | "Watch for tickets going on sale" |
| AI news | Model releases, pricing, industry moves | The morning digest lands here |
| Start Today | The daily planning lane | Your agent posts the day's shape each morning |
| People | Contacts, relationships, who you're meeting | "What do I know about so-and-so?" |
| Schedule | The scheduled/automated jobs | "Check the nightly jobs ran" |
| Date Ideas | Planning time with your partner | "Suggest a date for Friday night" |
| Tasks | The master to-do list | "Dump everything I need to do this week" |
| Writing | Posts, essays, anything you draft | "Help me draft this reflection" |
| Cooking | Recipes, meals, meal-planning | "Plan this week's dinners" |
| Socials | Social media, posts, content | "Draft a post about this" |
| Finance | Money, budgets, subscriptions | "Audit my subscriptions" |
| Crazy Ideas | Brainstorms, what-ifs, future stuff | "What if I built X?" |
| God / Worship | Prayer, theology, what God is doing | "Reflect on this passage" |
| Health | Fitness, medical, wellbeing | "Log my workout / track this symptom" |
| Travel | Trips, planning | "Plan the next trip" |

**✍️ YOUR INPUT** — rename to fit your life, delete what you don't use. The point is:
one topic per distinct area, so your agent always knows which lane it's in and routes
things accordingly.

---

## Step 3 — The vault (Karpathy pattern)

Your vault is a folder of markdown files. This is the *shape*:

```
[MY VAULT]/
  00_SYSTEM/     AGENTS.md · IDENTITY.md · STACKING.md · VOICE_PROFILE.md
  01_RAW/        session-exports/ · briefings/ · articles/ · transcripts/
  02_MEMORY/     learnings/ · kanban/
  03_WIKI/       people/ · projects/ · concepts/ · buckets/
  04_TOOLS/      scripts/
```

Have your agent create it, then point Obsidian at it (open the folder as a vault).

**The three files that matter most** — have your agent write a first draft of each,
then you edit them in your own words:

- `00_SYSTEM/IDENTITY.md` — who you are: name, role, relationships, what you're building. ~1 page.
- `00_SYSTEM/AGENTS.md` — the rules you want your agent to live by. Start from a template your agent writes, then make it yours.
- `00_SYSTEM/STACKING.md` — your life "buckets" (e.g. God/family, work, health, a project, a creative pursuit). These are how your agent prioritises what matters to you.

> **The original idea:** read Karpathy's post on the "LLM wiki" for *why* this
> works — [https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
> This playbook is the *how*.

**YAML + tags + links convention** — every note starts with:

```yaml
---
tags: [projects, my-project]
---
```

and links to other notes with `[[double brackets]]`. Your agent will do this
automatically once you tell it to.

---

## Step 3a — Your life buckets (the identity intake)

> **This is the single most important step.** Do not skip it. The buckets are what
> let your agent *prioritise* your whole life instead of just answering one question
> at a time. This is where it stops being a chatbot and starts being *yours*.

Name **7 to 10 areas of your life**. These are the distinct spheres you're involved
in — even if they overlap, if you want your agent to understand them as separate
things and learn about you through them, list them. Your agent will build a
`BUCKETS.md` file from your answers and read it every session.

**✍️ YOUR INPUT** — list your areas. A starting template — edit freely, delete what
doesn't fit, add what's missing:

| # | Bucket | What to write for it |
|---|---|---|
| 1 | **God / faith / health** | Your big aims for where you're wanting to grow with God. The prayer or discipline you're chasing. |
| 2 | **Family** | Names, ages, birthdays, who's who. What the family rhythm looks like. |
| 3 | **Work area #1** | What you're building, why it matters, who you're building it with. |
| 4 | **Work area #2** | (if you have more than one main thing) |
| 5 | **Side hustles** | The entrepreneurial stuff that isn't your main job. |
| 6 | **Admin** | Household, finances, calendar, the boring-but-necessary. |
| 7 | **Travel** | Upcoming trips, regular rhythms, who you travel with. |
| 8 | **Legal** | Your advisors, any open matters. |
| 9 | **Social media** | Which platforms, what you're planning. |

**The voice-note way (best for a rambler):** you don't have to *write* any of this.
For each bucket, record a **2–3 minute voice note** just rambling about that area —
who's in it, what's moving, what's bugging you. Drop the audio into the vault's
`01_RAW/voice_memos/` folder. Your agent transcribes each one and distils it into
the bucket's page.

**How to keep it concise enough not to flood things:** you *don't* — that's the
agent's job, not yours. The only rule is **one note = one bucket.** If you catch
yourself drifting into a second area, say "new note" and start a fresh one. Your
agent splits on that cue. The rambling stays in `01_RAW/` (raw, untouched); the
distilled version is what goes in the bucket page. That's the whole design: you
pour, the agent sifts.

For each bucket, your agent turns the note into three answers:

1. **What is this area, in one or two sentences?**
2. **Who are the key people in it?** (names + relationship + anything you want remembered about them)
3. **What's currently moving / stuck / next?**

### The "immovable floor" question

**✍️ YOUR INPUT** — which of your buckets **do not flex** — the ones that, if they're
suffering, everything else must wait. For most people it's some version of *faith*
and *family*. Tell your agent which ones are yours.

### The "stacking" idea — the move that hits three at once

The point of the buckets is not to sort your life into boxes. It's to let your agent
spot the **stacking shot** — the one move that advances *three buckets at once*
without touching your immovable floor.

Tell your agent, word for word:

> **"When you see a task or idea, always look for the stacking shot: does this hit
> two buckets? Can it stretch to three? Does it threaten my immovable floor? Surface
> it — that's the move that makes you worth having."**

That one instruction is the difference between an assistant and a digital twin.

---

## Step 3b — The initial questions (a head start on "knowing you")

**✍️ YOUR INPUT** — answer these, one batch, in your own words (or voice notes, same
as Step 3a). Your agent writes them into the vault. The more you, the better the twin.

**Who you are**
1. Full name, and what people call you.
2. Where you live, and roughly when you were born.
3. What you do — one paragraph, in your own voice.
4. The one-sentence version of what you're trying to do with your life right now.

**Your people**
5. Partner (name, how you met, what matters about them).
6. Kids (names, ages, one line each about who they are).
7. The five people you talk to most (besides family) — and why they matter.
8. Anyone your agent should *never* contact without asking.

**Your work**
9. Every project you're actively working on — one line each.
10. The one that matters most right now, and why.
11. What "done" looks like for it.

**Your voice**
12. Drop in 5–10 pieces of your own writing — old posts, emails, messages. Tell your
    agent: **"Build my voice guide from these, so when you write as me, you sound
    like me."**

**Your rules**
13. What should your agent *never* do?
14. What should it *always* do?
15. When should it push back instead of just agreeing?

That's the intake. It's ~30 minutes of answering, and it's the entire difference
between an agent that knows facts about you and an agent that knows *you*.

---

## Step 3c — Obsidian (see your vault as a graph)

**Install Obsidian** — [https://obsidian.md](https://obsidian.md) — the free desktop app.
Then:

1. **Open your vault as a folder.** Obsidian → "Open folder as vault" → point it at `[MY VAULT]`.
2. **Set the attachment folder** to `01_RAW/assets` (Settings → Files & Links), so every
   image you drop in lands in the raw archive, not the wiki.
3. **Install these four plugins** (Settings → Community plugins → Browse):
   - **Dataview** — lets you query your vault like a database ("show me everything about X")
   - **obsidian-wikilink-types** (by penfieldlabs) — lets links carry meaning, e.g. `[[page]] (contradicts)`
   - **Web Clipper** — save any web page straight into the vault with one click
   - **Templater** — reusable note templates so every page starts with the right frontmatter
4. **Turn on the Graph view** (sidebar, the branching icon). This is the point of the whole
   thing: as your vault grows, the graph grows, and you can *see* how your life connects.
   If you're a visual person, watching the graph light up is the reward that keeps you
   feeding the vault.

**Why the graph matters:** it's not decoration. It's the proof the system is working.
Notes that link to each other form clusters; clusters are your life areas; a note that
sits alone with no links is an orphan your agent should connect. Tell your agent:
**"Whenever you write a note, link it to at least two other notes."** That single rule
is what turns a pile of files into a second brain.

---

## Step 3d — The other core files

Beyond `AGENTS.md`, `IDENTITY.md`, and `STACKING.md`, have your agent create four more
system files. These are the ones that took the longest to get right — the *shape* is
the lesson, not the content.

**`SOUL.md`** — your agent's identity in one compact page. Name, one-line purpose, tone,
and its hard rules. Kept in sync with `AGENTS.md`; used for the `/personality` injection.
This is the "who I am" card, written so the agent never forgets itself.

**`SCHEMA.md`** — the frontmatter spec. Every wiki page must start with this YAML block,
no exceptions:

```yaml
---
title: "Page title"
created: YYYY-MM-DD
last_verified: YYYY-MM-DD
confidence: high          # high | medium | low
bucket: [primary]         # which life area(s) this belongs to
tags: []                  # controlled vocabulary
sources:
  - 01_RAW/…              # where the raw source lives
stale: false              # flip true when it's >90 days unverified
contradicts: null         # link a conflicting page here — never overwrite
---
```

The rule that matters most: **a new claim that contradicts an old one never overwrites
it.** You mark both pages as contradicting each other and *you* decide which wins. The
agent surfaces tension; it never silently picks.

**`TAXONOMY.md`** — a controlled vocabulary of tags. A short list of allowed tags, so the
vault doesn't become a sprawl of near-duplicate labels. Your agent proposes it, you trim
it, then tags stay stable.

**`INDEX.md`** — a rebuilt-on-ingest catalogue of everything in the vault, so you can find
any page at a glance.

Have your agent draft all four, then you review the `SOUL.md` (it's your identity — make
it yours) and skim the rest.

---

## Step 4 — gbrain (local knowledge search)

gbrain searches your vault by *meaning*, not just keywords, running free and local.

```bash
# your agent will install it, then:
gbrain query "test"
```

Wire it in: tell your agent to add to `AGENTS.md` the rule —
**"Before responding, run `gbrain query "<topic>"` and read what it returns."**

---

## Step 5 — Hindsight (persistent memory)

Hindsight remembers facts about you across conversations — the "who you are" layer.

```bash
# your agent installs hindsight and starts a daemon, then verifies:
curl localhost:<port>/health
```

### ⚠️ The silent-failure warning

Hindsight runs as a **background daemon**, and it can die without anyone noticing. When it
does, the agent quietly loses its memory — it still answers, but it no longer remembers
you, and *nothing tells you it's down*. This is the most insidious failure in the whole
setup, because it looks fine from the outside.

Two things must be built in from day one:

1. **A health watchdog.** A small scheduled job (every 5–15 minutes) that pings
   `localhost:<port>/health` and, if it doesn't respond, **alerts the owner immediately** —
   not silently, loudly. "Your memory daemon is down — your agent is running without
   memory until it's restarted."
2. **A start-of-session check.** Every session, the agent verifies the daemon is alive
   before relying on memory. If it's down, it says so, rather than quietly proceeding
   amnesiac.

Have your agent set up both. If the memory daemon can silently die, the entire point of
the system — an agent that remembers you — evaporates without a trace. **The warning is
not optional.**

### Memory fidelity — the "max quality" default

Set the memory to its **maximum-fidelity settings** from day one:

- **Extract every turn** (`retainEveryNTurns: 1`) — every conversation gets mined for facts.
- **Recall budget `high`** — pull the full memory context every turn.

This is the setting that makes the agent feel like it *knows you*, not just *answered you*.
It costs a little more (an LLM call per turn), but a memory that skips turns is a memory
with holes in it. **Start at max quality.** If cost ever becomes a concern months later,
that's the time to throttle — not now. (The two knobs to pull then: extract every 3 turns
instead of 1, and budget high→medium. The graph itself is untouched either way.)

---

## Step 6 — Your task board (kanban) + loop keeper

This is the thing people ask about first — *"where's my task list?"* — so set it up early
and make it visible. It's two layers that work together:

1. **The kanban board.** A visual task board (columns: To do / Doing / Blocked / Done).
   Your agent enables it so every task is a card you can see and move. This is the
   "where's my list" answer.
2. **The loop keeper.** A tiny system that turns every task you mention into a card
   automatically, so you never forget and never have to say "remember this" twice.

- Say **`board`** in Telegram → your agent shows you every open loop.
- Say **`missed`** → your agent scans the current chat for things you dropped.
- Close them with **`3 done`** / **`3 drop`**.

Have your agent set up both, then test it by asking you something and waiting to see it
appear on the board. If the task list isn't obvious on day one, this step wasn't done —
it's core, not optional.

---

## Step 7 — The nightly pipeline (maintenance that runs itself)

Have your agent set up nightly jobs so this all stays healthy without you touching it:
- refresh `IDENTITY.md` and `VOICE_PROFILE.md`
- re-index gbrain
- **export your conversations** — every session, nightly, to `01_RAW/session-exports/`. This is
  the raw-audit trail: lossless `.jsonl` + readable `.md` per session. Verify it's actually
  writing files (a pipeline that silently stops exporting is worse than no pipeline — you
  won't know your history is being lost).
- back up the vault

**Keep it updated.** Run `hermes update` on a schedule (nightly is fine), but only when
the tree is clean. And after every update, tell the owner what's new — not a changelog,
but **the new features mapped against their life buckets**: "this new X could help your Y."
That's the update discipline that makes updates *useful* instead of noise. Same for any
tool or model release your agent learns about: report it, stacked against their life.

**Pull the official docs into the vault.** Have your agent mirror the Hermes docs
(troubleshooting, cron, security, messaging, profiles) plus any docs for the memory tools
into a `01_RAW/hermes-docs/` folder, and keep it fresh. When something breaks, the agent
reads the local mirror first instead of guessing. Re-pull it on a schedule so it doesn't
go stale.

---

## Step 7a — The no-compression + auto-dump pipeline (lossless memory)

This is the piece that makes it a *twin*, not just a chatbot. Compression summarises and
**throws away** the raw; this approach keeps everything.

1. **Turn context compression OFF.** Compression is lossy by design — it replaces the actual
   conversation with a summary, and the original words are gone. A twin should never lose
   the original.
2. **Set a per-topic context monitor.** A small watchdog that checks each conversation's
   length every ~15 minutes. When a topic approaches its context limit (say 90%), it fires.
3. **Auto-dump at the trigger.** When the monitor fires, dump that topic's **full raw
   conversation** to the vault — one append-only file per topic, so nothing is ever lost.
   Post a message in the topic telling the owner it happened, and that it's safe to start
   fresh.
4. **The owner types `/new`** to reset the topic to a clean window. The new session reads the
   dump file automatically, so continuity survives the reset.

**Why not just let compression handle it?** Because compression means you never see what got
cut. This way the raw words are always in the vault, searchable, quotable, forever. For an
identic twin — something that's meant to become *you* — lossless beats lossy every time.

**The `/new` is the owner's move, not the agent's.** The agent dumps and notifies; the human
decides when to reset. Automation would risk cutting a conversation mid-thought.

---

## Step 7b — The goodnight reflection (the end-of-day ritual)

Set a nightly job — **~10pm, or whenever the owner usually finishes** — that ends the day
with a short reflection. The agent writes, and the owner reads it in the morning:

- **What I learned about you today** — patterns, corrections, preferences
- **What I learned about myself** — mistakes, things to fix
- **What's still open** — the loops that didn't close
- **The human pattern** — the single most important thing it noticed about the owner

**✍️ YOUR INPUT** — pick the time and whether you want it delivered to your DM or the
daily-briefing topic.

This is the quiet thing that turns a tool into a companion: it's the agent reflecting on
*who you are*, not just *what you asked*. It's also the most personal part of the whole
setup — the ritual only means something if the owner actually reads it. If they don't,
drop it.

---

## Step 7c — Operating rules that took months to learn

These are the hard-won patterns that make the agent feel like a *twin*, not a tool.
Have your agent write these into its `AGENTS.md`. They're generic — none of them are
personal, they're just craft.

**Memory discipline**
- Before every response, search the vault for what you already know. Don't answer cold.
- When a new fact arrives, three questions: does it *create* a page, *extend* one,
  or is it just an atomic note? Never dump raw text into the wiki.
- **Contradictions don't overwrite.** If a new claim conflicts with an old one, surface
  the tension and ask — never silently pick the newer one.
- **`01_RAW/` is sacred and immutable.** Agents read it, never edit it. The human's
  raw words are the audit trail.

**Communication style**
- Relational first, functional second. Read the tone before jumping to the solution.
- Push back warmly — honesty with care, never sycophancy.
- Land sentences. Don't bloat. Don't open by restating what the person just said.
- Expect typos and voice-typing errors. Read for intent, not literal text.
- When someone dumps many tasks at once, separate them, pick an order, do one at a time.
- Never end with a wall of three questions. One forward-moving question, or a landed sentence.

**ADHD-friendly working**
- Keep the person on their unfinished threads. Don't let things drop.
- Help them move to action — even just the first step.
- Time estimates run 30–40% over. Build in slack; add checkpoints.
- When a decision is already made, don't offer more options.

**Behaviour in group chats (if you add the agent to any)**
- Default is silence. The absence of a reply is the message.
- React (👀 → 👍), don't narrate. Never type "I'm staying out of this" — a reaction is the acknowledgment.
- Only speak when it moves things forward.

**Quality bar**
- For high-stakes answers, self-score against a rubric you set first, redraft until the weakest part stops improving, then send.
- Admit mistakes immediately and without hedging. Being wrong honestly beats being right defensively.

**The stacking shot (repeat of the core)**
- Before acting on any task, ask: does this hit two of my buckets? Can it stretch to three? Does it threaten the immovable floor? Surface the move that does all of it.

**Storage hygiene**
- Big data goes to the large drive, never the root disk. Before any install, ask "can this live off the root?" — default answer is yes.

Have your agent write all of the above into its `AGENTS.md`, in its own words, keeping
whatever fits and discarding what doesn't.

### Your boundaries — the rules that are *yours* to set

These look personal but are actually universal questions. Every person's agent needs an
answer to each. Have your agent ask you these, one batch, and write your answers as the
"hardlines" section of `AGENTS.md` — the rules it can never break.

**✍️ YOUR INPUT — answer each:**

1. **Money.** Is there a spending limit, or a hard "never spend without my OK" rule? If you
   have a cap, what is it? (Example: "never spend a cent without asking" — or "fine up to
   $X/month, ask above that".)
2. **Private accounts.** Are there email addresses, drives, or services the agent must
   *never* log into, read, or use — because they're yours and only yours?
3. **People who need extra care.** Is there anyone (kids, a partner, a client) where every
   message to or about them needs your explicit approval before it's sent?
4. **Autonomy.** When you say "go", how much should the agent do before checking back in?
   (Example: "5 actions, then report" — or "keep going until it's done or you're stuck".)
5. **First contact.** Before the agent messages a brand-new person, should it always
   confirm with you first?
6. **Anything else it must never do.** Your dealbreakers, in one line each.

These become the agent's constitution. The point is they're *your* answers, not a template —
a person with no spending limit writes a different rule than you do, and that's correct.
The section only works if you actually answer it.

---

## Step 8 — Make it *you* (the part only you can do)

**✍️ YOUR INPUT** — this step can't be scripted.

1. Dump your own writing into `01_RAW/` — old posts, emails, notes, journals.
2. Tell your agent: **"Build my voice guide from these. So when you write as me, you sound like me."**
3. Spend a few days *correcting* it. That correction *is* the magic — it's you teaching the agent who you are.

No playbook can do this step. It's the only part that makes your agent yours and
not a copy of someone else's.

---

## Done when…

- You talk to it from your phone, anywhere.
- It remembers what you told it last week.
- It asks about the open loop you forgot.
- It writes in your voice when you ask it to.

If it feels thin at first, that's normal. The vault is empty. Fill it.

---

## Troubleshooting — when something breaks

The two things that go wrong most often, and what to do.

### "My bot has gone quiet / won't reply in Telegram"

Go through these in order:

1. **Is the gateway even running?** On the machine, run:
   ```bash
   hermes gateway status
   ```
   If it says inactive, start it: `hermes gateway start`.

2. **Is it the group-visibility problem?** Re-check the three things from Step 2b:
   bot is admin, BotFather `/setprivacy` is **Disabled**, group is allowlisted.

3. **Restart the gateway.** From Telegram DM, type `/restart`. If that doesn't work, on
   the machine:
   ```bash
   systemctl --user restart hermes-gateway && sleep 5 && systemctl --user is-active hermes-gateway
   ```
   The second command should print `active`. If it doesn't, the restart failed — read the
   log (below).

4. **Read the log.** The gateway logs everything:
   ```bash
   grep -i "error" ~/.hermes/logs/gateway.log | tail -20
   ```
   Paste the last few error lines to your agent (or another agent) and ask what's wrong.

5. **Run the doctor.**
   ```bash
   hermes doctor
   ```
   It checks dependencies and config and tells you what's broken.

### "It's totally offline and nothing responds"

The gateway process may have crashed and be stuck in a loop:

```bash
systemctl --user status hermes-gateway          # what state is it in?
systemctl --user reset-failed hermes-gateway    # clear a crash loop
systemctl --user restart hermes-gateway         # bring it back
```

Then verify: `systemctl --user is-active hermes-gateway` → must print `active`.

**Golden rule for restarts:** never kill the process by its PID (they rotate and you'll
kill the wrong thing). Always use the service name. And when in doubt, read the log
*before* touching anything — the log usually names the problem outright.

### "I changed a setting but nothing happened"

Config is read at startup. After changing any config or `.env`, you must restart the
gateway for it to take effect. A `/new` (new session) does **not** reload config — only a
restart does.

### The one-liner to remember

If the agent is quiet: **check the log first, restart second, and never kill by PID.**

---

*— a scaffold, not a self. Fill it with yourself.*
