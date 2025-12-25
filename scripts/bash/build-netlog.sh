#!/bin/bash
# Build flowspec-netlog proxy
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NETLOG_DIR="$PROJECT_ROOT/utils/flowspec-netlog"

echo "Building flowspec-netlog..."
cd "$NETLOG_DIR"

go mod download
go mod tidy
go build -o flowspec-netlog .

echo ""
echo "✓ Build complete: $NETLOG_DIR/flowspec-netlog"
echo ""
echo "To install system-wide:"
echo "  sudo cp $NETLOG_DIR/flowspec-netlog /usr/local/bin/"
