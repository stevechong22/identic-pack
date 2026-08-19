#!/usr/bin/env python3
"""
context_monitor.py — per-topic token threshold watchdog.

Queries this agent's state.db for active Telegram sessions and warns when any
single topic approaches the context limit. Designed to run as a no_agent cron
job every 15 minutes. Stdout IS the deliverable; silent when all sessions are
healthy.

GENERIC — no owner-specific paths or identity. Configure via environment:

    HERMES_HOME           → where this agent's state.db + .env live (default ~/.hermes)
    IDENTIC_VAULT         → the agent's vault root (for the dump path); set explicitly
    IDENTIC_TOPIC_NAMES   → optional JSON file: thread_id → friendly topic name
    IDENTIC_GROUP_CHAT    → the Telegram group chat id the agent lives in (e.g. -100…)
    IDENTIC_GROUP_URL     → t.me/c/ prefix without the -100 (e.g. 3899944742)
    IDENTIC_CONTEXT_LIMIT → context window in tokens (default 1_000_000)

Cron: */15 * * * *  python3 <path>/context_monitor.py   (no_agent=true)
"""
import sqlite3
import subprocess
import sys
import os
import json
import urllib.request
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))).expanduser()
STATE_DB = HERMES_HOME / "state.db"
DUMP_SCRIPT = HERMES_HOME / "scripts" / "topic_dump.py"
CONTEXT_LIMIT = int(os.environ.get("IDENTIC_CONTEXT_LIMIT", "1000000"))
WARN_THRESHOLD = 0.80
TRIGGER_THRESHOLD = 0.90

GROUP_CHAT_ID = os.environ.get("IDENTIC_GROUP_CHAT", "")
GROUP_URL_PREFIX = os.environ.get("IDENTIC_GROUP_URL", "")

TOPIC_NAMES = {}
_names_json = os.environ.get("IDENTIC_TOPIC_NAMES", "")
if _names_json:
    _p = Path(_names_json).expanduser()
    if _p.exists():
        try:
            TOPIC_NAMES = {str(k): v for k, v in json.loads(_p.read_text()).items()}
        except Exception:
            TOPIC_NAMES = {}


def topic_label(thread_id):
    if not thread_id:
        return "DM"
    name = TOPIC_NAMES.get(str(thread_id))
    return f"{name} (thread {thread_id})" if name else f"thread {thread_id}"


def topic_url(thread_id):
    if not thread_id or not GROUP_URL_PREFIX:
        return None
    return f"{GROUP_URL_PREFIX}/{thread_id}"


def _read_bot_token():
    env_path = HERMES_HOME / ".env"
    if not env_path.exists():
        return ""
    for line in env_path.read_text().splitlines():
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def send_topic_message(thread_id: str, text: str) -> bool:
    """Post a message into a specific Telegram topic thread via the Bot API."""
    token = _read_bot_token()
    if not token or not GROUP_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "message_thread_id": int(thread_id),
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = json.loads(r.read())
            return bool(resp.get("ok"))
    except Exception:
        return False


