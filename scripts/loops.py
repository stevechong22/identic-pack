#!/usr/bin/env python3
"""
Loop Keeper — durable per-topic loop store (the "nothing gets lost" layer).

Every topic is a lane. Cards are written by the agent during conversation (the
fabric rule) and closed by the owner with one-word replies ("N done" / "N drop" /
"N do it").

GENERIC — no owner-specific paths or identity. Configure via environment:

    IDENTIC_STORE         → where loops.json lives (default: <IDENTIC_VAULT>/02_MEMORY/kanban/loops.json)
    IDENTIC_VAULT         → the agent's vault root (used for the store default)
    IDENTIC_TOPIC_NAMES   → optional JSON file mapping thread_id → friendly topic name
    IDENTIC_OWNER_NAME    → the human's name, for "waiting on you" wording (default "the owner")

Store is append-only (vault-backed nightly), one card per actionable, and the
kanban mirror is best-effort: if `hermes kanban` isn't available the script
still works, it just skips the mirror.

Commands:
  add <topic> "<summary>" [--next "..."] [--streams "#3 work,family"] [--waiting]
  list <topic>                     # punchy markdown table for one topic
  all                              # one row per topic with open loops
  digest                           # JSON dump of all open loops (for cron/agent)
  done <card_id> [--note "..."]    # close a loop
  drop <card_id> [--note "..."]    # abandon a loop
  edit <card_id> [--summary] [--next]
  stats                            # counts
  sync-kanban                      # mirror loops to the desktop kanban board (best-effort)
"""
import argparse, datetime, json, os, subprocess, sys

VAULT = os.environ.get("IDENTIC_VAULT", "").strip()
STORE = os.environ.get(
    "IDENTIC_STORE",
    os.path.join(VAULT, "02_MEMORY", "kanban", "loops.json") if VAULT else "",
).strip()
if not STORE:
    print("ERROR: set IDENTIC_VAULT (or IDENTIC_STORE) — the loop store needs a home.")
    sys.exit(1)

OWNER_NAME = os.environ.get("IDENTIC_OWNER_NAME", "the owner")

TOPIC_MAP = {}
_names_json = os.environ.get("IDENTIC_TOPIC_NAMES", "")
if _names_json:
    _p = os.path.expanduser(_names_json)
    if os.path.exists(_p):
        try:
            TOPIC_MAP = {int(k): v for k, v in json.loads(open(_p).read()).items()}
        except Exception:
            TOPIC_MAP = {}


def today():
    return datetime.date.today().isoformat()


def load():
    if not os.path.exists(STORE):
        return {"cards": [], "seq": {}, "updated": today()}
    with open(STORE) as f:
        return json.load(f)


def save(data):
    data["updated"] = today()
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    tmp = STORE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STORE)


def next_seq(data, topic):
    n = data["seq"].get(str(topic), 0) + 1
    data["seq"][str(topic)] = n
    return f"L{topic}-{n}"


def find_card(data, card_id):
    for c in data["cards"]:
        if c["id"] == card_id:
            return c
    return None


def topic_name(t):
    return TOPIC_MAP.get(int(t), f"topic {t}")


def add(topic, summary, next_action="", streams=None, waiting=False):
    data = load()
    card = {
        "id": next_seq(data, topic),
        "topic": int(topic),
        "summary": summary,
        "next": next_action,
        "streams": [s.strip() for s in (streams or "").split(",") if s.strip()],
        "lane": "open",
        "waiting": bool(waiting),
        "created": today(),
        "done": None,
        "note": "",
    }
    data["cards"].append(card)
    save(data)
    return card


def open_cards(data, topic=None):
    cards = [c for c in data["cards"] if c["lane"] == "open"]
    if topic is not None:
        cards = [c for c in cards if c["topic"] == int(topic)]
    return cards


def done_cards(data, topic=None, limit=3):
    cards = [c for c in data["cards"] if c["lane"] == "done"]
    if topic is not None:
        cards = [c for c in cards if c["topic"] == int(topic)]
    cards.sort(key=lambda c: c.get("done") or c["created"], reverse=True)
    return cards[:limit]


def render_topic(topic):
    data = load()
    opens = open_cards(data, topic)
    dones = done_cards(data, topic)
    name = topic_name(topic)
    lines = [f"📋 {name} (#{topic}) — {len(opens)} open"]
    if not opens:
        lines.append("No open loops. 🎉")
    for i, c in enumerate(opens, 1):
        tag = f"[{'/'.join(c['streams'])}] " if c["streams"] else ""
        wait = " ⏳" if c.get("waiting") else ""
        lines.append(f"{i}. ❌ {tag}{c['summary']}{wait}")
        if c.get("next"):
            lines.append(f"   → {c['next']}")
    if dones:
        lines.append(f"✅ Done (last {len(dones)}):")
        for c in dones:
            when = c.get("done") or c["created"]
            lines.append(f"  · {c['summary']} ({when})")
    lines.append("Reply: N done / N drop / N do it")
    text = "\n".join(lines)
    return f"```\n{text}\n```", opens, dones


def render_all():
    data = load()
    opens = open_cards(data)
    by_topic = {}
    for c in opens:
        by_topic.setdefault(c["topic"], []).append(c)
    total = len(opens)
    if not opens:
        return "🌍 Nothing open 🎉"
    lines = [f"🌍 {total} open — waiting on {OWNER_NAME}"]
    n = 0
    for t in sorted(by_topic):
        cards = by_topic[t]
        lines.append(f"#{t} {topic_name(t)} ({len(cards)})")
        for c in cards:
            n += 1
            nxt = f" — {c['next']}" if c.get("next") else ""
            lines.append(f"{n}. {c['summary']}{nxt}")
    lines.append("Reply: N done / N drop / N do it")
    text = "\n".join(lines)
    return f"```\n{text}\n```"


