# Task Memory System - Security Review

**Review Date**: 2025-12-09
**Reviewer**: QA Engineer / Security Reviewer
**Component**: Task Memory System (backlog/memory/)
**Version**: v1.0.0

## Executive Summary

This security review assesses the Task Memory system for potential security vulnerabilities, focusing on:
- Secrets exposure risks
- Input validation and sanitization
- File path security
- Archive/delete safety
- Access control considerations

**Overall Risk Level**: LOW
**Critical Issues**: 0
**High Issues**: 0
**Medium Issues**: 2
**Low Issues**: 3
**Informational**: 2

## Security Findings

### MEDIUM-001: Secrets Exposure in Memory Files

**Risk**: Medium
**Component**: TaskMemoryStore, memory file creation/append

**Description**:
Task memory files are plain-text markdown stored in `backlog/memory/`. Developers may inadvertently include sensitive information (API keys, passwords, tokens) in memory notes, which would then be:
1. Committed to git
2. Synced across machines
3. Potentially visible in git history permanently

**Evidence**:
```python
# No sanitization or scanning in store.py
def append(self, task_id: str, content: str) -> None:
    """Append content to task memory."""
    memory_path.write_text(existing + "\n" + content)
```

**Impact**:
- Secrets committed to version control
- Exposure in git history even if later removed
- Potential unauthorized access if repository is compromised

**Recommendations**:
1. **Implement secret scanning**: Add pre-commit hook to scan memory files for patterns like:
   - API keys (e.g., `sk_live_`, `AIza`)
   - AWS credentials (`AKIA`, `aws_secret_access_key`)
   - Tokens and passwords
   - Email addresses in sensitive contexts

2. **Add warnings in template**: Update `templates/memory/default.md`:
   ```markdown
   ## ⚠️ Security Warning

   DO NOT include sensitive information in this memory:
   - API keys, tokens, or passwords
   - Customer data or PII
   - Proprietary algorithms or trade secrets

   Use environment variables and secure vaults instead.
   ```

3. **Gitignore option**: Allow users to add `backlog/memory/*.md` to `.gitignore` if desired

4. **Implement secret detection library**: Integrate `detect-secrets` or similar:
   ```python
   from detect_secrets import SecretsCollection
   from detect_secrets.settings import default_settings

   def check_for_secrets(content: str) -> list:
       secrets = SecretsCollection()
       secrets.scan_string(content)
       return list(secrets)
   ```

**Acceptance Criteria for Fix**:
- [ ] Secret scanning hook implemented
- [ ] Template includes security warning
- [ ] Documentation updated with security best practices
- [ ] CI/CD includes secret scanning for memory files

---

### MEDIUM-002: Path Traversal in Task ID

**Risk**: Medium
**Component**: TaskMemoryStore.get_path()

**Description**:
Task IDs are used to construct file paths without sufficient validation. A malicious or malformed task ID could potentially traverse directories:

```python
# Current implementation in store.py
def get_path(self, task_id: str) -> Path:
    return self.memory_dir / f"{task_id}.md"
```

**Attack Vectors**:
1. Task ID: `../../etc/passwd` → attempts to write outside memory dir
2. Task ID: `task-1/../../../secrets` → directory traversal
3. Task ID: `task-1/.git/config` → attempts to overwrite git files

**Impact**:
- Arbitrary file writes outside intended directory
- Potential overwrite of system or project files
- Security boundary violation

**Recommendations**:

1. **Strict task ID validation**:
   ```python
   import re

   TASK_ID_PATTERN = re.compile(r'^task-\d+(-[a-z0-9-]+)?$')

   def validate_task_id(task_id: str) -> None:
       """Validate task ID format."""
       if not task_id:
           raise ValueError("Task ID cannot be empty")

       if not TASK_ID_PATTERN.match(task_id):
           raise ValueError(
               f"Invalid task ID format: {task_id}. "
               "Must match pattern: task-<number>[-optional-name]"
           )

       # Check for path traversal attempts
       if ".." in task_id or "/" in task_id or "\\" in task_id:
           raise ValueError(f"Task ID contains invalid characters: {task_id}")
   ```

2. **Path sanitization**:
   ```python
   def get_path(self, task_id: str) -> Path:
       """Get path to task memory file with security checks."""
       validate_task_id(task_id)

       # Construct path
       memory_path = self.memory_dir / f"{task_id}.md"

       # Verify path is within memory_dir (resolve symlinks)
       resolved_path = memory_path.resolve()
       resolved_memory_dir = self.memory_dir.resolve()

       if not str(resolved_path).startswith(str(resolved_memory_dir)):
           raise ValueError(f"Path traversal detected: {task_id}")

       return memory_path
   ```

