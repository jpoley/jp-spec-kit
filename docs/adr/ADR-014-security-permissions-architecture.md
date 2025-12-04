# ADR-014: Security Permissions Architecture

**Status:** Proposed
**Date:** 2025-12-04
**Author:** Platform Engineer
**Context:** task-184 - Configure permissions.deny security rules
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

Claude Code has powerful file manipulation capabilities that, if misused, can:
- **Expose secrets** - Read/write .env files, API keys, credentials
- **Corrupt critical files** - Overwrite CLAUDE.md, constitution.md, lock files
- **Execute dangerous commands** - `sudo rm -rf /`, `chmod 777`, privilege escalation
- **Violate compliance** - Unintentional access to PII/PHI data

**The Core Tension:** Claude Code needs broad file access to be productive, but unconstrained access creates security risks.

### Business Value

**Primary Value Streams:**

1. **Security** - Prevent accidental secret exposure and dangerous operations
2. **Compliance** - Meet security requirements for NIST/SSDF, SOC 2
3. **Reliability** - Protect critical configuration from corruption
4. **Trust** - Users can run Claude Code without fear of system damage

**Success Metrics:**

- Zero secret exposure incidents
- Zero critical file corruption incidents
- Security audit compliance score >90%
- User trust: "I feel safe using Claude Code" (NPS >50)

---

## Decision

### Chosen Architecture: Defense-in-Depth with Layered Permissions

Implement **permissions.deny** rules in `.claude/settings.json` using a layered approach:

1. **Layer 1: Secret Protection** - Block access to sensitive files (.env, secrets/, credentials)
2. **Layer 2: Critical File Protection** - Prevent writes to constitution, CLAUDE.md, lock files
3. **Layer 3: Dangerous Command Blocking** - Prevent execution of privilege escalation commands
4. **Layer 4: Pattern-Based Blocking** - Block known dangerous patterns (rm -rf, chmod 777)

**Key Pattern:** **Defense in Depth (Security Pattern)** + **Least Privilege Principle**

