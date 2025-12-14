#!/bin/bash
# Create Agent Event System tasks
# This script creates all backlog tasks for the unified event system implementation

set -e

cd /Users/jasonpoley/brainclean/flowspec

echo "Creating Phase 1: Foundation tasks..."

# Task 2: Event Writer Library
backlog task create "Implement JSONL Event Writer Library" \
  -d "Create Python module flowspec.events with emit_event function and JSONL file writer with daily rotation." \
  --ac "Python module flowspec.events.writer with emit_event function" \
  --ac "JSONL files auto-rotate daily with configurable retention" \
  --ac "Events validated against schema before write" \
  --ac "Async emit_event_async for non-blocking writes" \
  --ac "CLI command specify events emit for manual emission" \
  -l "architecture,infrastructure,foundation" \
  --dep task-485 \
  --priority high --plain

# Task 3: Event Router
backlog task create "Implement Event Router with Namespace Dispatch" \
  -d "Create event routing system dispatching events to handlers based on namespace with pluggable consumers." \
  --ac "EventRouter class with register_handler method" \
  --ac "Pattern matching supports wildcards" \
  --ac "Built-in handlers for JSONL file and MCP server" \
  --ac "Event filtering by task_id agent_id time_range" \
  --ac "Unit tests for routing to multiple handlers" \
  -l "architecture,infrastructure,foundation" \
  --dep task-485 \
  --priority high --plain

# Task 4: Event Query CLI
backlog task create "Implement Event Query CLI and API" \
  -d "Build jq-based query utilities and Python API for event analysis with CLI interface." \
  --ac "CLI command specify events query with filters" \
  --ac "Python module flowspec.events.query with fluent API" \
  --ac "Export capabilities JSON CSV markdown" \
  --ac "Aggregation functions count_by group_by time_series" \
  --ac "Query 100k events in under 5 seconds" \
  -l "architecture,infrastructure,foundation" \
  --dep task-485 \
  --priority medium --plain

# Task 5: Git Workflow Config Schema
backlog task create "Create Git Workflow Configuration Schema" \
  -d "Define YAML schema for git-workflow.yml with worktree local_pr signing isolation sections." \
  --ac "Configuration schema with all required sections documented" \
  --ac "Default configuration template with comments" \
  --ac "Validation command specify workflow config validate" \
  --ac "Environment variable override support" \
  --ac "Documentation in docs reference" \
  -l "infrastructure,configuration" \
  --priority high --plain

# Task 6: Config Loader
backlog task create "Implement Configuration Loader with Validation" \
  -d "Build configuration loader that validates and merges defaults with user overrides." \
  --ac "Configuration class GitWorkflowConfig in Python" \
  --ac "Load from git-workflow.yml with fallback to defaults" \
  --ac "Emit system.config_change event on reload" \
  --ac "CLI command specify config show" \
  --ac "Unit tests for all config sections" \
  -l "infrastructure,configuration" \
  --priority high --plain

echo "Creating Phase 2: Event Emission Integration tasks..."

# Task 7: Hook Integration
backlog task create "Integrate Claude Code Hooks with Event Emission" \
  -d "Wire Claude Code hooks to emit events using unified schema. Extends hook infrastructure." \
  --ac "All 10 Claude Code hook types emit events" \
  --ac "Events include proper context with task_id branch_name" \
  --ac "Correlation IDs propagated across hook chains" \
  --ac "Performance impact under 50ms per hook" \
  --ac "Backward compatible with existing hook configurations" \
  -l "architecture,hooks,event-emission" \
  --priority high --plain

# Task 8: Backlog Event Integration (extends task-204)
backlog task create "Integrate Backlog Operations with Event Emission" \
  -d "Emit task events on backlog operations. Extends task-204 with full event schema support." \
  --ac "task.created event on backlog task create" \
  --ac "task.state_changed event on status updates" \
  --ac "task.ac_checked event on acceptance criteria completion" \
  --ac "task.assigned event on assignee changes" \
  --ac "Events include full task metadata in task object" \
  -l "architecture,backlog-integration,event-emission" \
  --dep task-204 \
  --priority high --plain

