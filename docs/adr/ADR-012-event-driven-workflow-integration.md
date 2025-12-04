# ADR-012: Event-Driven Workflow Integration

**Status:** Proposed
**Date:** 2025-12-04
**Author:** Enterprise Software Architect (Hohpe Principles Expert)
**Context:** Backlog.md event emission and workflow automation (4 tasks: 204, 204.01, 204.02, 204.03)
**Supersedes:** None
**Amended by:** None
**Related:** ADR-005 (Event Model Architecture)

---

## Strategic Context (Penthouse View)

### Business Problem

JP Spec Kit's backlog.md integration currently operates as a **write-only system**:
- Tasks are created by `/jpspec` commands
- Task status changes happen outside the workflow (manual `backlog task edit`)
- No automatic triggers when tasks transition states
- Workflow commands can't react to backlog changes

**The Core Tension:** Backlog.md is the **source of truth** for task state, but workflow automation has **no visibility** into state changes.

**Business Impact:**
- **Manual Coordination:** Developers must manually trigger next workflow phase after task completion
- **Missed Notifications:** No Slack/email alerts when tasks are blocked or completed
- **Limited Observability:** Can't track task lifecycle metrics (time in state, completion velocity)
- **Brittle Automation:** Agent hooks can't react to task state changes

### Business Value (Strategic Investment)

**Primary Value Streams:**

1. **Workflow Automation** - Auto-trigger next phase when tasks complete (e.g., validation after implementation)
2. **Team Notifications** - Slack/email alerts on task state changes
3. **Observability** - Task lifecycle metrics and analytics
4. **External Integrations** - Sync with Jira, Linear, GitHub Issues

**Success Metrics:**

| Metric | Target | Timeline |
|--------|--------|----------|
| Automated workflow transitions | >50% | 3 months |
| Notification delivery latency | <30 seconds | 1 month |
| Task lifecycle visibility | 100% | 2 months |

### Investment Justification

**Option Value:**
- **Automation Foundation:** Enables future agent orchestration scenarios
- **Integration Platform:** Unlocks Jira, Linear, GitHub Issues sync
- **Observability Premium:** Task metrics enable data-driven process improvement

**Cost:**
- **Development:** 2-3 weeks (git hook + CLI wrapper + upstream contribution)
- **Maintenance:** Low (event schema is stable from ADR-005)

**Decision:** Build event emission for backlog operations

---

## Decision

### Chosen Architecture: Three-Layer Event Emission Strategy

Implement event emission at **three integration points**:

```
┌─────────────────────────────────────────────────────────────────┐
│               EVENT EMISSION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  LAYER 1: Git Hook (Lowest-Level Detection)                │ │
│  │                                                              │ │
│  │  .git/hooks/post-commit                                     │ │
│  │      ↓                                                       │ │
│  │  Detect: backlog/tasks/task-*.md file changes              │ │
│  │      ↓                                                       │ │
│  │  Parse: YAML frontmatter for status, assignee, etc.        │ │
│  │      ↓                                                       │ │
│  │  Emit: task.updated, task.status_changed events            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │  LAYER 2: CLI Wrapper (High-Level Semantic Events)         │ │
│  │                                                              │ │
│  │  jpspec-backlog task create "title"                        │ │
│  │      ↓                                                       │ │
│  │  Call: backlog task create "title"                         │ │
│  │      ↓                                                       │ │
│  │  Emit: task.created event (with full context)              │ │
│  │                                                              │ │
│  │  jpspec-backlog task edit 42 -s "Done"                     │ │
│  │      ↓                                                       │ │
│  │  Call: backlog task edit 42 -s "Done"                      │ │
│  │      ↓                                                       │ │
│  │  Emit: task.status_changed + task.completed events         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │  LAYER 3: Upstream Contribution (Native Event Support)     │ │
│  │                                                              │ │
│  │  backlog.md library modification:                           │ │
│  │      ↓                                                       │ │
│  │  Add: Event hooks in backlog-md core                       │ │
│  │      ↓                                                       │ │
│  │  Emit: Native events from task operations                  │ │
│  │      ↓                                                       │ │
│  │  Benefit: No wrapper needed, all users get events          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              EVENT DISPATCH (Shared)                        │ │
│  │                                                              │ │
│  │  All layers emit to:                                        │ │
│  │      ↓                                                       │ │
│  │  .claude/hooks/hook-runner.sh                              │ │
│  │      ↓                                                       │ │
│  │  Execute: Matching hooks based on event type               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

1. **Chain of Responsibility** (Event Dispatch) - Hooks executed in priority order
2. **Observer Pattern** (Event Emission) - Multiple consumers listen to same events
3. **Adapter Pattern** (Git Hook) - Adapt file system changes to semantic events
4. **Decorator Pattern** (CLI Wrapper) - Wrap backlog CLI with event emission

---

## Engine Room View: Component Architecture

### Layer 1: Git Hook Implementation

**File:** `.git/hooks/post-commit`

**Responsibility:** Detect backlog task file changes and emit low-level events

```bash
#!/usr/bin/env bash
# post-commit hook - Emit events for backlog task file changes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Function to emit event
emit_event() {
    local event_type="$1"
    local event_payload="$2"

    # Call hook runner with event
    "${PROJECT_ROOT}/.claude/hooks/hook-runner.sh" "$event_type" "$event_payload"
}

