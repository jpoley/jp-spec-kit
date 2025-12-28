---
id: task-252
title: Implement Security Policy as Code Configuration
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 02:26'
updated_date: '2025-12-28 20:18'
labels:
  - security
  - scanning
  - on-hold
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build .flowspec/security-policy.yml parser and enforcement engine. Support severity-based gates, tool configuration, compliance mappings, and finding exemptions with expiration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define YAML schema for security policy configuration (gates, tools, triage, reporting, exemptions)
- [ ] #2 Implement policy parser and validator with clear error messages
- [ ] #3 Add policy enforcement in scan/triage/fix commands
- [ ] #4 Support exemptions (paths, specific findings with justification and expiration)
- [ ] #5 Create default policy template with OWASP Top 10 compliance
- [ ] #6 Test policy enforcement with multiple test cases
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Security Policy as Code Configuration

### Overview
Build .flowspec/security-policy.yml parser and enforcement engine to support version-controlled security policies with severity gates, tool configuration, and exemptions.

### Step-by-Step Implementation

#### Step 1: Define YAML Schema
**File**: `src/specify_cli/security/policy_schema.py`
**Duration**: 2 hours

1. Create Pydantic models for policy structure:
   ```python
   from pydantic import BaseModel, Field
   from typing import List, Dict, Optional
   
   class GateConfig(BaseModel):
       block_on: List[str] = []  # ["critical", "high"]
       warn_on: List[str] = []   # ["medium"]
       audit_only: List[str] = ["low"]
   
   class Gates(BaseModel):
       pre_commit: GateConfig
       pull_request: GateConfig
       main_branch: GateConfig
   
   class ToolConfig(BaseModel):
       enabled: bool = True
       rulesets: List[str] = ["auto"]
       custom_rules: Optional[str] = None
   
   class TriageConfig(BaseModel):
       enabled: bool = True
       model: str = "claude-sonnet-4"
       confidence_threshold: float = 0.7
       false_positive_suppression: bool = True
   
   class FindingExemption(BaseModel):
       rule_id: str
       file: str
       justification: str
       approved_by: str
       expires: str  # ISO date
   
   class SecurityPolicy(BaseModel):
       version: str = "1.0"
       gates: Gates
       tools: Dict[str, ToolConfig]
       triage: TriageConfig
       reporting: Dict
       exemptions: Dict[str, List]
   ```

2. Add schema validation:
   - Validate severity levels
   - Validate date formats for exemptions
   - Validate tool names
   - Validate file paths

#### Step 2: Implement Policy Parser
**File**: `src/specify_cli/security/policy.py`
**Duration**: 2 hours

1. Create policy loader:
   ```python
   def load_security_policy(path: str = ".flowspec/security-policy.yml") -> SecurityPolicy:
       """Load and validate security policy from YAML file."""
       if not Path(path).exists():
           logger.warning(f"No policy file found at {path}, using defaults")
           return get_default_policy()
       
       with open(path) as f:
           data = yaml.safe_load(f)
       
       try:
           policy = SecurityPolicy(**data)
           return policy
       except ValidationError as e:
           raise PolicyValidationError(f"Invalid policy: {e}")
   ```

2. Add default policy factory:
   ```python
   def get_default_policy() -> SecurityPolicy:
       """Return default security policy with OWASP Top 10 compliance."""
       return SecurityPolicy(
           gates=Gates(
               pre_commit=GateConfig(block_on=[], warn_on=["critical"]),
               pull_request=GateConfig(block_on=["critical", "high"], warn_on=["medium"]),
               main_branch=GateConfig(block_on=["critical"], warn_on=["high", "medium"], audit_all=True)
           ),
           tools={
               "semgrep": ToolConfig(
                   enabled=True,
                   rulesets=["auto", "p/owasp-top-ten", "p/security-audit"]
               ),
               "codeql": ToolConfig(enabled=False)
           },
           triage=TriageConfig(),
           reporting={
               "formats": ["markdown", "sarif", "json"],
               "output_dir": "docs/security"
           },
           exemptions={"paths": ["tests/**", "vendor/**"], "findings": []}
       )
   ```

3. Add policy validator CLI command:
   ```bash
   specify security policy validate [--file .flowspec/security-policy.yml]
   ```

#### Step 3: Implement Policy Enforcement
**File**: `src/specify_cli/security/enforcement.py`
**Duration**: 3 hours

1. Add gate enforcement logic:
   ```python
   def enforce_gate(findings: List[Finding], gate_type: str, policy: SecurityPolicy) -> GateResult:
       """Enforce security gate based on policy."""
       gate_config = getattr(policy.gates, gate_type)
       
       blocked = []
       warnings = []
       
       for finding in findings:
           if finding.severity in gate_config.block_on:
               blocked.append(finding)
           elif finding.severity in gate_config.warn_on:
               warnings.append(finding)
       
       if blocked:
           return GateResult(
               status="blocked",
               message=f"{len(blocked)} {gate_type} gate violations",
               blocked=blocked,
               warnings=warnings
           )
       
       if warnings:
           return GateResult(
               status="warning",
               message=f"{len(warnings)} warnings (non-blocking)",
               warnings=warnings
           )
       
       return GateResult(status="passed")
   ```