def get_active_telegram_sessions(db_path: Path) -> list[dict]:
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("""
        SELECT id, title, source, chat_id, thread_id,
               input_tokens, output_tokens,
               (input_tokens + output_tokens) as total_tokens,
               started_at
        FROM sessions
        WHERE ended_at IS NULL AND source = 'telegram' AND chat_id IS NOT NULL
        ORDER BY total_tokens DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def pct(total: int) -> float:
    return (total or 0) / CONTEXT_LIMIT * 100


def format_started(ts: float | None) -> str:
    if not ts:
        return "unknown"
    return datetime.fromtimestamp(ts).strftime("%b %d %H:%M")


def main():
    sessions = get_active_telegram_sessions(STATE_DB)
    if not sessions:
        return

    triggered = []
    warned = []
    for s in sessions:
        total = s["total_tokens"] or 0
        ratio = total / CONTEXT_LIMIT
        if ratio >= TRIGGER_THRESHOLD:
            triggered.append(s)
        elif ratio >= WARN_THRESHOLD:
            warned.append(s)

    if not triggered and not warned:
        return

    STATE_FILE = HERMES_HOME / "cache" / "context-monitor-state.txt"
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    state = {}
    if STATE_FILE.exists():
        try:
            for line in STATE_FILE.read_text().splitlines():
                if ":" in line:
                    sid, level = line.split(":", 1)
                    state[sid] = level
        except Exception:
            state = {}

    new_state = {}
    should_print = False
    dump_results = {}

    for s in sessions:
        sid = str(s["id"])
        if s in triggered:
            if state.get(sid) != "trigger":
                r = subprocess.run(
                    [sys.executable, str(DUMP_SCRIPT), "--session", sid],
                    capture_output=True, text=True, timeout=120,
                )
                if r.returncode == 0 and r.stdout.strip():
                    dump_results[sid] = r.stdout.strip()
                    should_print = True
                    new_state[sid] = "trigger"
                    label = topic_label(s["thread_id"])
                    pct_s = f"{pct(s['total_tokens']):.0f}"
                    topic_msg = (
                        f"🛡️ *Context dump complete — {label}*\n\n"
                        f"This topic hit {pct_s}% of its context window, so I "
                        f"auto-dumped the full history before anything was lost.\n\n"
                        f"📄 Saved to: `{dump_results[sid]}`\n\n"
                        f"Run `/new` here to reset this topic to a fresh window. "
                        f"The next session reads the dump automatically — we pick "
                        f"up where we left off, nothing lost."
                    )
                    if s["thread_id"]:
                        send_topic_message(str(s["thread_id"]), topic_msg)
                else:
                    new_state[sid] = state.get(sid, "warn")
            else:
                new_state[sid] = "trigger"
        elif s in warned:
            if state.get(sid) != "warn":
                should_print = True
            new_state[sid] = "warn"
        else:
            if state.get(sid) != "clear":
                should_print = True
            new_state[sid] = "clear"

    try:
        STATE_FILE.write_text("\n".join(f"{k}:{v}" for k, v in new_state.items()))
    except Exception:
        pass

    if not should_print:
        return

    lines = ["## Context Monitor", ""]
    if triggered:
        lines.append("🔴 **TRIGGER — 90%+ — AUTO-DUMPED**")
        lines.append("")
        for s in triggered:
            label = topic_label(s["thread_id"])
            url = topic_url(s["thread_id"])
            lines.append(
                f"- **{label}** — {s['title'] or '(untitled)'}: "
                f"{pct(s['total_tokens']):.0f}% — "
                f"{s['total_tokens']:,} / {CONTEXT_LIMIT:,} tokens "
                f"(since {format_started(s['started_at'])})\n"
            )
            if url:
                lines.append(f"  {url}")
            if s["id"] in dump_results:
                lines.append(f"  ✅ Raw dump saved: `{dump_results[s['id']]}`")
            lines.append("")
        lines.append("_Dumped automatically — raw archive appended. Reply `/new` here to reset this topic with a clean window._")
        lines.append("")

    if warned:
        lines.append("🟡 **WARNING — 80%+ — heads up**")
        lines.append("")
        for s in warned:
            label = topic_label(s["thread_id"])
            url = topic_url(s["thread_id"])
            lines.append(
                f"- **{label}** — {s['title'] or '(untitled)'}: "
                f"{pct(s['total_tokens']):.0f}% — "
                f"{s['total_tokens']:,} / {CONTEXT_LIMIT:,} tokens "
                f"(since {format_started(s['started_at'])})\n"
            )
            if url:
                lines.append(f"  {url}")
        lines.append("")

    lines.append("_Context compression is intentionally disabled. Auto-dump at 90%, then offer /new with raw dump path._")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
