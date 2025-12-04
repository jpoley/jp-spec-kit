# Security Architecture - Defense-in-Depth Permissions

**Date:** 2025-12-04
**Related Tasks:** task-184, task-249
**Related ADRs:** ADR-014-security-permissions-architecture, ADR-013-tool-dependency-management

---

## Overview

JP Spec Kit implements a **defense-in-depth security architecture** using layered permissions to prevent accidental secret exposure, protect critical files, and block dangerous operations.

### Security Principles

1. **Defense in Depth** - Multiple layers of protection
2. **Least Privilege** - Default deny, explicit allow
3. **Fail-Safe Defaults** - Deny on misconfiguration
4. **Complete Mediation** - Check every operation

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│ SECURITY ARCHITECTURE (Defense-in-Depth)             │
│                                                      │
│  ┌────────────────────────────────────┐             │
│  │ Layer 1: Secret Protection         │             │
│  │ - Block .env, .env.*               │             │
│  │ - Block secrets/, credentials/     │             │
│  │ - Block .ssh/, *.pem, *.key        │             │
│  └────────────────────────────────────┘             │
│                   │                                  │
│  ┌────────────────▼───────────────────┐             │
│  │ Layer 2: Critical File Protection  │             │
│  │ - Read-only: CLAUDE.md             │             │
│  │ - Read-only: constitution.md       │             │
│  │ - Read-only: Lock files            │             │
│  └────────────────────────────────────┘             │
│                   │                                  │
│  ┌────────────────▼───────────────────┐             │
│  │ Layer 3: Dangerous Command Blocking│             │
│  │ - Block: sudo, rm -rf /            │             │
│  │ - Block: chmod 777, dd, mkfs       │             │
│  │ - Block: curl | bash               │             │
│  └────────────────────────────────────┘             │
│                   │                                  │
│  ┌────────────────▼───────────────────┐             │
│  │ Layer 4: Pattern-Based Blocking    │             │
│  │ - Regex: API keys (AWS, GitHub)    │             │
│  │ - Regex: Private keys, passwords   │             │
│  └────────────────────────────────────┘             │
│                   │                                  │
│  ┌────────────────▼───────────────────┐             │
│  │ Audit Logging                      │             │
│  │ - Log all denied operations        │             │
│  │ - JSON format for SIEM             │             │
│  │ - 30-day retention                 │             │
│  └────────────────────────────────────┘             │
└──────────────────────────────────────────────────────┘
```

---

## permissions.deny Configuration

**File:** `.claude/settings.json`

### Layer 1: Secret Protection

```json
{
  "permissions": {
    "deny": {
      "files": {
        "read": [
          ".env", ".env.*",
          "**/.env", "**/.env.*",
          "**/secrets/**",
          "**/credentials/**",
          "**/.ssh/**",
          "**/*.pem", "**/*.key",
          "**/id_rsa*",
          "**/.aws/credentials",
          "**/.gcp/credentials.json"
        ]
      }
    }
  }
}
```

**Protected:**
- Environment variables (.env files)
- Secret directories (secrets/, credentials/)
- SSH keys (.ssh/, *.pem, *.key, id_rsa*)
- Cloud credentials (AWS, GCP)

**Exceptions:**
```json
{
  "allow": {
    "files": {
      "read": [".env.example", ".env.template"]
    }
  }
}
```

### Layer 2: Critical File Protection

```json
{
  "permissions": {
    "deny": {
      "files": {
        "write": [
          "CLAUDE.md", "**/CLAUDE.md",
          "memory/constitution.md", "**/constitution.md",
          "uv.lock", "package-lock.json",
          "yarn.lock", "poetry.lock",
          ".git/**", "**/.git/**"
        ]
      }
    }
  }
}
```

**Protected:**
- Documentation (CLAUDE.md, constitution.md)
- Lock files (uv.lock, package-lock.json, etc.)
- Git metadata (.git/)

**Rationale:**
- Lock files modified by package managers only
- Constitution changes require human review
- Git corruption breaks version control

### Layer 3: Dangerous Command Blocking

```json
{
  "permissions": {
    "deny": {
      "commands": {
        "patterns": [
          "sudo *", "su *",
          "rm -rf /*", "rm -rf ~/*",
          "chmod 777 *", "chmod -R 777 *",
          "dd if=*", "mkfs.*",
          "> /dev/sd*",
          "curl * | bash", "curl * | sh",
          "wget * | bash", "wget * | sh",
          "systemctl *", "service *",
          "iptables *", "firewall-cmd *"
        ]
      }
    }
  }
}
```

**Blocked:**
- Privilege escalation (sudo, su, systemctl)
- Destructive (rm -rf /, dd, mkfs)
- Permission changes (chmod 777)
- Remote execution (curl | bash)
- Firewall changes (iptables)

### Layer 4: Content Pattern Blocking

```json
{
  "permissions": {
    "deny": {
      "content_patterns": {
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
    }
  }
}
```

**Detected:**
- Private keys (PEM format)
- AWS keys (AKIA...)
- GitHub tokens (ghp_...)
- GitLab tokens (glpat-...)
- Passwords (non-test values)
- API keys

---

## Audit Logging

**File:** `.claude/audit.log` (JSON lines)

**Format:**
```json
{"timestamp": "2025-12-04T10:15:30Z", "operation": "write", "path": ".env", "result": "denied", "reason": "Denied by pattern: **/.env", "category": "file_protection"}
{"timestamp": "2025-12-04T10:16:00Z", "operation": "execute", "command": "sudo apt install", "result": "denied", "reason": "Dangerous command blocked: sudo *", "category": "command_protection"}
```

**Fields:**
- timestamp: ISO 8601
- operation: read, write, execute
- path/command: Target of operation
- result: denied, allowed
- reason: Why denied/allowed
- category: file_protection, command_protection, etc.

**Retention:** 30 days

**SIEM Integration:** JSON format for easy parsing

---

## User Notification

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

## Tool Dependency Security

**Related:** ADR-013-tool-dependency-management-architecture

### SLSA Level 2 Compliance

**Requirements:**
1. **Build Integrity** - Tool version pinning
2. **Provenance** - Track tool source and version
3. **Isolation** - Permission boundaries

**Implementation:**
- versions.lock.json tracks all tool versions
- Integrity hashes (SHA256) for downloads
- Tool cache isolated in ~/.specify/tools/

### Tool Installation Security

**Semgrep (pip):**
```python
# Version pinning
package = "semgrep==1.95.0"

# Integrity check
pip install --require-hashes semgrep==1.95.0 \
  --hash sha256:abc123...
```

**CodeQL (binary):**
```bash
# Download from GitHub releases
url="https://github.com/github/codeql-cli-binaries/releases/download/v2.15.5/codeql-linux.tar.gz"

# Verify integrity
sha256sum -c codeql.sha256

# License check (proprietary)
if ! accept_license; then
  exit 1
fi
```

---

## Compliance Alignment

### NIST SSDF

- **PW.1.1:** Secure development environment ✓
- **PW.4.4:** Software integrity verification ✓
- **PW.7.1:** Vulnerability detection ✓
- **PW.8.1:** Audit logging ✓

### SLSA Level 2

- **Build Integrity:** Version pinning ✓
- **Provenance:** Tool source tracking ✓
- **Isolation:** Permission boundaries ✓

### SOC 2 (Type II)

- **Access Control:** Permissions deny rules ✓
- **Monitoring:** Audit logging ✓
- **Change Management:** Git workflow, PR reviews ✓

---

## Risk Assessment

### High Impact Risks

**Risk 1: False Positives**
- **Impact:** Blocks legitimate operations
- **Mitigation:** Clear override, user feedback loop
- **Metric:** <5% false positive rate

**Risk 2: False Negatives**
- **Impact:** Secrets still exposed
- **Mitigation:** Multiple layers, pattern updates
- **Metric:** Zero secret exposures

### Medium Impact Risks

**Risk 3: Performance Overhead**
- **Impact:** Slow operations (content scanning)
- **Mitigation:** Lazy evaluation, regex optimization
- **Metric:** <50ms overhead per operation

---

## Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Secret Exposure | Zero | Incidents per month |
| Critical File Corruption | Zero | Incidents per month |
| False Positive Rate | <5% | Legitimate ops blocked |
| Audit Compliance | >90% | Security audit score |
| User Trust | NPS >50 | "I feel safe using Claude Code" |

---

## Implementation Phases

### Phase 1: Secret Protection (Week 1)
- Implement Layer 1 (secret files)
- Implement Layer 2 (critical files)
- Test with .env, CLAUDE.md

### Phase 2: Command Blocking (Week 2)
- Implement Layer 3 (dangerous commands)
- Test with sudo, rm -rf

### Phase 3: Content Scanning (Week 3)
- Implement Layer 4 (patterns)
- Add audit logging
- User notification system

---

## Conclusion

The security architecture provides defense-in-depth protection against:
- Accidental secret exposure (Layer 1)
- Critical file corruption (Layer 2)
- Dangerous operations (Layer 3)
- Content-based threats (Layer 4)

**Next Steps:**
1. Implement permissions.deny in .claude/settings.json
2. Test with real workflows
3. Refine patterns based on feedback
