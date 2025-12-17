---
name: "flow-security_web"
description: "Test web applications for security vulnerabilities using dynamic analysis with Playwright."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"
---
# /flow:security_web

Test web applications for security vulnerabilities using dynamic analysis with Playwright.

## Purpose

This command performs Dynamic Application Security Testing (DAST) on running web applications:
- Automated crawling of web pages
- OWASP Top 10 vulnerability detection
- Security header and cookie analysis
- Authenticated crawling support
- Findings in Unified Finding Format

## Prerequisites

- Target web application is running and accessible
- Playwright browser automation available
- Network access to target URL
- Optional: Authentication credentials for protected areas

## Workflow

### 1. Load Configuration

Read security configuration for DAST settings:

```bash
# Check if config exists
if [ -f .flowspec/security-config.yml ]; then
    echo "Using DAST configuration from .flowspec/security-config.yml"
else
    echo "No DAST configuration found. Using defaults."
fi
```

**Configuration Parameters:**
- `dast.target_url` - Base URL to test
- `dast.max_depth` - Maximum crawl depth (default: 3)
- `dast.max_pages` - Maximum pages to crawl (default: 100)
- `dast.timeout` - Page load timeout in ms (default: 30000)
- `dast.auth.type` - Authentication method: `form`, `bearer`, `basic`
- `dast.auth.login_url` - Login page URL (for form auth)
- `dast.auth.username` - Username (read from env: `${DAST_USERNAME}`)
- `dast.auth.password` - Password (read from env: `${DAST_PASSWORD}`)
- `dast.exclusions` - URLs to skip (e.g., logout, delete endpoints)

### 2. Validate Target URL

Ensure target is accessible before scanning:

```bash
# Get target URL from CLI arg or config
TARGET_URL="${1:-$(yq '.dast.target_url' .flowspec/security-config.yml 2>/dev/null)}"

if [ -z "$TARGET_URL" ]; then
    echo "ERROR: No target URL specified. Use --url or set dast.target_url in config."
    exit 1
fi

# Validate URL format
if ! [[ "$TARGET_URL" =~ ^https?:// ]]; then
    echo "ERROR: Invalid URL format. Must start with http:// or https://"
    exit 1
fi

# Test connectivity
if ! curl -s --head --max-time 10 "$TARGET_URL" > /dev/null 2>&1; then
    echo "ERROR: Cannot reach target URL: $TARGET_URL"
    exit 1
fi

echo "Target URL: $TARGET_URL"
```

### 3. Initialize Playwright

Set up browser automation for testing:

```python
from playwright.async_api import async_playwright

# Launch browser (headless for CI/CD)
playwright = await async_playwright().start()
browser = await playwright.chromium.launch(headless=True)

# Create browser context
context = await browser.new_context(
    viewport={"width": 1920, "height": 1080},
    user_agent="FlowspecKit-DAST-Scanner/1.0",
    ignore_https_errors=False,  # Fail on invalid certs
)

# Create page
page = await context.new_page()
```

### 4. Authenticate (If Configured)

Handle authentication before crawling:

**Form-based Authentication:**
```python
if auth_type == "form":
    # Navigate to login page
    await page.goto(f"{base_url}{login_url}")

    # Fill credentials
    await page.locator("input[name=username], input[name=email]").fill(username)
    await page.locator("input[name=password]").fill(password)

    # Submit form
    await page.locator("button[type=submit], input[type=submit]").click()
    await page.wait_for_load_state("networkidle")

    # Verify authentication succeeded
    if "login" in page.url.lower():
        raise ValueError("Authentication failed - still on login page")

    # Save authenticated session
    await context.storage_state(path=".flowspec/.dast-session.json")
    print("Authentication successful")
```

**Bearer Token Authentication:**
```python
elif auth_type == "bearer":
    # Add Authorization header to all requests
    await context.set_extra_http_headers({
        "Authorization": f"Bearer {token}"
    })
```

**Basic Authentication:**
```python
elif auth_type == "basic":
    # Recreate context with credentials
    context = await browser.new_context(
        http_credentials={"username": username, "password": password}
    )
    page = await context.new_page()
```

