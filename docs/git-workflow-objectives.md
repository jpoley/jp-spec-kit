# Git Workflow Objectives

> **Domain**: Software Development
> **Status**: Proposed
> **Source**: Extracted from brainclean/more-objectives.md (section 4)

These objectives define native git tooling integration for flowspec to support multi-agent coding workflows with proper isolation, tracking, and quality gates.

**Key Principle**: All git operations emit events to the [JSONL Event System](jsonl-event-system.md), creating a complete audit trail and enabling event-driven state management.

## 1. Git Worktree Support

Use separate git worktrees with matching branch names so a single checkout can support multiple parallel work streams.

**Requirements:**
- Create worktree automatically when starting a task
- Branch naming convention tied to task ID (e.g., `task-123-feature-name`)
- Clean up worktrees when tasks complete or are abandoned
- Support concurrent work on multiple tasks without checkout conflicts

**Events Emitted:**
| Action | Event Type | Key Fields |
|--------|------------|------------|
| Create worktree | `git.worktree_created` | `context.task_id`, `context.branch_name`, `context.worktree_path` |
| Remove worktree | `git.worktree_removed` | `context.task_id`, `context.worktree_path` |

**Rationale:** Agents and humans can work on different tasks simultaneously without stepping on each other's work.

## 2. Local PR Approval (Pre-GitHub)

Support a local approval workflow similar to a PR, but executed via git hooks before pushing to GitHub.

**Requirements:**
- Two-tier PR system: local approval → GitHub PR to main
- Git hooks enforce quality gates before local "merge"
- Configurable approval requirements per project

**Quality Gates (Merge Checks):**
1. **Linting** - Always lint for formatting (prettier, eslint, gofmt, etc.)
2. **Tests** - Run all relevant tests, must pass
3. **No merge conflicts** - Require rebase, reject merge commits
4. **SAST** - Run static analysis security testing, address all issues
5. **Custom checks** - Project-specific validation hooks

**Events Emitted:**
| Action | Event Type | Key Fields |
|--------|------------|------------|
| Submit for review | `git.local_pr_submitted` | `context.task_id`, `context.branch_name` |
| Approval passed | `git.local_pr_approved` | `metadata.checks` (lint, test, sast results) |
| Approval failed | `git.local_pr_rejected` | `metadata.checks`, `metadata.failure_reason` |
| Push to remote | `git.pushed` | `context.branch_name`, `git.branch_name` |
| GitHub PR created | `git.pr_created` | `context.pr_number`, `metadata.pr_url` |

**Approval Modes** (stored in `metadata.approval_mode`):
- `auto` - All checks pass automatically approves
- `human_required` - Human sign-off required even if checks pass
- `agent_review` - Require review from another agent (e.g., `@security-reviewer`)

**Rationale:** Catch issues before they hit GitHub, reduce PR review cycles, enforce consistency.

## 3. Agent-Specific GPG Signing

Track which agents contributed to changes using GPG signatures.

**Requirements:**
- Each agent has unique GPG key identity
- Commits signed to identify contributing agent
- Support tracking when 2+ agents collaborated on a task
- Audit trail: which agent made which changes

**Events Emitted:**
| Action | Event Type | Key Fields |
|--------|------------|------------|
| Commit created | `git.commit` | `git.gpg_key_id`, `git.gpg_fingerprint`, `git.signer_agent_id` |
| Key registered | `system.config_change` | `metadata.gpg_key_id`, `metadata.agent_id` |

**Key Management:**
- GPG keys stored in `.flowspec/agent-keys/` directory
- Key registration emits `system.config_change` event
- Multiple agent signatures possible via co-authored-by commits

**Use Cases:**
- Verify human vs AI authorship
- Track agent collaboration patterns
- Compliance and audit requirements
- Debug agent behavior by tracing changes

## 4. Container-Based Parallel Experiments

Support running agents in containers with worktrees for parallel experimentation on a task.

**Requirements:**
- Spin up containers with isolated worktree mounts
- Multiple containers can experiment on same task
- Results can be compared and best approach selected
- Resource limits and cleanup automation

