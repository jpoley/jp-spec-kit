# Feature Assessment: /flow:security Commands with Raptor Integration

**Date**: 2025-12-02
**Assessed By**: Claude AI Agent
**Status**: Assessed

## Feature Overview

Add comprehensive security scanning capabilities to JP Flowspec via new `/flow:security` commands with subcommands. The decision point is whether to:

1. **Option A: Integrate Raptor** - Fork/vendor the [gadievron/raptor](https://github.com/gadievron/raptor) framework and maintain it as a dependency
2. **Option B: Build Native** - Implement security features directly in JP Flowspec using the same underlying tools (Semgrep, CodeQL, etc.)

### Raptor Capabilities Summary

| Capability | Description | Tools Used |
|------------|-------------|------------|
| Static Analysis | Code scanning with dataflow validation | Semgrep, CodeQL |
| Fuzzing | Binary fuzzing | AFL++ |
| Vulnerability Analysis | LLM-powered reasoning | Claude Code |
| Exploit Generation | PoC creation | Custom |
| Patch Generation | Security fix suggestions | Custom |
| Expert Personas | 9 security expert modes | Prompt engineering |

### JP Flowspec Current State

- `security-audit-workflow.yml` - Example workflow with threat modeling + security audit phases
- `security-report-template.md` - Template for security reports
- `/flow:validate` - Includes security validation agent
- `@secure-by-design-engineer` agent already defined

## Scoring Analysis

### Complexity Score: 7.3/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Effort Days | 8/10 | Either approach requires 2-4 weeks: Raptor integration has hidden complexity (6GB deps, privileged containers, CodeQL licensing), native build needs tool orchestration |
| Component Count | 7/10 | New CLI commands, scanner orchestration, report generation, workflow integration, potentially 5-7 new modules |
| Integration Points | 7/10 | Semgrep, CodeQL, AFL++ (optional), existing flowspec workflows, backlog.md, CI/CD pipelines |
| **Average** | **7.3/10** | |

### Risk Score: 7.0/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Security Implications | 8/10 | Security tooling itself is high-risk - false positives erode trust, false negatives miss vulnerabilities; also handles sensitive code |
| Compliance Requirements | 6/10 | CodeQL has commercial license restrictions; must handle SLSA attestation properly |
| Data Sensitivity | 7/10 | Scans customer codebases, may expose vulnerability details |
| **Average** | **7.0/10** | |

### Architecture Impact Score: 6.7/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| New Patterns | 7/10 | Introduces scanner orchestration pattern, unified reporting, possibly DevContainer requirements |
| Breaking Changes | 5/10 | New commands, no breaking changes to existing flowspec commands |
| Dependencies Affected | 8/10 | Heavy external deps (Semgrep ~50MB, CodeQL ~2GB), may require privileged execution, affects CI/CD |
| **Average** | **6.7/10** | |

## Overall Assessment

**Total Score**: 21.0/30
**Recommendation**: Full SDD
**Confidence**: High

### Rationale

All three dimensions score >= 6.7, and total exceeds 18. This feature:
- Introduces significant external dependencies with licensing concerns
- Requires careful security architecture (security tools scanning security code)
- Has multiple valid implementation approaches with major trade-offs
- Impacts CI/CD pipelines and developer workflows

### Key Factors

- **Complexity**: High due to multi-tool orchestration (Semgrep, CodeQL, AFL++) and heavy dependencies
- **Risk**: High because security tooling accuracy is critical and CodeQL licensing needs review
- **Impact**: Moderate-high as it adds new workflow phase and external dependencies

## Decision Analysis: Raptor Integration vs Native Build

### Option A: Integrate Raptor

**Pros:**
- Immediate functionality (9 expert personas, fuzzing, exploit PoCs)
- Active development (221 stars, 6 contributors)
- MIT licensed core (good for reuse)
- Proven Claude Code integration patterns

**Cons:**
- Heavy dependencies (~6GB DevContainer, `--privileged` required)
- Alpha maturity - API may change
- CodeQL commercial restrictions still apply
- Maintenance burden: tracking upstream changes
- Feature bloat: includes offensive capabilities (exploit gen) we may not want
- Architecture mismatch: designed for autonomous offensive testing, not SDD workflow integration

**Effort Estimate:**
- Fork and adapt: 1 week
- Ongoing maintenance: ~4 hrs/month
- Risk of upstream divergence

### Option B: Build Native `/flow:security`

**Pros:**
- Tight integration with existing flowspec workflow
- Control over feature scope (start with scanning, add fuzzing later)
- Cleaner dependency management (install tools on-demand)
- Aligned with SDD philosophy (specification-driven security)
- No upstream maintenance burden
- Can leverage Raptor's approach without wholesale import

**Cons:**
- More initial development effort
- Must design scanner orchestration from scratch
- No fuzzing/exploit generation initially

**Effort Estimate:**
- MVP (Semgrep + basic CodeQL): 2 weeks
- Full feature parity: 4-6 weeks
- No ongoing upstream maintenance

### Recommendation: Option B (Build Native) with Raptor as Reference

**Rationale:**
1. **Scope alignment**: JP Flowspec is for SDD workflows, not autonomous offensive testing
2. **Dependency hygiene**: Avoid 6GB DevContainer and `--privileged` requirements
3. **Incremental delivery**: Start with Semgrep scanning, add CodeQL, defer fuzzing
4. **Architecture fit**: Native commands integrate naturally with workflow states
5. **Reference, don't fork**: Borrow Raptor's patterns (prompt engineering, tool orchestration) without the maintenance burden

## Proposed `/flow:security` Command Structure

```bash
# Subcommands
/flow:security scan      # Run security scans (Semgrep, optionally CodeQL)
/flow:security audit     # Generate security audit report
/flow:security triage    # AI-assisted vulnerability triage
/flow:security fix       # Generate fix suggestions for findings

# Future (post-MVP)
/flow:security fuzz      # Binary fuzzing (AFL++)
/flow:security pentest   # Penetration testing mode
```

### MVP Scope (Recommended for First Implementation)

1. `/flow:security scan` - Orchestrate Semgrep with custom rules
2. `/flow:security audit` - Generate formatted security report
3. `/flow:security triage` - AI triage of findings

### Integration with Existing Workflow

```yaml
# Addition to security-audit-workflow.yml
security-scan:
  command: "/flow:security scan"
  description: "Run security scans"
  agents:
    - name: "secure-by-design-engineer"
  input_states: ["In Implementation"]
  output_state: "Scanned"
```

## Next Steps

### Full SDD Path (Recommended)

```bash
/flow:specify flowspec-security-commands
```

This will create a detailed PRD covering:
- Exact subcommand specifications
- Scanner tool selection and licensing review
- Report format design
- Workflow integration points
- CI/CD considerations
- Dependency management strategy

### Alternative: Spec-Light for MVP

If time-constrained, a spec-light approach:
1. Create `docs/prd/flowspec-security-commands-spec.md` with:
   - Problem statement
   - MVP scope (scan + audit only)
   - Key acceptance criteria
2. Proceed to implementation

### Skip SDD: Not Recommended

Given the complexity score (7.3) and security risk (7.0), skipping specification would likely result in:
- Scope creep
- Licensing issues discovered late
- Poor workflow integration

## Override

If this assessment doesn't match your needs:

```bash
# Force full SDD workflow
/flow:assess flowspec-security-commands --mode full

# Force spec-light mode
/flow:assess flowspec-security-commands --mode light

# Force skip SDD
/flow:assess flowspec-security-commands --mode skip
```

## Appendix: Raptor Reference Architecture

Key patterns to borrow from Raptor (without forking):

1. **Progressive Token Disclosure**: Load expertise layers on-demand
2. **Tool Orchestration**: Unified Python launcher for multiple tools
3. **Prioritization Formula**: `Impact x Exploitability / Detection Time`
4. **Expert Personas**: Security-focused agent identities

---

*Assessment generated by /flow:assess workflow*
