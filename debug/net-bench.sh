#!/bin/bash
# Cold-TLS benchmark for Claude Code endpoints
# Usage: ./net-bench.sh [label]
# Label = network name (e.g. "office", "hotspot") for the output file

LABEL="${1:-unlabeled}"
SAMPLES=5
ENDPOINTS=(
  "https://console.anthropic.com/"
  "https://api.anthropic.com/"
  "https://statsigapi.net/v1/initialize"
)
OUT="/Users/pinpongt/.claude/debug/bench-${LABEL}-$(date +%Y%m%d-%H%M%S).txt"

flush_dns() {
  sudo dscacheutil -flushcache
  sudo killall -HUP mDNSResponder
}

echo "Cold-TLS benchmark — label: ${LABEL}" | tee "$OUT"
echo "Date: $(date)" | tee -a "$OUT"
echo "Wi-Fi SSID: $(networksetup -getairportnetwork en0 | sed 's/Current Wi-Fi Network: //')" | tee -a "$OUT"
echo "DNS: $(scutil --dns | grep nameserver | sort -u | head -2 | tr '\n' ' ')" | tee -a "$OUT"
echo "Samples per endpoint: ${SAMPLES}" | tee -a "$OUT"
echo "----" | tee -a "$OUT"

echo "Need sudo to flush DNS between samples..."
sudo -v

for url in "${ENDPOINTS[@]}"; do
  echo "" | tee -a "$OUT"
  echo "=== $url ===" | tee -a "$OUT"
  printf "%-8s %-8s %-8s %-8s %-8s\n" "sample" "dns" "connect" "tls" "total" | tee -a "$OUT"
  for i in $(seq 1 $SAMPLES); do
    flush_dns >/dev/null 2>&1
    result=$(curl -o /dev/null -s -w "%{time_namelookup} %{time_connect} %{time_appconnect} %{time_total}" "$url")
    printf "%-8s %s\n" "$i" "$result" | awk '{printf "%-8s %-8s %-8s %-8s %-8s\n", $1, $2, $3, $4, $5}' | tee -a "$OUT"
    sleep 1
  done
done

echo "" | tee -a "$OUT"
echo "Saved to: $OUT"
