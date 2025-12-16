#!/bin/bash
# Create Agent Event System tasks
# This script creates all backlog tasks for the unified event system implementation
#
# ALL tasks include:
# - `agent-event-system` label for initiative tracking
# - `phase-N` label for phase identification
# - Domain-specific labels for filtering
#
# Corresponding planning document: docs/plan/agent-event-system-tasks.md

set -e

cd "$(dirname "$0")/.."

echo "=========================================="
echo "Agent Event System - Task Creation Script"
echo "=========================================="
echo ""

# =============================================================================
# PHASE 1: Foundation (6 tasks: 485-490)
# Core infrastructure for event schema, writing, routing, and configuration
# =============================================================================
echo "Creating Phase 1: Foundation tasks..."

# Note: Phase 1.1 (task-485) and Phase 1.2 (task-486) already created manually
# Skipping to avoid duplicates

# Phase 1.3: Event Router
backlog task create "Implement Event Router with Namespace Dispatch" \
  -d "Create event routing system dispatching events to handlers based on namespace with pluggable consumers." \
  --ac "EventRouter class with register_handler method" \
  --ac "Pattern matching supports wildcards like git.* matches all git events" \
  --ac "Built-in handlers for JSONL file and MCP server" \
  --ac "Event filtering by task_id agent_id time_range" \
  --ac "Unit tests for routing to multiple handlers" \
  -l "agent-event-system,phase-1,architecture,infrastructure,foundation" \
  --dep task-485 \
  --priority high --plain

# Phase 1.4: Event Query CLI
backlog task create "Implement Event Query CLI and API" \
  -d "Build jq-based query utilities and Python API for event analysis with CLI interface." \
  --ac "CLI command specify events query with filters" \
  --ac "Python module flowspec.events.query with fluent API" \
  --ac "Export capabilities JSON CSV markdown" \
  --ac "Aggregation functions count_by group_by time_series" \
  --ac "Query 100k events in under 5 seconds" \
  -l "agent-event-system,phase-1,architecture,infrastructure,foundation" \
  --dep task-485 \
  --priority medium --plain

# Phase 1.5: Git Workflow Config Schema
backlog task create "Create Git Workflow Configuration Schema" \
  -d "Define YAML schema for git-workflow.yml with worktree local_pr signing isolation sections." \
  --ac "Configuration schema with all required sections documented" \
  --ac "Default configuration template with comments" \
  --ac "Validation command flowspec workflow config validate" \
  --ac "Environment variable override support" \
  --ac "Documentation in docs reference" \
  -l "agent-event-system,phase-1,infrastructure,configuration" \
  --priority high --plain

# Phase 1.6: Config Loader
backlog task create "Implement Configuration Loader with Validation" \
  -d "Build configuration loader that validates and merges defaults with user overrides." \
  --ac "Configuration class GitWorkflowConfig in Python" \
  --ac "Load from git-workflow.yml with fallback to defaults" \
  --ac "Emit system.config_change event on reload" \
  --ac "CLI command specify config show" \
  --ac "Unit tests for all config sections" \
  -l "agent-event-system,phase-1,infrastructure,configuration" \
  --priority high --plain

echo "Phase 1 complete."
echo ""

# =============================================================================
# PHASE 2: Event Emission Integration (4 tasks: 492-495)
# Wire event emission into hooks, backlog, git, and MCP
# =============================================================================
echo "Creating Phase 2: Event Emission Integration tasks..."

# Phase 2.1: Hook Integration
backlog task create "Integrate Claude Code Hooks with Event Emission" \
  -d "Wire Claude Code hooks to emit events using unified schema. Extends hook infrastructure." \
  --ac "All 10 Claude Code hook types emit events" \
  --ac "Events include proper context with task_id branch_name" \
  --ac "Correlation IDs propagated across hook chains" \
  --ac "Performance impact under 50ms per hook" \
  --ac "Backward compatible with existing hook configurations" \
  -l "agent-event-system,phase-2,architecture,hooks,event-emission" \
  --dep task-486 \
  --priority high --plain

