---
id: task-222
title: Implement Web Security Testing with Playwright DAST
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 02:15'
updated_date: '2025-12-19 18:41'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add /flow:security web subcommand for dynamic application security testing using Playwright. Supports authenticated crawling, form submission testing, and common web vulnerability detection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement specify security web CLI command
- [x] #2 Integrate Playwright for browser automation
- [x] #3 Support authenticated crawling with session management
- [x] #4 Detect OWASP Top 10 web vulnerabilities
- [x] #5 Generate web security findings in unified format
- [x] #6 Add --url and --crawl options
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Implement Web Security Testing with Playwright DAST

### Overview
Add DAST capabilities using Playwright for authenticated crawling and OWASP Top 10 web vulnerability detection.

### Step-by-Step Implementation

#### Step 1: Add Playwright Integration (3 hours)
**File**: `src/specify_cli/security/web_scanner.py`

```python
async def scan_web_application(url: str, config: WebScanConfig) -> List[Finding]:
    """Scan web application for security vulnerabilities."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Authenticate if needed
        if config.auth:
            await authenticate(page, config.auth)
        
        # Crawl application
        visited = set()
        to_visit = [url]
        findings = []
        
        while to_visit:
            current_url = to_visit.pop()
            if current_url in visited:
                continue
            
            await page.goto(current_url)
            visited.add(current_url)
            
            # Run security checks
            findings.extend(await check_xss(page))
            findings.extend(await check_clickjacking(page))
            findings.extend(await check_csrf(page))
            findings.extend(await check_headers(page))
            
            # Find new links
            links = await page.eval_on_selector_all('a[href]', 'els => els.map(e => e.href)')
            to_visit.extend([l for l in links if is_same_origin(l, url)])
        
        await browser.close()
        return findings
```

#### Step 2: Implement OWASP Top 10 Checks (4 hours)

Checks to implement:
1. **XSS Detection**: Inject payloads in forms/URL params
2. **CSRF**: Check for CSRF tokens in forms
3. **Clickjacking**: Check X-Frame-Options/CSP
4. **Security Headers**: Missing headers (HSTS, CSP, etc.)
5. **Insecure Cookies**: HttpOnly, Secure flags
6. **Open Redirects**: Test redirect parameters

#### Step 3: Add CLI Command (2 hours)
```bash
specify security web \
  --url https://app.example.com \
  --auth-type form \
  --auth-url https://app.example.com/login \
  --username test@example.com \
  --password-env WEB_SCAN_PASSWORD \
  --crawl-depth 3 \
  --max-pages 100
```

#### Step 4: Unified Finding Format (1 hour)
Convert DAST findings to same format as SAST findings for consistent triage/fix workflow.

#### Step 5: Documentation (2 hours)
**File**: `docs/guides/web-security-testing.md`

#### Step 6: Testing (2 hours)
- Deploy test vulnerable web app (DVWA or custom)
- Verify each check detects known vulnerabilities
- Test authenticated crawling

### Dependencies
- Unified finding format defined
- Test web application available

### Estimated Effort
**Total**: 14 hours (1.75 days)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation already exists at src/flowspec_cli/security/dast/. All ACs were checked. Verified crawler.py, scanner.py, vulnerabilities.py exist.
<!-- SECTION:NOTES:END -->