# Get list of changed files in this commit
changed_files=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Filter for backlog task files
for file in $changed_files; do
    if [[ "$file" =~ ^backlog/tasks/task-[0-9]+.*\.md$ ]]; then
        # Extract task ID
        task_id=$(echo "$file" | grep -oE 'task-[0-9]+')

        # Parse task file for metadata
        task_file="${PROJECT_ROOT}/${file}"
        if [[ -f "$task_file" ]]; then
            # Extract YAML frontmatter fields
            status=$(grep -E '^status:' "$task_file" | sed 's/status:[[:space:]]*//')
            title=$(grep -E '^title:' "$task_file" | sed 's/title:[[:space:]]*//')

            # Build event payload
            event_payload=$(cat <<EOF
{
  "event_type": "task.updated",
  "event_id": "$(uuidgen)",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "task_id": "$task_id",
  "task_title": "$title",
  "task_status": "$status",
  "file_path": "$file",
  "commit_sha": "$(git rev-parse HEAD)"
}
EOF
)

            # Emit event
            emit_event "task.updated" "$event_payload"

            # Emit status-specific events
            if [[ "$status" == "Done" ]]; then
                emit_event "task.completed" "$event_payload"
            elif [[ "$status" == "In Progress" ]]; then
                emit_event "task.started" "$event_payload"
            fi
        fi
    fi
done
```

**Design Decisions:**
- **File-Based Detection:** Git hook is natural integration point for file changes
- **Frontmatter Parsing:** Use grep/sed for simplicity (no YAML library dependency)
- **Event Payload:** Include commit SHA for audit trail
- **Granular Events:** Emit both generic `task.updated` and specific events

### Layer 2: CLI Wrapper Implementation

**File:** `src/specify_cli/backlog_wrapper.py`

**Responsibility:** Wrap backlog CLI with semantic event emission

```python
import subprocess
import json
from datetime import datetime
from typing import List, Optional
from specify_cli.events.emitter import EventEmitter, Event

