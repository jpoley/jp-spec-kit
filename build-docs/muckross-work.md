 Key Documents for Action-Event System

  Primary PRD

  - docs/prd/agent-hooks-prd.md - Main requirements document for the hooks/event system

  Architecture & Design

  - docs/adr/ADR-005-event-model-architecture.md - Event model schema, taxonomy, and payload structure
  - docs/adr/ADR-006-hook-execution-model.md - How hooks are executed
  - docs/adr/ADR-007-hook-configuration-schema.md - Hook configuration format
  - docs/architecture/agent-hooks-architecture.md - Overall architecture

  ADRs (Related)

  - docs/adr/ADR-003-stop-hook-quality-gate.md - Stop hook quality gate pattern
  - docs/adr/adr-session-start-hook.md - Session start hook

  Implementation Guides

  - docs/guides/hooks-quickstart.md - Getting started with hooks
  - docs/platform/hook-testing-strategy.md - Testing hooks
  - docs/platform/hook-security-framework.md - Security considerations
  - docs/platform/hook-cicd-integration.md - CI/CD integration
  - docs/platform/hook-observability.md - Observability for hooks

  Assessment & Case Studies

  - docs/assess/agent-hooks-assessment.md - Complexity and risk analysis
  - docs/case-studies/01-workflow-hook-system.md - Case study

  Upstream Contributions

  - docs/upstream-contributions/hooks-api.md - API design
  - docs/upstream-contributions/backlog-hooks-design.md - Backlog.md integration

  The core event model is defined in ADR-005-event-model-architecture.md with event types like workflow.assessed, spec.created, task.created, etc.


-------
Here are the action-event system related tasks:

  Event Emission Tasks

  | Task        | Priority | Status | Description                                                 |
  |-------------|----------|--------|-------------------------------------------------------------|
  | task-204    | HIGH     | To Do  | Integrate Event Emission into Backlog Task Operations       |
  | task-204.01 | MEDIUM   | To Do  | Create git hook to emit events on backlog task file changes |
  | task-204.02 | MEDIUM   | Done   | Create backlog CLI wrapper with auto-emit events            |
  | task-204.03 | LOW      | To Do  | Contribute hooks/events feature to upstream backlog.md      |

  Hook System Tasks

  | Task     | Priority | Status | Description                                                        |
  |----------|----------|--------|--------------------------------------------------------------------|
  | task-385 | HIGH     | Done   | Integrate Lifecycle Hooks into Backlog CLI                         |
  | task-402 | HIGH     | To Do  | Task Memory: Upstream contribution to backlog CLI for hook support |
  | task-377 | HIGH     | Done   | Task Memory: Claude Code integration via hooks and MCP (Phase 3)   |
  | task-370 | HIGH     | To Do  | Task Memory: Lifecycle integration with backlog.md (Phase 2)       |
  | task-473 | HIGH     | To Do  | claude-improves: Enable hooks by default in flowspec init           |
  | task-283 | MEDIUM   | To Do  | Create post-workflow-archive.sh hook for agent-triggered archiving |

  Related Telemetry/Event Tasks

  | Task     | Priority | Status      | Description                                          |
  |----------|----------|-------------|------------------------------------------------------|
  | task-403 | MEDIUM   | To Do       | Telemetry: Core telemetry module with event tracking |
  | task-405 | MEDIUM   | To Do       | Telemetry: Event integration with role system        |
  | task-366 | LOW      | In Progress | Telemetry: Role Usage Analytics Framework            |

  Pre-commit Hook Tasks

  | Task     | Priority | Status | Description                                                |
  |----------|----------|--------|------------------------------------------------------------|
  | task-334 | MEDIUM   | To Do  | Create pre-commit hook for agent sync                      |
  | task-328 | MEDIUM   | To Do  | Design: Git Hook Integration for Agent Sync                |
  | task-251 | LOW      | To Do  | Create Pre-commit Hook Configuration for Security Scanning |
  | task-482 | HIGH     | To Do  | claude-improves: Add pre-commit configuration template     |
