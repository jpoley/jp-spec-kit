---
id: task-247
title: 'Plan /jpspec:security Architecture and Platform Design'
status: Done
assignee:
  - '@platform-engineer'
created_date: '2025-12-03 02:18'
updated_date: '2025-12-03 02:34'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create comprehensive architecture and platform design for the /jpspec:security commands feature, including ADRs, system design, CI/CD integration, and observability.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create ADRs for key architectural decisions (scanner orchestration, AI triage, MCP server)
- [x] #2 Design system architecture with component boundaries and integration patterns
- [x] #3 Design platform architecture for CI/CD integration and observability
- [x] #4 Document security scanning tool orchestration pattern
- [x] #5 Define DORA metrics targets for security scanning workflow
- [x] #6 Create infrastructure requirements for tool dependencies
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Architecture design complete:

Strategic Framing:
- Created docs/architecture/jpspec-security-architecture.md
- Business value analysis: >95% pre-production vulnerability catch rate
- Investment justification: Build native (reference Raptor patterns)
- Platform quality assessment (7 C's): Clarity 9/10, Consistency 9/10, Composability 10/10

ADR-005: Scanner Orchestration Pattern
- Location: docs/adr/ADR-005-scanner-orchestration-pattern.md
- Decision: Pluggable adapter pattern with parallel execution
- Patterns: Service Activator (EIP), Adapter (GoF), Chain of Responsibility
- Implementation task: task-255

ADR-006: AI Triage Engine Design
- Location: docs/adr/ADR-006-ai-triage-engine-design.md
- Decision: LLM-powered triage with specialized classifiers
- Risk scoring: (Impact × Exploitability) / Detection_Time (Raptor formula)
- Target accuracy: >85% agreement with expert manual triage
- Implementation task: task-256

ADR-007: Unified Security Finding Format
- Location: docs/adr/ADR-007-unified-security-finding-format.md
- Decision: Domain-driven dataclasses with SARIF compatibility
- Patterns: Canonical Data Model (EIP), Message Translator (EIP)
- SARIF 2.1.0 export for GitHub Code Scanning
- Implementation task: task-257

ADR-008: Security MCP Server Architecture (v2.0)
- Location: docs/adr/ADR-008-security-mcp-server-architecture.md
- Decision: MCP server with tools + resources
- Tools: security_scan, security_triage, security_fix
- Resources: security://findings, security://status, security://config
- Implementation task: task-258

Layered Architecture:
┌─────────────────────────────────────────┐
│ User Interface Layer                    │
│ (/jpspec:security + specify security)   │
├─────────────────────────────────────────┤
│ Workflow Orchestration Layer            │
│ (scan, triage, fix, audit coordinators) │
├─────────────────────────────────────────┤
│ Security Core Library                   │
│ (Scanner Orchestrator, Triage Engine,   │
│  Report Generator, Unified Format)      │
├─────────────────────────────────────────┤
│ Tool Integration Layer (Adapters)       │
│ (Semgrep, CodeQL, Trivy)                │
└─────────────────────────────────────────┘

DORA Metrics Targets:
- Scan performance: 10K LOC < 1min, 100K LOC < 5min
- AI triage accuracy: >85%
- False positive rate: <15%
- Pre-production catch rate: >95%

Next Steps:
1. Begin task-257 (Unified Finding Format) - foundation for all others
2. Follow with task-255 (Scanner Orchestration)
3. Then task-256 (AI Triage Engine)
4. Defer task-258 (MCP Server) to v2.0
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Platform design complete for /jpspec:security commands.

## Deliverables Created

### 1. Platform Engineering Documentation
- **docs/platform/jpspec-security-platform.md**: Comprehensive platform design covering DORA metrics, CI/CD integration, tool dependency management, DevSecOps patterns, observability architecture, and infrastructure as code
- **docs/platform/security-cicd-integration.md**: Detailed CI/CD integration guide for GitHub Actions, GitLab CI, Jenkins, and CircleCI with performance optimization strategies

### 2. Infrastructure as Code
- **.github/workflows/security-scan.yml**: Production-ready reusable GitHub Actions workflow with incremental scanning, SARIF upload, caching, PR comments, and artifact retention

### 3. DORA Elite Performance Targets
| Metric | Target | Strategy |
|--------|--------|----------|
| Deployment Frequency | Multiple/day | Security scans run in parallel; only critical blocks merge |
| Lead Time | <1 hour | Incremental scanning; pre-commit hooks; caching |
| Change Failure Rate | <5% | AI triage reduces false positives |
| MTTR | <1 hour | Clear fix suggestions with auto-apply |

### 4. Tool Dependency Strategy
- **Semgrep (MVP)**: pip install with version pinning (1.50.0), ~50MB, LGPL 2.1 license
- **CodeQL (v2.0)**: Deferred due to 2GB+ size and commercial licensing complexity
- **Caching**: GitHub Actions cache for binaries and results (7-day retention)
- **Performance**: <5 minutes for 100K LOC with incremental scanning

### 5. CI/CD Pipeline Design
Three-stage integration:
1. **Pre-commit** (local): <10s fast scan, warning only
2. **PR Pipeline** (CI): <5 min incremental scan, blocks on critical/high
3. **Post-Merge** (audit): <20 min full scan, compliance reporting

### 6. Observability Architecture
**Metrics**: scan_duration, findings_total, triage_accuracy, fix_application_rate, gate_blocks
**Logging**: Structured JSON with scan_id, tool, duration, findings
**Dashboards**: Grafana templates for security posture, scan performance, AI effectiveness
**Alerts**: critical_vulnerability_found, scan_performance_degraded, ai_triage_accuracy_low

### 7. DevSecOps Integration
- **Security Gates**: Severity-based blocking (critical/high block, medium warn)
- **Policy as Code**: .jpspec/security-policy.yml for configurable gates
- **Emergency Bypass**: Requires approval + audit trail
- **SBOM Integration**: CycloneDX format for compliance

## Implementation Tasks Created

Created 7 backlog tasks for infrastructure implementation:
- **task-248**: Setup CI/CD Security Scanning Pipeline (HIGH priority)
- **task-249**: Implement Tool Dependency Management Module (HIGH priority)
- **task-250**: Implement Security Scanning Observability (MEDIUM priority)
- **task-251**: Create Pre-commit Hook Configuration (LOW priority)
- **task-252**: Implement Security Policy as Code (MEDIUM priority)
- **task-253**: Track DORA Metrics for Security Scanning (MEDIUM priority)
- **task-254**: Build and Publish Security Scanner Docker Image (LOW priority)

## Performance Benchmarks
| Scenario | LOC | Target Time | Strategy |
|----------|-----|-------------|----------|
| Pre-commit | Changed files | <10s | Fast scan only |
| PR (small) | 10K | <1 min | Incremental |
| PR (large) | 100K | <5 min | Incremental + cache |
| Post-merge | 500K | <20 min | Parallel + progress |

## Key Architectural Decisions
1. **Native implementation** over Raptor fork (avoid 6GB DevContainer)
2. **Semgrep MVP** with CodeQL deferred to v2.0 (licensing complexity)
3. **Incremental scanning** as default for DORA Elite performance
4. **SARIF output** for GitHub Security tab integration
5. **Policy as code** for flexible security gate configuration

## Next Steps
1. Review platform design documents
2. Begin implementation with task-248 (CI/CD pipeline)
3. Test workflow on JP Spec Kit repository
4. Iterate based on performance benchmarks
<!-- SECTION:NOTES:END -->