# Task 9: Git Operation Events (extends task-204.01)
backlog task create "Integrate Git Operations with Event Emission" \
  -d "Emit git events on branch commits push and merge operations. Extends task-204.01." \
  --ac "git.commit event on every commit with sha message" \
  --ac "git.branch_created and git.branch_deleted events" \
  --ac "git.pushed event on push to remote" \
  --ac "git.merged event on merge completion" \
  --ac "Events include GPG signing info when available" \
  -l "architecture,scm,event-emission" \
  --dep task-204.01 \
  --priority high --plain

echo "Creating Phase 3: Action System tasks..."

# Task 10: Action Registry
backlog task create "Implement Action Registry with 55 Actions" \
  -d "Create registry for 55 actions across 18 categories as defined in action-system.md." \
  --ac "ActionRegistry class with register and lookup methods" \
  --ac "All 55 actions from documentation registered" \
  --ac "Actions categorized by domain and category" \
  --ac "Input and output contracts defined per action" \
  --ac "Idempotency and side-effects documented per action" \
  -l "architecture,action-system" \
  --priority high --plain

# Task 11: Action Decorator System
backlog task create "Implement Action Decorator and Helper System" \
  -d "Create Python decorator for defining actions with automatic event emission and validation." \
  --ac "action decorator with verb domain category parameters" \
  --ac "Automatic action.invoked event on execution start" \
  --ac "Automatic action.succeeded or action.failed on completion" \
  --ac "Input validation against action contract" \
  --ac "Duration tracking in action events" \
  -l "architecture,action-system" \
  --priority high --plain

# Task 12: Action-Event Mapping
backlog task create "Implement Action to Event Mapping" \
  -d "Implement automatic mapping from action execution to event emission as per action-system.md." \
  --ac "Every accepted action emits action.invoked" \
  --ac "Guaranteed terminal event succeeded failed or aborted" \
  --ac "Side-effect events emitted as documented" \
  --ac "Mapping table matches action-system.md documentation" \
  --ac "Unit tests validate all 55 action mappings" \
  -l "architecture,action-system" \
  --priority high --plain

# Task 13: Allowed Followups Validation
backlog task create "Implement Allowed Followups Validation" \
  -d "Validate action sequences against allowed followups graph from action-system.md." \
  --ac "Followup graph defined matching documentation" \
  --ac "ValidationError on invalid action sequence" \
  --ac "Warnings logged for unusual but allowed sequences" \
  --ac "Query API for valid next actions given current state" \
  --ac "Visualization of followup graph available" \
  -l "architecture,action-system" \
  --priority medium --plain

echo "Creating Phase 4: Git Workflow tasks..."

# Task 14: Worktree Creation
backlog task create "Implement Worktree Creation Automation" \
  -d "Create script to generate git worktrees for tasks with proper branch naming." \
  --ac "Script worktree-create.sh task-id feature-description" \
  --ac "Creates worktree at worktrees/task-id-feature-description" \
  --ac "Creates branch from configured base branch" \
  --ac "Emits git.branch_created and git.worktree_created events" \
  --ac "Validates task exists in backlog before creating" \
  -l "infrastructure,scm,git-workflow" \
  --priority high --plain

# Task 15: Worktree Cleanup
backlog task create "Implement Worktree Cleanup Automation" \
  -d "Create cleanup automation for completed or abandoned task worktrees." \
  --ac "Script worktree-cleanup.sh task-id" \
  --ac "Removes worktree safely checking for uncommitted changes" \
  --ac "Optionally deletes branch if merged" \
  --ac "Emits git.worktree_removed and git.branch_deleted events" \
  --ac "Post-merge hook triggers automatic cleanup" \
  -l "infrastructure,scm,git-workflow" \
  --priority medium --plain

# Task 16: Git Hook Framework
backlog task create "Design Git Hook Framework for Local PR" \
  -d "Create extensible git hook framework with centralized dispatcher for quality gates." \
  --ac "Dispatcher script hook-dispatcher.sh" \
  --ac "Installation script install-hooks.sh" \
  --ac "Hook registration via symlinks in .git/hooks" \
  --ac "Event emission for all hook triggers" \
  --ac "Documentation for adding custom hooks" \
  -l "infrastructure,devops,cicd,git-workflow" \
  --priority high --plain