class BacklogCLIWrapper:
    """Wrapper around backlog CLI with event emission."""

    def __init__(self):
        self.emitter = EventEmitter()

    def task_create(
        self,
        title: str,
        description: Optional[str] = None,
        assignee: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[str] = None,
    ) -> str:
        """Create task and emit task.created event."""

        # Build CLI command
        cmd = ["backlog", "task", "create", title]
        if description:
            cmd.extend(["--description", description])
        if assignee:
            for a in assignee:
                cmd.extend(["--assignee", a])
        if labels:
            for l in labels:
                cmd.extend(["--label", l])
        if priority:
            cmd.extend(["--priority", priority])

        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse task ID from output
        task_id = self._extract_task_id(result.stdout)

        # Emit event
        self.emitter.emit(
            event_type="task.created",
            context={
                "task_id": task_id,
                "task_title": title,
                "task_status": "To Do",
                "assignee": assignee,
                "labels": labels,
                "priority": priority,
            }
        )

        return task_id

    def task_edit(
        self,
        task_id: str,
        status: Optional[str] = None,
        assignee: Optional[List[str]] = None,
        check_ac: Optional[int] = None,
    ) -> None:
        """Edit task and emit appropriate events."""

        # Load current task state
        old_state = self._load_task_state(task_id)

        # Build CLI command
        cmd = ["backlog", "task", "edit", task_id]
        if status:
            cmd.extend(["-s", status])
        if assignee:
            for a in assignee:
                cmd.extend(["-a", a])
        if check_ac:
            cmd.extend(["--check-ac", str(check_ac)])

        # Execute
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Load new task state
        new_state = self._load_task_state(task_id)

        # Emit events based on changes
        if status and old_state["status"] != new_state["status"]:
            self.emitter.emit(
                event_type="task.status_changed",
                context={
                    "task_id": task_id,
                    "old_status": old_state["status"],
                    "new_status": new_state["status"],
                }
            )

            # Emit completion event
            if new_state["status"] == "Done":
                self.emitter.emit(
                    event_type="task.completed",
                    context={"task_id": task_id}
                )

        if check_ac:
            self.emitter.emit(
                event_type="task.ac_checked",
                context={
                    "task_id": task_id,
                    "ac_number": check_ac,
                }
            )

    def _extract_task_id(self, output: str) -> str:
        """Parse task ID from backlog CLI output."""
        import re
        match = re.search(r'task-(\d+)', output)
        if match:
            return f"task-{match.group(1)}"
        raise ValueError(f"Could not extract task ID from output: {output}")

    def _load_task_state(self, task_id: str) -> dict:
        """Load current task state from file."""
        import yaml
        task_file = f"backlog/tasks/{task_id}.md"
        with open(task_file, 'r') as f:
            content = f.read()

        # Extract YAML frontmatter
        frontmatter = content.split('---')[1]
        return yaml.safe_load(frontmatter)
```

**Design Decisions:**
- **Wrapper Not Replacement:** Still uses backlog CLI under the hood
- **State Diffing:** Compare old vs new state to emit accurate events
- **Semantic Events:** Emit high-level events (`task.completed`) not just generic changes
- **Error Handling:** Propagate backlog CLI errors unchanged

### Layer 3: Upstream Contribution

**Goal:** Contribute event hooks to backlog.md library for native support

**Proposed API (for backlog.md maintainers):**

```typescript
// src/task.ts (backlog.md library)
import { EventEmitter } from 'events';

export class TaskManager extends EventEmitter {
  async createTask(task: Task): Promise<string> {
    // ... existing create logic ...

    // Emit event
    this.emit('task:created', {
      taskId: task.id,
      title: task.title,
      status: task.status,
      timestamp: new Date().toISOString(),
    });

    return task.id;
  }

  async updateTask(taskId: string, updates: Partial<Task>): Promise<void> {
    const oldTask = await this.getTask(taskId);

    // ... existing update logic ...

    // Emit event
    this.emit('task:updated', {
      taskId,
      oldStatus: oldTask.status,
      newStatus: updates.status,
      timestamp: new Date().toISOString(),
    });

    // Emit specific events
    if (updates.status === 'Done' && oldTask.status !== 'Done') {
      this.emit('task:completed', { taskId, timestamp: new Date().toISOString() });
    }
  }
}
```

**Upstream Contribution Strategy:**
1. Open GitHub issue proposing event hooks feature
2. Discuss API design with maintainers
3. Submit PR with event emission implementation
4. Add configuration flag (`--emit-events`) for backward compatibility
5. Document event contract in backlog.md README

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 9/10

**Strengths:**
- Clear separation: Git hook (low-level), CLI wrapper (high-level), upstream (native)
- Well-defined event schema (ADR-005)
- Simple integration points

**Improvement:**
- Document event precedence (if multiple layers emit same event)

### 2. Consistency - 10/10

**Strengths:**
- All layers use same event schema (ADR-005)
- Consistent event naming (`task.created`, `task.status_changed`)
- Unified dispatch mechanism (hook-runner.sh)

### 3. Composability - 10/10

**Strengths:**
- Events enable automation without modifying core workflow
- Multiple consumers can listen to same events
- Git hook works independently of CLI wrapper

### 4. Consumption (Developer Experience) - 8/10

**Strengths:**
- Zero-config for git hook (automatic after git clone)
- CLI wrapper is drop-in replacement (`jpspec-backlog` vs `backlog`)
- Events are transparent (don't affect user workflow)

**Needs Work:**
- Git hook installation automation (currently manual)

### 5. Correctness (Validation) - 9/10

**Strengths:**
- Event schema validation (JSON Schema from ADR-005)
- State diffing prevents spurious events
- Commit SHA provides audit trail

**Needs Work:**
- Race condition handling (rapid task edits)

### 6. Completeness - 8/10

**Covers:**
- Task creation, updates, status changes
- Acceptance criteria checks
- Task archival

**Missing (Future):**
- Bulk operations (archive multiple tasks)
- Task dependencies (parent/child relationships)

### 7. Changeability - 10/10

**Strengths:**
- Git hook is script (easy to modify)
- CLI wrapper is Python (refactor-friendly)
- Event schema versioning (ADR-005) supports evolution

---

## Alternatives Considered and Rejected

### Option A: Polling Backlog Files

**Approach:** Background process polls `backlog/tasks/` for file changes.

**Rejected Because:**
- **Latency:** Polling interval introduces delay (30-60 seconds)
- **Resource Waste:** Constant polling even when no changes
- **Missed Events:** Could miss rapid changes between polls

### Option B: File System Watchers (inotify, fswatch)

**Approach:** Use OS file system events to detect changes.

**Rejected Because:**
- **Platform Dependency:** inotify (Linux), FSEvents (macOS), different APIs
- **Daemon Required:** Background process must run continuously
- **Complexity:** More complex than git hook integration

### Option C: Modify Backlog.md CLI Source

**Approach:** Fork backlog.md CLI and add event emission directly.

**Rejected Because:**
- **Maintenance Burden:** Must track upstream changes
- **Community Fragmentation:** Fork diverges from official CLI
- **Upstream Better:** Layer 3 (contribution) achieves same goal without fork

---

## Implementation Guidance

### Task Dependency Graph

```
Layer 1: Git Hook (task-204.01)
    ↓
