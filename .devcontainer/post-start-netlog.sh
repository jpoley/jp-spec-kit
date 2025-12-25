#!/bin/bash
# Auto-start flowspec-netlog if FLOWSPEC_CAPTURE_NETWORK is enabled
# Source this from .devcontainer/post-start.sh

if [ "$FLOWSPEC_CAPTURE_NETWORK" = "true" ]; then
    LOG_DIR="${LOG_DIR:-.logs}"
    
    echo "Starting flowspec-netlog..."
    
    # Install CA cert if it exists and isn't already installed
    if [ -f "$LOG_DIR/.certs/flowspec-ca-system.crt" ]; then
        if [ ! -f /usr/local/share/ca-certificates/flowspec-netlog.crt ]; then
            echo "Installing CA certificate..."
            sudo cp "$LOG_DIR/.certs/flowspec-ca-system.crt" \
                /usr/local/share/ca-certificates/flowspec-netlog.crt
            sudo update-ca-certificates
        fi
    fi
    
    # Start proxy in background
    flowspec-netlog &
    NETLOG_PID=$!
    echo "flowspec-netlog started (PID: $NETLOG_PID)"
    
    # Wait a moment for proxy to start
    sleep 1
    
    # Verify it's running
    if ps -p $NETLOG_PID > /dev/null; then
        echo "✓ Network capture enabled"
        echo "  Logs: $LOG_DIR/network.*.jsonl"
    else
        echo "✗ Failed to start flowspec-netlog"
    fi
else
    echo "Network capture disabled (FLOWSPEC_CAPTURE_NETWORK not set to 'true')"
fi
