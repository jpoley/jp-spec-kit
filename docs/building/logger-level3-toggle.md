# Level 3 Network Logging - Enable/Disable Guide

## Quick Reference

Level 3 is **disabled by default** in the devcontainer. Enable it only when you need to debug network issues.

## Enable Level 3 Network Logging

### Option 1: Current Session Only (Temporary)

```bash
# In your terminal session
export FLOWSPEC_CAPTURE_NETWORK=true
export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080

# Start the proxy in background
flowspec-netlog &

# Use claude normally - network requests will be logged
claude

# Logs appear in .logs/network.*.jsonl
```

### Option 2: Persistent (Update Devcontainer)

Edit `.devcontainer/devcontainer.json`:

```json
{
  "remoteEnv": {
    "FLOWSPEC_CAPTURE_NETWORK": "true",     // Change from "false" to "true"
    "HTTP_PROXY": "http://localhost:8080",  // Change from "" to proxy URL
    "HTTPS_PROXY": "http://localhost:8080"  // Change from "" to proxy URL
  }
}
```

Then rebuild the devcontainer or restart the terminal.

## Disable Level 3 Network Logging

### Option 1: Current Session Only

```bash
# Stop the proxy
pkill flowspec-netlog

# Unset proxy variables
export FLOWSPEC_CAPTURE_NETWORK=false
export HTTP_PROXY=
export HTTPS_PROXY=
```

### Option 2: Persistent (Default Configuration)

Edit `.devcontainer/devcontainer.json`:

```json
{
  "remoteEnv": {
    "FLOWSPEC_CAPTURE_NETWORK": "false",  // Disabled
    "HTTP_PROXY": "",                     // Empty
    "HTTPS_PROXY": ""                     // Empty
  }
}
```

## Check Current Status

```bash
# Check if proxy is running
ps aux | grep flowspec-netlog

# Check environment variables
echo "FLOWSPEC_CAPTURE_NETWORK: $FLOWSPEC_CAPTURE_NETWORK"
echo "HTTP_PROXY: $HTTP_PROXY"
echo "HTTPS_PROXY: $HTTPS_PROXY"

# Check for recent logs
ls -lht .logs/network.*.jsonl | head -5
```

## View Network Logs

```bash
# View all captured requests
cat .logs/network.*.jsonl | jq .

# View most recent 10 requests
tail -10 .logs/network.*.jsonl | jq .

# Filter by host
cat .logs/network.*.jsonl | jq 'select(.host == "api.github.com")'

# Show only errors
cat .logs/network.*.jsonl | jq 'select(.error != null)'

# Count requests by method
cat .logs/network.*.jsonl | jq -s 'group_by(.method) | map({method: .[0].method, count: length})'
```

## HTTPS Interception (Optional)

By default, HTTPS requests will fail with certificate errors unless you install the CA certificate:

### Install CA Certificate (One-time Setup)

```bash
# The proxy auto-generates certificates in .logs/.certs/
# To enable HTTPS interception, install the CA cert:

sudo cp .logs/.certs/flowspec-ca-system.crt \
  /usr/local/share/ca-certificates/flowspec-netlog.crt
sudo update-ca-certificates
```

### Alternative: Environment Variables (Per Session)

```bash
export NODE_EXTRA_CA_CERTS=.logs/.certs/flowspec-ca-system.crt
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

## Performance Impact

| Metric | Without Level 3 | With Level 3 | Overhead |
|--------|-----------------|--------------|----------|
| Latency | 0ms | +5ms | Minimal |
| CPU | Baseline | +1-2% | Negligible |
| Memory | Baseline | +20-30MB | Low |
| Disk I/O | 0 | ~1KB/request | Minimal |

## When to Use Level 3

**Use Level 3 when:**
- Debugging API integration issues
- Investigating network timeouts or failures
- Analyzing request/response payloads
- Troubleshooting MCP server communication
- Auditing external API calls

**Skip Level 3 when:**
- Normal development work (Level 1 + 2 is sufficient)
- Performance-sensitive workloads
- Working with Playwright (browsers don't respect proxy)

## Troubleshooting

### Proxy won't start

```bash
# Check if port 8080 is already in use
lsof -i :8080

# Use different port
export FLOWSPEC_NETLOG_PORT=8081
export HTTP_PROXY=http://localhost:8081
export HTTPS_PROXY=http://localhost:8081
```

### No requests being logged

```bash
# Verify proxy is running
ps aux | grep flowspec-netlog

# Check environment variables are set
env | grep PROXY

# Test with explicit curl command
curl -x http://localhost:8080 http://httpbin.org/get
```

### HTTPS requests fail

```bash
# Check if CA cert is installed
ls -l /usr/local/share/ca-certificates/flowspec-netlog.crt

# Reinstall CA cert
sudo cp .logs/.certs/flowspec-ca-system.crt \
  /usr/local/share/ca-certificates/flowspec-netlog.crt
sudo update-ca-certificates

# Or bypass HTTPS interception for specific hosts
export NO_PROXY="github.com,githubusercontent.com"
```

## Security Notes

- **Logs may contain sensitive data** (API keys, credentials, PII)
- **Review logs before sharing**
- **Never commit `.logs/` directory** (already in `.gitignore`)
- **Rotate CA certificates periodically**
- **Only enable Level 3 when needed for debugging**

## Related Documentation

- Full implementation plan: `build-docs/logger-plan.md`
- Level 3 quickstart: `build-docs/level3-quickstart.md`
- Level 3 implementation summary: `build-docs/level3-implementation-summary.md`
- flowspec-netlog README: `utils/flowspec-netlog/README.md`