# Phase 2.2: Backlog Event Integration (extends task-204)
backlog task create "Integrate Backlog Operations with Event Emission" \
  -d "Emit task events on backlog operations. Extends task-204 with full event schema support." \
  --ac "task.created event on backlog task create" \
  --ac "task.state_changed event on status updates" \
  --ac "task.ac_checked event on acceptance criteria completion" \
  --ac "task.assigned event on assignee changes" \
  --ac "Events include full task metadata in task object" \
  -l "agent-event-system,phase-2,architecture,backlog-integration,event-emission" \
  --dep task-204 \
  --priority high --plain

# Phase 2.3: Git Operation Events (extends task-204.01)
backlog task create "Integrate Git Operations with Event Emission" \
  -d "Emit git events on branch commits push and merge operations. Extends task-204.01." \
  --ac "git.commit event on every commit with sha message" \
  --ac "git.branch_created and git.branch_deleted events" \
  --ac "git.pushed event on push to remote" \
  --ac "git.merged event on merge completion" \
  --ac "Events include GPG signing info when available" \
  -l "agent-event-system,phase-2,architecture,scm,event-emission" \
  --dep task-204.01 \
  --priority high --plain

# Phase 2.4: MCP Server Integration
backlog task create "Integrate MCP Server with Event Emission" \
  -d "Enable event emission to MCP server for real-time observability and agent coordination." \
  --ac "MCP tool emit_event available to agents" \
  --ac "Events routed to MCP in addition to JSONL" \
  --ac "Configurable MCP endpoint in git-workflow.yml" \
  --ac "Graceful degradation if MCP unavailable" \
  --ac "Integration tests with agent-updates-collector" \
  -l "agent-event-system,phase-2,architecture,mcp,event-emission" \
  --priority medium --plain

echo "Phase 2 complete."
echo ""

# =============================================================================
# PHASE 3: Action System (4 tasks: 496-499)
# Implement 55 actions with lifecycle, decorators, and validation
# =============================================================================
echo "Creating Phase 3: Action System tasks..."

# Phase 3.1: Action Registry
backlog task create "Implement Action Registry with 55 Actions" \
  -d "Create registry for 55 actions across 18 categories as defined in action-system.md." \
  --ac "ActionRegistry class with register and lookup methods" \
  --ac "All 55 actions from documentation registered" \
  --ac "Actions categorized by domain and category" \
  --ac "Input and output contracts defined per action" \
  --ac "Idempotency and side-effects documented per action" \
  -l "agent-event-system,phase-3,architecture,action-system" \
  --priority high --plain

# Phase 3.2: Action Decorator System
backlog task create "Implement Action Decorator and Helper System" \
  -d "Create Python decorator for defining actions with automatic event emission and validation." \
  --ac "action decorator with verb domain category parameters" \
  --ac "Automatic action.invoked event on execution start" \
  --ac "Automatic action.succeeded or action.failed on completion" \
  --ac "Input validation against action contract" \
  --ac "Duration tracking in action events" \
  -l "agent-event-system,phase-3,architecture,action-system" \
  --priority high --plain

# Phase 3.3: Action-Event Mapping
backlog task create "Implement Action to Event Mapping" \
  -d "Implement automatic mapping from action execution to event emission as per action-system.md." \
  --ac "Every accepted action emits action.invoked" \
  --ac "Guaranteed terminal event succeeded failed or aborted" \
  --ac "Side-effect events emitted as documented" \
  --ac "Mapping table matches action-system.md documentation" \
  --ac "Unit tests validate all 55 action mappings" \
  -l "agent-event-system,phase-3,architecture,action-system" \
  --priority high --plain

# Phase 3.4: Allowed Followups Validation
backlog task create "Implement Allowed Followups Validation" \
  -d "Validate action sequences against allowed followups graph from action-system.md." \
  --ac "Followup graph defined matching documentation" \
  --ac "ValidationError on invalid action sequence" \
  --ac "Warnings logged for unusual but allowed sequences" \
  --ac "Query API for valid next actions given current state" \
  --ac "Visualization of followup graph available" \
  -l "agent-event-system,phase-3,architecture,action-system" \
  --priority medium --plain

echo "Phase 3 complete."
echo ""

# =============================================================================
# PHASE 4: Git Workflow (10 tasks: 500-509)
# Worktree automation, local PR gates, and GPG signing
# =============================================================================
echo "Creating Phase 4: Git Workflow tasks..."

