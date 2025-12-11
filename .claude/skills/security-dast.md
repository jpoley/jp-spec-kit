# Security DAST Skill

## Purpose

This skill enables Claude Code to perform Dynamic Application Security Testing (DAST) on web applications using Playwright. You will crawl web applications, test for OWASP Top 10 vulnerabilities, analyze security headers, and detect common web security issues.

## When to Use This Skill

- When invoked by `/flow:security_web` command
- When user asks to test web application security
- When analyzing running web applications for vulnerabilities

## Prerequisites

- Target web application is running and accessible
- Playwright browser automation configured
- Optional: Authentication credentials for protected areas
- Optional: Seed URLs for deep crawling

## Input

Target application specified by:
1. URL from command line: `--url https://example.com`
2. Configuration file: `.flowspec/security-config.yml` under `dast.target_url`
3. User prompt when neither is provided

Expected configuration:
```yaml
dast:
  target_url: "https://example.com"
  max_depth: 3
  max_pages: 100
  timeout: 30000
  auth:
    type: "form"  # or "bearer", "basic"
    login_url: "/login"
    username: "${DAST_USERNAME}"  # Read from env
    password: "${DAST_PASSWORD}"  # Read from env
  exclusions:
    - "/logout"
    - "/admin/delete"
    - "*.pdf"
```

## Web Security Tests

For EACH page discovered during crawling, perform these security checks:

### 1. Security Headers Analysis

Check for essential security headers:

**Required Headers:**
- `Content-Security-Policy` - Prevents XSS and data injection
- `X-Frame-Options` - Prevents clickjacking (or frame-ancestors in CSP)
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `Strict-Transport-Security` - Enforces HTTPS
- `Referrer-Policy` - Controls referrer information

**Report missing or misconfigured headers as findings.**

Example check:
```python
response = await page.goto(url)
headers = response.headers

# Missing CSP
if "content-security-policy" not in headers:
    create_finding(
        title="Missing Content-Security-Policy header",
        severity="high",
        cwe_id="CWE-693",
        description="No CSP header found. Application vulnerable to XSS attacks.",
        location={"url": url, "header": "Content-Security-Policy"},
        remediation="Add CSP header: Content-Security-Policy: default-src 'self'"
    )
```

### 2. Cookie Security Flags

Inspect all cookies set by the application:

**Required Flags:**
- `Secure` - Cookie only sent over HTTPS
- `HttpOnly` - Cookie not accessible via JavaScript (prevents XSS cookie theft)
- `SameSite` - Protection against CSRF (Strict or Lax)

Example check:
```python
cookies = await context.cookies()

for cookie in cookies:
    if not cookie.get("secure"):
        create_finding(
            title=f"Cookie '{cookie['name']}' missing Secure flag",
            severity="medium",
            cwe_id="CWE-614",
            description="Cookie transmitted over unencrypted connections",
            remediation="Set Secure flag on cookie"
        )

    if not cookie.get("httpOnly") and "session" in cookie["name"].lower():
        create_finding(
            title=f"Session cookie '{cookie['name']}' missing HttpOnly flag",
            severity="high",
            cwe_id="CWE-1004",
            description="Session cookie accessible via JavaScript, vulnerable to XSS theft",
            remediation="Set HttpOnly flag on session cookies"
        )
```

### 3. XSS (Cross-Site Scripting) Detection

Test input fields for reflected and stored XSS:

**Test Payloads:**
```python
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    "<svg/onload=alert('XSS')>",
    "'-alert('XSS')-'",
]
```

**Test Process:**
1. Identify all input fields (text inputs, textareas, search boxes)
2. Submit each payload to each field
3. Check if payload appears unescaped in response
4. Check if JavaScript executes (using Playwright event listeners)

Example:
```python
# Find all forms
forms = await page.locator("form").all()

for form in forms:
    inputs = await form.locator("input[type=text], input[type=search], textarea").all()

    for input_elem in inputs:
        name = await input_elem.get_attribute("name")

        for payload in xss_payloads:
            # Fill and submit
            await input_elem.fill(payload)
            await form.evaluate("form => form.submit()")

            # Wait for navigation
            await page.wait_for_load_state()

            # Check if payload appears unescaped
            content = await page.content()
            if payload in content:
                create_finding(
                    title=f"Reflected XSS in form field '{name}'",
                    severity="high",
                    cwe_id="CWE-79",
                    description=f"Input field '{name}' reflects user input without encoding",
                    location={"url": page.url, "field": name},
                    remediation="HTML-encode all user input before rendering"
                )
```