### 5. Invoke Security DAST Skill

Use the `security-dast` skill to crawl and test the application:

**Crawling Process:**

For each page discovered:

1. **Navigate to page:**
   ```python
   response = await page.goto(url, wait_until="networkidle")
   ```

2. **Run security checks:**
   - Check security headers (CSP, X-Frame-Options, HSTS, etc.)
   - Analyze cookies (Secure, HttpOnly, SameSite flags)
   - Test XSS in all input fields
   - Test SQL injection in all input fields
   - Check CSRF protection on forms
   - Scan for sensitive data exposure

3. **Extract links:**
   ```python
   links = await page.locator("a[href]").evaluate_all(
       "elements => elements.map(el => el.href)"
   )

   # Filter to same domain
   internal_links = [
       link for link in links
       if urlparse(link).netloc == urlparse(base_url).netloc
   ]
   ```

4. **Add to crawl queue:**
   ```python
   for link in internal_links:
       if link not in visited and link not in queue:
           if not should_exclude(link, exclusions):
               queue.append(link)
   ```

**Progress Reporting:**
```bash
echo "Crawling $TARGET_URL..."
echo "Max depth: $MAX_DEPTH, Max pages: $MAX_PAGES"
echo ""

# Show progress during crawl
# Pages crawled: 42/100 | Findings: 8 (3 critical, 2 high, 3 medium)
```

### 6. Generate Security Findings

Create findings in Unified Finding Format for each vulnerability:

**Finding Structure:**
```python
finding = {
    "id": f"DAST-{test_type.upper()}-{counter:03d}",
    "scanner": "playwright-dast",
    "severity": severity,  # critical, high, medium, low
    "title": title,
    "description": description,
    "location": {
        "url": url,
        "parameter": parameter,  # if applicable
        "method": method,  # GET, POST, etc.
    },
    "cwe_id": cwe_id,
    "cvss_score": cvss_score,
    "confidence": "high",  # DAST findings are high confidence
    "remediation": remediation,
    "references": references,
    "metadata": {
        "test_type": test_type,
        "payload": payload,  # if applicable
        "timestamp": datetime.now().isoformat(),
    }
}
```

**CWE Mapping:**
- XSS: CWE-79
- SQL Injection: CWE-89
- CSRF: CWE-352
- Missing CSP: CWE-693
- Insecure Cookies: CWE-614, CWE-1004
- Sensitive Data Exposure: CWE-200
- Missing HTTPS: CWE-319

### 7. Save Findings

Write findings to `docs/security/web-findings.json`:

```bash
# Create output directory if needed
mkdir -p docs/security

# Save findings
echo "Saving findings to docs/security/web-findings.json"
# Python code writes findings to file
```

### 8. Generate Report

Create summary report and display to user:

```bash
# Generate report
TOTAL=$(jq 'length' docs/security/web-findings.json)
CRITICAL=$(jq '[.[] | select(.severity=="critical")] | length' docs/security/web-findings.json)
HIGH=$(jq '[.[] | select(.severity=="high")] | length' docs/security/web-findings.json)
MEDIUM=$(jq '[.[] | select(.severity=="medium")] | length' docs/security/web-findings.json)
LOW=$(jq '[.[] | select(.severity=="low")] | length' docs/security/web-findings.json)

echo "
Web Security Scan Complete
===========================
Target: $TARGET_URL
Pages Crawled: $PAGES_CRAWLED
Total Findings: $TOTAL

Severity Breakdown:
  Critical: $CRITICAL
  High: $HIGH
  Medium: $MEDIUM
  Low: $LOW

Findings saved to: docs/security/web-findings.json

Next Steps:
1. Review findings: cat docs/security/web-findings.json | jq
2. Triage findings: /flow:security_triage --input docs/security/web-findings.json
3. Generate report: /flow:security_report
"

# Exit with failure if critical findings
if [ "$CRITICAL" -gt 0 ]; then
    echo "ERROR: Critical vulnerabilities found!"
    exit 1
fi
```