```
┌─────────────────────────────────────────────────────────────────┐
│                   PERMISSIONS ARCHITECTURE                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Layer 1: Secret Protection                         │        │
│  │ - Block .env, .env.*                               │        │
│  │ - Block secrets/, credentials/, .ssh/             │        │
│  │ - Block API key patterns                           │        │
│  └─────────────────────────────────────────────────────┘        │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Layer 2: Critical File Protection                  │        │
│  │ - Read-only: CLAUDE.md, constitution.md           │        │
│  │ - Read-only: Lock files (uv.lock, package-lock)   │        │
│  │ - Read-only: .git/ directory                       │        │
│  └─────────────────────────────────────────────────────┘        │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Layer 3: Dangerous Command Blocking                │        │
│  │ - Block: sudo, su, chmod 777                       │        │
│  │ - Block: rm -rf /, dd, mkfs                        │        │
│  │ - Block: curl | bash, wget | sh                    │        │
│  └─────────────────────────────────────────────────────┘        │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Layer 4: Pattern-Based Blocking                    │        │
│  │ - Regex patterns for API keys (AWS, GitHub, etc.)  │        │
│  │ - File path patterns (private keys, certificates) │        │
│  └─────────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Engine Room View: Technical Architecture

### Configuration Schema

**File:** `.claude/settings.json`

```json
{
  "permissions": {
    "deny": {
      "files": {
        "read": [
          ".env",
          ".env.*",
          "**/.env",
          "**/.env.*",
          "**/secrets/**",
          "**/credentials/**",
          "**/.ssh/**",
          "**/*.pem",
          "**/*.key",
          "**/id_rsa*",
          "**/.aws/credentials",
          "**/.gcp/credentials.json"
        ],
        "write": [
          ".env",
          ".env.*",
          "**/.env",
          "**/.env.*",
          "**/secrets/**",
          "**/credentials/**",
          "CLAUDE.md",
          "**/CLAUDE.md",
          "memory/constitution.md",
          "**/constitution.md",
          "uv.lock",
          "package-lock.json",
          "yarn.lock",
          "poetry.lock",
          "Gemfile.lock",
          ".git/**",
          "**/.git/**"
        ]
      },
      "commands": {
        "patterns": [
          "sudo *",
          "su *",
          "rm -rf /*",
          "rm -rf ~/*",
          "chmod 777 *",
          "chmod -R 777 *",
          "dd if=*",
          "mkfs.*",
          "> /dev/sd*",
          "curl * | bash",
          "curl * | sh",
          "wget * | bash",
          "wget * | sh",
          "curl -s * | sudo *",
          "systemctl *",
          "service *",
          "iptables *",
          "firewall-cmd *"
        ]
      },
      "content_patterns": {
        "description": "Block files containing sensitive patterns",
        "patterns": [
          "-----BEGIN PRIVATE KEY-----",
          "-----BEGIN RSA PRIVATE KEY-----",
          "AKIA[0-9A-Z]{16}",
          "ghp_[a-zA-Z0-9]{36}",
          "glpat-[a-zA-Z0-9_-]{20,}",
          "password\\s*=\\s*['\"](?!test|example)[^'\"]{8,}",
          "api[_-]?key\\s*=\\s*['\"][^'\"]{20,}"
        ]
      }
    },
    "allow": {
      "description": "Exceptions to deny rules",
      "files": {
        "read": [
          ".env.example",
          ".env.template",
          "docs/examples/**/.env"
        ],
        "write": [
          "tests/**/.env.test",
          ".env.test"
        ]
      }
    }
  },
  "security": {
    "audit_mode": false,
    "log_denied_operations": true,
    "notification_on_deny": true,
    "emergency_override": {
      "enabled": false,
      "requires_confirmation": true
    }
  }
}
```

### Permission Evaluation Logic

**Pseudo-code for permission checking:**

```python
def check_permission(operation: str, path: str, content: str = None) -> PermissionResult:
    """Check if operation is allowed based on permissions.deny rules.

    Args:
        operation: "read" | "write" | "execute"
        path: File path or command
        content: Optional file content for pattern matching

    Returns:
        PermissionResult with allowed status and reason.
    """
    # 1. Check explicit deny rules
    if operation in ["read", "write"]:
        for pattern in get_deny_patterns(operation):
            if matches_glob(path, pattern):
                return PermissionResult(
                    allowed=False,
                    reason=f"Denied by pattern: {pattern}",
                    category="file_protection"
                )

    # 2. Check command patterns (for execute)
    if operation == "execute":
        for pattern in get_command_deny_patterns():
            if matches_command_pattern(path, pattern):
                return PermissionResult(
                    allowed=False,
                    reason=f"Dangerous command blocked: {pattern}",
                    category="command_protection"
                )

    # 3. Check content patterns
    if content:
        for pattern in get_content_deny_patterns():
            if matches_regex(content, pattern):
                return PermissionResult(
                    allowed=False,
                    reason=f"Sensitive content detected: {pattern}",
                    category="content_protection"
                )

    # 4. Check allow exceptions
    for pattern in get_allow_patterns(operation):
        if matches_glob(path, pattern):
            return PermissionResult(
                allowed=True,
                reason=f"Allowed by exception: {pattern}",
                category="exception"
            )

    # 5. Default allow (fail-open for usability)
    return PermissionResult(
        allowed=True,
        reason="No deny rule matched",
        category="default_allow"
    )
```

### Audit Logging

**Format:** JSON lines in `.claude/audit.log`

```json
{"timestamp": "2025-12-04T10:15:30Z", "operation": "write", "path": ".env", "result": "denied", "reason": "Denied by pattern: **/.env", "category": "file_protection"}
{"timestamp": "2025-12-04T10:16:00Z", "operation": "execute", "command": "sudo apt install", "result": "denied", "reason": "Dangerous command blocked: sudo *", "category": "command_protection"}
{"timestamp": "2025-12-04T10:17:00Z", "operation": "read", "path": "src/config.py", "result": "allowed", "reason": "No deny rule matched", "category": "default_allow"}
```

### User Notification

**Format:** Interactive prompt on denied operation

```
⚠️  PERMISSION DENIED ⚠️

Operation: Write to .env
Reason: Sensitive file protection (.env files contain secrets)
Category: file_protection

Why this is blocked:
- .env files typically contain API keys, passwords, and secrets
- Accidental writes could expose credentials
- Use .env.example for documentation instead

Options:
1. Cancel operation (recommended)
2. Override (requires confirmation)
3. Add exception to .claude/settings.json

