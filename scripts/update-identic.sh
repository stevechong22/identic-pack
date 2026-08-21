#!/bin/bash
# update-identic.sh — pull the latest identic pack into THIS agent's home.
#
# Box-independent: works on a shared box or a standalone machine — it's just git.
# The agent pulls; it never pushes. Only the owner promotes.
#
# Usage:
#   update-identic.sh                 # full update: skills + scripts + workflows
#   update-identic.sh --dry-run       # show what WOULD change, change nothing
#
# Env (set in the agent's .env or before calling):
#   IDENTIC_REPO_URL  → the git repo (e.g. git@github.com:stevechong22/identic-pack.git)
#   HERMES_HOME       → where this agent lives (default ~/.hermes)
#   IDENTIC_VAULT     → the agent's vault root (used to place workflows)
set -euo pipefail

REPO_URL="${IDENTIC_REPO_URL:-}"
HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CACHE_DIR="${HOME_DIR}/.cache/identic-pack"
SKILLS_TARGET="${HOME_DIR}/skills"
SCRIPTS_TARGET="${HOME_DIR}/scripts"
DOCS_TARGET="${HOME_DIR}/docs/identic"

DRY=""
[ "${1:-}" = "--dry-run" ] && DRY=1

if [ -z "$REPO_URL" ]; then
  echo "ERROR: set IDENTIC_REPO_URL (e.g. git@github.com:stevechong22/identic-pack.git)" >&2
  exit 1
fi

echo "→ Identic pack update"
echo "  repo:   $REPO_URL"
echo "  target: $HOME_DIR"

# Clone/pull the repo
if [ ! -d "$CACHE_DIR/.git" ]; then
  mkdir -p "$(dirname "$CACHE_DIR")"
  git clone --quiet "$REPO_URL" "$CACHE_DIR"
  echo "  cloned fresh"
else
  cd "$CACHE_DIR"
  git pull --quiet
  echo "  pulled latest"
fi

if [ -n "$DRY" ]; then
  echo ""
  echo "→ DRY RUN — would install:"
  find "$CACHE_DIR/skills" -name SKILL.md 2>/dev/null | sed "s|$CACHE_DIR/skills/||;s|/SKILL.md||" | sort | sed 's/^/  skill: /'
  ls "$CACHE_DIR"/scripts/*.py "$CACHE_DIR"/scripts/*.sh 2>/dev/null | xargs -n1 basename 2>/dev/null | sort | sed 's/^/  script: /'
  ls "$CACHE_DIR"/install/*.md 2>/dev/null | xargs -n1 basename 2>/dev/null | sort | sed 's/^/  doc: /'
  echo ""
  echo "→ Nothing changed (dry run)."
  exit 0
fi

# Install skills
count_skills=0
for skill_dir in "$CACHE_DIR"/skills/*/ "$CACHE_DIR"/skills/*/*/; do
  [ -d "$skill_dir" ] || continue
  rel="${skill_dir#$CACHE_DIR/skills/}"
  rel="${rel%/}"
  if [ -f "$skill_dir/SKILL.md" ]; then
    mkdir -p "$SKILLS_TARGET/$rel"
    cp -r "$skill_dir"/* "$SKILLS_TARGET/$rel/"
    count_skills=$((count_skills+1))
  fi
done

# Install scripts
mkdir -p "$SCRIPTS_TARGET"
count_scripts=0
for script in "$CACHE_DIR"/scripts/*.py "$CACHE_DIR"/scripts/*.sh; do
  [ -f "$script" ] || continue
  name="$(basename "$script")"
  cp "$script" "$SCRIPTS_TARGET/$name"
  chmod +x "$SCRIPTS_TARGET/$name"
  count_scripts=$((count_scripts+1))
done

# Install bootstrap docs
mkdir -p "$DOCS_TARGET"
count_docs=0
for doc in "$CACHE_DIR"/install/*.md; do
  [ -f "$doc" ] || continue
  name="$(basename "$doc")"
  cp "$doc" "$DOCS_TARGET/$name"
  count_docs=$((count_docs+1))
done

echo "→ Installed: $count_skills skill(s), $count_scripts script(s), $count_docs doc(s)"
echo "→ Docs: $DOCS_TARGET"
echo "→ Done. New skills load on the next session; scripts are available immediately."
