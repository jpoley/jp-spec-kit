#!/bin/bash
# Install flowspec-netlog for devcontainer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up flowspec-netlog for devcontainer..."

# Build and install
cd "$PROJECT_ROOT"
bash scripts/bash/build-netlog.sh
sudo cp utils/flowspec-netlog/flowspec-netlog /usr/local/bin/
sudo chmod +x /usr/local/bin/flowspec-netlog

echo "✓ flowspec-netlog installed to /usr/local/bin/"
echo ""
echo "To enable network capture, set in devcontainer.json:"
echo '  "remoteEnv": {'
echo '    "FLOWSPEC_CAPTURE_NETWORK": "true",'
echo '    "LOG_DIR": ".logs",'
echo '    "HTTP_PROXY": "http://localhost:8080",'
echo '    "HTTPS_PROXY": "http://localhost:8080",'
echo '    "NO_PROXY": "localhost,127.0.0.1"'
echo '  }'
