# Web Security Testing with DAST

Dynamic Application Security Testing (DAST) performs security testing on running web applications using browser automation. This guide covers using Specify CLI's Playwright-based DAST scanner.

## Overview

The DAST module provides:

- **Authenticated Crawling**: Automatic discovery of pages and forms with session management
- **XSS Detection**: Cross-site scripting vulnerability detection through payload injection
- **CSRF Testing**: Cross-site request forgery protection validation
- **Session Security**: Cookie and session management security checks
- **Security Headers**: HTTP security header validation (CSP, HSTS, etc.)
- **Unified Findings**: Results in standard UFFormat for consistent triage

## Installation

Install DAST dependencies:

```bash
# Install with DAST extras
pip install 'specify-cli[dast]'

# Or install Playwright separately
pip install playwright

# Install browser binaries
playwright install chromium
```

## Quick Start

### Basic Scan

```python
from specify_cli.security.dast import DASTScanner

# Create scanner
scanner = DASTScanner(
    base_url="https://example.com",
    max_depth=3,
    max_pages=100
)

# Run scan
result = scanner.scan_sync()

print(f"Scanned {result.pages_scanned} pages")
print(f"Found {len(result.findings)} vulnerabilities")

# Access findings
for finding in result.findings:
    print(f"{finding.severity.value}: {finding.title}")
    print(f"  URL: {finding.metadata['url']}")
```

### Authenticated Scan

```python
import asyncio
from specify_cli.security.dast import DASTScanner

async def login(page):
    """Authentication callback."""
    await page.goto("https://example.com/login")
    await page.fill("#username", "testuser")
    await page.fill("#password", "testpass")
    await page.click("#login-button")
    await page.wait_for_selector("#dashboard")  # Wait for redirect

async def main():
    scanner = DASTScanner(
        base_url="https://example.com",
        auth_callback=login,
        max_depth=2,
        max_pages=50
    )

    result = await scanner.scan()

    for finding in result.findings:
        print(f"{finding.severity.value}: {finding.title}")

asyncio.run(main())
```

## Configuration Options

### DASTScanner Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str | required | Starting URL for scan |
| `auth_callback` | Callable | None | Async function for authentication |
| `max_depth` | int | 3 | Maximum crawl depth |
| `max_pages` | int | 100 | Maximum pages to scan |
| `excluded_patterns` | list[str] | [] | URL patterns to exclude |

### CrawlConfig Options

```python
from specify_cli.security.dast import CrawlConfig, PlaywrightCrawler

config = CrawlConfig(
    base_url="https://example.com",
    max_depth=3,
    max_pages=100,
    timeout_ms=30000,  # Page load timeout
    excluded_patterns=["/admin", "/logout"],
    include_external=False  # Don't crawl external links
)

crawler = PlaywrightCrawler(config)
result = await crawler.crawl()
```

## Vulnerability Detection

### XSS Detection

The scanner tests for cross-site scripting by:

1. Discovering input fields and forms
2. Injecting XSS payloads (script tags, event handlers, etc.)
3. Checking if payloads appear unescaped in responses
4. Validating execution context

**Example XSS Finding:**

```python
Finding(
    id="DAST-XSS-001",
    scanner="dast-playwright",
    severity=Severity.HIGH,
    title="Cross-Site Scripting (XSS)",
    cwe_id="CWE-79",
    location=Location(file=Path("web://https://example.com/search")),
    metadata={
        "url": "https://example.com/search",
        "parameter": "q",
        "payload": "<script>alert(1)</script>"
    }
)
```

### CSRF Detection

The scanner checks for CSRF protection by:

1. Analyzing forms for CSRF tokens
2. Validating cookie SameSite attributes
3. Checking HTTP headers for CSRF protection

**Example CSRF Finding:**

