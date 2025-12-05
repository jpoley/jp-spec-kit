# Lessons Learned: MCP Security Code Review (2025-12-05)

## Summary

A comprehensive code review of unmerged MCP security code identified **34 issues** (28 code quality + 6 security vulnerabilities). This document captures the lessons learned to prevent similar issues in future code.

## Critical Issues Found

### 1. File Duplication (CRITICAL)

**Problem:** `pre-commit-dogfood.sh` was a 100% exact copy of `pre-commit-dev-setup.sh` with wrong header comments.

**Root Cause:** Copy-paste coding without thinking about DRY principle.

**Prevention:**
- Always ask: "Does similar code already exist?"
- Use symlinks for identical functionality
- Never copy-paste files - extract to shared modules
- CI should detect duplicate files

### 2. Duplicate Pre-commit Hooks (CRITICAL)

**Problem:** Two hooks doing the exact same validation ran on every commit.

**Root Cause:** Adding "new" functionality without checking existing hooks.

**Prevention:**
- Review existing hooks before adding new ones
- Document what each hook does
- Test that new hooks actually add value

## Security Issues Found

### 3. Path Traversal (HIGH - SEC-1)

**Problem:** User-supplied paths were joined directly without validation:
```python
target_path = PROJECT_ROOT / target  # NO validation!
```

**Attack:** `../../../etc/passwd` escapes PROJECT_ROOT.

**Fix Applied:**
```python
def _validate_path(user_path: str, base_dir: Path) -> Path:
    if Path(user_path).is_absolute():
        raise ValueError(f"Absolute paths not allowed: {user_path}")
    resolved = (base_dir / user_path).resolve()
    try:
        resolved.relative_to(base_dir.resolve())
    except ValueError:
        raise ValueError(f"Path traversal detected: {user_path}")
    return resolved
```

**Prevention:**
- NEVER use user input directly in path operations
- Always validate paths against allowed base directory
- Resolve to canonical form before checking containment
- Add path validation tests for every path-accepting function

### 4. Information Disclosure (MEDIUM - SEC-2)

**Problem:** Full stack traces printed to stderr exposing internal paths.

**Prevention:**
- Log detailed errors to secure log files, not stdout/stderr
- Return generic messages to users
- Only show details in explicit debug mode

### 5. Missing Resource Limits (MEDIUM - SEC-4)

**Problem:** No limits on findings count, file size, or scan duration.

**Fix Applied:**
```python
MAX_FINDINGS = 10000  # Maximum findings to process

if len(findings) > MAX_FINDINGS:
    truncated = True
    findings = findings[:MAX_FINDINGS]
```

**Prevention:**
- Always define limits for user-controlled resources
- Document limits clearly
- Return truncation information to clients

### 6. Missing Input Validation (MEDIUM - SEC-5)

**Problem:** Scanner names accepted without whitelist validation.

**Fix Applied:**
```python
VALID_SCANNERS = frozenset({"semgrep", "codeql", "trivy", "bandit", "safety"})

invalid = [s for s in scanners if s not in VALID_SCANNERS]
if invalid:
    raise ValueError(f"Invalid scanner names: {invalid}")
```

**Prevention:**
- Define whitelists for all enumerable inputs
- Validate at API boundaries (defense-in-depth)
- Return clear error messages with valid options

## Code Quality Issues Found

### 7. Unsafe JSON Parsing (HIGH)

**Problem:** Direct dict access without validation:
```python
scan_data = json.loads(scan_result.content[0].text)
print(f"Total: {scan_data['findings_count']}")  # KeyError if missing!
```

**Fix Applied:** Created `parse_mcp_response()` helper with validation.

**Prevention:**
- Always use `.get()` with defaults for optional keys
- Validate required keys before access
- Use schema validation (pydantic) for complex structures

### 8. Broad Exception Catching (HIGH)

**Problem:**
```python
except Exception as e:  # Catches EVERYTHING including KeyboardInterrupt
```

**Fix Applied:**
```python
except KeyboardInterrupt:
    sys.exit(130)  # Standard signal exit code
except MCPConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    logger.exception("Unexpected error")
    print("See logs for details.")
```

**Prevention:**
- Catch specific exceptions
- Handle KeyboardInterrupt separately
- Log unexpected exceptions with full traceback
- Return generic messages for unexpected errors

### 9. Magic Numbers (HIGH)

**Problem:**
```python
print("-" * 60)  # Why 60?
findings_data[:3]  # Why 3?
desc[:100]  # Why 100?
```

**Fix Applied:**
```python
SEPARATOR_WIDTH = 60
DEFAULT_FINDINGS_PREVIEW_COUNT = 3
MAX_DESCRIPTION_LENGTH = 100
```

**Prevention:**
- Extract all numbers to named constants
- Document the reason for each constant
- Make configurable via CLI args when appropriate

### 10. Code Duplication (MEDIUM)

