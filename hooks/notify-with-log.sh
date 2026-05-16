#!/bin/bash
# Log notification stdin + speak based on type
LOG="/Users/pinpongt/.claude/debug/notifications.log"
INPUT=$(cat)

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  echo "$INPUT" | jq .
  echo ""
} >> "$LOG"

TYPE=$(echo "$INPUT" | jq -r '.notification_type // empty')

case "$TYPE" in
  idle_prompt)
    say -v "Sandy (Japanese (Japan))" "idle"
    ;;
  *)
    say -v "Sandy (Japanese (Japan))" "master, need your help"
    ;;
esac
