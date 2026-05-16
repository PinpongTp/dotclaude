#!/bin/bash
# Capture DNS queries + TLS handshakes during a mode switch event.
# Usage: ./capture-mode-switch.sh
# 1. Run this script
# 2. When it says READY, sลับ plan mode ใน Claude Code
# 3. รอ 10 วิ จะหยุดเอง

OUT_DIR="/Users/pinpongt/.claude/debug"
TS=$(date +%Y%m%d-%H%M%S)
PCAP="$OUT_DIR/capture-$TS.pcap"
DNS_LOG="$OUT_DIR/capture-$TS-dns.txt"
SUM="$OUT_DIR/capture-$TS-summary.txt"

echo "Listing interfaces (find your active one, usually en0):"
ifconfig | grep -E "^[a-z]" | head -8
IFACE=$(route get default 2>/dev/null | awk '/interface:/ {print $2}')
echo "Active interface: $IFACE"
echo ""

# Need sudo for tcpdump
echo "Need sudo for tcpdump..."
sudo -v || exit 1

echo ""
echo "Starting 15s packet capture..."
sudo tcpdump -i "$IFACE" -nn -s 0 -w "$PCAP" \
  '(udp port 53) or (tcp port 443 and (tcp[tcpflags] & tcp-syn != 0 or tcp[tcpflags] & tcp-fin != 0))' \
  >/dev/null 2>&1 &
TCPDUMP_PID=$!

# Also capture DNS in human-readable form in parallel
sudo tcpdump -i "$IFACE" -nn -l 'udp port 53' 2>/dev/null \
  | awk '{print strftime("%H:%M:%S"), $0}' > "$DNS_LOG" &
DNS_PID=$!

sleep 1
echo ""
echo "========================================"
echo "READY — switch to/from PLAN MODE in Claude Code NOW"
echo "Capturing for 15 seconds..."
echo "========================================"
sleep 15

sudo kill $TCPDUMP_PID $DNS_PID 2>/dev/null
sleep 1

echo ""
echo "=== DNS queries during window ===" | tee "$SUM"
grep -E "A\?|AAAA\?" "$DNS_LOG" 2>/dev/null | awk '{print $1, $NF}' | sort -u | tee -a "$SUM"

echo "" | tee -a "$SUM"
echo "=== TLS / TCP connections established ===" | tee -a "$SUM"
sudo tcpdump -r "$PCAP" -nn 'tcp port 443 and tcp[tcpflags] & tcp-syn != 0' 2>/dev/null \
  | awk '{print $3, "->", $5}' | sort -u | tee -a "$SUM"

echo "" | tee -a "$SUM"
echo "Saved: $PCAP, $DNS_LOG, $SUM"