# Task 17: Lint Quality Gate
backlog task create "Implement Pre-Commit Quality Gate - Lint" \
  -d "Create lint quality gate running configured linters before commit." \
  --ac "Pre-commit hook calls quality-gates/lint.sh" \
  --ac "Supports ruff eslint golangci-lint" \
  --ac "Emits quality_gate events started and passed or failed" \
  --ac "Configurable skip with git commit no-verify" \
  --ac "Exit code 1 blocks commit on failure" \
  -l "infrastructure,quality,cicd,git-workflow" \
  --priority high --plain

# Task 18: Test Quality Gate
backlog task create "Implement Pre-Commit Quality Gate - Test" \
  -d "Create test quality gate running relevant test suite before commit." \
  --ac "Pre-commit hook calls quality-gates/test.sh" \
  --ac "Runs pytest vitest or go test based on project" \
  --ac "Smart test selection for affected tests only" \
  --ac "Emits quality_gate events" \
  --ac "Configurable timeout default 600s" \
  -l "infrastructure,quality,cicd,git-workflow" \
  --priority high --plain

# Task 19: SAST Quality Gate
backlog task create "Implement Pre-Commit Quality Gate - SAST" \
  -d "Create security scanning gate with bandit and semgrep." \
  --ac "Pre-commit hook calls quality-gates/sast.sh" \
  --ac "Runs bandit and semgrep" \
  --ac "Emits security.vulnerability_found events" \
  --ac "Fail on high or critical findings" \
  --ac "SARIF output stored in .flowspec/security/sarif" \
  -l "infrastructure,security,devsecops,cicd,git-workflow" \
  --priority high --plain

# Task 20: Local PR Approval Workflow
backlog task create "Implement Local PR Approval Workflow" \
  -d "Create orchestrator running all quality gates and making approval decision." \
  --ac "Script local-pr-submit.sh" \
  --ac "Runs all configured checks in parallel where possible" \
  --ac "Implements approval modes auto human_required agent_review" \
  --ac "Emits git.local_pr_submitted and approved or rejected events" \
  --ac "Human approval workflow prompts for sign-off if required" \
  -l "infrastructure,cicd,devops,git-workflow" \
  --priority high --plain

# Task 21: GPG Key Management
backlog task create "Design Agent GPG Key Management System" \
  -d "Design secure key storage and registration system for agent identities." \
  --ac "Key storage at .flowspec/agent-keys with gitignore" \
  --ac "Key registry file keyring.txt" \
  --ac "Public keys in repo private keys in secure storage" \
  --ac "Key rotation strategy documented" \
  --ac "Emit system.config_change on key registration" \
  -l "infrastructure,security,devsecops,git-workflow" \
  --priority high --plain

# Task 22: GPG Key Generation
backlog task create "Implement GPG Key Generation for Agents" \
  -d "Create automation to generate unique GPG keys for each agent." \
  --ac "Script gpg-setup-agent.sh agent-id" \
  --ac "Generates 4096-bit RSA key non-interactively" \
  --ac "Registers key in keyring with agent ID mapping" \
  --ac "Exports public key to agent-keys directory" \
  --ac "Emits security.gpg_key_generated event" \
  -l "infrastructure,security,devsecops,git-workflow" \
  --priority high --plain

# Task 23: Automated Commit Signing
backlog task create "Implement Automated Commit Signing" \
  -d "Configure git to automatically sign commits with agent GPG keys." \
  --ac "Post-commit hook emits git.commit with GPG info" \
  --ac "Git config automatically set for agent identity" \
  --ac "Verify signatures before push" \
  --ac "Reject unsigned commits in CI if required" \
  --ac "Support co-authored-by for multi-agent collaboration" \
  -l "infrastructure,security,scm,git-workflow" \
  --priority medium --plain

echo "Creating Phase 5: Container Integration tasks..."

