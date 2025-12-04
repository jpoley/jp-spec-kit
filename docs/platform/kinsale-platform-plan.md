# Kinsale Platform Plan - Infrastructure and DevSecOps

**Date:** 2025-12-04
**Platform Engineer:** @kinsale
**Status:** Planning Complete
**Related Tasks:** task-085, task-136, task-168, task-171, task-184, task-195, task-196, task-197, task-249

---

## Executive Summary

This document outlines the platform engineering strategy for JP Spec Kit, covering 9 infrastructure and DevSecOps tasks assigned to the @kinsale machine. The platform design focuses on:

1. **Security** - Permissions architecture, secret protection, dangerous command blocking
2. **Tool Management** - Auto-installation, version pinning, cache management
3. **Observability** - claude-trace integration for workflow debugging
4. **CI/CD** - Local CI simulation with act, cross-platform testing
5. **Developer Experience** - Plugin packaging, output styles, custom statusline

The platform targets **DORA Elite metrics** (deployment frequency, lead time, MTTR, change failure rate) while maintaining **NIST/SSDF compliance** and **SLSA Level 2** attestation.

---

## Platform Principles

### 1. Security by Default

**Principle:** Security controls are enabled by default, not opt-in.

**Application:**
- `permissions.deny` blocks sensitive files (.env, secrets/) by default
- Dangerous commands (sudo, rm -rf) blocked without confirmation
- Secret redaction in traces enabled by default
- Lock files protected from accidental writes

**Trade-off:** May block legitimate operations → provide clear override mechanism

### 2. Developer Velocity First

**Principle:** Platform should accelerate development, not slow it down.

**Application:**
- Local CI simulation (<1 min feedback vs 5-10 min GitHub Actions)
- Auto-install tools on first use (zero manual setup)
- Fast trace queries (<1 sec for debugging)
- Selective job execution (run only lint, skip tests)

**Trade-off:** Auto-install may surprise users → notify before large downloads

### 3. Observable by Default

**Principle:** All operations should be traceable for debugging and optimization.

**Application:**
- claude-trace captures all operations (file ops, tool calls, API requests)
- Audit logging for permission denials (security review)
- Token usage attribution (cost optimization)
- Performance profiling (identify bottlenecks)

**Trade-off:** Trace storage grows → implement retention policy (30 days)

### 4. Environment Parity

**Principle:** Local development should match CI/CD environment.

**Application:**
- act uses same Docker images as GitHub Actions (ubuntu-latest)
- Tool versions pinned (reproducible builds)
- Cross-platform testing (Linux, macOS, Windows)
- Lock files prevent dependency drift

**Trade-off:** Docker overhead → but environment parity more important

### 5. Composability Over Monoliths

**Principle:** Small, focused tools that compose well.

**Application:**
- Tool dependency manager (install, cache, version) is independent
- Permissions system (deny, allow, audit) is independent
- Observability (trace, query, visualize) is independent
- Each tool can be used standalone or combined

**Trade-off:** More moving parts → but easier to maintain and extend

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   KINSALE PLATFORM ARCHITECTURE                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │ SECURITY LAYER                                    │         │
│  │ - Permissions (deny/allow rules)                  │         │
│  │ - Secret detection (API keys, passwords)          │         │
│  │ - Command blocking (sudo, rm -rf)                 │         │
│  │ - Audit logging                                   │         │
│  │                                                    │         │
│  │ ADR: ADR-014-security-permissions-architecture    │         │
│  │ Task: task-184                                    │         │
│  └────────────────────────────────────────────────────┘         │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ TOOL MANAGEMENT LAYER                             │         │
│  │ - Auto-installation (pip, binary, npm)            │         │
│  │ - Version pinning (SLSA compliance)               │         │
│  │ - Cache management (size monitoring, eviction)    │         │
│  │ - Offline mode (air-gapped support)               │         │
│  │                                                    │         │
│  │ ADR: ADR-013-tool-dependency-management           │         │
│  │ Task: task-249                                    │         │
│  └────────────────┬───────────────────────────────────┘         │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ OBSERVABILITY LAYER                               │         │
│  │ - Trace collection (claude-trace)                 │         │
│  │ - Token usage tracking                            │         │
│  │ - Performance profiling                           │         │
│  │ - Audit log aggregation                           │         │
│  │                                                    │         │
│  │ ADR: ADR-015-observability-strategy               │         │
│  │ Task: task-136                                    │         │
│  └────────────────┬───────────────────────────────────┘         │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ CI/CD LAYER                                       │         │
│  │ - Local CI (act runner)                           │         │
│  │ - Cross-platform testing (Linux, macOS)           │         │
│  │ - Selective job execution                         │         │
│  │ - DORA metrics optimization                       │         │
│  │                                                    │         │
│  │ ADR: ADR-016-cicd-pipeline-design                 │         │
│  │ Tasks: task-085, task-168                         │         │
│  └────────────────┬───────────────────────────────────┘         │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ DEVELOPER EXPERIENCE LAYER                        │         │
│  │ - Plugin packaging (distribution)                 │         │
│  │ - Output styles (PM, Architect personas)          │         │
│  │ - Custom statusline (workflow context)            │         │
│  │ - MCP integration (library docs)                  │         │
│  │                                                    │         │
│  │ Tasks: task-171, task-195, task-196, task-197     │         │
│  └────────────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