3. **Whitelist allowed characters**: Only allow `[a-z0-9-]` in task IDs

**Acceptance Criteria for Fix**:
- [ ] Task ID validation function implemented
- [ ] Path traversal protection added
- [ ] Tests cover malicious task ID inputs
- [ ] Documentation specifies allowed task ID format

---

### LOW-001: No Access Control on Memory Files

**Risk**: Low
**Component**: File system permissions

**Description**:
Task memory files are created with default file permissions (usually 0644), making them readable by all users on the system. In shared development environments, this could expose sensitive project information.

**Current Behavior**:
```bash
$ ls -la backlog/memory/
-rw-r--r-- 1 user group 1234 Dec 09 10:00 task-100.md
```

**Impact**:
- Other users on same system can read task memories
- Potential information disclosure in shared environments
- No encryption at rest

**Recommendations**:

1. **Restrict file permissions**:
   ```python
   import os

   def create(self, task_id: str, ...) -> Path:
       memory_path = self.get_path(task_id)
       memory_path.write_text(content)

       # Set restrictive permissions (user read/write only)
       os.chmod(memory_path, 0o600)

       return memory_path
   ```

2. **Document security expectations**: Add to README:
   ```markdown
   ## Security Considerations

   Task memory files are stored as plaintext markdown in `backlog/memory/`.
   In shared environments:
   - Files are restricted to user read/write (0600)
   - Consider encrypting sensitive memories
   - Use separate user accounts for isolation
   ```

3. **Optional encryption**: Provide encryption option for sensitive projects:
   ```python
   # Future enhancement
   def create_encrypted(self, task_id: str, passphrase: str):
       from cryptography.fernet import Fernet
       # Encrypt memory content
   ```

**Acceptance Criteria for Fix**:
- [ ] File permissions set to 0600 on creation
- [ ] Directory permissions verified secure
- [ ] Documentation includes security guidelines

---

### LOW-002: Archive Directory Unbounded Growth

**Risk**: Low
**Component**: Cleanup Manager, archive retention

**Description**:
Archived task memories are retained indefinitely in `backlog/memory/archive/`. Over time, this could lead to:
- Excessive disk usage
- Performance degradation
- Difficulty finding relevant archived memories
- Increased attack surface (more files to scan for secrets)

**Current Behavior**:
- Archives never deleted automatically
- No retention policy
- No size limits

**Impact**:
- Disk space exhaustion (long-term)
- Performance impact on search/list operations
- Compliance issues (data retention requirements)

**Recommendations**:

1. **Implement retention policy**:
   ```python
   class CleanupManager:
       def cleanup_old_archives(
           self,
           max_age_days: int = 90,
           max_count: int = 1000
       ) -> list:
           """Delete archived memories older than max_age_days."""
           cutoff = datetime.now() - timedelta(days=max_age_days)

           deleted = []
           for archive_path in self.store.archive_dir.glob("*.md"):
               modified_time = datetime.fromtimestamp(
                   archive_path.stat().st_mtime
               )

               if modified_time < cutoff:
                   archive_path.unlink()
                   deleted.append(archive_path.stem)

           return deleted
   ```

2. **Add configuration**:
   ```yaml
   # .specify/config.yml
   memory:
     archive:
       retention_days: 90  # Keep archives for 90 days
       max_size_mb: 100    # Max archive directory size
       auto_cleanup: true  # Enable automatic cleanup
   ```

3. **Provide cleanup command**:
   ```bash
   specify memory cleanup --older-than 90d --dry-run
   specify memory cleanup --older-than 90d --confirm
   ```

**Acceptance Criteria for Fix**:
- [ ] Cleanup manager implements retention policy
- [ ] Configuration option for retention period
- [ ] CLI command for manual cleanup
- [ ] Automated cleanup option (configurable)

---

### LOW-003: No Input Size Limits

**Risk**: Low
**Component**: TaskMemoryStore.append()

**Description**:
No limits on content size when appending to memories. This could enable:
- Denial of service (extremely large files)
- Accidental resource exhaustion
- Performance degradation

**Current Behavior**:
```python
def append(self, task_id: str, content: str) -> None:
    """Append content (no size validation)."""
    existing = self.read(task_id)
    updated = existing + "\n" + content
    memory_path.write_text(updated)  # No size check
```