# Task 24: Container Strategy
backlog task create "Design Container Orchestration Strategy" \
  -d "Design architecture for spinning up isolated containers per task with worktree mounts." \
  --ac "Architecture document in docs/guides/container-strategy.md" \
  --ac "Container naming convention documented" \
  --ac "Volume mount strategy worktree RW repo RO" \
  --ac "Network isolation modes documented" \
  --ac "Resource limits defined" \
  -l "infrastructure,devops,container" \
  --priority high --plain

# Task 25: Container Launch
backlog task create "Implement Container Launch Automation" \
  -d "Create script to launch devcontainers with proper configuration." \
  --ac "Script container-launch.sh task-id agent-id" \
  --ac "Uses flowspec-agents base image" \
  --ac "Mounts worktree at /workspace" \
  --ac "Applies configured resource limits" \
  --ac "Emits container.started event with container ID" \
  -l "infrastructure,devops,container" \
  --priority high --plain

# Task 26: Secret Injection
backlog task create "Implement Runtime Secret Injection" \
  -d "Securely inject secrets into running containers without baking into images." \
  --ac "Script inject-secrets.sh container-id" \
  --ac "Reads secrets from host keychain or secret service" \
  --ac "Injects via environment variables" \
  --ac "Secrets never written to disk or logs" \
  --ac "Emits container.secrets_injected event names only" \
  -l "infrastructure,security,devsecops,container" \
  --priority high --plain

# Task 27: Container Monitoring
backlog task create "Implement Container Resource Monitoring" \
  -d "Monitor container resource usage and emit events on limit hits." \
  --ac "Monitoring script monitor-containers.sh" \
  --ac "Runs in background checks every 30s" \
  --ac "Emits container.resource_limit_hit when over 90 percent" \
  --ac "Logs resource usage to metrics file" \
  --ac "Graceful shutdown on persistent limit hits" \
  -l "infrastructure,observability,container" \
  --priority medium --plain

# Task 28: Container Cleanup
backlog task create "Implement Container Cleanup Automation" \
  -d "Automatically stop and remove containers when tasks complete." \
  --ac "Cleanup triggered by task.completed or task.archived events" \
  --ac "Script container-cleanup.sh task-id" \
  --ac "Saves container logs before removal" \
  --ac "Emits container.stopped event with exit code" \
  --ac "Force-kill containers running over 24 hours" \
  -l "infrastructure,devops,container" \
  --priority medium --plain

echo "Creating Phase 6: Decision Tracking tasks..."

# Task 29: Decision Event Helpers
backlog task create "Implement Decision Event Emission Helpers" \
  -d "Create helper functions for emitting well-formed decision events." \
  --ac "Function emit_decision with decision_id category message" \
  --ac "Reversibility assessment helper with type lock_in_factors cost" \
  --ac "Alternatives tracking with option rejected_reason pairs" \
  --ac "Supporting material links with url title type" \
  --ac "Integration with flowspec commands for automatic emission" \
  -l "architecture,decision-tracker" \
  --priority high --plain

# Task 30: Decision Query Utilities
backlog task create "Implement Decision Query Utilities" \
  -d "Create utilities to query and analyze decision events from JSONL stream." \
  --ac "CLI command specify decisions list with filters" \
  --ac "Query by category reversibility_type time_range" \
  --ac "Export decision timeline as markdown" \
  --ac "Identify one-way-door decisions for review" \
  --ac "Link decisions to tasks and branches" \
  -l "architecture,decision-tracker" \
  --priority medium --plain

# Task 31: Reversibility Assessment Tool
backlog task create "Implement Reversibility Assessment Tool" \
  -d "Create interactive tool for assessing decision reversibility with prompts." \
  --ac "CLI command specify decision assess" \
  --ac "Prompts for lock-in factors from predefined list" \
  --ac "Calculates reversal cost based on factors" \
  --ac "Suggests reversal window based on project phase" \
  --ac "Outputs formatted decision event ready for emission" \
  -l "architecture,decision-tracker" \
  --priority low --plain

echo "Creating Phase 7: State Machine and Automation tasks..."

