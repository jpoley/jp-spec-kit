# ADR-005: Security Scanner Architecture

**Status**: Accepted
**Date**: 2025-12-19
**Decision Maker**: Software Architect
**Stakeholders**: Security Team, Engineering Team, Platform Engineers

## Context

The flowspec project has two security-related initiatives that appeared to overlap:

1. **`/flow:security` commands** - Implemented security scanning system with Semgrep-based SAST, AI-powered triage, automated fix generation, and comprehensive reporting (see PRD: flowspec-security-commands)
2. **task-198** - Originally conceived as "Unified Vulnerability Scanner" combining Trivy + Snyk for dependency and container scanning

During investigation of task-220 ("Resolve Relationship with task-198 Unified Vulnerability Scanner"), we discovered:

1. **task-198 was repurposed** - It now covers "Define Event Model Schema for flowspec Hooks" (completed 2025-12-03), NOT vulnerability scanning
2. **No separate unified scanner exists** - The "Trivy + Snyk unified scanner" was a conceptual reference, not an implemented or planned task
3. **Native /flow:security supersedes the concept** - The existing security architecture (documented in build-docs/adr/ADR-005 through ADR-008) provides unified scanning through an adapter pattern

### Problem Statement

How should the flowspec security architecture handle:
1. Static Application Security Testing (SAST) - code analysis for vulnerabilities
2. Software Composition Analysis (SCA) - dependency vulnerability scanning
3. Container Security - container image scanning
4. Dynamic Application Security Testing (DAST) - runtime web application testing

And ensure:
- No duplication of effort across security initiatives
- Clear roadmap for scanner integration
- Maintainable architecture supporting multiple scanning tools
- Unified finding format across all scanners

### Current Security Implementation

The `/flow:security` system is already implemented with the following architecture:

| Component | ADR | Status | Description |
|-----------|-----|--------|-------------|
| Scanner Orchestration | ADR-005 | ✅ Implemented | Adapter-based pattern for integrating multiple scanners |
| AI Triage Engine | ADR-006 | ✅ Implemented | AI-powered vulnerability classification and prioritization |
| Unified Finding Format | ADR-007 | ✅ Implemented | Cross-scanner normalized security finding data model |
| MCP Server Integration | ADR-008 | ✅ Implemented | External tool integration via Model Context Protocol |

**Implemented Scanners:**
- **Semgrep** (SAST) - Fast static analysis with OWASP ruleset, CWE mapping, and SARIF export
- **DAST Framework** (Playwright-based) - Dynamic application security testing support

**Architecture Highlights:**
- Adapter pattern enables adding new scanners without architectural changes
- Unified Finding Format (UFFormat) normalizes findings from all scanners
- Parallel execution with fingerprint-based deduplication
- AI-powered triage for false positive reduction
- Automated fix generation with code patches
- Comprehensive audit reporting

**Planned Scanner Additions:**
| Scanner | Type | Priority | Status |
|---------|------|----------|--------|
| CodeQL | SAST | P1 | Planned (task-225) |
| Trivy | SCA/Container | P2 | Planned |
| Snyk | SCA | P2 | Planned |
| Playwright DAST | DAST | P2 | Planned (task-222) |

### Alternatives Considered

#### Option 1: Separate Unified Scanner (Original task-198 Concept)
Build a standalone "unified vulnerability scanner" combining Trivy + Snyk outside the /flow:security architecture.

**Pros:**
- Focused tool for dependency/container scanning
- Could be used independently of flowspec

**Cons:**
- Duplicates orchestration logic already in /flow:security
- Creates two competing security tools in the same project
- Fragments security findings across two systems
- Increases maintenance burden (two codebases)
- Confuses users ("which scanner should I use?")

**Verdict:** Rejected - duplicates existing capability

#### Option 2: Integrate Trivy/Snyk into /flow:security (Adapter Pattern)
Extend the existing /flow:security architecture to support SCA and container scanning via new adapters.