### 4. SQL Injection Detection

Test input fields for SQL injection vulnerabilities:

**Test Payloads:**
```python
sqli_payloads = [
    "' OR '1'='1",
    "admin'--",
    "' UNION SELECT NULL--",
    "1' AND '1'='2",
    "'; DROP TABLE users--",
]
```

**Error Signatures:**
```python
sql_errors = [
    "SQL syntax",
    "mysql_fetch",
    "ORA-",
    "PostgreSQL",
    "ODBC",
    "Microsoft SQL Server",
    "SQLite",
]
```

**Test Process:**
1. Submit payloads to input fields
2. Check response for SQL error messages
3. Check for behavioral changes (authentication bypass, different responses)

Example:
```python
for payload in sqli_payloads:
    await input_elem.fill(payload)
    await form.evaluate("form => form.submit()")
    await page.wait_for_load_state()

    content = await page.content()

    # Check for SQL errors
    for error_sig in sql_errors:
        if error_sig.lower() in content.lower():
            create_finding(
                title=f"SQL Injection in form field '{name}'",
                severity="critical",
                cwe_id="CWE-89",
                description=f"SQL error message detected after injecting payload",
                location={"url": page.url, "field": name, "payload": payload},
                remediation="Use parameterized queries or prepared statements"
            )
```

### 5. CSRF (Cross-Site Request Forgery) Detection

Check for CSRF protection on state-changing operations:

**Test Process:**
1. Identify forms that modify state (POST, PUT, DELETE)
2. Check for CSRF tokens in forms
3. Check for CSRF tokens in headers
4. Verify SameSite cookie attribute

Example:
```python
forms = await page.locator("form[method=post], form[method=put]").all()

for form in forms:
    action = await form.get_attribute("action")

    # Look for CSRF token field
    csrf_field = await form.locator("input[name*=csrf], input[name*=token]").count()

    if csrf_field == 0:
        # Check for CSRF token in meta tags
        csrf_meta = await page.locator("meta[name=csrf-token]").count()

        if csrf_meta == 0:
            create_finding(
                title=f"Missing CSRF protection on form",
                severity="high",
                cwe_id="CWE-352",
                description=f"State-changing form lacks CSRF token",
                location={"url": page.url, "form_action": action},
                remediation="Add CSRF token to all state-changing forms"
            )
```

### 6. Sensitive Data Exposure

Check for sensitive information in responses:

**Sensitive Patterns:**
```python
sensitive_patterns = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "email addresses"),
    (r'\b\d{3}-\d{2}-\d{4}\b', "SSN"),
    (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', "credit card numbers"),
    (r'password\s*[:=]\s*["\']?[\w@#$%]+', "hardcoded passwords"),
    (r'api[_-]?key\s*[:=]\s*["\']?[\w-]+', "API keys"),
    (r'secret\s*[:=]\s*["\']?[\w-]+', "secrets"),
]
```

Example:
```python
import re

content = await page.content()

for pattern, description in sensitive_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)

    if matches:
        create_finding(
            title=f"Sensitive data exposure: {description}",
            severity="medium",
            cwe_id="CWE-200",
            description=f"Found {len(matches)} instance(s) of {description} in page content",
            location={"url": page.url},
            remediation=f"Remove {description} from client-side code"
        )
```

### 7. TLS/SSL Configuration

Test HTTPS configuration:

**Checks:**
- Redirects HTTP to HTTPS
- Valid SSL certificate
- Strong cipher suites
- TLS 1.2+ (no TLS 1.0/1.1)

Example:
```python
# Test HTTP -> HTTPS redirect
http_url = url.replace("https://", "http://")
response = await page.goto(http_url)

if response.url.startswith("http://"):
    create_finding(
        title="No HTTPS redirect",
        severity="medium",
        cwe_id="CWE-319",
        description="HTTP requests not redirected to HTTPS",
        location={"url": http_url},
        remediation="Configure server to redirect all HTTP traffic to HTTPS"
    )
```

## Crawling Strategy

Use Playwright to discover pages:

### Breadth-First Crawling

