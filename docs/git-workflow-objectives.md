# Git Workflow Objectives

> **Domain**: Software Development
> **Status**: Proposed
> **Source**: Extracted from brainclean/more-objectives.md (section 4)

These objectives define native git tooling integration for flowspec to support multi-agent coding workflows with proper isolation, tracking, and quality gates.

## 1. Git Worktree Support

Use separate git worktrees with matching branch names so a single checkout can support multiple parallel work streams.

**Requirements:**
- Create worktree automatically when starting a task
- Branch naming convention tied to task ID (e.g., `task-123-feature-name`)
- Clean up worktrees when tasks complete or are abandoned
- Support concurrent work on multiple tasks without checkout conflicts

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

**Rationale:** Catch issues before they hit GitHub, reduce PR review cycles, enforce consistency.

## 3. Agent-Specific GPG Signing

Track which agents contributed to changes using GPG signatures.

**Requirements:**
- Each agent has unique GPG key identity
- Commits signed to identify contributing agent
- Support tracking when 2+ agents collaborated on a task
- Audit trail: which agent made which changes

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

**Rationale:** Test multiple approaches simultaneously, reduce time to solution.

## 5. Devcontainer Isolation

Run agents in devcontainers for security isolation and reduced blast radius.

**Requirements:**
- Agent runs inside devcontainer, not on host
- Secrets injected at runtime, not baked in
- No access to user home directory or credentials outside container
- Minimal permissions principle
- Network isolation options

**Security Benefits:**
- Compromised agent can't access host filesystem
- Secrets aren't persisted in container images
- Blast radius limited to container scope
- Easier to audit and monitor agent actions

## Implementation Considerations

### Integration Points

| Component | Integration |
|-----------|-------------|
| `/flow:plan` | Create worktree + branch when task starts |
| `/flow:implement` | Run in devcontainer with worktree |
| `/flow:validate` | Execute local PR quality gates |
| Backlog.md | Track worktree/branch metadata on tasks |
| Decision log | Record workflow decisions |

### Configuration

```yaml
# .flowspec/git-workflow.yml
worktree:
  enabled: true
  branch_prefix: "task-"
  cleanup_on_complete: true

local_pr:
  enabled: true
  require_rebase: true
  checks:
    - lint
    - test
    - sast

signing:
  require_gpg: true
  agent_keys_path: ".flowspec/agent-keys/"

isolation:
  use_devcontainer: true
  inject_secrets:
    - GITHUB_TOKEN
    - OPENAI_API_KEY
  mount_paths:
    - source: "${workspaceFolder}"
      target: "/workspace"
```

### Reversibility Assessment

| Feature | Reversibility | Lock-in Factors |
|---------|--------------|-----------------|
| Worktree convention | Two-way door | Branch naming only |
| Local PR hooks | Two-way door | Git hooks removable |
| GPG signing | Partially reversible | Historical commits stay signed |
| Devcontainer | Two-way door | Container config removable |

## Open Questions

1. How to handle worktree cleanup for abandoned tasks?
2. Should local PR approval require human sign-off or can agents auto-approve?
3. How to manage GPG keys across multiple machines/agents?
4. What's the minimum devcontainer spec for flowspec agents?
5. How to handle secrets rotation in long-running containers?

## Related

- [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Claude Quickstarts: Autonomous Coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Beads System](https://github.com/steveyegge/beads) - JSONL task elegance reference
