#!/usr/bin/env python3
"""
topic_dump.py — dump a session's full transcript to a per-topic append-only file.

One raw dump file per topic, appended over time (the archive is lossless and
grows; the state file / memory layer is what gets re-read).

GENERIC — no owner-specific paths or identity. Configure via environment:

    HERMES_HOME          → where this agent's state.db lives (default ~/.hermes)
    IDENTIC_VAULT        → the agent's vault root (required; NOT assumed, e.g.
                           ~/my-vault)
    IDENTIC_TOPIC_NAMES  → optional JSON file mapping thread_id → friendly topic name.
                           Absent = labels fall back to "thread <id>".

Usage:
    python3 topic_dump.py --session <session_id> [--topic-label "Agent Workshop"]
    python3 topic_dump.py --thread <thread_id> [--topic-label "..."]

Writes to <IDENTIC_VAULT>/01_RAW/sessions/topic-<label>-dump.md (append-only).
Prints the absolute path on success so callers can report it to the owner.
"""
import json, os, sqlite3, sys
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()
STATE_DB = HERMES_HOME / "state.db"
VAULT_RAW = Path(os.environ.get("IDENTIC_VAULT", "")).expanduser() / "01_RAW" / "sessions"

TOPIC_NAMES = {}
_names_json = os.environ.get("IDENTIC_TOPIC_NAMES", "")
if _names_json:
    _p = Path(_names_json).expanduser()
    if _p.exists():
        try:
            TOPIC_NAMES = {str(k): v for k, v in json.loads(_p.read_text()).items()}
        except Exception:
            TOPIC_NAMES = {}

if str(VAULT_RAW).startswith("/01_RAW"):  # IDENTIC_VAULT unset → nothing writable
    print("NO_VAULT: set IDENTIC_VAULT (e.g. ~/my-vault)")
    sys.exit(1)


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "")).strip("-").lower() or "untitled"


def main():
    args = {}
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            args[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            i += 1

    if not STATE_DB.exists():
        print("NO_DB")
        return

    conn = sqlite3.connect(str(STATE_DB))
    conn.row_factory = sqlite3.Row

    session = None
    if args.get("session"):
        session = conn.execute(
            "SELECT * FROM sessions WHERE id=?", (args["session"],)
        ).fetchone()
    elif args.get("thread"):
        # Dump the most recent session FOR THIS THREAD that actually holds
        # messages. After /new, a fresh empty session is the "active" one —
        # skipping it and grabbing the just-ended session is what makes a
        # retroactive dump work (the owner /new's first, we dump after).
        session = conn.execute(
            "SELECT * FROM sessions WHERE thread_id=? AND message_count > 0 "
            "ORDER BY last_activity_at DESC LIMIT 1",
            (args["thread"],),
        ).fetchone()

    if session is None:
        print("NO_SESSION")
        conn.close()
        return

    label = args.get("topic-label") or TOPIC_NAMES.get(str(session["thread_id"]), "DM")
    fname = f"topic-{slug(label)}-dump.md"
    path = VAULT_RAW / fname
    path.parent.mkdir(parents=True, exist_ok=True)

    msgs = conn.execute(
        "SELECT role, content, timestamp FROM messages WHERE session_id=? ORDER BY timestamp",
        (session["id"],),
    ).fetchall()
    conn.close()

    # Append a new dump block. If the file exists, add a separator + new header.
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = []
    if path.exists():
        block.append(f"\n\n---\n\n## Dump {now} — session {session['id']}\n")
    else:
        block.append(f"# Topic dump — {label}\n")
        block.append(f"\nAppend-only archive. One file per topic. Refreshed at each 90% context dump.\n")
        block.append(f"\n## Dump {now} — session {session['id']}\n")

    block.append(f"_title: {session['title'] or '(untitled)'} · started: {session['started_at']} · {len(msgs)} messages_\n")
    for m in msgs:
        role = m["role"]
        content = (m["content"] or "").strip()
        if not content:
            continue
        who = "**Owner**" if role == "user" else "**Agent**"
        block.append(f"\n{who}: {content}\n")

    with open(path, "a") as f:
        f.write("\n".join(block))

    print(str(path))


if __name__ == "__main__":
    main()