```python
from collections import deque

visited = set()
queue = deque([base_url])

while queue and len(visited) < max_pages:
    url = queue.popleft()

    if url in visited:
        continue

    visited.add(url)

    # Run security tests on this page
    await test_page_security(page, url)

    # Extract links
    links = await page.locator("a[href]").all()

    for link in links:
        href = await link.get_attribute("href")

        # Resolve relative URLs
        absolute_url = urljoin(url, href)

        # Skip excluded URLs
        if should_exclude(absolute_url):
            continue

        # Stay within domain
        if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
            queue.append(absolute_url)
```

### Authentication Handling

Support multiple authentication methods:

**Form-based:**
```python
# Navigate to login page
await page.goto(login_url)

# Fill credentials
await page.locator("input[name=username]").fill(username)
await page.locator("input[name=password]").fill(password)

# Submit form
await page.locator("button[type=submit]").click()
await page.wait_for_load_state()

# Save authenticated context
context_state = await context.storage_state()
```

**Bearer Token:**
```python
# Add Authorization header to all requests
await context.set_extra_http_headers({
    "Authorization": f"Bearer {token}"
})
```

**Basic Auth:**
```python
# Set credentials in browser context
context = await browser.new_context(
    http_credentials={"username": username, "password": password}
)
```

## Output Format

Write findings to `docs/security/web-findings.json` in Unified Finding Format:

```json
[
  {
    "id": "DAST-XSS-001",
    "scanner": "playwright-dast",
    "severity": "high",
    "title": "Reflected XSS in search parameter",
    "description": "Search input reflects user data without HTML encoding",
    "location": {
      "url": "https://example.com/search",
      "parameter": "q",
      "method": "GET"
    },
    "cwe_id": "CWE-79",
    "cvss_score": 7.3,
    "confidence": "high",
    "remediation": "HTML-encode all user input before rendering in responses",
    "references": [
      "https://owasp.org/www-community/attacks/xss/",
      "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
    ],
    "metadata": {
      "test_type": "xss",
      "payload": "<script>alert('XSS')</script>",
      "timestamp": "2025-12-04T18:30:00Z"
    }
  }
]
```

Sort findings by severity (critical first), then by URL.

## Rate Limiting and Politeness

- Respect robots.txt (optional, configurable)
- Add delay between requests: `await page.wait_for_timeout(100)`
- Limit concurrent requests: max 5 parallel pages
- Stop on repeated errors (3 consecutive failures)

## Error Handling

**Connection Errors:**
- Retry up to 3 times with exponential backoff
- Skip page and continue crawling if timeout

**Authentication Errors:**
- Fail fast if login fails (don't crawl as unauthenticated)
- Report authentication failure clearly

**JavaScript Errors:**
- Log but don't stop (some pages have intentional JS errors)

## Success Criteria

- Crawl all pages within depth limit
- Test all discovered forms and inputs
- Check security headers on all pages
- Generate findings in Unified Finding Format
- Report summary with vulnerability counts
- Exit code 0 if no critical findings, 1 if critical vulnerabilities found

## Example Workflow

```bash
# User runs web security test
/flow:security_web --url https://example.com --crawl

# You execute:
1. Load configuration from .flowspec/security-config.yml
2. Launch Playwright browser (headless mode)
3. Authenticate if credentials provided
4. Start crawling from base URL
5. For each page:
   - Check security headers
   - Check cookie flags
   - Test XSS in all inputs
   - Test SQL injection in all inputs
   - Check CSRF protection
   - Scan for sensitive data
6. Generate findings in UFFormat
7. Write to docs/security/web-findings.json
8. Report summary to user
9. Exit with appropriate code
```

## Notes

- This is a SKILL, not Python code. You (Claude Code) execute the logic natively.
- No LLM API calls from Python. All AI reasoning happens in this skill.
- Python code handles Playwright automation and data structures.
- Use Playwright Browser tool for web interactions.
- Apply domain knowledge from `memory/security/web-security-patterns.md`.
- False positives are common in DAST - use conservative classification.

## Integration with Triage

After web scan, findings can be triaged:

```bash
# Run web scan
/flow:security_web --url https://example.com

# Triage findings
/flow:security_triage --input docs/security/web-findings.json
```

The triage skill will classify DAST findings as TP/FP/NI and generate remediation guidance.