---

## DORA Metrics Strategy

### Lead Time for Changes: <1 Hour (Elite)

**Current State:** 2-4 hours (traditional CI workflow)

**Target State:** <1 hour (local CI + fast iteration)

**Implementation:**
- Local CI simulation (task-085): Catch failures in <1 min (vs 5-10 min GitHub)
- Observability (task-136): Debug failures in 5 min (vs 1 hour trial-and-error)
- Auto-install tools (task-249): Zero setup time (vs 15 min manual install)

**Measurement:**
- Time from commit to production-ready code
- Exclude external review time (human factor)

### Deployment Frequency: Multiple Times Per Day (Elite)

**Current State:** Once per day (slow CI discourages frequent deploys)

**Target State:** 5-10 times per day (fast feedback encourages small commits)

**Implementation:**
- Fast local feedback loop (<1 min)
- Selective job execution (run only lint, skip tests for quick validation)
- Pre-validated commits (local CI passes before push)

**Measurement:**
- Deployments per day to main branch
- Small, incremental commits (vs large, risky commits)

### Change Failure Rate: <15% (Elite)

**Current State:** 25-30% (many commits fail first CI run)

**Target State:** <15% (local validation catches issues before push)

**Implementation:**
- Local CI catches lint, test, security issues before push
- Security permissions prevent dangerous operations
- Cross-platform testing catches macOS/Linux-specific issues

**Measurement:**
- Percentage of commits that fail CI
- Percentage of commits requiring rollback

### Mean Time to Restore: <1 Hour (Elite)

**Current State:** 2-4 hours (slow debugging, slow CI feedback)

**Target State:** <1 hour (fast debugging with traces, fast local iteration)

**Implementation:**
- Observability (claude-trace): Root cause analysis in 5 min
- Local CI: Test fixes in <1 min (vs 5-10 min GitHub)
- Audit logs: Security incident response

**Measurement:**
- Time from incident detection to fix deployed
- Exclude incident detection time (external monitoring)

---

## Security Posture

### Defense-in-Depth Layers

**Layer 1: File Permissions**
- Deny read: .env, secrets/, credentials/, .ssh/, *.pem, *.key
- Deny write: CLAUDE.md, constitution.md, lock files, .git/

**Layer 2: Command Blocking**
- Block: sudo, rm -rf /, chmod 777, dd, mkfs, systemctl
- Block: curl | bash, wget | sh (remote code execution)

**Layer 3: Content Scanning**
- Detect: Private keys, AWS keys, GitHub tokens, API keys
- Redact: Secrets in audit logs and traces

**Layer 4: Audit Logging**
- Log all permission denials
- Retain 30 days for security review
- JSON format for SIEM integration

### Compliance Alignment

**NIST SSDF:**
- PW.1.1: Secure development environment ✓ (permissions)
- PW.4.4: Software integrity verification ✓ (SLSA Level 2)
- PW.7.1: Vulnerability detection ✓ (Semgrep, CodeQL)
- PW.8.1: Audit logging ✓ (permission denials, traces)

**SLSA Level 2:**
- Build integrity: Tool version pinning (versions.lock.json)
- Provenance: Trace collection (who, what, when)
- Isolation: Permission boundaries (deny rules)

**SOC 2 (Type II):**
- Access control: Permissions deny rules
- Monitoring: Audit logging, trace collection
- Change management: Git workflow, PR reviews

---

## Tool Ecosystem

### Required Tools

| Tool | Purpose | Installation | Version Pinning |
|------|---------|-------------|----------------|
| Semgrep | SAST security scanning | pip install | 1.95.0 |
| CodeQL | Dataflow analysis | Binary download | 2.15.5 |
| act | Local CI runner | Binary download | 0.2.68 |
| claude-trace | Observability | npm install | 1.2.0 |

### Tool Management Strategy

**Discovery Chain:**
1. System PATH (pre-installed tools)
2. Project venv (.venv/bin/)
3. Specify cache (~/.specify/tools/)
4. Download on demand (network required)

