# Security Audit Workflow Example

## Overview

This configuration adds enhanced security validation to the standard SDD workflow:

1. **Threat Modeling** - Pre-implementation security design review
2. **Security Audit** - Post-implementation comprehensive security verification
3. **Compliance Verification** - SOC2/HIPAA/GDPR compliance checks

## Use Cases

- Financial services applications (PCI-DSS)
- Healthcare systems (HIPAA)
- Government contracts (FedRAMP)
- Customer-facing applications with sensitive data
- SOC2/ISO27001 compliance requirements
- Applications handling PII/PHI
- Multi-tenant SaaS platforms

## Key Additions

### 1. Threat Modeled State

**When**: After Planning, before Implementation

**Purpose**: Identify security risks before writing code

**Agents**:
- **secure-by-design-engineer** - STRIDE threat modeling, attack surface analysis
- **compliance-officer** - Compliance requirement mapping, privacy impact assessment

**Approval Gate**: `KEYWORD[SECURITY_APPROVED]` - Human must approve before proceeding

**Artifacts Created**:
- `docs/security/{feature}-threat-model.md` - STRIDE analysis, threat scenarios
- `docs/security/{feature}-attack-surface.md` - Entry points, trust boundaries

### 2. Security Audited State

**When**: After Validation, before Deployment

**Purpose**: Verify security controls are implemented correctly

**Agents**:
- **secure-by-design-engineer** - Penetration testing, vulnerability assessment
- **compliance-officer** - SOC2/GDPR/HIPAA verification, audit trail validation

**Approval Gate**: `KEYWORD[AUDIT_PASSED]` - Human must approve before production

**Artifacts Created**:
- `docs/security/{feature}-audit-report.md` - Penetration test results, vulnerability status
- `docs/security/{feature}-compliance.md` - Compliance verification report

### 3. Compliance Officer Agent

**Custom Agent** for organization-specific compliance requirements

**Responsibilities**:
- SOC2 compliance verification
- GDPR/HIPAA/PCI-DSS compliance checks
- Privacy impact assessments
- Audit trail validation
- Regulatory framework mapping

## Workflow Diagram

```
To Do
  ↓ /flow:assess
Assessed
  ↓ /flow:specify
Specified
  ↓ /flow:research (optional)
Researched
  ↓ /flow:plan
Planned
  ↓ /flow:threat-model (NEW - with approval gate)
Threat Modeled
  ↓ /flow:implement
In Implementation
  ↓ /flow:validate
Validated
  ↓ /flow:security-audit (NEW - with approval gate)
Security Audited
  ↓ /flow:operate
Deployed
  ↓ manual
Done
```

## Security Gates

### Gate 1: Threat Modeling Approval

**Location**: Threat Modeled → In Implementation

**Validation**: `KEYWORD[SECURITY_APPROVED]`

**Checklist**:
- [ ] STRIDE threat model complete for all components
- [ ] Attack surface documented with trust boundaries
- [ ] Security controls designed for identified threats
- [ ] Data flow diagrams reviewed for security
- [ ] Compliance requirements mapped to controls
- [ ] Privacy impact assessment complete (if applicable)

**To Proceed**:
```bash
# After reviewing threat model artifacts:
backlog task edit task-123 --notes "SECURITY_APPROVED by [Your Name]

Threat model reviewed. All high-risk threats have mitigations."
```

### Gate 2: Security Audit Approval

**Location**: Security Audited → Deployed

**Validation**: `KEYWORD[AUDIT_PASSED]`

**Checklist**:
- [ ] Penetration testing complete with no critical findings
- [ ] Vulnerability scanning passed or findings triaged
- [ ] OWASP Top 10 validated
- [ ] Security controls verified as implemented
- [ ] Compliance requirements verified (SOC2/HIPAA/etc.)
- [ ] Audit trail functional and complete

**To Proceed**:
```bash
# After security audit passes:
backlog task edit task-123 --notes "AUDIT_PASSED by [Security Team]

Pen test complete. All critical vulns resolved."
```

## Usage

1. **Copy the configuration**:
   ```bash
   cp docs/examples/workflows/security-audit-workflow.yml flowspec_workflow.yml
   ```

2. **Create compliance-officer agent definition**:
   ```bash
   mkdir -p .agents
   cat > .agents/compliance-officer.md <<EOF
   # Compliance Officer Agent

   ## Identity
   @compliance-officer

   ## Description
   SOC2/HIPAA/GDPR Compliance Officer

   ## Responsibilities
   - SOC2 compliance verification
   - GDPR/HIPAA compliance checks
   - Privacy impact assessments
   - Audit trail validation
   EOF
   ```

3. **Validate configuration**:
   ```bash
   specify workflow validate
   ```

4. **Run the workflow**:
   ```bash
   /flow:assess
   /flow:specify
   /flow:plan

   # Threat Modeling Phase
   /flow:threat-model
   # Review docs/security/{feature}-threat-model.md
   # Type SECURITY_APPROVED to proceed

   /flow:implement
   /flow:validate

   # Security Audit Phase
   /flow:security-audit
   # Review docs/security/{feature}-audit-report.md
   # Type AUDIT_PASSED to proceed

   /flow:operate
   backlog task edit task-123 -s Done
   ```

## Threat Modeling Workflow Detail

### STRIDE Analysis

The threat modeling phase uses STRIDE methodology:

- **Spoofing** - Authentication threats
- **Tampering** - Data integrity threats
- **Repudiation** - Audit/logging threats
- **Information Disclosure** - Confidentiality threats
- **Denial of Service** - Availability threats
- **Elevation of Privilege** - Authorization threats

### Artifacts Created

