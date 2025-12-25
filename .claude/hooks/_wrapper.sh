#!/bin/bash
# .claude/hooks/_wrapper.sh
# Wrapper that logs all hook executions

HOOK="$1"
shift  # Remove hook name, pass rest to actual hook

if [ "$FLOWSPEC_CAPTURE_HOOKS" = "true" ]; then
  LOG_DIR="${LOG_DIR:-.logs}"
  mkdir -p "$LOG_DIR"
  LOG_FILE="$LOG_DIR/hooks.log"

  echo "[$(date -Iseconds)] START: $HOOK $*" >> "$LOG_FILE"
  ".claude/hooks/$HOOK" "$@" 2>&1 | tee -a "$LOG_FILE"
  EXIT_CODE="${PIPESTATUS[0]}"
  echo "[$(date -Iseconds)] END: $HOOK (exit $EXIT_CODE)" >> "$LOG_FILE"
  exit $EXIT_CODE
else
  exec ".claude/hooks/$HOOK" "$@"
fi