**Cache Management:**
- Max cache size: 500MB (alert threshold)
- Eviction policy: LRU (least recently used)
- Retention: No time limit (manual cleanup only)
- Offline mode: Use cached tools only (no network)

**Version Pinning:**
- versions.lock.json tracks all tool versions
- Integrity hashes prevent tampering (SLSA Level 2)
- Update mechanism with automated testing

---

## Observability Strategy

### Trace Collection

**What is Traced:**
- File operations (Read, Write, Edit)
- Tool calls (Bash, Grep, Glob)
- API requests (Claude API, token usage)
- Agent decisions (which agent, which task)

**What is NOT Traced:**
- File contents from .env, secrets/ (privacy)
- Secrets in API requests (redacted)
- Large file contents (truncated to 1000 chars)

### Trace Storage

**Location:** ~/.claude-trace/traces.db (SQLite)

**Retention:** 30 days (configurable)

**Size:** ~5MB per 1000 traces (manageable)

**Query Performance:**
- <1 sec for recent traces (indexed by timestamp)
- <5 sec for full-text search (SQLite FTS5)

### Privacy Guarantees

1. **Local-only**: No external transmission (no telemetry)
2. **Redaction**: Secrets automatically redacted (API keys, passwords)
3. **Exclusion**: .env, secrets/ never traced
4. **Retention**: Auto-purge after 30 days

---

## CI/CD Architecture

### Inner Loop (Local Development)

**Workflow:**
```
1. Make changes
2. run-local-ci.sh (lint, test, build, security)
3. Fix issues (<1 min feedback)
4. Repeat until clean
5. git push (pre-validated)
```

**Performance:**
- Lint: 5-10 sec
- Test: 20-30 sec
- Build: 10-15 sec
- Security: 15-20 sec
- **Total: <1 min** (vs 5-10 min GitHub Actions)

### Outer Loop (GitHub Actions)

**Workflow:**
```
1. GitHub Actions triggers on push/PR
2. Matrix build (Linux, macOS, Windows)
3. Full test suite (unit, integration, e2e)
4. Security scanning (Semgrep, CodeQL)
5. Build and publish artifacts
```

**Performance:**
- Matrix build: 5-7 min (parallel)
- Security scan: 2-3 min
- Artifact publish: 1-2 min
- **Total: 8-12 min**

**Cost Optimization:**
- 50% reduction in GitHub Actions usage (pre-validated commits)
- Within free tier (2000 min/month)

---

## Cross-Platform Support

### Supported Platforms

| Platform | CI Matrix | Local CI (act) | Notes |
|----------|-----------|---------------|-------|
| Linux (Ubuntu) | ✓ | ✓ | Primary platform |
| macOS | ✓ | ✓ | Task-168 adds matrix support |
| Windows | Planned | Partial | act Windows support limited |

### Platform-Specific Considerations

**Linux:**
- Default platform (all features supported)
- Docker widely available
- act fully functional

**macOS:**
- M1/M2 Macs require Rosetta for some tools (act, claude-trace)
- Docker Desktop required (not free for enterprise)
- Homebrew for tool installation

**Windows:**
- Git Bash required for scripts
- Docker Desktop required
- act Windows support experimental

---

## Developer Experience Enhancements

### Plugin Packaging (task-195)

**Goal:** Package JP Spec Kit as Claude Code plugin for easy distribution.

**Structure:**
```
.claude-plugin/
├── manifest.json       # Plugin metadata
├── commands/           # /jpspec commands
├── skills/             # SDD skills
├── hooks/              # Pre-commit, stop hooks
└── settings.json       # Default settings
```

**Distribution:**
- Install via `/plugin install jp-spec-kit`
- Automatic updates
- Community sharing

### Output Styles (task-196)

**Goal:** Experiment with persona-based output formatting.

**Personas:**
- PM style for /jpspec:specify (bullet points, user stories)
- Architect style for /jpspec:plan (diagrams, ADRs)
- QA style for /jpspec:validate (test reports, coverage)

**Assessment:** Evaluate value vs complexity trade-off.

### Custom Statusline (task-197)

**Goal:** Display workflow context in Claude Code statusline.

**Content:**
- Current workflow phase (/jpspec:implement)
- Active backlog task (task-085)
- Acceptance criteria progress (AC 3/9)
- Git branch (feature/ci-cd)

**Format:**
```
[/jpspec:implement] task-085 (AC 3/9) | feature/ci-cd
```

### Library Documentation MCP (task-171)

**Goal:** Replace context7 MCP with reliable library documentation source.

**Candidates:**
- MCP Server 1: docs.rs (Rust docs)
- MCP Server 2: devdocs.io (multi-language)
- MCP Server 3: Custom MCP (built-in Python stdlib docs)

