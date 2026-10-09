#!/usr/bin/env bash
# Install this skill into one or more agents' skill directories.
#
#   bash install.sh <claude|cursor|zcode|agents|all> [--user] [--project DIR]
#
# Project scope (default) copies into DIR/.claude/skills, DIR/.cursor/skills, DIR/.zcode/skills or
# DIR/.agents/skills, where DIR is --project, else the git root of the current directory, else $PWD.
# --user copies into ~/.claude/skills, ~/.cursor/skills, ~/.zcode/skills or ~/.agents/skills.
# Re-running overwrites the installed copy (local 工作区/ folders inside it are kept).
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="amazon-aplus-copywriter-canva"
TARGET="${1:-}"
shift || true
SCOPE=project
PROJECT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) SCOPE=user ;;
    --project) PROJECT="$2"; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if [[ -z "$PROJECT" ]]; then
  PROJECT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

case "$TARGET" in
  claude) DIRS=(.claude) ;;
  cursor) DIRS=(.cursor) ;;
  zcode) DIRS=(.zcode) ;;
  agents) DIRS=(.agents) ;;
  all) DIRS=(.claude .cursor .zcode .agents) ;;
  *) sed -n '2,9p' "$0"; exit 2 ;;
esac

for d in "${DIRS[@]}"; do
  if [[ "$SCOPE" == user ]]; then base="$HOME/$d/skills"; else base="$PROJECT/$d/skills"; fi
  dest="$base/$NAME"
  if [[ "$(cd "$SRC" && pwd -P)" == "$(mkdir -p "$dest" && cd "$dest" && pwd -P)" ]]; then
    echo "skip $dest (source)"; continue
  fi
  mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete --exclude '工作区/' --exclude '__pycache__/' --exclude 'install.sh' "$SRC/" "$dest/"
  else
    find "$dest" -mindepth 1 -maxdepth 1 ! -name '工作区' -exec rm -rf {} +
    (cd "$SRC" && tar --exclude='./工作区' --exclude='__pycache__' --exclude='./install.sh' -cf - .) | (cd "$dest" && tar -xf -)
  fi
  echo "installed $dest"
done

python3 -c "import openpyxl" 2>/dev/null || echo "note: pip install openpyxl  (needed by scripts/build_xlsx.py)"
