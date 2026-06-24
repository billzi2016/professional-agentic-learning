#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DJANGO_SESSION="agentic-learning-django"
VUE_SESSION="agentic-learning-vue"
PYTHON_BIN="${PYTHON_BIN:-/opt/anaconda3/bin/python3.13}"

command -v tmux >/dev/null 2>&1 || {
  echo "tmux is required"
  exit 1
}

command -v pnpm >/dev/null 2>&1 || {
  echo "pnpm is required"
  exit 1
}

if tmux has-session -t "$DJANGO_SESSION" 2>/dev/null; then
  echo "tmux session '$DJANGO_SESSION' already exists."
  echo "Run: tmux attach -t $DJANGO_SESSION"
  exit 1
fi

if tmux has-session -t "$VUE_SESSION" 2>/dev/null; then
  echo "tmux session '$VUE_SESSION' already exists."
  echo "Run: tmux attach -t $VUE_SESSION"
  exit 1
fi

tmux new-session -d -s "$DJANGO_SESSION" -n django
tmux send-keys -t "$DJANGO_SESSION:django" "cd '$ROOT_DIR/backend' && '$PYTHON_BIN' manage.py migrate && '$PYTHON_BIN' manage.py runserver 127.0.0.1:8000" C-m

tmux new-session -d -s "$VUE_SESSION" -n vue
tmux send-keys -t "$VUE_SESSION:vue" "cd '$ROOT_DIR/frontend' && pnpm install && pnpm dev --host 127.0.0.1" C-m

echo "Started:"
echo "  $DJANGO_SESSION -> Django API"
echo "  $VUE_SESSION -> Vue frontend"
echo
echo "Attach Django: tmux attach -t $DJANGO_SESSION"
echo "Attach Vue:    tmux attach -t $VUE_SESSION"

tmux attach -t "$VUE_SESSION"