**Pros:**
- Single unified security interface for all scanning
- Reuses existing orchestration, triage, reporting infrastructure
- Findings automatically normalized to UFFormat
- AI triage works across all scanner types
- Consistent user experience
- Maintainable (one architecture, multiple adapters)

**Cons:**
- Slightly more complex adapter layer
- Requires Trivy/Snyk integration work

**Verdict:** **SELECTED** - Best architecture alignment

#### Option 3: Keep Separate with Integration Layer
Build separate tools but create an integration layer to share findings.

**Pros:**
- Tools can evolve independently
- Separation of concerns

**Cons:**
- Complex integration layer required
- Duplicates triage and reporting logic
- Multiple user interfaces to learn
- Higher testing complexity

**Verdict:** Rejected - unnecessary complexity

## Decision

**We will use the existing `/flow:security` adapter-based architecture as the sole security scanning system in flowspec.**

### Architecture Principles

1. **Single Security Interface**: `/flow:security` commands provide unified access to all scanning capabilities
2. **Adapter Pattern**: Each scanner (Semgrep, CodeQL, Trivy, Snyk, DAST) integrates via a scanner adapter
3. **Unified Finding Format**: All scanners output findings in UFFormat (CWE-based, SARIF-compatible)
4. **Composable Scanning**: Users can select scanners based on need (`--tool semgrep|codeql|trivy|all`)
5. **AI-Powered Triage**: All findings flow through AI triage engine regardless of source scanner

### Scanner Integration Roadmap

**Phase 1: SAST (Completed)**
- ✅ Semgrep adapter with OWASP ruleset
- ✅ AI triage engine (classification, risk scoring, clustering)
- ✅ Automated fix generation
- ✅ Audit reporting

**Phase 2: Advanced SAST (Planned - Q1 2026)**
- 🔲 CodeQL adapter (task-225) - Deep dataflow analysis
- 🔲 MCP integration for external scanners

**Phase 3: SCA and Container Scanning (Planned - Q2 2026)**
- 🔲 Trivy adapter - Container image + dependency scanning
- 🔲 Snyk adapter (optional) - Commercial SCA with fix PRs
- 🔲 Unified triage across SAST + SCA findings

**Phase 4: DAST (Planned - Q2 2026)**
- 🔲 Playwright DAST adapter (task-222) - Web application testing
- 🔲 Integration with /flow:validate workflow

### Command Structure

```bash
# Run all available scanners
/flow:security scan

# Run specific scanner type
/flow:security scan --tool semgrep      # SAST only
/flow:security scan --tool trivy        # SCA + container only
/flow:security scan --tool all          # SAST + SCA + DAST

# AI-powered triage (works on all findings)
/flow:security triage

# Generate fixes (works on all finding types)
/flow:security fix

# Comprehensive audit report (includes all scanners)
/flow:security audit
```

### Resolution of task-198 Confusion

**task-198 Status**: COMPLETE (repurposed to Event Model Schema for Hooks)
- task-198 is NOT about vulnerability scanning
- The event model schema work is complete and unrelated to security
- No conflict exists between task-198 and /flow:security

**task-220 Resolution**: COMPLETE (this ADR)
- No "unified vulnerability scanner" task exists to supersede
- The /flow:security architecture already provides unified scanning
- Future scanners (Trivy, Snyk) will integrate via adapters

### Primary Reasons

1. **Architectural Coherence**: Single security architecture is simpler and more maintainable than multiple competing systems

2. **Reuse of Infrastructure**: Triage engine, fix generation, and reporting work across all scanner types

3. **Unified User Experience**: Developers learn one set of commands, not multiple tools

4. **Adapter Pattern Proven**: Existing Semgrep adapter demonstrates extensibility - adding Trivy/Snyk follows same pattern

5. **No Duplication**: Avoids building a second orchestration layer, triage system, and reporting engine

