# Muckross Machine - December 5th Sprint Plan

## Overview

Muckross is responsible for the **security scanning platform** - the `/flow:security` command suite including scanning, AI triage, fix generation, and reporting.

## Task Status Summary

### Completed (6 tasks)
| Task | Description | Status |
|------|-------------|--------|
| task-211 | Implement Semgrep Scanner Orchestration Module | Done |
| task-215 | Implement /flow:security CLI Commands | Done |
| task-247 | Plan /flow:security Architecture and Platform | Done |
| task-249 | Implement Tool Dependency Management Module | Done |
| task-255 | Implement ADR-005: Scanner Orchestration Pattern | Done |
| task-256 | Implement ADR-006: AI Triage Engine Design | Done |
| task-257 | Implement ADR-007: Unified Security Finding Format | Done |

### In Progress (3 tasks)
| Task | Description | Assignee | Notes |
|------|-------------|----------|-------|
| task-212 | Build AI-Powered Vulnerability Triage Engine | @backend-engineer | AC 1-5 done, AC 6 needs benchmark |
| task-258 | Implement ADR-008: Security MCP Server | @backend-engineer | AC 1-9,13 done, needs examples/testing |
| task-261 | Add dev-setup validation pre-commit hook | - | Infrastructure task |

### Remaining To Do (20 tasks)

#### HIGH Priority - Core Security Features (9 tasks)
| Task | Description | Dependencies | Est. Effort |
|------|-------------|--------------|-------------|
| task-280 | Benchmark AI Triage Engine Accuracy | task-212 | 3-4 days |
| task-213 | Implement Automated Fix Generation | task-212 | 3-4 days |
| task-214 | Build Security Audit Report Generator | task-212 | 2.5-3.5 days |
| task-216 | Integrate /flow:security with Workflow | task-215 | 2-3 days |
| task-218 | Write Security Commands Documentation | task-215 | 1-2 days |
| task-219 | Build Security Commands Test Suite | task-215 | 2-3 days |
| task-221 | Implement Security Expert Personas | task-212 | 2-3 days |
| task-222 | Implement Playwright DAST | None | 3-4 days |
| task-248 | Setup CI/CD Security Scanning Pipeline | task-211 | 2-3 days |

#### MEDIUM Priority - Extended Features (7 tasks)
| Task | Description | Dependencies | Est. Effort |
|------|-------------|--------------|-------------|
| task-217 | Build Security Configuration System | None | 2-3 days |
| task-223 | Implement Custom Security Rules | task-211 | 2-3 days |
| task-224 | Design Security Scanner MCP Server | task-258 | 3-4 days |
| task-225 | Integrate CodeQL Deep Dataflow | task-211, task-249 | 3-4 days |
| task-250 | Implement Security Scanning Observability | task-211 | 2-3 days |
| task-252 | Implement Security Policy as Code | task-217 | 2-3 days |
| task-253 | Track DORA Metrics for Security | task-250 | 1-2 days |

#### LOW Priority - Advanced/Optional (4 tasks)
| Task | Description | Dependencies | Est. Effort |
|------|-------------|--------------|-------------|
| task-220 | Resolve task-198 Unified Scanner Relationship | task-211 | 1 day |
| task-226 | Implement AFL++ Fuzzing Support | None | 3-4 days |
| task-251 | Pre-commit Hook for Security Scanning | task-248 | 1 day |
| task-254 | Build Security Scanner Docker Image | task-248 | 2-3 days |

---

## Execution Order

### Wave 1: Complete In-Progress Tasks
Finish what's started before adding new work.

1. **task-212** - Complete AC #6 (benchmark accuracy)
   - Blocked by: task-280 (benchmark dataset)
   - Action: Start task-280 first, then validate task-212

2. **task-258** - Complete AC #10-12 (examples, testing)
   - AC #10: Create Claude agent example
   - AC #11: Create cross-repo dashboard example
   - AC #12: Test with MCP Inspector

3. **task-261** - Complete pre-commit hook
   - Infrastructure task, quick win

### Wave 2: Benchmark & Validation
Validate AI triage accuracy before building dependent features.

4. **task-280** - Benchmark AI Triage Engine Accuracy
   - **CRITICAL**: Validates task-212 AC #6
   - Creates benchmark dataset (100+ findings)
   - Target: >85% accuracy
   - Must complete before task-213, task-214, task-221

### Wave 3: Core Security Commands
Build the remaining /flow:security subcommands.

