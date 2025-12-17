# ADR-002: Task Memory Context Injection Method

**Status**: Accepted
**Date**: 2025-12-09
**Decision Makers**: Architecture Team, Enterprise Software Architect

## Context

Task Memory provides persistent, task-scoped context storage (ADR-001). The next challenge is **how to inject this context into AI agents** so they automatically receive task memory when working on a task.

### Requirements

1. **Zero-latency injection** for primary use case (Claude Code)
2. **Agent-agnostic** protocol for secondary agents (GitHub Copilot, Cursor, etc.)
3. **Automatic discovery** - agents find memory without manual file paths
4. **Human-readable fallback** - developers can manually access memory
5. **Cross-agent compatibility** - multiple agents can access same memory

### Agent Landscape

| Agent | Usage % | Capabilities | Constraints |
|-------|---------|--------------|-------------|
| Claude Code | 70% | @import in CLAUDE.md, MCP | Requires file reference |
| GitHub Copilot | 15% | MCP client | Requires URI protocol |
| Cursor | 10% | File reading | Manual file paths |
| Others | 5% | Varies | Lowest common denominator |

## Decision

**Adopt multi-agent strategy with CLAUDE.md @import as primary method, MCP resource as fallback**

### Strategy 1: CLAUDE.md @import (Primary - 70% of use)

Leverage Claude Code's existing `@import` directive to inject task memory directly into the agent's context.

**Implementation**:
```markdown
# backlog/CLAUDE.md

## Backlog Management

This directory contains task definitions and task memory files.

## Active Task Context

@import memory/task-${ACTIVE_TASK_ID}.md
```

**Mechanism**:
1. When developer starts task: `backlog task edit task-368 -s "In Progress"`
2. CLI lifecycle hook updates `backlog/CLAUDE.md` with current task ID
3. Next time Claude Code reads `backlog/CLAUDE.md`, task memory automatically injected
4. Claude Code has task context without explicit prompting

### Strategy 2: MCP Resource (Secondary - 30% of use)

Provide standardized MCP resource URI for agents supporting Model Context Protocol.

**Implementation**:
```python
# src/specify_cli/mcp/server.py

@server.resource("backlog://memory/{task_id}")
async def get_task_memory(task_id: str) -> Resource:
    """Retrieve task memory via MCP resource URI."""
    memory_path = memory_store.get_path(task_id)
    if not memory_path.exists():
        raise ResourceNotFoundError(f"Memory for {task_id} not found")

    content = memory_path.read_text()
    return Resource(
        uri=f"backlog://memory/{task_id}",
        mimeType="text/markdown",
        text=content
    )
```

**Usage by agents**:
```typescript
// GitHub Copilot or other MCP client
const memory = await mcpClient.readResource("backlog://memory/task-368");
```

### Strategy 3: Manual Fallback (Edge cases)

For agents without @import or MCP support, provide clear file path in task definition.

**Implementation**:
```markdown
# backlog/tasks/task-368.md

## Task Memory

**Location**: `backlog/memory/task-368.md`

Context for this task is maintained in the memory file above.
```

## Rationale

### Why Multi-Agent Strategy?

**Single approach insufficient because**:
- No universal agent protocol exists yet
- Claude Code dominates our usage (70%) but not exclusive
- MCP adoption growing but not universal
- Need graceful degradation for all agents

### Why CLAUDE.md @import as Primary?

1. **Zero-latency**: Context loaded automatically when Claude Code starts
2. **Zero-configuration**: Developers don't need to configure anything
3. **Automatic discovery**: No explicit file path needed
4. **Existing infrastructure**: Leverages proven @import mechanism
5. **Immediate availability**: Works today, no new features needed

### Why MCP as Secondary?

1. **Standard protocol**: MCP becoming industry standard for agent context
2. **Growing adoption**: GitHub Copilot, Cursor, others adding MCP support
3. **Structured access**: Resources provide metadata, discoverability
4. **Agent-agnostic**: Works with any MCP-compatible agent
5. **Future-proof**: Positions us for MCP ecosystem growth

### Why Not Primary MCP?

- **Requires explicit request**: Agent must know to query MCP resource
- **Latency overhead**: Network request vs. file inclusion
- **Not universally adopted**: Claude Code doesn't prioritize MCP resources yet
- **Prompting burden**: Developer must tell agent to query MCP

## Consequences

### Positive

