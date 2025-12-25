#!/bin/bash
# Build flowspec-netlog proxy
set -e

# Error handler: send error messages to stderr
trap 'echo "ERROR: Build failed at line $LINENO" >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NETLOG_DIR="$PROJECT_ROOT/utils/flowspec-netlog"

echo "Building flowspec-netlog..."
cd "$NETLOG_DIR"

go mod download || { echo "ERROR: go mod download failed" >&2; exit 1; }
go mod tidy || { echo "ERROR: go mod tidy failed" >&2; exit 1; }
go build -o flowspec-netlog . || { echo "ERROR: go build failed" >&2; exit 1; }

echo ""
echo "✓ Build complete: $NETLOG_DIR/flowspec-netlog"
echo ""
echo "To install system-wide:"
echo "  sudo cp $NETLOG_DIR/flowspec-netlog /usr/local/bin/"