[C]ancel / [O]verride / [E]xception: _
```

---

## Layer-by-Layer Design

### Layer 1: Secret Protection

**Purpose:** Prevent accidental exposure of credentials and API keys.

**Protected Patterns:**
- `.env`, `.env.*` (environment variables)
- `secrets/`, `credentials/` (secret directories)
- `.ssh/`, `*.pem`, `*.key`, `id_rsa*` (SSH keys)
- `.aws/credentials`, `.gcp/credentials.json` (cloud credentials)
- Content patterns: `AKIA*` (AWS), `ghp_*` (GitHub), `glpat-*` (GitLab)

**Exception Handling:**
- Allow read/write for `.env.example`, `.env.template` (documentation)
- Allow write for `tests/**/.env.test` (test fixtures)

**Implementation Notes:**
- Use glob patterns for broad coverage (`**/.env` matches all directories)
- Content scanning for accidental secret commits (pre-commit hook integration)

### Layer 2: Critical File Protection

**Purpose:** Prevent corruption of configuration and dependency files.

**Protected Patterns (Write-only):**
- `CLAUDE.md`, `constitution.md` (project documentation)
- `uv.lock`, `package-lock.json`, `yarn.lock`, `poetry.lock` (dependency locks)
- `.git/**` (Git metadata)

**Rationale:**
- Lock files should only be modified by package managers
- Constitution changes require human review
- Git metadata corruption breaks version control

**Implementation Notes:**
- Read is allowed (Claude needs context)
- Write is blocked (prevents accidental corruption)
- Override available for legitimate updates (with confirmation)

### Layer 3: Dangerous Command Blocking

**Purpose:** Prevent execution of privilege escalation and destructive commands.

**Blocked Commands:**
- Privilege escalation: `sudo`, `su`, `systemctl`, `service`
- Destructive: `rm -rf /`, `dd if=`, `mkfs.*`, `> /dev/sd*`
- Permission changes: `chmod 777`, `chmod -R 777`
- Remote execution: `curl | bash`, `wget | sh`
- Firewall changes: `iptables`, `firewall-cmd`

**Exception Handling:**
- Allow non-destructive sudo (e.g., `sudo apt update` in controlled contexts)
- Require explicit confirmation for overrides

**Implementation Notes:**
- Pattern matching with wildcards (`sudo *` matches all sudo commands)
- Whitelist approach for safe commands (future enhancement)

### Layer 4: Pattern-Based Blocking

**Purpose:** Detect and block sensitive content patterns.

**Content Patterns:**
- Private keys: `-----BEGIN PRIVATE KEY-----`, `-----BEGIN RSA PRIVATE KEY-----`
- AWS keys: `AKIA[0-9A-Z]{16}`
- GitHub tokens: `ghp_[a-zA-Z0-9]{36}`
- GitLab tokens: `glpat-[a-zA-Z0-9_-]{20,}`
- Passwords: `password = "..."`
- API keys: `api_key = "..."`

**Exception Handling:**
- Exclude test/example values (e.g., `password = "test"`)
- Allow patterns in documentation (`docs/examples/**`)

**Implementation Notes:**
- Regex-based matching for flexible detection
- Balance false positives (too restrictive) vs false negatives (missed secrets)

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 10/10

**Strengths:**
- Four distinct layers with clear purposes
- Explicit deny rules (no implicit behavior)
- Clear exception handling (allow overrides)

### 2. Consistency - 9/10

**Strengths:**
- All layers use same glob/regex pattern format
- Consistent audit logging across layers
- Uniform user notification

**Improvement:**
- Standardize exception syntax across layers

### 3. Composability - 8/10

**Strengths:**
- Layers are independent (can enable/disable individually)
- Patterns can be added without code changes

**Needs Work:**
- Custom rules require JSON editing (no CLI yet)

### 4. Consumption (Developer Experience) - 9/10

**Strengths:**
- Clear error messages explaining why operation was blocked
- Override option for legitimate use cases
- Audit log for security review

**Needs Work:**
- First-time setup guidance (example configurations)
- CLI for managing permissions (`specify permissions add`)

### 5. Correctness (Validation) - 9/10

**Strengths:**
- Defense-in-depth prevents single point of failure
- Audit logging enables post-incident review
- Pattern testing (unit tests for glob/regex)

**Risks:**
- False positives (legitimate operations blocked)
- False negatives (new secret patterns not caught)

### 6. Completeness - 8/10

**Covers:**
- File read/write protection
- Command execution blocking
- Content pattern detection
- Audit logging and notifications

**Missing (Future):**
- Network access restrictions (external API calls)
- Process isolation (sandboxing)
- Time-based restrictions (no operations after hours)

### 7. Changeability - 10/10

**Strengths:**
- Add new patterns: edit JSON, no code changes
- Add new layers: extend schema, backward compatible
- Change enforcement policy: modify settings, no restart

---

## Alternatives Considered and Rejected

### Option A: No Permissions (Trust Model)

**Approach:** Trust Claude Code completely, no restrictions.

**Pros:**
- Simplest implementation (no code)
- Maximum flexibility

**Cons:**
- High security risk (accidental exposure)
- No compliance (fails security audits)
- No recourse after incidents

**Rejected:** Unacceptable risk for production use

---

### Option B: Sandboxed Execution (Container Isolation)

**Approach:** Run Claude Code in isolated container with minimal permissions.

**Pros:**
- Strongest security (kernel-level isolation)
- Proven technology (Docker, Podman)

**Cons:**
- Requires container runtime (not available everywhere)
- Poor developer experience (container overhead)
- Limited file access (defeats purpose)

**Rejected:** Over-engineered for CLI tool

---

### Option C: Defense-in-Depth with Layered Permissions (RECOMMENDED)

**Approach:** Multiple permission layers with deny rules and exceptions.

**Pros:**
- Balance security and usability
- Clear audit trail
- Configurable (adjust for environment)
- No external dependencies

**Cons:**
- More complex than Option A
- Requires maintenance (update patterns)

**Accepted:** Best balance of security and developer experience

---

## Implementation Guidance

### Phase 1: Core Permissions (Week 1)

**Scope:** Layer 1 (Secret Protection) + Layer 2 (Critical File Protection)

**Tasks:**
- Define JSON schema for permissions.deny
- Implement glob pattern matching
- Implement file read/write checks
- Add .env and CLAUDE.md protection
- Unit tests for pattern matching

### Phase 2: Command Blocking (Week 2)

**Scope:** Layer 3 (Dangerous Command Blocking)

**Tasks:**
- Implement command pattern matching
- Add sudo, rm -rf blocking
- Add curl | bash blocking
- Integration tests with real commands

### Phase 3: Content Scanning (Week 3)

**Scope:** Layer 4 (Pattern-Based Blocking) + Audit Logging

**Tasks:**
- Implement regex content scanning
- Add API key detection patterns
- Implement audit logging
- Implement user notification system
- Documentation and examples

---

## Risks and Mitigations

### Risk 1: False Positives (Legitimate Operations Blocked)

**Likelihood:** Medium
**Impact:** Medium (frustration, workarounds)

**Mitigation:**
- Provide clear override mechanism
- Add common exceptions to allow list
- User feedback loop (refine patterns based on complaints)
- Audit log review (identify frequently blocked legitimate operations)

### Risk 2: False Negatives (Secrets Still Exposed)

**Likelihood:** Medium
**Impact:** High (security incident)

**Mitigation:**
- Defense-in-depth (multiple layers)
- Regular pattern updates (new API key formats)
- Pre-commit hooks (backup detection)
- Security scanning (Semgrep, CodeQL)

### Risk 3: Performance Degradation (Content Scanning Overhead)

**Likelihood:** Low
**Impact:** Medium (slow operations)

**Mitigation:**
- Lazy evaluation (only scan when deny rule matches path)
- Regex optimization (compiled patterns)
- File size limits (skip scanning >10MB files)
- Caching (cache scan results for unchanged files)

---

## Success Criteria

**Objective Measures:**

1. **Zero Secret Exposure** - No .env or credentials leaked
2. **Zero Critical File Corruption** - No CLAUDE.md or lock file corruption
3. **Audit Compliance** - >90% security audit score
4. **False Positive Rate** - <5% (legitimate operations blocked)

**Subjective Measures:**

1. **User Trust** - "I feel safe using Claude Code" (NPS >50)
2. **Security Team Approval** - "Permissions are adequate" (thumbs up)

---

## Decision

**APPROVED for implementation as Option C: Defense-in-Depth with Layered Permissions**

**Next Steps:**

1. Create implementation task for Phase 1 (Secret + Critical File Protection)
2. Draft .claude/settings.json template
3. Begin development (permission checker module)

**Review Date:** 2025-12-18 (after Phase 1 complete)

---

## References

### Security Principles Applied

1. **Defense in Depth** - Multiple layers of protection
2. **Least Privilege** - Default deny with explicit allow
3. **Fail-Safe Defaults** - Deny on misconfiguration
4. **Complete Mediation** - Check every operation

### Related Documents

- **Task:** task-184 - Add permissions.deny Security Rules to settings.json
- **Related Docs:** docs/prd/claude-capabilities-review.md (Section 2.5)

### External References

- [OWASP Access Control](https://owasp.org/www-community/Access_Control)
- [NIST SSDF](https://csrc.nist.gov/projects/ssdf)
- [CIS Controls](https://www.cisecurity.org/controls)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