```python
Finding(
    id="DAST-CSRF-001",
    scanner="dast-playwright",
    severity=Severity.MEDIUM,
    title="Cross-Site Request Forgery (CSRF)",
    cwe_id="CWE-352",
    metadata={
        "url": "https://example.com/profile/update",
        "parameter": None,
        "payload": None
    },
    remediation="Implement CSRF protection using synchronizer token pattern"
)
```

### Session Security

The scanner validates:

- Cookie security attributes (Secure, HttpOnly, SameSite)
- Session fixation vulnerabilities
- Session timeout enforcement

### Security Headers

Checks for:

- Content-Security-Policy (CSP)
- X-Frame-Options (clickjacking protection)
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options

## Integration with Security Orchestrator

Use DAST via the security adapter:

```python
from pathlib import Path
from specify_cli.security.adapters.dast import DASTAdapter

adapter = DASTAdapter()

# Check availability
if not adapter.is_available():
    print(adapter.get_install_instructions())
    exit(1)

# Configure scan
config = {
    "url": "https://example.com",
    "max_depth": 2,
    "max_pages": 50,
}

# Run scan
findings = adapter.scan(Path("."), config)

# Process findings
for finding in findings:
    print(f"{finding.severity.value}: {finding.title}")
```

## Advanced Usage

### Custom Authentication

```python
import os

async def complex_auth(page):
    """Handle multi-step authentication."""
    # Step 1: Navigate to login
    await page.goto("https://example.com/login")

    # Step 2: Fill credentials
    await page.fill("#email", "user@example.com")
    await page.fill("#password", "password123")

    # Step 3: Handle MFA (if needed)
    await page.click("#login")

    # Wait for MFA page
    await page.wait_for_selector("#mfa-code", timeout=5000)

    # Get MFA code from your MFA provider
    # Example implementation:
    def get_mfa_code():
        """Get MFA code - implement based on your setup."""
        return os.environ.get("MFA_CODE") or input("Enter MFA code: ")

    mfa_code = get_mfa_code()
    await page.fill("#mfa-code", mfa_code)
    await page.click("#verify")

    # Step 4: Verify successful login
    await page.wait_for_url("**/dashboard")

    # Step 5: Check for session cookie
    cookies = await page.context.cookies()
    assert any(c["name"] == "session_id" for c in cookies)

scanner = DASTScanner(
    base_url="https://example.com",
    auth_callback=complex_auth
)
```

### Excluding Sensitive Pages

```python
scanner = DASTScanner(
    base_url="https://example.com",
    excluded_patterns=[
        "/admin",
        "/logout",
        "/api/delete",
        "/payment/process",
    ]
)
```

### Processing Results

```python
result = scanner.scan_sync()

# Group by severity
by_severity = {}
for finding in result.findings:
    severity = finding.severity.value
    if severity not in by_severity:
        by_severity[severity] = []
    by_severity[severity].append(finding)

# Print summary
for severity in ["critical", "high", "medium", "low", "info"]:
    if severity in by_severity:
        print(f"{severity.upper()}: {len(by_severity[severity])} findings")

# Export to JSON (SARIF export coming in future release)
import json
from dataclasses import asdict

with open("dast-results.json", "w") as f:
    findings_data = [asdict(f) for f in result.findings]
    json.dump(findings_data, f, indent=2, default=str)
```

## Best Practices

### 1. Use Test Environments

**Never run DAST against production without authorization.**

```python
# Good: Test environment
scanner = DASTScanner(base_url="https://staging.example.com")

# Bad: Production without authorization
# scanner = DASTScanner(base_url="https://example.com")
```

### 2. Limit Scan Scope

```python
# Limit depth and pages for faster scans
scanner = DASTScanner(
    base_url="https://staging.example.com",
    max_depth=2,  # Only crawl 2 levels deep
    max_pages=50,  # Limit to 50 pages
    excluded_patterns=["/admin", "/api"]
)
```

### 3. Handle Authentication Securely

