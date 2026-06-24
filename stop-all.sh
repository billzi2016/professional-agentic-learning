#!/usr/bin/env bash
set -euo pipefail

SESSIONS=(
  "agentic-learning-django"
  "agentic-learning-vue"
)

command -v tmux >/dev/null 2>&1 || {
  echo "tmux is required"
  exit 1
}

for session in "${SESSIONS[@]}"; do
  if tmux has-session -t "$session" 2>/dev/null; then
    tmux kill-session -t "$session"
    echo "Stopped $session"
  else
    echo "Session $session is not running"
  fi
done