6. **Future-Proof**: Easy to add new scanners (Grype, osv-scanner, etc.) as adapters

## Consequences

### Positive

1. **Clear Direction**: No ambiguity about security architecture - /flow:security is the answer
2. **Extensible**: Adapter pattern makes adding scanners straightforward
3. **Consistent**: All findings normalized to UFFormat enables uniform triage and reporting
4. **Maintainable**: Single codebase for security infrastructure
5. **User-Friendly**: One interface for all security scanning needs

### Negative

1. **Single Point of Failure**: If /flow:security has bugs, affects all scanner integrations
   - **Mitigation**: Comprehensive test coverage (>80%), adapter isolation
2. **Dependency Growth**: More scanners = more dependencies
   - **Mitigation**: Adapters check availability, provide install instructions

### Neutral

1. **Work Required**: Trivy and Snyk adapters need to be built
   - **Timeline**: Q2 2026 based on priority
2. **Learning Curve**: New users must learn /flow:security commands
   - **Mitigation**: Comprehensive documentation (docs/guides/security-quickstart.md)

## Implementation

### Completed

1. ✅ Scanner orchestration pattern (ADR-005 in build-docs/adr/)
2. ✅ Semgrep SAST adapter
3. ✅ AI triage engine (ADR-006)
4. ✅ Unified Finding Format (ADR-007)
5. ✅ MCP server architecture (ADR-008)
6. ✅ Automated fix generation
7. ✅ Security audit reporting
8. ✅ This ADR documenting resolution

### Remaining Work

1. 🔲 CodeQL adapter (task-225) - P1
2. 🔲 Trivy adapter - P2 (create task)
3. 🔲 Snyk adapter - P2 (create task)
4. 🔲 Playwright DAST adapter (task-222) - P2
5. 🔲 Update task-220 with resolution notes
6. 🔲 Archive task-220 as complete

### No Changes Required

- No architectural changes needed
- No refactoring of existing /flow:security code
- No migration path (no legacy system exists)

## Validation

### Success Criteria

1. **Single Source of Truth**: /flow:security is the only security scanning interface ✅
2. **Clear Roadmap**: Scanner integration priority documented ✅
3. **No Confusion**: task-198 vs /flow:security resolved ✅
4. **Extensibility**: Adapter pattern supports future scanners ✅

### Metrics

- **Scanner Coverage**: SAST (✅ 1/2), SCA (⏳ 0/2), DAST (⏳ 0/1), Container (⏳ 0/1)
- **Finding Normalization**: 100% of findings mapped to UFFormat ✅
- **User Adoption**: Target >80% of flowspec projects using /flow:security
- **False Positive Rate**: Target <10% after AI triage

### Red Flags

- **Adapter Complexity**: If new adapters require >2 days to build, pattern may need refinement
- **Performance**: If scanning >1M LOC takes >10 minutes, need optimization
- **Fragmentation**: If teams bypass /flow:security, indicates UX issues

## Related Decisions

- **build-docs/adr/ADR-005**: Scanner Orchestration Pattern (original architecture)
- **build-docs/adr/ADR-006**: AI Triage Engine Design
- **build-docs/adr/ADR-007**: Unified Security Finding Format
- **build-docs/adr/ADR-008**: Security MCP Server Architecture
- **build-docs/adr/ADR-009**: task-198 Scanner Resolution (clarifies task-198 repurposing)
- **ADR-003**: Branch Naming Convention (PR workflow for security fixes)

## References

- **PRD**: build-docs/prd/flowspec-security-commands.md - Complete security commands specification
- **task-198**: backlog/archive/tasks/task-198 - Event Model Schema (unrelated to scanning)
- **task-220**: backlog/tasks/task-220 - This resolution task
- **task-225**: backlog/tasks/task-225 - CodeQL integration (next scanner)
- **task-222**: Playwright DAST integration (future work)

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-19 | 1.0 | Software Architect | Initial decision resolving task-220 |