def render_digest_json():
    data = load()
    opens = open_cards(data)
    by_topic = {}
    for c in opens:
        by_topic.setdefault(c["topic"], []).append(c)
    out = {
        "generated": today(),
        "total_open": len(opens),
        "waiting_on_owner": sum(1 for c in opens if not c.get("waiting")),
        "topics": [
            {"topic": t, "name": topic_name(t), "cards": by_topic[t]}
            for t in sorted(by_topic)
        ],
    }
    return json.dumps(out, indent=2, ensure_ascii=False)


def stats():
    data = load()
    opens = open_cards(data)
    dones = [c for c in data["cards"] if c["lane"] == "done"]
    drops = [c for c in data["cards"] if c["lane"] == "dropped"]
    return f"{len(opens)} open · {len(dones)} done · {len(drops)} dropped"


def close_card(card_id, lane, note=""):
    data = load()
    c = find_card(data, card_id)
    if not c:
        return None, f"no card {card_id}"
    c["lane"] = lane
    c["done"] = today()
    if note:
        c["note"] = note
    save(data)
    return c, None


def kb_current_board():
    out, _ = _kb("boards", "list")
    for line in out.splitlines():
        if line.startswith("Current board:"):
            return line.split(":", 1)[1].strip()
    return None


def _kb(*args):
    try:
        r = subprocess.run(["hermes", "kanban", *args],
                           capture_output=True, text=True, timeout=180)
        return r.stdout.strip(), r.returncode
    except Exception:
        return "", 1


def sync_kanban(quiet=True):
    """Mirror loops.json -> kanban.db active board (one-way, best-effort)."""
    board = kb_current_board()
    if not board:
        return -1
    data = load()
    mirrored = 0
    for c in data["cards"]:
        try:
            if c["lane"] == "open":
                if c.get("kb_id"):
                    continue
                title = f"[{topic_name(c['topic'])}] {c['summary']}"
                body = (f"Owner loop {c['id']} | topic: {topic_name(c['topic'])}"
                        f" | next: {c.get('next') or ''}")
                out, rc = _kb("--board", board, "create", "--json",
                              "--idempotency-key", f"loop-{c['id']}",
                              "--project", topic_name(c["topic"]),
                              "--body", body, title)
                if rc != 0:
                    continue
                info = json.loads(out) if out else {}
                tid = info.get("task_id") or info.get("id")
                if tid:
                    c["kb_id"] = tid
                    save(data)
                    mirrored += 1
            else:  # done / dropped
                if c.get("kb_id"):
                    _kb("--board", board, "complete", c["kb_id"],
                        "--summary", f"closed {c.get('done') or today()}")
                    c["kb_id"] = None
                    save(data)
        except Exception:
            continue
    if not quiet:
        print(f"kanban mirror synced to board '{board}': {mirrored} new")
    return mirrored


def main():
    p = argparse.ArgumentParser(description="Loop Keeper — per-topic loop store")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="add a card")
    a.add_argument("topic", type=int)
    a.add_argument("summary")
    a.add_argument("--next", default="")
    a.add_argument("--streams", default="")
    a.add_argument("--waiting", action="store_true")

    l = sub.add_parser("list", help="render one topic's table")
    l.add_argument("topic", type=int)

    sub.add_parser("all", help="render whole-group round-up")
    sub.add_parser("digest", help="JSON dump of open loops (cron)")
    sub.add_parser("stats", help="counts")

    d = sub.add_parser("done", help="close a loop")
    d.add_argument("card_id")
    d.add_argument("--note", default="")

    dr = sub.add_parser("drop", help="abandon a loop")
    dr.add_argument("card_id")
    dr.add_argument("--note", default="")

    e = sub.add_parser("edit", help="rewrite a card (plain English)")
    e.add_argument("card_id")
    e.add_argument("--summary", default=None)
    e.add_argument("--next", default=None)

    s = sub.add_parser("sync-kanban", help="mirror loops to the desktop kanban board")

    args = p.parse_args()

    if args.cmd == "add":
        c = add(args.topic, args.summary, args.next, args.streams, args.waiting)
        sync_kanban()
        print(f"added {c['id']}: {c['summary']}")
    elif args.cmd == "list":
        text, opens, dones = render_topic(args.topic)
        print(text)
    elif args.cmd == "all":
        print(render_all())
    elif args.cmd == "digest":
        print(render_digest_json())
    elif args.cmd == "stats":
        print(stats())
    elif args.cmd in ("done", "drop"):
        c, err = close_card(args.card_id, args.cmd, args.note)
        if err:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(1)
        sync_kanban()
        print(f"{args.cmd}: {args.card_id} — {c['summary']}")
    elif args.cmd == "edit":
        data = load()
        c = find_card(data, args.card_id)
        if not c:
            print(f"ERROR: no card {args.card_id}", file=sys.stderr)
            sys.exit(1)
        if args.summary is not None:
            c["summary"] = args.summary
        if args.next is not None:
            c["next"] = args.next
        save(data)
        sync_kanban()
        print(f"edited {args.card_id}: {c['summary']}")
    elif args.cmd == "sync-kanban":
        n = sync_kanban(quiet=False)
        print(f"mirrored {n} new card(s) to the desktop kanban" if n >= 0 else "ERROR: could not read kanban board")


if __name__ == "__main__":
    main()
