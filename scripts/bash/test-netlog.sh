#!/bin/bash
# Test flowspec-netlog proxy
set -e

echo "Testing flowspec-netlog..."
echo ""

# Check if binary exists
if [ ! -f "utils/flowspec-netlog/flowspec-netlog" ]; then
    echo "Binary not found. Building..."
    bash scripts/bash/build-netlog.sh
fi

# Start proxy in background
echo "Starting proxy..."
export FLOWSPEC_CAPTURE_NETWORK=true
export LOG_DIR=".logs-test"
mkdir -p "$LOG_DIR"

utils/flowspec-netlog/flowspec-netlog &
PROXY_PID=$!

# Wait for proxy to start
sleep 2

# Check if proxy is running
if ! ps -p $PROXY_PID > /dev/null; then
    echo "✗ Failed to start proxy"
    exit 1
fi

echo "✓ Proxy started (PID: $PROXY_PID)"
echo ""

# Configure proxy
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080

# Test HTTP
echo "Testing HTTP request..."
if curl -s http://httpbin.org/get > /dev/null; then
    echo "✓ HTTP request successful"
else
    echo "✗ HTTP request failed"
fi

# Test HTTPS (may fail if CA cert not installed)
echo "Testing HTTPS request..."
if curl -s https://api.github.com/users/octocat > /dev/null 2>&1; then
    echo "✓ HTTPS request successful"
else
    echo "⚠ HTTPS request failed (CA cert may not be installed)"
    echo "  To install CA cert:"
    echo "  sudo cp $LOG_DIR/.certs/flowspec-ca-system.crt /usr/local/share/ca-certificates/flowspec-netlog.crt"
    echo "  sudo update-ca-certificates"
fi

# Test NO_PROXY bypass
echo "Testing NO_PROXY bypass..."
export NO_PROXY="localhost,127.0.0.1"
# Use a request that will be logged even if it fails; failure is expected and should not abort the script
set +e
curl -s --max-time 1 http://localhost:9999 > /dev/null 2>&1
set -e
unset NO_PROXY

# Verify bypass was logged
sleep 1
BYPASS_COUNT=$(grep -c '"bypassed".*true' "$LOG_DIR"/network.*.jsonl 2>/dev/null || echo "0")
if [ "$BYPASS_COUNT" -gt 0 ]; then
    echo "✓ NO_PROXY bypass verified ($BYPASS_COUNT bypassed requests in logs)"
else
    echo "⚠ NO_PROXY bypass not verified in logs (check manually)"
fi

# Check logs
echo ""
echo "Checking logs..."
LOG_FILE=$(ls -t "$LOG_DIR"/network.*.jsonl 2>/dev/null | head -1)

if [ -n "$LOG_FILE" ]; then
    COUNT=$(wc -l < "$LOG_FILE")
    echo "✓ Log file created: $LOG_FILE"
    echo "  Captured $COUNT requests"
    echo ""
    echo "Sample log entries:"
    head -3 "$LOG_FILE" | jq -C '.' 2>/dev/null || cat "$LOG_FILE" | head -3
else
    echo "✗ No log file found"
fi

# Cleanup
echo ""
echo "Stopping proxy..."
kill $PROXY_PID
wait $PROXY_PID 2>/dev/null

echo "✓ Test complete"
echo ""
echo "To view all logs:"
echo "  cat $LOG_DIR/network.*.jsonl | jq ."
echo ""
echo "To clean up test logs:"
echo "  rm -rf $LOG_DIR"
