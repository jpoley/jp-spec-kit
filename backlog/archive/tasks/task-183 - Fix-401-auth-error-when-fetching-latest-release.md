---
id: task-183
title: Fix 401 auth error when fetching latest release
status: Done
assignee:
  - '@claude'
created_date: '2025-12-01 02:17'
updated_date: '2025-12-01 04:09'
labels:
  - bug
  - github-api
  - authentication
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**GitHub Issue:** #161

**Problem:**
The specify CLI fails with a 401 authentication error when attempting to fetch the latest release from GitHub:

```
Could not resolve release for github/spec-kit (version='latest'). Last HTTP status: 401
```

The tool attempts multiple resolution paths:
- `/releases/latest`
- `/releases/tags/` with version prefixes
- `/releases list`

All fail with 401 Unauthorized.

**Key Insight:** This is a public repository - no authentication should be required to fetch release info from the GitHub API.

**Likely Root Causes:**
1. **Incorrect API URL** - May be hitting a wrong endpoint or malformed URL
2. **Wrong repo reference** - `github/spec-kit` looks wrong; should likely be `jpoley/jp-spec-kit`
3. **Sending invalid/stale auth header** - If a token is being sent but is invalid, GitHub returns 401
4. **Rate limiting edge case** - Though this typically returns 403, not 401

**Environment:**
- jp extension v0.0.147
- AI Assistant: copilot
- Script Type: sh
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Verify correct repository path is used (jpoley/jp-spec-kit, not github/spec-kit)
- [x] #2 CLI can fetch latest release from public repos without any authentication
- [x] #3 If an invalid token is present, either skip it or handle the 401 gracefully
- [x] #4 Add unit tests for release fetching from public repos
- [x] #5 Error messages clearly indicate the actual problem (not just 'add a token')
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via branch task-183-fix-401-auth-error

Root Cause: Invalid GitHub tokens caused 401 errors even for public repos.
Fix: Automatic retry without authentication when 401 occurs with a token.

Files changed:
- src/specify_cli/__init__.py (retry logic + better error messages)
- tests/test_github_auth.py (11 new tests)

All 1102 tests passing.

PR #167: https://github.com/jpoley/jp-spec-kit/pull/167

PR #169: https://github.com/jpoley/jp-spec-kit/pull/169 (replaces closed #167)

Fix details:
- Added skip_auth parameter to _github_headers
- Retry logic now properly skips all auth on public repo fallback
- 26 comprehensive tests added
<!-- SECTION:NOTES:END -->
