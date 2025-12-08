---
id: task-229
title: >-
  Create agent progress tracking via event emission (multi-machine
  observability)
status: Done
assignee: []
created_date: '2025-12-03 02:10'
updated_date: '2025-12-03 22:27'
labels:
  - hooks
  - observability
  - multi-agent
  - architecture
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable agents to emit progress events during long-running tasks, creating an observability layer for tracking agent activity across multiple machines and projects.

**Vision**: Any agent (Claude Code, Copilot, Gemini, custom) working on a jp-spec-kit project can emit progress events. These events can be:
1. Stored locally in audit log
2. Sent to a central collector (webhook)
3. Used to coordinate multi-agent workflows

**Use Cases**:
1. **Progress Tracking**: "Agent on muckross is 60% through task-198"
2. **Multi-Machine Coordination**: "Agent on galway finished planning, agent on kinsale can start implementing"
3. **Debugging**: "Why did the build fail? Check agent activity log"
4. **Metrics**: "How long do agents spend on each workflow phase?"

**Event Types to Add**:
```
agent.started        - Agent began working on task
agent.progress       - Agent reports progress (percentage, status message)
agent.blocked        - Agent is waiting for something
agent.completed      - Agent finished task
agent.error          - Agent encountered error
agent.handoff        - Agent handing off to another agent/machine
```

**Event Payload**:
```json
{
  "event_type": "agent.progress",
  "agent_id": "claude-code@muckross",
  "task_id": "task-198",
  "spec_id": "agent-hooks",
  "progress_percent": 60,
  "status_message": "Implementing event emitter module",
  "machine": "muckross",
  "timestamp": "2025-12-02T20:30:00Z"
}
```

**Emission Methods**:
1. **CLI**: `specify hooks emit agent.progress --progress 60 --message "Working on X"`
2. **MCP Tool**: Add `emit_progress` tool to backlog MCP server
3. **Agent Instruction**: Tell agent to emit at key milestones

**Aggregation Options** (v2):
- Local: `.specify/hooks/audit.log` (current)
- Webhook: Send to central server
- File share: Write to shared network location
- Git: Commit events to repo (audit trail)

**Multi-Machine Scenario**:
```
muckross (planning)     → emit plan.created
    ↓ webhook
central-collector       → stores event, notifies
    ↓ webhook
galway (implementing)   → receives "ready to implement" signal
    ↓
galway                  → emit implement.started
```
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add agent.* event types to EventType enum (started, progress, blocked, completed, error, handoff)
- [ ] #2 Extend Event payload with agent_id, machine, progress_percent, status_message fields
- [ ] #3 Add --progress and --message flags to specify hooks emit CLI
- [ ] #4 Create MCP tool for progress emission (optional, if MCP integration feasible)
- [ ] #5 Add agent progress section to hooks-quickstart.md documentation
- [ ] #6 Create example hook that aggregates progress to a summary file
- [ ] #7 Test multi-agent scenario with events from different 'machines' (simulated)
<!-- AC:END -->
