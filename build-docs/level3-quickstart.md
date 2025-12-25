# Level 3 Network Logging - Quick Start

## Overview

Level 3 adds HTTP/HTTPS network request logging to Flowspec using `flowspec-netlog`, a lightweight Go proxy.

**What you get:**
- Structured JSON logs of all HTTP/HTTPS traffic
- Request/response bodies (up to 1MB)
- Headers, timing, status codes
- Selective bypass with NO_PROXY

## Installation

### 1. Build and Install

```bash
# Build the proxy
bash scripts/bash/build-netlog.sh

# Install to /usr/local/bin
bash scripts/bash/install-netlog.sh
```

### 2. Install CA Certificate

For HTTPS interception, install the auto-generated CA certificate:

```bash
# Start the proxy once to generate certs
export FLOWSPEC_CAPTURE_NETWORK=true
flowspec-netlog &
# Press Ctrl+C after a moment

# Install system-wide
sudo cp .logs/.certs/flowspec-ca-system.crt /usr/local/share/ca-certificates/flowspec-netlog.crt
sudo update-ca-certificates
```

### 3. Configure Environment

Add to your shell config or devcontainer:

```bash
export FLOWSPEC_CAPTURE_NETWORK=true
export LOG_DIR=".logs"
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
export NO_PROXY="localhost,127.0.0.1"
```

### 4. Start Proxy

```bash
flowspec-netlog &
```

## Usage

### Start Logging

```bash
# Terminal 1: Start proxy
export FLOWSPEC_CAPTURE_NETWORK=true
flowspec-netlog

# Terminal 2: Use normally
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080
curl https://api.github.com/users/octocat
```

### View Logs

Logs are written to `.logs/network.*.jsonl` as structured JSON:

```bash
# View all requests
cat .logs/network.*.jsonl | jq .

# Filter by host
cat .logs/network.*.jsonl | jq 'select(.host == "api.github.com")'

# Show only errors
cat .logs/network.*.jsonl | jq 'select(.error != null)'

# Count requests by method
cat .logs/network.*.jsonl | jq -s 'group_by(.method) | map({method: .[0].method, count: length})'

# Show slow requests (>1s)
cat .logs/network.*.jsonl | jq 'select(.duration_ms > 1000)'
```

### Bypass Specific Hosts

Exclude hosts from logging (useful for Playwright, localhost):

```bash
export NO_PROXY="localhost,127.0.0.1,*.internal.example.com"
```

## Devcontainer Integration

### .devcontainer/devcontainer.json

```json
{
  "remoteEnv": {
    "FLOWSPEC_CAPTURE_TTY": "true",
    "FLOWSPEC_CAPTURE_HOOKS": "true",
    "FLOWSPEC_CAPTURE_NETWORK": "true",
    "LOG_DIR": ".logs",
    "HTTP_PROXY": "http://localhost:8080",
    "HTTPS_PROXY": "http://localhost:8080",
    "NO_PROXY": "localhost,127.0.0.1"
  },
  "postCreateCommand": "bash .devcontainer/install-netlog.sh",
  "postStartCommand": "bash .devcontainer/post-start-netlog.sh"
}
```

## Troubleshooting

### HTTPS requests failing

```bash
# Check CA cert is installed
ls -l /usr/local/share/ca-certificates/flowspec-netlog.crt

# Reinstall
sudo cp .logs/.certs/flowspec-ca-system.crt /usr/local/share/ca-certificates/flowspec-netlog.crt
sudo update-ca-certificates
```

### Playwright browsers showing certificate warnings

```bash
# Exempt Playwright from proxy
export NO_PROXY="localhost,127.0.0.1"
```

### Proxy not starting

```bash
# Check if port 8080 is in use
lsof -i :8080

# Use different port
export FLOWSPEC_NETLOG_PORT=9090
export HTTP_PROXY=http://localhost:9090
export HTTPS_PROXY=http://localhost:9090
```

### No logs appearing

```bash
# Verify environment variable
echo $FLOWSPEC_CAPTURE_NETWORK  # Should be "true"

# Check proxy is running
ps aux | grep flowspec-netlog

# Check log directory
ls -la .logs/
```

## Log Format

Each request is logged as a single JSON line:

```json
{
  "timestamp": "2025-12-25T12:00:00Z",
  "method": "GET",
  "url": "https://api.github.com/users/octocat",
  "host": "api.github.com",
  "status_code": 200,
  "headers": {
    "Content-Type": "application/json",
    "User-Agent": "curl/8.0.1"
  },
  "request_body": "",
  "response_body": "{\"login\":\"octocat\",\"id\":1,...}",
  "duration_ms": 145
}
```

Bypassed requests:

```json
{
  "timestamp": "2025-12-25T12:00:00Z",
  "method": "GET",
  "url": "http://localhost:3000/health",
  "host": "localhost",
  "bypassed": true
}
```

## Performance

- **CPU**: <2% overhead
- **Memory**: ~20-30MB baseline
- **Latency**: ~5ms per request
- **Disk**: ~1KB per request

## Security Notes

- CA private key stored in `.logs/.certs/` (0600 permissions)
- Add `.logs/` to `.gitignore` to prevent committing logs
- Only enable when needed for debugging
- Review logs before sharing (may contain secrets)

## See Also

- `utils/flowspec-netlog/README.md` - Full proxy documentation
- `build-docs/logger-plan.md` - Complete logging implementation plan
- `logger-plan.md` - Level 1 (TTY) and Level 2 (Hooks) setup