**Problem:** Same MCP connection logic copy-pasted 3+ times.

**Fix Applied:** Created `mcp_utils.py` with shared utilities:
- `connect_to_security_mcp()` - connection context manager
- `parse_mcp_response()` - safe JSON parsing
- `validate_target_directory()` - path validation

**Prevention:**
- If you copy-paste code, stop and extract to module
- Create shared utilities for common patterns
- Review for duplication before PR

### 11. Missing Timeouts (MEDIUM)

**Problem:** No timeout on MCP operations - can hang forever.

**Fix Applied:**
```python
async with asyncio.timeout(timeout):
    async with stdio_client(server_params) as (read, write):
        # ...
```

**Prevention:**
- Always add timeouts to network/subprocess operations
- Make timeouts configurable
- Document default timeout values

### 12. sys.exit() in Async Functions (MEDIUM)

**Problem:** `sys.exit()` in async code doesn't clean up properly.

**Fix Applied:** Raise exception, catch in sync main():
```python
async def run_dashboard(...):
    if not repos_status:
        raise DashboardError(error_msg)  # Not sys.exit()!

def main():
    try:
        asyncio.run(run_dashboard(...))
    except DashboardError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
```

**Prevention:**
- Never call `sys.exit()` in async code
- Use exceptions for error propagation
- Handle exits in synchronous entry points

### 13. Unused Variables (LOW)

**Problem:** `MCP_AVAILABLE = True` set but never used.

**Prevention:**
- Run linter before committing
- Remove dead code
- If keeping for future use, add comment explaining why

## Testing Improvements

### Tests Added

1. **Path Validation Tests:**
   - `test_validate_path_accepts_relative_path`
   - `test_validate_path_rejects_absolute_path`
   - `test_validate_path_rejects_path_traversal`
   - `test_validate_path_rejects_double_traversal`

2. **Input Validation Tests:**
   - `test_validate_scanners_accepts_valid`
   - `test_validate_scanners_rejects_invalid`
   - `test_validate_severities_accepts_valid`
   - `test_validate_severities_rejects_invalid`

3. **Security Scan Validation Tests:**
   - `test_scan_rejects_path_traversal`
   - `test_scan_rejects_absolute_path`
   - `test_scan_rejects_invalid_scanner`
   - `test_scan_rejects_nonexistent_target`

**Lesson:** Security code needs extra test coverage for:
- All validation functions
- Error cases and edge cases
- Attack scenarios (path traversal, injection, etc.)

## Architecture Improvements

### Before (Sloppy)
```
examples/mcp/
├── claude_security_agent.py  # 230 lines, copy-pasted code
└── security_dashboard.py     # 340 lines, same patterns duplicated
```

### After (Clean)
```
examples/mcp/
├── mcp_utils.py              # Shared utilities (270 lines)
├── claude_security_agent.py  # Now 220 lines, uses utilities
├── security_dashboard.py     # Now 310 lines, uses utilities
└── README.md                 # Usage documentation
```

## Checklist for Future Code Reviews

Before merging ANY MCP/security code:

- [ ] Path inputs validated against traversal
- [ ] All inputs validated against whitelists
- [ ] Resource limits defined and enforced
- [ ] Timeouts on all network/subprocess operations
- [ ] No broad `except Exception` without specific handlers
- [ ] No `sys.exit()` in async code
- [ ] No magic numbers (extract to constants)
- [ ] No code duplication (extract to shared modules)
- [ ] Stack traces logged to file, not printed to users
- [ ] Tests for all validation functions
- [ ] Tests for error cases and attack scenarios
- [ ] Linter passes with no warnings

## Files Modified

**New Files:**
- `examples/mcp/mcp_utils.py` - Shared MCP utilities

**Fixed Files:**
- `examples/mcp/claude_security_agent.py` - Refactored with proper error handling
- `examples/mcp/security_dashboard.py` - Refactored with proper error handling
- `examples/mcp/README.md` - Documentation
- `src/specify_cli/security/mcp_server.py` - Added security hardening
- `tests/security/test_mcp_server.py` - Added 15 new security tests

**Removed/Not Created:**
- `scripts/bash/pre-commit-dogfood.sh` - Duplicate of existing script
- `dogfood-check` hook - Duplicate of existing hook

## Summary of Fixes

| Category | Issues Found | Issues Fixed |
|----------|-------------|--------------|
| Critical (Duplicates) | 2 | 2 |
| High Security | 1 | 1 |
| Medium Security | 4 | 4 |
| Low Security | 1 | 1 |
| High Code Quality | 6 | 6 |
| Medium Code Quality | 10 | 10 |
| Low Code Quality | 10 | 10 |
| **Total** | **34** | **34** |

---

**Date:** 2025-12-05
**Author:** Backend Engineer + Security Reviewer Agents
**Review Type:** Ultrathink Code Quality + Security Review