# Phase 4.1: Worktree Creation
backlog task create "Implement Worktree Creation Automation" \
  -d "Create script to generate git worktrees for tasks with proper branch naming." \
  --ac "Script worktree-create.sh task-id feature-description" \
  --ac "Creates worktree at worktrees/task-id-feature-description" \
  --ac "Creates branch from configured base branch" \
  --ac "Emits git.branch_created and git.worktree_created events" \
  --ac "Validates task exists in backlog before creating" \
  -l "agent-event-system,phase-4,infrastructure,scm,git-workflow" \
  --priority high --plain

# Phase 4.2: Worktree Cleanup
backlog task create "Implement Worktree Cleanup Automation" \
  -d "Create cleanup automation for completed or abandoned task worktrees." \
  --ac "Script worktree-cleanup.sh task-id" \
  --ac "Removes worktree safely checking for uncommitted changes" \
  --ac "Optionally deletes branch if merged" \
  --ac "Emits git.worktree_removed and git.branch_deleted events" \
  --ac "Post-merge hook triggers automatic cleanup" \
  -l "agent-event-system,phase-4,infrastructure,scm,git-workflow" \
  --priority medium --plain

# Phase 4.3: Git Hook Framework
backlog task create "Design Git Hook Framework for Local PR" \
  -d "Create extensible git hook framework with centralized dispatcher for quality gates." \
  --ac "Dispatcher script hook-dispatcher.sh" \
  --ac "Installation script install-hooks.sh" \
  --ac "Hook registration via symlinks in .git/hooks" \
  --ac "Event emission for all hook triggers" \
  --ac "Documentation for adding custom hooks" \
  -l "agent-event-system,phase-4,infrastructure,devops,cicd,git-workflow" \
  --priority high --plain

# Phase 4.4: Lint Quality Gate
backlog task create "Implement Pre-Commit Quality Gate - Lint" \
  -d "Create lint quality gate running configured linters before commit." \
  --ac "Pre-commit hook calls quality-gates/lint.sh" \
  --ac "Supports ruff eslint golangci-lint" \
  --ac "Emits quality_gate.started and quality_gate.passed or quality_gate.failed events" \
  --ac "Configurable skip with git commit no-verify" \
  --ac "Exit code 1 blocks commit on failure" \
  -l "agent-event-system,phase-4,infrastructure,quality,cicd,git-workflow" \
  --priority high --plain

# Phase 4.5: Test Quality Gate
backlog task create "Implement Pre-Commit Quality Gate - Test" \
  -d "Create test quality gate running relevant test suite before commit." \
  --ac "Pre-commit hook calls quality-gates/test.sh" \
  --ac "Runs pytest vitest or go test based on project" \
  --ac "Smart test selection for affected tests only" \
  --ac "Emits quality-gate events" \
  --ac "Configurable timeout default 600s" \
  -l "agent-event-system,phase-4,infrastructure,quality,cicd,git-workflow" \
  --priority high --plain

# Phase 4.6: SAST Quality Gate
backlog task create "Implement Pre-Commit Quality Gate - SAST" \
  -d "Create security scanning gate with bandit and semgrep." \
  --ac "Pre-commit hook calls quality-gates/sast.sh" \
  --ac "Runs bandit and semgrep" \
  --ac "Emits security.vulnerability_found events" \
  --ac "Fail on high or critical findings" \
  --ac "SARIF output stored in .flowspec/security/sarif" \
  -l "agent-event-system,phase-4,infrastructure,security,devsecops,cicd,git-workflow" \
  --priority high --plain

# Phase 4.7: Local PR Approval Workflow
backlog task create "Implement Local PR Approval Workflow" \
  -d "Create orchestrator running all quality gates and making approval decision." \
  --ac "Script local-pr-submit.sh" \
  --ac "Runs all configured checks in parallel where possible" \
  --ac "Implements approval modes auto human_required agent_review" \
  --ac "Emits git.local_pr_submitted and approved or rejected events" \
  --ac "Human approval workflow prompts for sign-off if required" \
  -l "agent-event-system,phase-4,infrastructure,cicd,devops,git-workflow" \
  --priority high --plain

