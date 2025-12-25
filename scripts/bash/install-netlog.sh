#!/bin/bash
# Install flowspec-netlog to /usr/local/bin
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NETLOG_DIR="$PROJECT_ROOT/utils/flowspec-netlog"

# Build if not already built
if [ ! -f "$NETLOG_DIR/flowspec-netlog" ]; then
    echo "Binary not found, building first..."
    bash "$SCRIPT_DIR/build-netlog.sh"
fi

echo "Installing flowspec-netlog to /usr/local/bin..."
sudo cp "$NETLOG_DIR/flowspec-netlog" /usr/local/bin/
sudo chmod +x /usr/local/bin/flowspec-netlog

echo "✓ Installation complete"
echo ""
echo "To enable network capture:"
echo "  export FLOWSPEC_CAPTURE_NETWORK=true"
echo "  export LOG_DIR=\".logs\""
echo "  flowspec-netlog &"