**Evaluation Criteria:**
- API key requirements (prefer no API key)
- Reliability (uptime, rate limits)
- Coverage (Python, TypeScript, Rust)

---

## Implementation Roadmap

### Week 1: Security and Tools (HIGH Priority)

**Tasks:**
- task-184: permissions.deny rules (4 ACs)
- task-249: Tool dependency manager (6 ACs)

**Deliverables:**
- .claude/settings.json with deny rules
- src/specify_cli/tools/ module
- Semgrep auto-installation

**Success Criteria:**
- Zero .env file exposures
- >95% tool installation success rate

### Week 2: Observability and CI (MEDIUM Priority)

**Tasks:**
- task-136: claude-trace integration (10 ACs)
- task-085: Local CI script (8 ACs)
- task-168: macOS CI matrix (4 ACs)

**Deliverables:**
- docs/guides/claude-trace-integration.md
- scripts/bash/run-local-ci.sh
- .github/workflows/ci.yml (matrix)

**Success Criteria:**
- 50% reduction in debugging time
- <1 min local CI feedback
- Cross-platform compatibility

### Week 3: Developer Experience (LOW Priority)

**Tasks:**
- task-171: Library docs MCP (7 ACs)
- task-195: Plugin package (5 ACs)
- task-196: Output styles (5 ACs)
- task-197: Custom statusline (5 ACs)

**Deliverables:**
- .mcp.json with new library MCP
- .claude-plugin/ structure
- Prototype output styles
- Custom statusline script

**Success Criteria:**
- Library docs accessible
- Plugin installable via /plugin
- Output styles evaluated

---

## Risk Assessment

### High Impact Risks

**Risk 1: Tool Installation Failures**
- **Impact:** Blocks security scanning, CI execution
- **Mitigation:** Fallback to system tools, clear error messages, retry logic
- **Contingency:** Manual installation instructions

**Risk 2: Permission False Positives**
- **Impact:** Blocks legitimate operations, frustration
- **Mitigation:** Clear override mechanism, user feedback loop, refine patterns
- **Contingency:** Emergency override flag

**Risk 3: Trace Storage Growth**
- **Impact:** Disk space exhaustion, performance degradation
- **Mitigation:** 30-day retention, auto-purge, size monitoring
- **Contingency:** Manual cleanup command

### Medium Impact Risks

**Risk 4: act Docker Requirement**
- **Impact:** Can't run local CI without Docker
- **Mitigation:** Provide native script fallback, document Docker requirement
- **Contingency:** Skip local CI, rely on GitHub Actions

**Risk 5: claude-trace Performance**
- **Impact:** Slow trace queries, UI hangs
- **Mitigation:** Disable FTS5 indexing, purge old traces
- **Contingency:** Use command-line queries (faster than UI)

---

## Success Metrics

### Objective Measures

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Lead Time for Changes | 2-4 hours | <1 hour | Time from commit to production-ready |
| Deployment Frequency | 1/day | 5-10/day | Commits to main per day |
| Change Failure Rate | 25-30% | <15% | Failed CI runs / total runs |
| MTTR | 2-4 hours | <1 hour | Time from incident to fix deployed |
| Tool Install Success | N/A | >95% | Successful installs / total attempts |
| GitHub Actions Usage | 650 min/month | 350 min/month | Minutes consumed |

### Subjective Measures

| Metric | Target | Measurement |
|--------|--------|-------------|
| Developer Trust | NPS >50 | "I feel safe using Claude Code" |
| Debugging Experience | NPS >30 | "Debugging workflows is manageable" |
| CI Experience | NPS >40 | "Local CI is fast and reliable" |

---

## Conclusion

The Kinsale platform plan delivers a comprehensive infrastructure and DevSecOps strategy for JP Spec Kit, addressing 9 critical tasks across security, tool management, observability, CI/CD, and developer experience.

**Key Outcomes:**
- **DORA Elite** metrics (lead time, deployment frequency, CFR, MTTR)
- **NIST/SSDF** compliance (secure development, vulnerability detection)
- **SLSA Level 2** attestation (build integrity, provenance)
- **50% cost reduction** in GitHub Actions usage
- **50% reduction** in debugging time

**Next Steps:**
1. Complete 4 ADRs (ADR-013 through ADR-016)
2. Update all 9 tasks with implementation plans
3. Create PR for review
4. Begin implementation (Week 1: Security and Tools)

---

**Platform Engineer:** @kinsale
**Review Date:** 2025-12-18 (after Phase 1 complete)
**Stakeholders:** JP Spec Kit maintainers, security team, developer community