2. Add exemption checking:
   ```python
   def check_exemptions(finding: Finding, policy: SecurityPolicy) -> Optional[Exemption]:
       """Check if finding is exempted."""
       # Check path exemptions
       for pattern in policy.exemptions.get("paths", []):
           if fnmatch(finding.location.file, pattern):
               return Exemption(reason="path_exempted", pattern=pattern)
       
       # Check specific finding exemptions
       for exemption in policy.exemptions.get("findings", []):
           if (exemption.rule_id == finding.rule_id and
               exemption.file == finding.location.file):
               # Check expiration
               if datetime.fromisoformat(exemption.expires) > datetime.now():
                   return exemption
               else:
                   logger.warning(f"Exemption expired: {exemption}")
       
       return None
   ```

3. Integrate enforcement into scan command:
   - Add `--gate-type` flag
   - Apply policy before exit
   - Set exit code based on gate result

#### Step 4: Create Default Policy Template
**File**: `templates/security-policy-template.yml`
**Duration**: 1 hour

1. Create comprehensive template:
   ```yaml
   version: 1.0
   
   # Security gate configuration
   gates:
     pre_commit:
       block_on: []  # Warning only for fast feedback
       warn_on: [critical]
       audit_only: [high, medium, low]
     
     pull_request:
       block_on: [critical, high]
       warn_on: [medium]
       audit_only: [low]
     
     main_branch:
       block_on: [critical]
       warn_on: [high, medium]
       audit_all: true
   
   # Tool configuration
   tools:
     semgrep:
       enabled: true
       rulesets:
         - auto  # Semgrep Registry OWASP rules
         - p/owasp-top-ten
         - p/security-audit
       custom_rules: .semgrep/rules
     
     codeql:
       enabled: false  # Defer to v2.0
       license_check: true
   
   # AI triage configuration
   triage:
     enabled: true
     model: claude-sonnet-4
     confidence_threshold: 0.7
     false_positive_suppression: true
   
   # Reporting configuration
   reporting:
     formats: [markdown, sarif, json]
     output_dir: docs/security
     retention_days: 90
     compliance:
       OWASP_Top_10: true
       CWE_Top_25: true
   
   # Exemptions
   exemptions:
     paths:
       - "tests/**"  # Don't scan test fixtures
       - "vendor/**"  # Third-party code
       - "docs/**"   # Documentation
     
     findings:
       # Example: Suppress specific false positive
       - rule_id: python.lang.security.audit.generic-exception-handler
         file: src/cli/error_handler.py
         justification: "Intentional catch-all for CLI error display"
         approved_by: security-team
         expires: "2026-06-01"
   ```

2. Add inline documentation in template
3. Create minimal example for quick start

#### Step 5: Add Policy Management Commands
**Duration**: 2 hours

1. **Init command**:
   ```bash
   specify security policy init [--minimal]
   # Creates .flowspec/security-policy.yml from template
   ```

2. **Validate command**:
   ```bash
   specify security policy validate [--file policy.yml]
   # Validates policy syntax and semantics
   ```

3. **Show command**:
   ```bash
   specify security policy show
   # Displays current effective policy (with defaults)
   ```

4. **Exemption commands**:
   ```bash
   specify security policy exempt add \
     --rule-id CWE-89 \
     --file src/auth.py \
     --justification "Using parameterized queries" \
     --expires 2026-01-01
   
   specify security policy exempt list
   specify security policy exempt remove <exemption-id>
   ```

#### Step 6: Testing
**Duration**: 2 hours

1. **Schema validation tests**:
   - Valid policy files parse correctly
   - Invalid files raise clear errors
   - Default policy is valid

2. **Enforcement tests**:
   - Blocking gates work correctly
   - Warning gates don't block
   - Exemptions are respected
   - Expired exemptions are ignored

3. **Integration tests**:
   - Policy affects scan command behavior
   - CI/CD respects policy
   - Multiple gate types work

4. **Edge cases**:
   - Missing policy file uses defaults
   - Invalid severity levels rejected
   - Malformed YAML handled gracefully

### Dependencies
- Security scan command implementation (task-210)
- Finding data models defined

### Testing Checklist
- [ ] Policy parser handles valid YAML
- [ ] Policy parser rejects invalid YAML with clear errors
- [ ] Gate enforcement blocks correctly
- [ ] Gate enforcement warns correctly
- [ ] Path exemptions work
- [ ] Finding exemptions work with expiration
- [ ] Default policy is sensible
- [ ] Policy commands work end-to-end

### Estimated Effort
**Total**: 12 hours (1.5 days)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**ON HOLD (Dec 2025)**: Security scanning features may move to dedicated security repo.
<!-- SECTION:NOTES:END -->