# Task 32: State Machine Implementation
backlog task create "Implement Git Workflow State Machine" \
  -d "Create event-driven state machine for git workflow transitions." \
  --ac "StateMachine class with states from git-workflow-objectives.md" \
  --ac "Transitions triggered by event_type matching" \
  --ac "Invalid transitions raise StateError" \
  --ac "Current state reconstructed from event replay" \
  --ac "Visualization of state machine as mermaid diagram" \
  -l "architecture,git-workflow,automation" \
  --priority high --plain

# Task 33: State Recovery Utilities
backlog task create "Implement State Recovery Utilities" \
  -d "Create utilities for reconstructing workflow state from event replay." \
  --ac "Script state-machine.py with replay functionality" \
  --ac "Reconstruct task state worktree associations container mappings" \
  --ac "Handle corrupted or missing events gracefully" \
  --ac "Validate recovered state against current system state" \
  --ac "Tested with 1000+ event corpus" \
  -l "architecture,git-workflow,automation" \
  --priority medium --plain

# Task 34: Automated Cleanup Orchestrator
backlog task create "Implement Automated Cleanup Orchestrator" \
  -d "Create orchestrator that monitors events and triggers cleanup actions." \
  --ac "CleanupOrchestrator class listening for completion events" \
  --ac "Triggers worktree cleanup on task.completed" \
  --ac "Triggers container cleanup on task.archived" \
  --ac "Configurable cleanup delays and conditions" \
  --ac "Emits lifecycle.cleanup_completed events" \
  -l "architecture,automation" \
  --priority medium --plain

echo "Creating Phase 8: Documentation and Testing tasks..."

# Task 35: Architecture Documentation
backlog task create "Create Agent Event System Architecture Documentation" \
  -d "Create comprehensive architecture documentation with diagrams and guides." \
  --ac "Architecture overview document in docs/guides/event-system-architecture.md" \
  --ac "ASCII and mermaid diagrams for event flow" \
  --ac "Component interaction documentation" \
  --ac "API reference for all public functions" \
  --ac "Migration guide from legacy systems" \
  -l "documentation" \
  --priority high --plain

# Task 36: Integration Tests
backlog task create "Create Event System Integration Tests" \
  -d "Create comprehensive integration test suite for event system." \
  --ac "End-to-end test task lifecycle emits correct events" \
  --ac "Test git workflow state machine transitions" \
  --ac "Test container lifecycle with event emission" \
  --ac "Test decision tracking workflow" \
  --ac "Coverage target 80 percent for event modules" \
  -l "testing,quality" \
  --priority high --plain

# Task 37: Performance Benchmarks
backlog task create "Create Event System Performance Benchmarks" \
  -d "Create benchmarks for event emission query and storage performance." \
  --ac "Benchmark emit_event latency target under 10ms" \
  --ac "Benchmark query performance for 100k events" \
  --ac "Benchmark file rotation and archival" \
  --ac "Memory usage profiling for long-running agents" \
  --ac "CI integration to track performance regressions" \
  -l "testing,performance" \
  --priority medium --plain

# Task 38: DORA Metrics Dashboard
backlog task create "Implement DORA Metrics Dashboard" \
  -d "Create dashboard displaying deployment frequency lead time CFR and MTTR from events." \
  --ac "CLI command specify metrics dora --dashboard" \
  --ac "Shows all four metrics with color-coded status" \
  --ac "Trend arrows showing improvement or degradation" \
  --ac "Exportable as JSON markdown or HTML" \
  --ac "GitHub Actions posts dashboard to PR comments" \
  -l "observability,devops" \
  --priority low --plain

# Task 39: Operational Runbooks
backlog task create "Create Operational Runbooks for Event System" \
  -d "Create runbooks for incident response state recovery and troubleshooting." \
  --ac "Incident response runbook in docs/runbooks" \
  --ac "State recovery runbook with event replay procedures" \
  --ac "Performance troubleshooting runbook" \
  --ac "Secrets rotation runbook" \
  --ac "All runbooks tested with simulated scenarios" \
  -l "documentation,devops" \
  --priority medium --plain

echo ""
echo "All tasks created successfully!"
echo "Run 'backlog task list --plain' to see all tasks"
