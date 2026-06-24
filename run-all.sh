#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_NAME="agentic-learning"
PYTHON_BIN="${PYTHON_BIN:-/opt/anaconda3/bin/python3.13}"

command -v tmux >/dev/null 2>&1 || {
  echo "tmux is required"
  exit 1
}

command -v pnpm >/dev/null 2>&1 || {
  echo "pnpm is required"
  exit 1
}

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session '$SESSION_NAME' already exists."
  echo "Run: tmux attach -t $SESSION_NAME"
  exit 1
fi

tmux new-session -d -s "$SESSION_NAME" -n backend
tmux send-keys -t "$SESSION_NAME:backend" "cd '$ROOT_DIR/backend' && '$PYTHON_BIN' manage.py migrate && '$PYTHON_BIN' manage.py runserver 127.0.0.1:8000" C-m

tmux new-window -t "$SESSION_NAME" -n frontend
tmux send-keys -t "$SESSION_NAME:frontend" "cd '$ROOT_DIR/frontend' && pnpm install && pnpm dev --host 127.0.0.1" C-m

tmux attach -t "$SESSION_NAME"