# Phase 4.8: GPG Key Management Design
backlog task create "Design Agent GPG Key Management System" \
  -d "Design secure key storage and registration system for agent identities." \
  --ac "Key storage at .flowspec/agent-keys with gitignore" \
  --ac "Key registry file keyring.txt" \
  --ac "Public keys in repo private keys in secure storage" \
  --ac "Key rotation strategy documented" \
  --ac "Emit system.config_change on key registration" \
  -l "agent-event-system,phase-4,infrastructure,security,devsecops,git-workflow" \
  --priority high --plain

# Phase 4.9: GPG Key Generation
backlog task create "Implement GPG Key Generation for Agents" \
  -d "Create automation to generate unique GPG keys for each agent." \
  --ac "Script gpg-setup-agent.sh agent-id" \
  --ac "Generates 4096-bit RSA key non-interactively" \
  --ac "Registers key in keyring with agent ID mapping" \
  --ac "Exports public key to agent-keys directory" \
  --ac "Emits security.gpg_key_generated event" \
  -l "agent-event-system,phase-4,infrastructure,security,devsecops,git-workflow" \
  --priority high --plain

# Phase 4.10: Automated Commit Signing
backlog task create "Implement Automated Commit Signing" \
  -d "Configure git to automatically sign commits with agent GPG keys." \
  --ac "Post-commit hook emits git.commit with GPG info" \
  --ac "Git config automatically set for agent identity" \
  --ac "Verify signatures before push" \
  --ac "Reject unsigned commits in CI if required" \
  --ac "Support co-authored-by for multi-agent collaboration" \
  -l "agent-event-system,phase-4,infrastructure,security,scm,git-workflow" \
  --priority medium --plain

echo "Phase 4 complete."
echo ""

# =============================================================================
# PHASE 5: Container Integration (5 tasks: 510-514)
# Devcontainer orchestration, secrets, and monitoring
# =============================================================================
echo "Creating Phase 5: Container Integration tasks..."

# Phase 5.1: Container Strategy
backlog task create "Design Container Orchestration Strategy" \
  -d "Design architecture for spinning up isolated containers per task with worktree mounts." \
  --ac "Architecture document in docs/guides/container-strategy.md" \
  --ac "Container naming convention documented" \
  --ac "Volume mount strategy worktree RW repo RO" \
  --ac "Network isolation modes documented" \
  --ac "Resource limits defined" \
  -l "agent-event-system,phase-5,infrastructure,devops,container" \
  --priority high --plain

# Phase 5.2: Container Launch
backlog task create "Implement Container Launch Automation" \
  -d "Create script to launch devcontainers with proper configuration." \
  --ac "Script container-launch.sh task-id agent-id" \
  --ac "Uses flowspec-agents base image" \
  --ac "Mounts worktree at /workspace" \
  --ac "Applies configured resource limits" \
  --ac "Emits container.started event with container ID" \
  -l "agent-event-system,phase-5,infrastructure,devops,container" \
  --priority high --plain

# Phase 5.3: Secret Injection
backlog task create "Implement Runtime Secret Injection" \
  -d "Securely inject secrets into running containers without baking into images." \
  --ac "Script inject-secrets.sh container-id" \
  --ac "Reads secrets from host keychain or secret service" \
  --ac "Injects via environment variables" \
  --ac "Secrets never written to disk or logs" \
  --ac "Emits container.secrets_injected event (secret names only, never values)" \
  -l "agent-event-system,phase-5,infrastructure,security,devsecops,container" \
  --priority high --plain

# Phase 5.4: Container Monitoring
backlog task create "Implement Container Resource Monitoring" \
  -d "Monitor container resource usage and emit events on limit hits." \
  --ac "Monitoring script monitor-containers.sh" \
  --ac "Runs in background checks every 30s" \
  --ac "Emits container.resource_limit_hit when >90%" \
  --ac "Logs resource usage to metrics file" \
  --ac "Graceful shutdown on persistent limit hits" \
  -l "agent-event-system,phase-5,infrastructure,observability,container" \
  --priority medium --plain