### 9. Cleanup

Close browser and cleanup temporary files:

```python
# Close browser
await browser.close()
await playwright.stop()

# Remove session file (contains credentials)
if os.path.exists(".flowspec/.dast-session.json"):
    os.remove(".flowspec/.dast-session.json")
```

## Command Options

```bash
/flow:security_web [OPTIONS]

Options:
  --url URL                  Target URL to scan (required if not in config)
  --crawl                    Enable crawling (default: single page only)
  --max-depth N              Maximum crawl depth (default: 3)
  --max-pages N              Maximum pages to crawl (default: 100)
  --auth-type TYPE           Authentication: form, bearer, basic
  --username USER            Username for authentication
  --password PASS            Password for authentication
  --login-url URL            Login page URL (for form auth)
  --output FILE              Output file (default: docs/security/web-findings.json)
  --timeout MS               Page load timeout in milliseconds (default: 30000)
  --exclude PATTERN          URL patterns to exclude (can be repeated)
  --headful                  Show browser window (for debugging)
```

## Example Usage

```bash
# Scan single page
/flow:security_web --url https://example.com

# Crawl entire site
/flow:security_web --url https://example.com --crawl --max-pages 200

# Authenticated scan
/flow:security_web \
  --url https://example.com \
  --crawl \
  --auth-type form \
  --login-url /login \
  --username admin \
  --password $ADMIN_PASSWORD

# Scan with exclusions
/flow:security_web \
  --url https://example.com \
  --crawl \
  --exclude "/logout" \
  --exclude "/admin/delete*" \
  --exclude "*.pdf"
```

## Integration with Backlog

After web scan, findings can be converted to backlog tasks:

```bash
# For each critical/high finding:
backlog task create "Fix [finding title]" \
  -d "[finding description]" \
  --ac "Implement remediation per web scan report" \
  --ac "Verify fix with re-scan" \
  --ac "Update security tests if needed" \
  -l security,web,bug \
  --priority high

# Add web scan report reference
backlog task edit [task-id] --notes "See web scan: docs/security/web-findings.json"
```

## Security Considerations

**Rate Limiting:**
- Add delays between requests to avoid overwhelming target
- Respect robots.txt (configurable)
- Limit concurrent requests (max 5 parallel pages)

**Scope Boundaries:**
- Only crawl within target domain (no external links)
- Respect exclusion patterns (don't crawl /logout, delete endpoints)
- Stop on repeated errors (don't hammer broken endpoints)

**Credential Safety:**
- Never log credentials (username, password, tokens)
- Use environment variables for sensitive data
- Delete session files after scan
- Don't commit credentials to git

## Error Handling

- **Target unreachable:** Fail fast with clear error message
- **Authentication failure:** Abort scan (don't proceed unauthenticated)
- **Page load timeout:** Skip page, continue crawling
- **JavaScript errors:** Log but don't stop (some errors are intentional)
- **Connection errors:** Retry 3 times with exponential backoff

## Performance Considerations

- **Parallel crawling:** Test up to 5 pages concurrently
- **Headless mode:** Faster than headful (use for CI/CD)
- **Caching:** Skip re-testing identical pages (same URL)
- **Progress indicators:** Show progress for long scans (>50 pages)

## Success Criteria

- All pages within depth limit crawled
- All forms and inputs tested for XSS and SQLi
- Security headers checked on all pages
- Findings saved in Unified Finding Format
- Exit code 0 if no critical findings, 1 if critical vulnerabilities found

## Related Commands

- `/flow:security scan` - Run SAST scanners (Semgrep, CodeQL, Bandit)
- `/flow:security_triage` - Triage web security findings
- `/flow:security_report` - Generate comprehensive security report
- `/flow:security_fix` - Apply automated fixes to findings

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web Security Patterns](../../../memory/security/web-security-patterns.md)
- [Security DAST Skill](../../../.claude/skills/security-dast.md)
- [ADR-007: Unified Security Finding Format](../../../docs/adr/ADR-007-unified-security-finding-format.md)
- [Playwright Documentation](https://playwright.dev/)
