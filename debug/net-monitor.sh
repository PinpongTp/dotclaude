#!/bin/bash
# Continuous latency monitor for Claude Code endpoints
# Logs to file every 30s. Watch for spikes during slow open/close/plan-mode events
# Usage: ./net-monitor.sh [duration-minutes]
# Default: 30 minutes. Stop with Ctrl+C.

DURATION_MIN="${1:-30}"
OUT="/Users/pinpongt/.claude/debug/monitor-$(date +%Y%m%d-%H%M%S).log"
END=$(($(date +%s) + DURATION_MIN * 60))

echo "Monitoring for ${DURATION_MIN} min. Log: $OUT"
echo "timestamp,endpoint,dns,tcp,tls,total" > "$OUT"

while [ $(date +%s) -lt $END ]; do
  for url in https://console.anthropic.com/ https://api.anthropic.com/ https://statsigapi.net/v1/initialize; do
    ts=$(date +%H:%M:%S)
    host=$(echo "$url" | sed -E 's|https://([^/]+)/.*|\1|')
    metrics=$(curl -o /dev/null -s -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_total}" "$url")
    line="$ts,$host,$metrics"
    echo "$line" | tee -a "$OUT"
  done
  sleep 30
done

echo ""
echo "=== Summary (median, p95 of total) ==="
for host in console.anthropic.com api.anthropic.com statsigapi.net; do
  grep ",$host," "$OUT" | awk -F, '{print $6}' | sort -n | awk -v h="$host" '
    { a[NR]=$1 }
    END {
      n=NR
      if (n==0) { print h": no data"; exit }
      med=a[int(n/2)+1]
      p95=a[int(n*0.95)+1]
      mx=a[n]
      printf "%-25s median=%.3fs  p95=%.3fs  max=%.3fs  samples=%d\n", h, med, p95, mx, n
    }'
done