```python
import os

async def secure_auth(page):
    # Get credentials from environment, not hardcoded
    username = os.getenv("DAST_USERNAME")
    password = os.getenv("DAST_PASSWORD")

    if not username or not password:
        raise ValueError("DAST credentials not configured")

    await page.goto("https://staging.example.com/login")
    await page.fill("#username", username)
    await page.fill("#password", password)
    await page.click("#login")
```

### 4. Review Findings

DAST can produce false positives. Review findings before creating issues:

```python
from specify_cli.security.dast import DASTScanner
from specify_cli.security.models import Confidence

# Initialize scanner
scanner = DASTScanner(base_url="https://example.com")
result = scanner.scan_sync()

# Filter high-confidence findings
high_confidence = [
    f for f in result.findings
    if f.confidence == Confidence.HIGH
]

print(f"High confidence findings: {len(high_confidence)}")
for finding in high_confidence:
    print(f"  {finding.title} at {finding.metadata['url']}")
```

### 5. Integrate with CI/CD

```python
from specify_cli.security.dast import DASTScanner
from specify_cli.security.models import Severity

# In CI pipeline - initialize scanner
scanner = DASTScanner(base_url="https://staging.example.com")
result = scanner.scan_sync()

# Fail build if critical/high severity found
critical_high = [
    f for f in result.findings
    if f.severity in [Severity.CRITICAL, Severity.HIGH]
]

if critical_high:
    print(f"FAIL: Found {len(critical_high)} critical/high severity issues")
    exit(1)
else:
    print("PASS: No critical/high severity issues found")
```

## Troubleshooting

### Playwright Not Installed

```
ImportError: Playwright is not installed
```

**Solution:**

```bash
pip install 'specify-cli[dast]'
playwright install chromium
```

### Browser Launch Failed

```
RuntimeError: Browser launch failed
```

**Solution:**

```bash
# Install system dependencies (Ubuntu/Debian)
playwright install-deps chromium

# Or use Docker
docker run -it mcr.microsoft.com/playwright:v1.48.0-focal
```

### Timeout Errors

```
TimeoutError: page.goto: Timeout 30000ms exceeded
```

**Solution:**

```python
# Increase timeout
config = CrawlConfig(
    base_url="https://example.com",
    timeout_ms=60000  # 60 seconds
)
```

### Authentication Fails

```python
# Add debugging to auth callback
async def debug_auth(page):
    await page.goto("https://example.com/login")

    # Take screenshot before filling
    await page.screenshot(path="before-login.png")

    await page.fill("#username", "test")
    await page.fill("#password", "test")
    await page.click("#login")

    # Take screenshot after clicking
    await page.screenshot(path="after-login.png")

    # Check for errors
    error = await page.query_selector(".error-message")
    if error:
        error_text = await error.text_content()
        print(f"Login error: {error_text}")
```

## Reference

### Detected Vulnerability Types

| Type | CWE | Severity | Description |
|------|-----|----------|-------------|
| XSS | CWE-79 | High | Cross-Site Scripting |
| CSRF | CWE-352 | Medium | Cross-Site Request Forgery |
| Session Fixation | CWE-384 | High | Session fixation vulnerability |
| Insecure Cookie | CWE-614 | Medium | Missing cookie security flags |
| Clickjacking | CWE-1021 | Medium | Missing frame protection |
| Missing CSP | CWE-1021 | Medium | No Content-Security-Policy |
| Missing HSTS | CWE-523 | Low | No Strict-Transport-Security |

### API Reference

See:
- `src/specify_cli/security/dast/scanner.py` - Main scanner
- `src/specify_cli/security/dast/crawler.py` - Web crawler
- `src/specify_cli/security/dast/vulnerabilities.py` - Detectors
- `src/specify_cli/security/adapters/dast.py` - Adapter integration

## Related Documentation

- [Security Overview](../reference/security-overview.md)
- [Unified Finding Format](../reference/unified-finding-format.md)
- [Security Orchestrator](../reference/security-orchestrator.md)