**Attack Scenarios**:
1. Malicious append of 1GB string → disk full
2. Accidental paste of large log file → memory unusable
3. Repeated appends creating 100MB file → performance issues

**Impact**:
- Disk space exhaustion
- Performance degradation
- Out-of-memory errors when reading

**Recommendations**:

1. **Implement size limits**:
   ```python
   MAX_MEMORY_SIZE = 1 * 1024 * 1024  # 1MB per memory file
   MAX_APPEND_SIZE = 100 * 1024        # 100KB per append

   def append(self, task_id: str, content: str) -> None:
       """Append with size validation."""
       if len(content) > MAX_APPEND_SIZE:
           raise ValueError(
               f"Content too large: {len(content)} bytes "
               f"(max {MAX_APPEND_SIZE})"
           )

       existing = self.read(task_id)
       updated = existing + "\n" + content

       if len(updated) > MAX_MEMORY_SIZE:
           raise ValueError(
               f"Memory file would exceed size limit: "
               f"{len(updated)} bytes (max {MAX_MEMORY_SIZE})"
           )

       memory_path.write_text(updated)
   ```

2. **Add configuration**:
   ```python
   # Allow users to configure limits
   class TaskMemoryStore:
       def __init__(
           self,
           base_path: Optional[Path] = None,
           max_memory_size: int = 1024 * 1024,
           max_append_size: int = 100 * 1024
       ):
           self.max_memory_size = max_memory_size
           self.max_append_size = max_append_size
   ```

3. **Provide warnings**:
   ```python
   WARN_THRESHOLD = 0.8 * MAX_MEMORY_SIZE

   if len(updated) > WARN_THRESHOLD:
       logger.warning(
           f"Memory file {task_id} is {len(updated)} bytes "
           f"({len(updated)/MAX_MEMORY_SIZE*100:.1f}% of limit)"
       )
   ```

**Acceptance Criteria for Fix**:
- [ ] Size limits implemented
- [ ] Configurable limits
- [ ] Clear error messages
- [ ] Tests for size limit enforcement

---

### INFO-001: Template Injection Not Applicable

**Risk**: Informational
**Component**: Template substitution

**Observation**:
Template substitution uses simple string replacement, not a template engine:

```python
content = template_content
for key, value in variables.items():
    placeholder = f"{{{key}}}"
    content = content.replace(placeholder, str(value))
```

**Analysis**:
- No Jinja2, Mako, or other template engine used
- No expression evaluation
- No code execution possible
- Simple string replacement only

**Conclusion**: Template injection is not a risk with current implementation.

**Recommendation**: If template engine is added in future, use sandboxed environment.

---

### INFO-002: Git Commit Safety

**Risk**: Informational
**Component**: Git integration

**Observation**:
Memory files are automatically committed with task state changes. This raises questions about:
- Commit signing
- GPG signatures
- Commit message security

**Analysis**:
This is outside the scope of the Task Memory system. Git security is the responsibility of:
- User's git configuration
- Repository settings (signed commits, branch protection)
- CI/CD pipeline security

**Recommendation**: Document git security best practices in user guide.

---

## Input Validation Summary

### Current Validation State

| Input | Validation | Status | Risk |
|-------|------------|--------|------|
| Task ID | None | ❌ VULNERABLE | MEDIUM |
| Task Title | Basic (string) | ⚠️ PARTIAL | LOW |
| Content | None | ⚠️ PARTIAL | LOW |
| Template Name | File existence check | ✅ ADEQUATE | LOW |
| File Paths | None | ❌ VULNERABLE | MEDIUM |

### Required Validation

