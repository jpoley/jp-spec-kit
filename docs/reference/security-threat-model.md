# Security Threat Model and Limitations

This document describes the threat model, security boundaries, and known limitations of the `/flow:security` scanning system.

## Scope

### What `/flow:security` Protects Against

| Category | Coverage | Tools |
|----------|----------|-------|
| **SAST vulnerabilities** | High | Semgrep, CodeQL, Bandit |
| **OWASP Top 10** | High | All scanners |
| **Hardcoded secrets** | High | Semgrep, custom rules |
| **Dependency vulnerabilities** | Medium | Trivy (containers) |
| **Configuration issues** | Medium | Custom rules |

### What `/flow:security` Does NOT Protect Against

| Category | Reason | Mitigation |
|----------|--------|------------|
| **Runtime vulnerabilities** | Static analysis only | Use DAST tools (Playwright, ZAP) |
| **Business logic flaws** | Requires domain knowledge | Manual code review |
| **Social engineering** | Non-code attack | Security training |
| **Infrastructure attacks** | Out of scope | Cloud security tools |
| **Zero-day exploits** | Unknown patterns | Keep rules updated |
| **Compiled binaries** | Source code analysis only | Binary analysis tools |

## Trust Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    TRUSTED BOUNDARY                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Local System                                           ││
│  │  - Source code (user's codebase)                       ││
│  │  - Scanner tools (Semgrep, Bandit)                     ││
│  │  - Configuration files (.specify/security.yml)         ││
│  │  - Scan results (local JSON files)                     ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  SEMI-TRUSTED BOUNDARY                       │
│  - AI API (Anthropic Claude) for triage                     │
│  - Semgrep Registry (rule downloads)                        │
│  - GitHub API (SARIF upload)                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    UNTRUSTED BOUNDARY                        │
│  - Third-party dependencies (scanned code)                  │
│  - External rule repositories                               │
│  - User-provided custom rules                               │
└─────────────────────────────────────────────────────────────┘
```

## Threat Analysis

### T1: Malicious Code Injection via Scan Results

**Threat**: Attacker crafts code that causes scanner to execute malicious commands.

**Likelihood**: Low
**Impact**: High

**Mitigations**:
- Scanners execute in subprocess with limited permissions
- Scan results are JSON/SARIF data only, not executed
- No shell interpolation of finding content

**Residual Risk**: Minimal - scanner tools themselves could be compromised

### T2: AI Prompt Injection via Code Comments

**Threat**: Attacker embeds prompt injection in code comments that influences AI triage decisions.

**Likelihood**: Medium
**Impact**: Medium (finding misclassified)

**Mitigations**:
- Code snippets are clearly delineated in prompts
- AI is instructed to analyze code structure, not follow instructions in code
- Human review required for critical findings

**Residual Risk**: AI may occasionally be influenced by cleverly crafted comments

### T3: False Negative from AI Triage

**Threat**: AI incorrectly classifies a true vulnerability as false positive.

**Likelihood**: Medium
**Impact**: High (vulnerability missed)

**Mitigations**:
- Conservative default: err toward true positive
- Confidence scores displayed for all classifications
- Interactive mode allows human override
- Critical/high severity findings require manual confirmation

**Residual Risk**: Some false negatives will occur; recommend periodic manual review

### T4: Sensitive Code Sent to AI API

**Threat**: Proprietary code snippets sent to external AI service.

**Likelihood**: High (by design for AI triage)
**Impact**: Varies (depends on code sensitivity)

**Mitigations**:
- Only relevant code snippets sent, not entire files
- Configurable: disable AI triage for sensitive projects
- See [Privacy Policy](./security-privacy-policy.md) for data handling

**Residual Risk**: Code snippets are shared with AI provider

### T5: Scanner Tool Supply Chain Attack

**Threat**: Compromised scanner tool (Semgrep, Bandit) delivers malicious code.

**Likelihood**: Low
**Impact**: Critical

**Mitigations**:
- Install tools from official sources only
- Verify tool checksums when possible
- Pin tool versions in CI/CD
- SLSA compliance for tool installation

**Residual Risk**: Supply chain attacks on scanner tools

### T6: Rule Manipulation

**Threat**: Attacker modifies custom rules to hide vulnerabilities.

**Likelihood**: Low
**Impact**: High

**Mitigations**:
- Custom rules stored in version control
- Rule changes visible in code review
- Use official rulesets as baseline

**Residual Risk**: Insider threat with commit access

### T7: Denial of Service via Scan

**Threat**: Malicious code causes scanner to hang or consume excessive resources.

**Likelihood**: Medium
**Impact**: Low (availability only)

**Mitigations**:
- Scan timeout configurable (default 5 minutes)
- Resource limits in CI/CD
- Incremental scans for large codebases

**Residual Risk**: Pathological inputs may slow scanning

## Known Limitations

### Static Analysis Limitations

1. **No runtime context**: Cannot detect issues that only manifest at runtime
2. **Limited data flow**: Complex data flows may not be tracked accurately
3. **Framework-specific**: Some frameworks require specialized rules
4. **Language support**: Not all languages equally supported

### AI Triage Limitations

1. **Accuracy**: Target 85%, meaning ~15% may be incorrect
2. **Novel vulnerabilities**: AI trained on known patterns
3. **Context understanding**: May miss business logic implications
4. **Consistency**: Same input may produce different outputs

### Fix Generation Limitations

1. **Syntax only**: Validates syntax, not semantic correctness
2. **Test coverage**: Generated fixes may not have tests
3. **Breaking changes**: Fixes may change API behavior
4. **Complex fixes**: Multi-file changes may be incomplete

### Coverage Gaps

| Scanner | Languages | Strengths | Weaknesses |
|---------|-----------|-----------|------------|
| Semgrep | Python, JS, Go, Java, Ruby | Pattern matching, speed | Limited data flow |
| CodeQL | Python, JS, Go, Java, C++ | Data flow, queries | Complex setup, slow |
| Bandit | Python only | Fast, security-focused | Python only |
| Trivy | Containers, IaC | Dependency scanning | Not SAST |

## Security Recommendations

### For High-Security Projects

1. **Enable manual review** for all critical/high findings
2. **Disable AI triage** if code confidentiality is critical
3. **Use multiple scanners** for defense in depth
4. **Pin scanner versions** to avoid supply chain attacks
5. **Review custom rules** in pull requests

### For CI/CD Integration

1. **Fail on critical only** to avoid alert fatigue
2. **Use incremental scans** in PRs for speed
3. **Full scans on main** for comprehensive coverage
4. **Store results** for trend analysis

### For Development Teams

1. **Review AI classifications** don't blindly trust
2. **Test generated fixes** before merging
3. **Update rules regularly** for new vulnerability patterns
4. **Report false positives** to improve accuracy

## Incident Response

### If a Vulnerability is Missed

1. Document the finding details
2. Identify why scanner/AI missed it
3. Create custom rule if pattern is detectable
4. Consider additional scanners

### If Sensitive Code is Exposed

1. Review AI API data retention policy
2. Rotate any secrets in exposed code
3. Consider disabling AI triage
4. Contact security team

## Security Updates

This threat model is reviewed and updated:
- Quarterly for routine updates
- Immediately when new threats are identified
- When major features are added

**Last Updated**: 2025-12-03
**Version**: 1.0

## Related Documentation

- [Privacy Policy](./security-privacy-policy.md) - AI data handling
- [Command Reference](./flowspec-security-commands.md) - CLI options
- [CI/CD Integration](../guides/security-cicd-integration.md) - Pipeline security