5. **task-213** - Automated Fix Generation
   - Enables: `/flow:security fix`
   - Dependencies: task-212 (triage engine)
   - Pattern library for 5 CWE categories

6. **task-214** - Security Audit Report Generator
   - Enables: `/flow:security audit`
   - Dependencies: task-212 (triage results)
   - Multi-format output (MD, HTML, PDF, SARIF)

7. **task-218** - Security Commands Documentation
   - Document all /flow:security subcommands
   - Usage examples, configuration reference

8. **task-219** - Security Commands Test Suite
   - Integration tests for security commands
   - Mock scanners for CI testing

### Wave 4: Workflow Integration
Integrate security into the SDD workflow.

9. **task-216** - Integrate with Workflow and Backlog
   - Hook into /flow:validate phase
   - Auto-create security tasks from findings
   - Track remediation progress

10. **task-248** - CI/CD Security Scanning Pipeline
    - GitHub Actions workflow
    - SARIF upload to Code Scanning
    - Fail builds on critical findings

### Wave 5: Enhanced Capabilities
Add advanced features after core is stable.

11. **task-221** - Security Expert Personas
    - Different triage perspectives (offensive, defensive, compliance)
    - Improves accuracy via multi-perspective

12. **task-222** - Playwright DAST
    - Web security testing
    - Authentication flow testing
    - XSS/CSRF detection

13. **task-217** - Security Configuration System
    - Centralized config for all security features
    - Per-project customization

14. **task-223** - Custom Security Rules
    - User-defined Semgrep rules
    - Organization-specific patterns

### Wave 6: Deep Analysis (Deferred)
Lower priority, can be scheduled later.

15. **task-225** - CodeQL Deep Dataflow
    - Complex vulnerability detection
    - Requires tool installation (task-249 done)

16. **task-250** - Security Scanning Observability
17. **task-252** - Security Policy as Code
18. **task-253** - DORA Metrics for Security

### Wave 7: Optional/Future
Schedule based on demand.

19. **task-220** - Resolve task-198 relationship
20. **task-226** - AFL++ Fuzzing (optional)
21. **task-251** - Pre-commit hook
22. **task-254** - Docker image

---

## Immediate Next Steps (Dec 5)

### Morning Session
1. **Complete task-261** - Pre-commit hook (1-2 hrs)
2. **Start task-280** - Begin curating benchmark dataset

### Afternoon Session
3. **Continue task-280** - Benchmark dataset curation (4-6 hrs)
   - Collect 100+ findings with ground truth
   - Cover 5 CWE categories
   - Expert validation

### Evening Session
4. **Complete task-258** - MCP server examples (2-3 hrs)
   - Create Claude agent example
   - Test with MCP Inspector

---

## Dependencies Graph

```
task-212 (Triage Engine) [IN PROGRESS - AC6 blocked]
    │
    ├── task-280 (Benchmark) ← START HERE
    │       │
    │       └── Validates task-212 AC#6 (>85% accuracy)
    │
    ├── task-213 (Fix Generation)
    │       └── Uses triage results
    │
    ├── task-214 (Report Generator)
    │       └── Uses triage results
    │
    └── task-221 (Expert Personas)
            └── Enhances triage accuracy

task-211 (Scanner Orchestration) [DONE]
    │
    ├── task-222 (Playwright DAST)
    ├── task-223 (Custom Rules)
    ├── task-225 (CodeQL)
    └── task-248 (CI/CD Pipeline)

task-258 (MCP Server) [IN PROGRESS - needs examples]
    │
    └── task-224 (Security Scanner MCP)

task-215 (CLI Commands) [DONE]
    │
    ├── task-216 (Workflow Integration)
    ├── task-218 (Documentation)
    └── task-219 (Test Suite)
```

---

## Risk Notes

1. **task-280 Benchmark** - Expert validation requires manual effort
2. **task-212 Accuracy** - May not hit >85% without multiple iterations
3. **task-225 CodeQL** - Installation complexity on Linux
4. **task-222 Playwright** - Browser automation can be flaky

## Branch Naming Convention

Follow established pattern:
```
muckross-task-{number}-{short-description}
```

Examples:
- `muckross-task-280-benchmark-triage`
- `muckross-task-213-fix-generator`
- `muckross-task-214-audit-reports`

---

## Success Metrics

- [ ] task-212 achieves >85% triage accuracy (validated by task-280)
- [ ] All HIGH priority tasks complete by end of week
- [ ] Security commands fully documented (task-218)
- [ ] CI/CD pipeline operational (task-248)
- [ ] All changes have passing tests