```python
def validate_task_id(task_id: str) -> None:
    """Comprehensive task ID validation."""
    # 1. Non-empty check
    if not task_id or not task_id.strip():
        raise ValueError("Task ID cannot be empty")

    # 2. Length check
    if len(task_id) > 100:
        raise ValueError("Task ID too long (max 100 characters)")

    # 3. Format check
    pattern = re.compile(r'^task-\d+(-[a-z0-9-]+)?$')
    if not pattern.match(task_id):
        raise ValueError(
            f"Invalid task ID format: {task_id}. "
            "Expected: task-<number>[-optional-name]"
        )

    # 4. Path traversal check
    dangerous_chars = ["..", "/", "\\", "\0", "\n", "\r"]
    if any(char in task_id for char in dangerous_chars):
        raise ValueError(f"Task ID contains dangerous characters: {task_id}")

def validate_content(content: str, max_size: int = 100 * 1024) -> None:
    """Validate content before appending."""
    if len(content) > max_size:
        raise ValueError(
            f"Content too large: {len(content)} bytes (max {max_size})"
        )

    # Optional: Check for null bytes
    if "\0" in content:
        raise ValueError("Content contains null bytes")

def validate_template_name(template: str) -> None:
    """Validate template name."""
    # Only allow alphanumeric and hyphen
    if not re.match(r'^[a-z0-9-]+$', template):
        raise ValueError(f"Invalid template name: {template}")

    # Check for path traversal
    if ".." in template or "/" in template:
        raise ValueError(f"Template name contains path traversal: {template}")
```

---

## File Path Security

### Current Implementation

```python
def get_path(self, task_id: str) -> Path:
    return self.memory_dir / f"{task_id}.md"
```

### Secure Implementation

```python
def get_path(self, task_id: str) -> Path:
    """Get path with security checks."""
    # 1. Validate task ID
    validate_task_id(task_id)

    # 2. Construct path
    memory_path = self.memory_dir / f"{task_id}.md"

    # 3. Resolve and verify within bounds
    resolved = memory_path.resolve()
    base_resolved = self.memory_dir.resolve()

    # 4. Check path is within memory directory
    try:
        resolved.relative_to(base_resolved)
    except ValueError:
        raise SecurityError(
            f"Path traversal detected: {task_id} resolves outside memory directory"
        )

    return memory_path
```

### Additional Protections

```python
def _check_symlink(self, path: Path) -> None:
    """Prevent symlink attacks."""
    if path.is_symlink():
        target = path.readlink()
        if not target.is_relative_to(self.memory_dir):
            raise SecurityError(f"Symlink points outside memory directory: {path}")

def _check_permissions(self, path: Path) -> None:
    """Verify file permissions are secure."""
    stat_info = path.stat()
    mode = stat_info.st_mode

    # Check world-readable
    if mode & 0o004:
        logger.warning(f"File is world-readable: {path}")

    # Check world-writable
    if mode & 0o002:
        raise SecurityError(f"File is world-writable: {path}")
```

---

## Archive/Delete Safety

### Safe Deletion Pattern

```python
def delete(self, task_id: str, confirm: bool = False) -> None:
    """Safely delete memory file."""
    memory_path = self.get_path(task_id)

    # 1. Verify file exists and is a file (not directory)
    if not memory_path.exists():
        raise FileNotFoundError(f"Memory not found: {task_id}")

    if not memory_path.is_file():
        raise ValueError(f"Not a file: {memory_path}")

    # 2. Require explicit confirmation for safety
    if not confirm:
        raise ValueError(
            "Delete requires explicit confirmation. Set confirm=True"
        )

    # 3. Create backup before delete (optional)
    if self.create_backup_on_delete:
        backup_path = memory_path.with_suffix('.md.bak')
        shutil.copy2(memory_path, backup_path)

    # 4. Delete file
    memory_path.unlink()

    # 5. Log deletion
    logger.info(f"Deleted memory: {task_id}")
```

### Archive Safety

```python
def archive(self, task_id: str) -> Path:
    """Safely archive memory file."""
    memory_path = self.get_path(task_id)
    archive_path = self.archive_dir / f"{task_id}.md"

    # 1. Verify source exists
    if not memory_path.exists():
        raise FileNotFoundError(f"Memory not found: {task_id}")

    # 2. Check if archive already exists
    if archive_path.exists():
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = self.archive_dir / f"{task_id}.{timestamp}.md"

    # 3. Move file (atomic on same filesystem)
    shutil.move(str(memory_path), str(archive_path))

    # 4. Verify archive created
    if not archive_path.exists():
        raise RuntimeError(f"Archive failed: {archive_path}")

    return archive_path
```

---

## Security Best Practices for Users

### Developer Guidelines

1. **Never commit secrets**: Use environment variables or secret vaults
2. **Review before commit**: Check memory files for sensitive data
3. **Use .gitignore**: Consider excluding memory files if they contain sensitive data
4. **Encrypt if needed**: Use git-crypt or git-secret for sensitive projects
5. **Regular cleanup**: Archive old memories to reduce attack surface

### Example .gitignore