**Threat Model Document** (`docs/security/{feature}-threat-model.md`):
```markdown
# Threat Model: User Authentication

## Components
- Web Frontend (React)
- API Gateway (Kong)
- Auth Service (Node.js)
- Database (PostgreSQL)

## Trust Boundaries
- Internet → Load Balancer
- Load Balancer → API Gateway
- API Gateway → Internal Services

## Threats Identified

### T-001: Brute Force Password Attack (Spoofing)
- **Severity**: High
- **Mitigation**: Rate limiting + account lockout
- **Status**: Mitigated

### T-002: SQL Injection (Tampering)
- **Severity**: Critical
- **Mitigation**: Parameterized queries + ORM
- **Status**: Mitigated
```

**Attack Surface Document** (`docs/security/{feature}-attack-surface.md`):
```markdown
# Attack Surface: User Authentication

## Entry Points
1. POST /api/login - Username/password authentication
2. POST /api/register - User registration
3. POST /api/reset-password - Password reset

## Data Flows
1. User → Frontend → API Gateway → Auth Service → Database
2. Auth Service → Email Service (password reset)

## Trust Boundaries
- Public internet → Application
- Application → Database
- Application → Email service
```

## Security Audit Workflow Detail

### Audit Activities

1. **Penetration Testing**
   - Automated OWASP ZAP scan
   - Manual security testing
   - Privilege escalation attempts
   - Injection attack testing

2. **Vulnerability Assessment**
   - Dependency scanning (npm audit, Snyk)
   - Container scanning (Trivy)
   - Infrastructure scanning
   - Configuration review

3. **Compliance Verification**
   - SOC2 control mapping
   - GDPR compliance (data minimization, consent, right to erasure)
   - HIPAA compliance (if applicable)
   - PCI-DSS compliance (if applicable)

### Artifacts Created

**Security Audit Report** (`docs/security/{feature}-audit-report.md`):
```markdown
# Security Audit Report: User Authentication

## Audit Date
2025-12-01

## Scope
- User authentication feature (task-123)
- Components: Frontend, API, Auth Service, Database

## Findings

### Critical: 0
None

### High: 1
- **H-001**: Missing rate limiting on password reset endpoint
  - **Status**: Remediated
  - **Fix**: Added rate limiting (10 req/hour per IP)

### Medium: 2
- **M-001**: Weak password policy (8 chars minimum)
  - **Status**: Accepted Risk (UX trade-off)
- **M-002**: Missing security headers (X-Frame-Options)
  - **Status**: Remediated

### Low: 3
- ...

## Compliance
- ✓ SOC2 CC6.1 (Logical access controls)
- ✓ SOC2 CC6.6 (Encryption)
- ✓ GDPR Article 32 (Security of processing)

## Recommendation
**APPROVED FOR PRODUCTION**
```

## Rework Scenarios

### Security Issues During Implementation

If security issues are found during implementation that require design changes:

```bash
# Move back to Threat Modeled state
backlog task edit task-123 -s "Threat Modeled" \
  --notes "Security design issue: Session management needs rework"

# Re-run threat modeling with updated design
/flow:threat-model

# Continue with implementation
/flow:implement
```

### Vulnerabilities Found in Audit

If the security audit finds vulnerabilities:

```bash
# Move back to In Implementation
backlog task edit task-123 -s "In Implementation" \
  --notes "Security audit found SQL injection in search endpoint (H-002)"

# Fix vulnerability
/flow:implement

# Re-validate
/flow:validate

# Re-audit
/flow:security-audit
```

## Customization

### Add Additional Security Phases

**Static Analysis Phase** (before threat modeling):

```yaml
states:
  - "Planned"
  - "Security Designed"  # New state
  - "Threat Modeled"
  # ...

workflows:
  security-design:
    command: "/flow:security-design"
    agents:
      - name: "secure-by-design-engineer"
        responsibilities:
          - "Security architecture design"
          - "Cryptographic design"
    input_states: ["Planned"]
    output_state: "Security Designed"
```

### Add Compliance-Specific Phases

**HIPAA Compliance Phase**:

```yaml
workflows:
  hipaa-compliance:
    command: "/flow:hipaa-compliance"
    agents:
      - name: "compliance-officer"
        responsibilities:
          - "HIPAA Privacy Rule verification"
          - "HIPAA Security Rule verification"
          - "PHI handling validation"
    input_states: ["Security Audited"]
    output_state: "HIPAA Compliant"
```

## Best Practices

1. **Threat Model Early** - Run `/flow:threat-model` before writing code
2. **Document Mitigations** - Link each threat to a mitigation control
3. **Track Accepted Risks** - Document why low-priority findings are accepted
4. **Involve Security Team** - Don't approve gates alone; involve security experts
5. **Automate Where Possible** - Use automated scanning tools (Snyk, Trivy, OWASP ZAP)
6. **Version Threat Models** - Update threat model when architecture changes

## Comparison to Standard Workflow

| Aspect | Standard Workflow | Security Audit Workflow |
|--------|-------------------|-------------------------|
| **Security Phases** | 1 (validation) | 3 (threat model + validation + audit) |
| **Approval Gates** | 0 | 2 (SECURITY_APPROVED + AUDIT_PASSED) |
| **Security Agents** | 1 | 2 (+ compliance-officer) |
| **Time to Deploy** | ~1-2 weeks | ~2-4 weeks |
| **Compliance Ready** | No | Yes (SOC2/HIPAA/GDPR) |
| **Best For** | Internal tools | Customer-facing, regulated industries |

## Related Examples

- [Minimal Workflow](./minimal-workflow.md) - Fast prototyping without security phases
- [Custom Agents Workflow](./custom-agents-workflow.md) - Adding organization-specific agents