Layer 2: CLI Wrapper (task-204.02)
    ↓
Layer 3: Upstream Contribution (task-204.03)
    ↓
Integration with Workflow (task-204)
```

### Week-by-Week Implementation Plan

**Week 1: Git Hook**
- [ ] Implement post-commit hook script
- [ ] Add frontmatter parsing
- [ ] Integrate with hook-runner.sh
- [ ] Test with manual task edits

**Week 2: CLI Wrapper**
- [ ] Implement BacklogCLIWrapper class
- [ ] Add state diffing logic
- [ ] Create `jpspec-backlog` CLI entry point
- [ ] Test wrapper with all backlog commands

**Week 3: Upstream Contribution**
- [ ] Open GitHub issue on backlog.md repo
- [ ] Draft PR with event hooks
- [ ] Collaborate with maintainers on API
- [ ] Submit PR and iterate on feedback

---

## Risks and Mitigations

### Risk 1: Git Hook Doesn't Fire

**Likelihood:** Medium (user might not install hook)
**Impact:** High (no events emitted)

**Mitigation:**
- Auto-install hook during `specify init`
- Check for hook in pre-commit validation
- Document manual installation in README

### Risk 2: Event Duplication

**Likelihood:** High (multiple layers might emit same event)
**Impact:** Low (hooks should be idempotent)

**Mitigation:**
- Event deduplication by event_id
- Document precedence: Layer 2 > Layer 1 (use CLI wrapper if available)
- Hooks designed to be idempotent

### Risk 3: Upstream Contribution Rejected

**Likelihood:** Medium (maintainers might not want feature)
**Impact:** Low (Layers 1 and 2 still work)

**Mitigation:**
- Propose optional feature flag (`--emit-events`)
- Offer to maintain event emission code
- Fallback: Keep using CLI wrapper (Layer 2)

---

## Success Criteria

**Objective Measures:**

1. **Event Delivery** - 100% of task operations emit events
2. **Latency** - Events emitted within 1 second of operation
3. **Reliability** - No missed events (audit log verification)

**Subjective Measures:**

1. **Developer Adoption** - >50% of users enable automated hooks within 3 months
2. **Integration Feedback** - "Event-driven workflows are powerful" (NPS >40)

---

## Decision

**APPROVED for implementation as Three-Layer Event Emission Strategy**

**Timing:** Phased rollout over 3 weeks

**Next Steps:**

1. Implement git hook (task-204.01)
2. Implement CLI wrapper (task-204.02)
3. Open upstream contribution discussion (task-204.03)

**Review Date:** 2026-Q1 (after upstream contribution outcome)

---

## References

### Related ADRs

- **ADR-005:** Event Model Architecture (defines event schema)
- **ADR-006:** Hook Execution Model

### External References

- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [backlog.md Repository](https://github.com/backlog-md/backlog.md)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
