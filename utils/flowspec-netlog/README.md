# flowspec-netlog

Lightweight HTTP/HTTPS network logger for Flowspec Level 3 logging.

## Features

- ✅ Transparent HTTP/HTTPS proxy
- ✅ Structured JSON logging (`.logs/network.*.jsonl`)
- ✅ Automatic CA certificate generation
- ✅ NO_PROXY support for selective bypass
- ✅ Request/response body capture (configurable limit)
- ✅ Low overhead (~5ms latency)
- ✅ Built with Mage for easy building

## Quick Start

```bash
# Build
cd utils/flowspec-netlog
mage build

# Install (optional)
mage install

# Enable network capture
export FLOWSPEC_CAPTURE_NETWORK=true
export LOG_DIR=".logs"

# Start proxy
flowspec-netlog
```

In another terminal:

```bash
# Configure your session to use the proxy
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080

# Run your commands
curl https://api.github.com/users/octocat
```

Logs appear in `.logs/network.*.jsonl` as structured JSON.

## CA Certificate Installation

For HTTPS interception, you need to trust the generated CA certificate:

### Option 1: System-wide (Recommended)

```bash
# After first run, flowspec-netlog generates a CA cert
sudo cp .logs/.certs/flowspec-ca-system.crt /usr/local/share/ca-certificates/flowspec-netlog.crt
sudo update-ca-certificates
```

### Option 2: Environment Variables (Current Session)

```bash
export NODE_EXTRA_CA_CERTS=.logs/.certs/flowspec-ca-system.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

### Option 3: HTTP Only (No Certificate Required)

Just use HTTP_PROXY without HTTPS_PROXY - only HTTP traffic will be logged.

## Selective Bypass with NO_PROXY

Exempt specific hosts from logging (useful for Playwright browsers):

```bash
export NO_PROXY="localhost,127.0.0.1,playwright.dev"
```

Any request to these hosts will be logged as "bypassed" without interception.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `FLOWSPEC_CAPTURE_NETWORK` | (required) | Set to `true` to enable |
| `LOG_DIR` | `.logs` | Directory for logs and certs |
| `FLOWSPEC_NETLOG_PORT` | `8080` | Proxy listen port |
| `HTTP_PROXY` | - | Set to `http://localhost:8080` |
| `HTTPS_PROXY` | - | Set to `http://localhost:8080` |
| `NO_PROXY` | - | Comma-separated hosts to bypass |

## Mage Targets

```bash
mage build      # Build binary
mage install    # Install to /usr/local/bin
mage clean      # Remove built artifacts
mage test       # Run tests
mage fmt        # Format code
mage mod        # Download and tidy dependencies
mage dev        # Build and run for development
mage dist       # Build for multiple platforms
mage info       # Print build information
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

## Integration with Flowspec

### devcontainer.json

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
  }
}
```

### post-start.sh

```bash
#!/bin/bash
if [ "$FLOWSPEC_CAPTURE_NETWORK" = "true" ]; then
  # Install CA cert if not already installed
  if [ ! -f /usr/local/share/ca-certificates/flowspec-netlog.crt ]; then
    if [ -f .logs/.certs/flowspec-ca-system.crt ]; then
      sudo cp .logs/.certs/flowspec-ca-system.crt /usr/local/share/ca-certificates/flowspec-netlog.crt
      sudo update-ca-certificates
    fi
  fi

  # Start proxy in background
  flowspec-netlog &
  echo "flowspec-netlog started (PID: $!)"
fi
```

## Troubleshooting

### HTTPS requests failing with certificate errors

```bash
# Verify CA cert is installed
ls -l /usr/local/share/ca-certificates/flowspec-netlog.crt

# Reinstall if needed
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
# Check if port 8080 is already in use
lsof -i :8080

# Use different port
export FLOWSPEC_NETLOG_PORT=9090
export HTTP_PROXY=http://localhost:9090
export HTTPS_PROXY=http://localhost:9090
```

### No logs being created

```bash
# Verify environment variable is set
echo $FLOWSPEC_CAPTURE_NETWORK  # Should be "true"

# Check log directory
ls -la .logs/

# Check proxy is running
ps aux | grep flowspec-netlog
```

## Performance

- **Latency**: ~5ms overhead per HTTP request
- **Memory**: ~20-30MB baseline
- **CPU**: <2% for typical workloads
- **Disk**: Depends on traffic volume; ~1KB per request

## Security Considerations

- CA private key is stored in `.logs/.certs/` with 0600 permissions
- Add `.logs/` to `.gitignore` to prevent committing sensitive logs
- Only enable network capture when needed for debugging
- Review logs before sharing (may contain API keys, tokens, etc.)

## License

Same as parent Flowspec project.