```gitignore
# Option 1: Exclude all memory files
backlog/memory/*.md
!backlog/memory/active-tasks.md

# Option 2: Include only specific memories
backlog/memory/*
!backlog/memory/task-public-*.md
```

### Pre-commit Hook Example

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Scan memory files for secrets
if command -v detect-secrets &> /dev/null; then
    detect-secrets scan backlog/memory/*.md
    if [ $? -ne 0 ]; then
        echo "ERROR: Secrets detected in memory files"
        echo "Remove secrets before committing"
        exit 1
    fi
fi

# Scan for common patterns
if grep -r "sk_live_\|AIza\|AKIA\|password.*=" backlog/memory/*.md; then
    echo "ERROR: Potential secrets detected in memory files"
    exit 1
fi
```

---

## Security Checklist for Implementation

### Immediate (Pre-Release)

- [ ] **CRITICAL**: Implement task ID validation (MEDIUM-002)
- [ ] **CRITICAL**: Add path traversal protection (MEDIUM-002)
- [ ] **HIGH**: Add secrets warning to template (MEDIUM-001)
- [ ] **HIGH**: Implement file size limits (LOW-003)
- [ ] Document security best practices

### Short-term (v1.1)

- [ ] Implement secret scanning hook (MEDIUM-001)
- [ ] Add file permission restrictions (LOW-001)
- [ ] Create cleanup retention policy (LOW-002)
- [ ] Add security tests for all findings

### Long-term (v2.0)

- [ ] Optional encryption support
- [ ] Audit logging for sensitive operations
- [ ] Integration with secret detection services
- [ ] Compliance features (GDPR, retention policies)

---

## Security Testing Recommendations

### Test Cases Required

```python
# Test path traversal protection
def test_path_traversal_attack():
    """Test that path traversal is prevented."""
    malicious_ids = [
        "../../../etc/passwd",
        "task-1/../../../secrets",
        "task-1/.git/config",
        "task-1\0bad",
    ]

    for task_id in malicious_ids:
        with pytest.raises(ValueError):
            store.create(task_id)

# Test secret detection
def test_secret_detection():
    """Test that secrets are detected in content."""
    secrets = [
        "sk_live_abcdef123456",
        "AIzaSyD1234567890",
        "AKIAIOSFODNN7EXAMPLE",
        "password=SuperSecret123",
    ]

    for secret in secrets:
        with pytest.raises(ValueError):
            store.append("task-1", f"Config: {secret}")

# Test size limits
def test_size_limits():
    """Test that size limits are enforced."""
    large_content = "x" * (2 * 1024 * 1024)  # 2MB

    with pytest.raises(ValueError, match="too large"):
        store.append("task-1", large_content)

# Test file permissions
def test_file_permissions():
    """Test that files have secure permissions."""
    store.create("task-1", task_title="Test")
    path = store.get_path("task-1")

    import os
    stat_info = os.stat(path)
    mode = stat_info.st_mode & 0o777

    # Should be 0600 (user read/write only)
    assert mode == 0o600, f"Insecure permissions: {oct(mode)}"
```

---

## Compliance Considerations

### Data Privacy

- **GDPR**: Memory files may contain personal data
  - Implement right to erasure (delete memories)
  - Add retention policies
  - Document data processing

- **CCPA**: Similar requirements for California users

### Data Retention

- Implement configurable retention periods
- Automated cleanup of old archives
- Audit trail for deletions

### Secure Development Lifecycle

- Security review before each release
- Automated security testing in CI/CD
- Dependency scanning (no 3rd party deps currently)
- Regular security audits

---

## Conclusion

The Task Memory system has a **LOW overall security risk** for typical usage in trusted development environments. However, two **MEDIUM** severity issues should be addressed before production release:

1. **Secrets exposure** (MEDIUM-001): Add warnings and optional scanning
2. **Path traversal** (MEDIUM-002): Implement strict validation

Additional **LOW** severity improvements will enhance security posture for shared environments and long-term usage.

## Recommended Actions

**Before v1.0 Release**:
1. Implement task ID validation and path security (MEDIUM-002)
2. Add secrets warning to template (MEDIUM-001)
3. Document security best practices
4. Add security tests

**Post-Release**:
1. Implement secret scanning hook
2. Add file permission restrictions
3. Create retention policy
4. Consider encryption option

---

**Review Status**: APPROVED WITH RECOMMENDATIONS
**Next Review**: After implementing MEDIUM-severity fixes
**Reviewer Signature**: QA Engineer Team
**Date**: 2025-12-09
