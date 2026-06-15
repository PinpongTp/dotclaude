#!/bin/bash
# Unified Stop + Notification hook — dynamic Thai speech via Kanya voice
LOG="/Users/pinpongt/.claude/debug/notifications.log"
INPUT=$(cat)
TMPJSON=$(mktemp /tmp/claude_hook_XXXXXX.json)
printf '%s' "$INPUT" > "$TMPJSON"

{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  jq . "$TMPJSON" 2>/dev/null || cat "$TMPJSON"
  echo ""
} >> "$LOG" 2>/dev/null

speak() { say -v "Kanya" "$1" & }

EVENT=$(jq -r '.hook_event_name // "Stop"' "$TMPJSON" 2>/dev/null)
TYPE=$(jq -r '.notification_type // ""' "$TMPJSON" 2>/dev/null)
TRANSCRIPT=$(jq -r '.transcript_path // ""' "$TMPJSON" 2>/dev/null)

case "$EVENT" in
  Notification)
    case "$TYPE" in
      idle_prompt) speak "รอคำสั่ง" ;;
      *)
        MSG=$(jq -r '.message // "แจ้งเตือน"' "$TMPJSON" 2>/dev/null)
        speak "${MSG:-แจ้งเตือน}"
        ;;
    esac
    ;;
  Stop)
    if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
      TEXT=$(python3 - "$TRANSCRIPT" <<'PYEOF'
import json, sys, re
try:
    lines = open(sys.argv[1]).readlines()
    for line in reversed(lines):
        try:
            obj = json.loads(line)
            if obj.get('type') == 'assistant':
                for block in obj.get('message', {}).get('content', []):
                    if not isinstance(block, dict) or block.get('type') != 'text':
                        continue
                    raw = block['text'].strip()
                    # Strip code fences and inline code
                    clean = re.sub(r'```.*?```', '', raw, flags=re.DOTALL)
                    clean = re.sub(r'`[^`]+`', '', clean)
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    # Take first 3 sentences
                    sentences, buf, count = [], '', 0
                    for ch in clean:
                        buf += ch
                        if ch in '.!?' and len(buf.strip()) > 10:
                            sentences.append(buf.strip())
                            buf = ''
                            count += 1
                            if count >= 3:
                                break
                    result = ' '.join(sentences) or clean[:400]
                    print(result[:500])
                    raise SystemExit(0)
        except SystemExit:
            raise
        except Exception:
            pass
    print('ทำเสร็จแล้ว')
except Exception:
    print('ทำเสร็จแล้ว')
PYEOF
)
      speak "${TEXT:-ทำเสร็จแล้ว}"
    else
      speak "ทำเสร็จแล้ว"
    fi
    ;;
  *) speak "เสร็จแล้ว" ;;
esac

rm -f "$TMPJSON"