# Phase 5.5: Container Cleanup
backlog task create "Implement Container Cleanup Automation" \
  -d "Automatically stop and remove containers when tasks complete." \
  --ac "Cleanup triggered by task.completed or task.archived events" \
  --ac "Script container-cleanup.sh task-id" \
  --ac "Saves container logs before removal" \
  --ac "Emits container.stopped event with exit code" \
  --ac "Force-kill containers running >24 hours" \
  -l "agent-event-system,phase-5,infrastructure,devops,container" \
  --priority medium --plain

echo "Phase 5 complete."
echo ""

# =============================================================================
# PHASE 6: Decision Tracking (3 tasks: 515-517)
# Decision emission, querying, and reversibility assessment
# =============================================================================
echo "Creating Phase 6: Decision Tracking tasks..."

# Phase 6.1: Decision Event Helpers
backlog task create "Implement Decision Event Emission Helpers" \
  -d "Create helper functions for emitting well-formed decision events." \
  --ac "Function emit_decision with decision_id category message" \
  --ac "Reversibility assessment helper with type lock_in_factors cost" \
  --ac "Alternatives tracking with option rejected_reason pairs" \
  --ac "Supporting material links with url title type" \
  --ac "Integration with flowspec commands for automatic emission" \
  -l "agent-event-system,phase-6,architecture,decision-tracker" \
  --priority high --plain

# Phase 6.2: Decision Query Utilities
backlog task create "Implement Decision Query Utilities" \
  -d "Create utilities to query and analyze decision events from JSONL stream." \
  --ac "CLI command specify decisions list with filters" \
  --ac "Query by category reversibility_type time_range" \
  --ac "Export decision timeline as markdown" \
  --ac "Identify one-way-door decisions for review" \
  --ac "Link decisions to tasks and branches" \
  -l "agent-event-system,phase-6,architecture,decision-tracker" \
  --priority medium --plain

# Phase 6.3: Reversibility Assessment Tool
backlog task create "Implement Reversibility Assessment Tool" \
  -d "Create interactive tool for assessing decision reversibility with prompts." \
  --ac "CLI command specify decision assess" \
  --ac "Prompts for lock-in factors from predefined list" \
  --ac "Calculates reversal cost based on factors" \
  --ac "Suggests reversal window based on project phase" \
  --ac "Outputs formatted decision event ready for emission" \
  -l "agent-event-system,phase-6,architecture,decision-tracker" \
  --priority low --plain

echo "Phase 6 complete."
echo ""

# =============================================================================
# PHASE 7: State Machine and Automation (3 tasks: 518-520)
# Workflow state machine, recovery, and cleanup orchestration
# =============================================================================
echo "Creating Phase 7: State Machine and Automation tasks..."

# Phase 7.1: State Machine Implementation
backlog task create "Implement Git Workflow State Machine" \
  -d "Create event-driven state machine for git workflow transitions." \
  --ac "StateMachine class with states from git-workflow-objectives.md" \
  --ac "Transitions triggered by event_type matching" \
  --ac "Invalid transitions raise StateError" \
  --ac "Current state reconstructed from event replay" \
  --ac "Visualization of state machine as mermaid diagram" \
  -l "agent-event-system,phase-7,architecture,git-workflow,automation" \
  --priority high --plain

# Phase 7.2: State Recovery Utilities
backlog task create "Implement State Recovery Utilities" \
  -d "Create utilities for reconstructing workflow state from event replay." \
  --ac "Script state-machine.py with replay functionality" \
  --ac "Reconstruct task state worktree associations container mappings" \
  --ac "Handle corrupted or missing events gracefully" \
  --ac "Validate recovered state against current system state" \
  --ac "Tested with 1000+ event corpus" \
  -l "agent-event-system,phase-7,architecture,git-workflow,automation" \
  --priority medium --plain

# Phase 7.3: Automated Cleanup Orchestrator
backlog task create "Implement Automated Cleanup Orchestrator" \
  -d "Create orchestrator that monitors events and triggers cleanup actions." \
  --ac "CleanupOrchestrator class listening for completion events" \
  --ac "Triggers worktree cleanup on task.completed" \
  --ac "Triggers container cleanup on task.archived" \
  --ac "Configurable cleanup delays and conditions" \
  --ac "Emits lifecycle.cleanup_completed events" \
  -l "agent-event-system,phase-7,architecture,automation" \
  --priority medium --plain