**Events Emitted:**
| Action | Event Type | Key Fields |
|--------|------------|------------|
| Container started | `container.started` | `context.task_id`, `container.container_id`, `container.image` |
| Agent attached | `container.agent_attached` | `agent_id`, `context.container_id` |
| Experiment result | `activity.progress` | `metadata.experiment_id`, `metadata.experiment_results` |
| Container stopped | `container.stopped` | `container.exit_code` |

**Parallel Experiment Pattern:**
```
task-123 (parent)
├── container-A → @backend-engineer (approach: REST API)
├── container-B → @backend-engineer (approach: GraphQL)
└── container-C → @backend-engineer (approach: gRPC)
```

Each container has same `context.task_id` but different `context.container_id` and `correlation.span_id`.

**Rationale:** Test multiple approaches simultaneously, reduce time to solution.

## 5. Devcontainer Isolation

Run agents in devcontainers for security isolation and reduced blast radius.

**Requirements:**
- Agent runs inside devcontainer, not on host
- Secrets injected at runtime, not baked in
- No access to user home directory or credentials outside container
- Minimal permissions principle
- Network isolation options

**Events Emitted:**
| Action | Event Type | Key Fields |
|--------|------------|------------|
| Secrets injected | `container.secrets_injected` | `container.secrets_injected` (names only, never values!) |
| Resource limit hit | `container.resource_limit_hit` | `container.resource_limits`, `metadata.limit_type` |
| Container stopped | `container.stopped` | `container.exit_code` |

**Security Benefits:**
- Compromised agent can't access host filesystem
- Secrets aren't persisted in container images
- Blast radius limited to container scope
- Easier to audit and monitor agent actions (via events)

## Event-Driven State Machine

The git workflow is driven by events. Each event transitions the task through states:

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Git Workflow State Machine                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  IDLE                                                                  │
│    │                                                                   │
│    └──[task.created]──► TASK_READY                                    │
│                            │                                           │
│                  [git.branch_created]                                  │
│                            ▼                                           │
│                       BRANCH_READY                                     │
│                            │                                           │
│                 [git.worktree_created]                                 │
│                            ▼                                           │
│                      WORKTREE_READY                                    │
│                            │                                           │
│                   [container.started]                                  │
│                            ▼                                           │
│                     CONTAINER_READY                                    │
│                            │                                           │
│                   [lifecycle.started]                                  │
│                            ▼                                           │
│                      AGENT_WORKING ◄──────────────────┐                │
│                            │                          │                │
│             [git.local_pr_submitted]    [git.local_pr_rejected]        │
│                            ▼                          │                │
│                    AWAITING_APPROVAL ─────────────────┘                │
│                            │                                           │
│                 [git.local_pr_approved]                                │
│                            ▼                                           │
│                        APPROVED                                        │
│                            │                                           │
│                      [git.pushed]                                      │
│                            ▼                                           │
│                         PUSHED                                         │
│                            │                                           │
│                    [git.pr_created]                                    │
│                            ▼                                           │
│                        PR_OPEN                                         │
│                            │                                           │
│                      [git.merged]                                      │
│                            ▼                                           │
│                         MERGED                                         │
│                            │                                           │
│                    [task.completed]                                    │
│                            ▼                                           │
│                          DONE                                          │
│                            │                                           │
│        [git.worktree_removed + container.stopped]                      │
│                            ▼                                           │
│                       CLEANED_UP                                       │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**State Recovery**: If a process crashes, the current state can be reconstructed by replaying events from the JSONL log:

```bash
# Find current state for task-123
jq -c 'select(.context.task_id == "task-123")' events.jsonl | tail -1
```

## Implementation Considerations

### Integration Points

| Component | Integration | Events |
|-----------|-------------|--------|
| `/flow:plan` | Create worktree + branch when task starts | `git.branch_created`, `git.worktree_created` |
| `/flow:implement` | Run in devcontainer with worktree | `container.started`, `lifecycle.*`, `git.commit` |
| `/flow:validate` | Execute local PR quality gates | `git.local_pr_submitted/approved/rejected` |
| Backlog.md | Track worktree/branch metadata on tasks | `task.state_changed` with context |
| Decision log | Record workflow decisions | `decision.made` events |

### Configuration

