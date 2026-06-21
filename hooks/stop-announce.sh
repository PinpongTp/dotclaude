#!/bin/bash
# Claude Code Stop announcer.
#
# The Stop payload carries `background_tasks` — the teammates / background agents
# of THIS session (harness already scopes it per session). If any are still
# running, an agent/subagent is in flight -> say "done done"; otherwise the turn
# is fully finished -> "all done".
#
# This reads live state straight from the payload, so there is no counter to
# drift and no cross-session contamination. Anything missing/garbled falls
# through to "all done".

set -u

LOG="/Users/pinpong/.claude/debug/hooks.log"
VOICE="Sandy (Japanese (Japan))"

INPUT=$(cat 2>/dev/null)
mkdir -p "$(dirname "$LOG")" 2>/dev/null

RUNNING=$(printf '%s' "$INPUT" \
  | jq -r '[ (.background_tasks // [])[] | select(.status=="running") ] | length' 2>/dev/null)

{
  echo "=== $(date '+%F %T') Stop sid=$(printf '%s' "$INPUT" | jq -r '(.session_id // "?")[0:8]' 2>/dev/null) running=${RUNNING:-?} ==="
} >> "$LOG" 2>/dev/null

if [ "${RUNNING:-0}" -gt 0 ] 2>/dev/null; then
  say -v "$VOICE" "done done"
else
  say -v "$VOICE" "all done"
fi

exit 0
