# PRD: Flowspec Platform & DevSecOps

**Related Tasks**: task-085, task-136, task-168, task-171, task-184, task-195, task-196, task-197, task-249

---

## Requirements Traceability Matrix

| Task ID | Task Title | Domain | Priority | Functional Req |
|---------|-----------|--------|----------|----------------|
| task-184 | Add permissions.deny Security Rules | Security Layer | High | FR-SEC-001, FR-SEC-002 |
| task-249 | Implement Tool Dependency Management Module | Tool Management | High | FR-TOOL-001 to FR-TOOL-005 |
| task-085 | Local CI Simulation Script | CI/CD | Medium | FR-CI-001, FR-CI-002 |
| task-168 | Add macOS CI Matrix Testing | CI/CD | Low | FR-CI-003 |
| task-136 | Add Primary Support for claude-trace Observability | Observability | Medium | FR-OBS-001 |
| task-171 | Research library documentation MCP replacement | Developer Experience | Medium | FR-DX-001 |
| task-195 | Create Flowspec Plugin Package | Developer Experience | Low | FR-DX-002 (deferred) |
| task-196 | Experiment with Output Styles for Workflow Phases | Developer Experience | Low | FR-DX-003 (exploratory) |
| task-197 | Create Custom Statusline with Workflow Context | Developer Experience | Low | FR-DX-004 (future) |

---

## Executive Summary

### Problem Statement

Flowspec users face critical platform challenges:

1. **Security Gaps**: No default protection against accidental exposure of sensitive files (.env, credentials, secrets)
2. **Slow Feedback Loops**: Developers wait 5-15 minutes for GitHub Actions feedback
3. **Limited Observability**: No visibility into AI agent decision-making or token usage
4. **Cross-Platform Fragility**: Scripts may fail on macOS without testing
5. **Tool Management Overhead**: Manual installation of Semgrep, CodeQL, act creates friction

### Proposed Solution

Build a comprehensive platform infrastructure layer:

1. **Security Layer** (High Priority) - Default permissions.deny rules, audit logging
2. **Local CI/CD** (High Priority) - act-based local runner providing <1 minute feedback
3. **Observability** (Medium Priority) - claude-trace integration for debugging
4. **Tool Management** (High Priority) - Auto-installation with version pinning
5. **Developer Experience** (Low Priority) - Plugin packaging, output styles, statusline

### Success Metrics (DORA Elite Targets)

| Metric | Current | Target |
|--------|---------|--------|
| Lead Time | 2-4 hours | <1 hour |
| Deployment Frequency | 1/day | 5-10/day |
| Change Failure Rate | 25-30% | <15% |
| MTTR | 2 hours | <1 hour |

## Platform Principles

1. **Security by Default** - Permissions deny sensitive files by default
2. **Developer Velocity First** - Local CI <1 min feedback
3. **Observable by Default** - claude-trace captures all operations
4. **Environment Parity** - Local dev matches CI/CD environment
5. **Composability Over Monoliths** - Small, focused tools

## Functional Requirements

### FR-SEC: Security Layer (task-184)

**FR-SEC-001**: File Protection
- Block read/write to .env, secrets/, credentials/, *.pem, *.key
- Block modifications to lock files (package-lock.json, uv.lock)
- Audit log all permission denials

**FR-SEC-002**: Command Protection
- Block dangerous commands: sudo, rm -rf /, dd, mkfs, chmod 777
- Require confirmation for destructive operations
- Provide override mechanism with audit trail

### FR-TOOL: Tool Dependency Management (task-249)

**FR-TOOL-001**: Tool Discovery Chain
- Check PATH → venv → cache → download (in order)
- Support Semgrep (pip), CodeQL (binary), act (binary)

**FR-TOOL-002**: Version Pinning
- Store versions in `.specify/versions.lock.json`
- SLSA Level 2 compliance with checksums

**FR-TOOL-003**: Cache Management
- Default cache location: `~/.cache/specify-tools/`
- 500MB threshold with LRU eviction
- `specify tools cache --clear` command

**FR-TOOL-004**: Offline Mode
- `--offline` flag uses cached tools only
- Error if required tool not in cache

**FR-TOOL-005**: Auto-Installation
- First use triggers install with user notification
- Progress indicator for large downloads

### FR-CI: Local CI/CD (task-085, task-168)

**FR-CI-001**: Local GitHub Actions Execution
- `run-local-ci.sh` script using act
- Support selective job execution: `--job lint`, `--job test`
- <1 minute for lint-only, <5 minutes for full pipeline

**FR-CI-002**: Environment Parity
- Use same Docker images as GitHub Actions
- Match environment variables and secrets handling

**FR-CI-003**: Cross-Platform Support (task-168)
- CI matrix includes ubuntu-latest and macos-latest
- Platform-specific test skips where needed

### FR-OBS: Observability (task-136)

**FR-OBS-001**: claude-trace Integration
- Documentation for trace collection setup
- Troubleshooting guide with examples
- Token usage tracking guidance

### FR-DX: Developer Experience (task-171, task-195, task-196, task-197)

**FR-DX-001**: Library Documentation MCP (task-171)
- Research MCP alternatives for library docs
- Evaluate context7, devdocs-mcp options

**FR-DX-002**: Plugin Packaging (task-195) - Deferred to P3
**FR-DX-003**: Output Styles (task-196) - Exploratory
**FR-DX-004**: Statusline (task-197) - Future enhancement

## Implementation Priority

**P0 (Must Have)**:
1. task-249: Tool Dependency Management (foundational)
2. task-184: Security Layer (foundational)

**P1 (Should Have)**:
3. task-085: Local CI (depends on task-249)
4. task-136: claude-trace Observability
5. task-171: MCP Documentation Research

**P2 (Could Have)**:
6. task-168: macOS CI (depends on task-085)
7. task-195, 196, 197: Future/Exploratory

## Out of Scope

- Windows support for local CI
- Custom security rule DSL
- Real-time trace visualization
- Token usage billing integration