```yaml
# .flowspec/git-workflow.yml
worktree:
  enabled: true
  branch_prefix: "task-"
  cleanup_on_complete: true
  cleanup_on_archive: true  # Also cleanup when task is archived

local_pr:
  enabled: true
  require_rebase: true
  approval_mode: auto  # auto | human_required | agent_review
  checks:
    - lint
    - test
    - sast
  timeout_seconds: 600  # Max time for all checks

signing:
  require_gpg: true
  agent_keys_path: ".flowspec/agent-keys/"
  verify_on_push: true  # Verify signatures before push

isolation:
  use_devcontainer: true
  image: "jpoley/flowspec-agents:latest"
  inject_secrets:
    - GITHUB_TOKEN
    - OPENAI_API_KEY
  mount_paths:
    - source: "${workspaceFolder}"
      target: "/workspace"
  network_mode: isolated  # isolated | bridge | host
  resource_limits:
    memory_mb: 2048
    cpu_cores: 2

events:
  log_file: "events-${date}.jsonl"
  emit_to_mcp: true  # Also emit to agent-updates-collector MCP server
```

### Reversibility Assessment

| Feature | Reversibility | Lock-in Factors |
|---------|--------------|-----------------|
| Worktree convention | Two-way door | Branch naming only |
| Local PR hooks | Two-way door | Git hooks removable |
| GPG signing | Partially reversible | Historical commits stay signed |
| Devcontainer | Two-way door | Container config removable |

## Resolved Questions

The following questions from the original proposal are now answered by the event-driven design:

### 1. How to handle worktree cleanup for abandoned tasks?

**Answer**: Event-driven cleanup. When `task.archived` or `task.completed` is emitted:
1. System emits `git.worktree_removed` event with cleanup status
2. Worktree is physically removed
3. Branch can optionally be deleted if merged, emitting `git.branch_deleted`

Abandoned detection via `system.heartbeat` timeout:
```json
{"event_type": "system.heartbeat", "context": {"task_id": "task-123"}, "metadata": {"last_activity": "2025-12-13T20:00:00Z"}}
```

If no heartbeat for configured timeout, emit cleanup events.

### 2. Should local PR approval require human sign-off or can agents auto-approve?

**Answer**: Configurable via `local_pr.approval_mode`:
- `auto` - All checks pass → automatic approval → `git.local_pr_approved` emitted
- `human_required` - Checks pass → `coordination.waiting` emitted → await human → `git.local_pr_approved`
- `agent_review` - Checks pass → handoff to `@security-reviewer` → `git.local_pr_approved`

The approval mode is recorded in `metadata.approval_mode` on approval events for audit.

### 3. How to manage GPG keys across multiple machines/agents?

**Answer**: Event-tracked key management:
1. Keys stored in `.flowspec/agent-keys/{agent-id}.gpg.pub`
2. Key registration emits `system.config_change` event:
```json
{"event_type": "system.config_change", "metadata": {"change_type": "gpg_key_registered", "agent_id": "@backend-engineer", "gpg_key_id": "ABCD1234"}}
```
3. Key sync via git (public keys only in repo)
4. Private keys in secure storage, injected at runtime

### 4. What's the minimum devcontainer spec for flowspec agents?

**Answer**: Defined in configuration with events for monitoring:
```yaml
resource_limits:
  memory_mb: 2048  # Minimum for Claude Code
  cpu_cores: 2
```

Resource exhaustion emits `container.resource_limit_hit` event before termination.

### 5. How to handle secrets rotation in long-running containers?

**Answer**: Event-driven rotation:
1. `system.config_change` emitted with `change_type: "secrets_rotation"`
2. Container receives signal to re-inject secrets
3. New `container.secrets_injected` event confirms rotation
4. Old secrets invalidated

Long-running containers should watch for `system.config_change` events with `secrets_rotation` type.

## Open Questions (New)

1. **Event storage location**: Local JSONL per worktree, or centralized event store?
2. **Event retention**: How long to keep events? Archive strategy?
3. **Real-time streaming**: WebSocket/SSE for live event monitoring?
4. **Cross-repo coordination**: How to correlate events across multiple repositories?

## Related

- [JSONL Event System](jsonl-event-system.md) - Complete event schema and types
- [Decision Tracker](decision-tracker.md) - Decision event format
- [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Claude Quickstarts: Autonomous Coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Beads System](https://github.com/steveyegge/beads) - JSONL task elegance reference