echo "Phase 7 complete."
echo ""

# =============================================================================
# PHASE 8: Documentation and Testing (5 tasks: 521-525)
# Architecture docs, integration tests, benchmarks, DORA metrics, runbooks
# =============================================================================
echo "Creating Phase 8: Documentation and Testing tasks..."

# Phase 8.1: Architecture Documentation
backlog task create "Create Agent Event System Architecture Documentation" \
  -d "Create comprehensive architecture documentation with diagrams and guides." \
  --ac "Architecture overview document in docs/guides/event-system-architecture.md" \
  --ac "ASCII and mermaid diagrams for event flow" \
  --ac "Component interaction documentation" \
  --ac "API reference for all public functions" \
  --ac "Migration guide from legacy systems" \
  -l "agent-event-system,phase-8,documentation" \
  --priority high --plain

# Phase 8.2: Integration Tests
backlog task create "Create Event System Integration Tests" \
  -d "Create comprehensive integration test suite for event system." \
  --ac "End-to-end test task lifecycle emits correct events" \
  --ac "Test git workflow state machine transitions" \
  --ac "Test container lifecycle with event emission" \
  --ac "Test decision tracking workflow" \
  --ac "Coverage target 80% for event modules" \
  -l "agent-event-system,phase-8,testing,quality" \
  --priority high --plain

# Phase 8.3: Performance Benchmarks
backlog task create "Create Event System Performance Benchmarks" \
  -d "Create benchmarks for event emission query and storage performance." \
  --ac "Benchmark emit_event latency target under 10ms" \
  --ac "Benchmark query performance for 100k events" \
  --ac "Benchmark file rotation and archival" \
  --ac "Memory usage profiling for long-running agents" \
  --ac "CI integration to track performance regressions" \
  -l "agent-event-system,phase-8,testing,performance" \
  --priority medium --plain

# Phase 8.4: DORA Metrics Dashboard
backlog task create "Implement DORA Metrics Dashboard" \
  -d "Create dashboard displaying deployment frequency lead time CFR and MTTR from events." \
  --ac "CLI command specify metrics dora --dashboard" \
  --ac "Shows all four metrics with color-coded status" \
  --ac "Trend arrows showing improvement or degradation" \
  --ac "Exportable as JSON markdown or HTML" \
  --ac "GitHub Actions posts dashboard to PR comments" \
  -l "agent-event-system,phase-8,observability,devops" \
  --priority low --plain

# Phase 8.5: Operational Runbooks
backlog task create "Create Operational Runbooks for Event System" \
  -d "Create runbooks for incident response state recovery and troubleshooting." \
  --ac "Incident response runbook in docs/runbooks" \
  --ac "State recovery runbook with event replay procedures" \
  --ac "Performance troubleshooting runbook" \
  --ac "Secrets rotation runbook" \
  --ac "All runbooks tested with simulated scenarios" \
  -l "agent-event-system,phase-8,documentation,devops" \
  --priority medium --plain

echo "Phase 8 complete."
echo ""

# =============================================================================
# Summary
# =============================================================================
echo "=========================================="
echo "Task Creation Complete!"
echo "=========================================="
echo ""
echo "Created tasks for 8 phases:"
echo "  Phase 1: Foundation (4 new tasks, 2 existing)"
echo "  Phase 2: Event Emission Integration (4 tasks)"
echo "  Phase 3: Action System (4 tasks)"
echo "  Phase 4: Git Workflow (10 tasks)"
echo "  Phase 5: Container Integration (5 tasks)"
echo "  Phase 6: Decision Tracking (3 tasks)"
echo "  Phase 7: State Machine and Automation (3 tasks)"
echo "  Phase 8: Documentation and Testing (5 tasks)"
echo ""
echo "Total tasks: 40 (38 new + 2 existing)"
echo "Existing tasks: task-485, task-486"
echo ""
echo "All tasks labeled with:"
echo "  - agent-event-system (initiative identifier)"
echo "  - phase-N (phase number)"
echo "  - Domain-specific labels"
echo ""
echo "Run 'backlog task list -l agent-event-system --plain' to see all tasks"