- ✅ **Works with Claude Code out-of-box**: Zero configuration for 70% of usage
- ✅ **MCP provides standard protocol**: Future-proof for emerging agents
- ✅ **Human-readable fallback**: Developers can manually copy file path
- ✅ **No lock-in**: Multiple injection methods prevent vendor lock-in
- ✅ **Graceful degradation**: Works with agents of varying capability

### Negative

- ⚠️ **Requires ACTIVE_TASK_ID tracking**: CLI must maintain current task state
- ⚠️ **Multi-agent testing burden**: Must validate across multiple agents
- ⚠️ **Variable injection timing**: @import is immediate, MCP is on-request

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| @import breaks in Claude Code | High | Low | MCP fallback, manual fallback |
| MCP not adopted by agents | Medium | Medium | @import primary, manual fallback |
| ACTIVE_TASK_ID gets stale | Medium | Low | CLI validation on each command |
| Multiple concurrent tasks | Low | Medium | Single active task per developer |

## Alternatives Considered

### Alternative 1: MCP Only

Use MCP resource as sole injection method.

**Rejected because**:
- Requires agent to explicitly query resource
- Not automatic for Claude Code (our primary agent)
- Adds latency overhead
- MCP adoption not universal yet

### Alternative 2: Agent Prompting

Rely on developers to prompt agents with memory file path.

**Rejected because**:
- High cognitive burden on developers
- Error-prone (forget to mention path)
- Defeats purpose of automatic context
- Not scalable across team

### Alternative 3: Git Commit Messages

Embed memory summaries in git commit messages.

**Rejected because**:
- Limited space in commit messages
- Not real-time (only on commit)
- Pollutes git history
- Not editable after commit

### Alternative 4: Environment Variables

Store task memory path in environment variable.

**Rejected because**:
- Not agent-accessible
- Shell-specific (doesn't cross tools)
- Not persistent across terminal sessions
- Not human-readable

## Implementation Considerations

### ACTIVE_TASK_ID Tracking

**Challenge**: How does CLI know which task is currently active?

**Solution**: Track in backlog state file

```yaml
# backlog/.state.yml (new file)
active_task: task-368
last_updated: 2025-12-09T14:30:00Z
```

**Updated by lifecycle hooks**:
- `To Do → In Progress`: Set active_task
- `In Progress → Done`: Clear active_task
- `In Progress → In Progress` (different task): Update active_task

### CLAUDE.md Update Mechanism

**Challenge**: How to update @import reference dynamically?

**Solution**: Template with substitution

```markdown
# backlog/CLAUDE.md (template)

## Active Task Context

{{ACTIVE_TASK_IMPORT}}
```

**CLI updates**:
```python
def update_claude_md(task_id: Optional[str]):
    if task_id:
        import_line = f"@import memory/{task_id}.md"
    else:
        import_line = "<!-- No active task -->"

    template = read_template("backlog/CLAUDE.md")
    content = template.replace("{{ACTIVE_TASK_IMPORT}}", import_line)
    write_file("backlog/CLAUDE.md", content)
```

### MCP Resource Discovery

**Challenge**: How do agents discover available memory resources?

**Solution**: Implement MCP resource listing

```python
@server.list_resources()
async def list_memories() -> List[Resource]:
    """List all active task memories."""
    active_tasks = memory_store.list_active()
    return [
        Resource(
            uri=f"backlog://memory/{task_id}",
            name=f"Task {task_id} Memory",
            mimeType="text/markdown"
        )
        for task_id in active_tasks
    ]
```

## Success Criteria

1. **Claude Code**: Task memory automatically available when working in backlog context
2. **MCP Agents**: Can query and retrieve task memory via standard resource URI
3. **Fallback**: Developers can manually access memory files when needed
4. **Reliability**: Context injection works >99% of time
5. **Latency**: @import < 10ms, MCP < 100ms

## Integration with Other ADRs

- **ADR-001**: Defines memory file location and format
- **ADR-003**: Lifecycle hooks update CLAUDE.md @import reference
- **ADR-004**: Sync ensures CLAUDE.md and memory files stay consistent across machines

## References

- [Claude Code @import Documentation](https://github.com/anthropics/claude-code)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Task Memory System Architecture](../architecture/task-memory-system.md)
- [ADR-001: Storage Mechanism](./ADR-001-task-memory-storage.md)

## Notes

This ADR establishes the bridge between storage (ADR-001) and agent consumption. The multi-agent strategy ensures we support current tools (Claude Code) while positioning for future MCP adoption.

**Implementation tracked in**:
- task-386 (CLAUDE.md @import integration)
- task-387 (MCP resource endpoint)
