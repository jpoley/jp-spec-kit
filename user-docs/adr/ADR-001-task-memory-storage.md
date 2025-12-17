# ADR-001: Task Memory Storage Mechanism

**Status**: Accepted
**Date**: 2025-12-09
**Decision Makers**: Architecture Team, Enterprise Software Architect

## Context

AI-augmented software development faces a critical capability gap: the absence of **persistent, task-scoped context** that travels with work units across sessions, machines, and tool boundaries. Developers lose significant productivity rebuilding mental context when resuming tasks after interruptions (15-30 minutes typical context rebuild time).

We need a storage mechanism that:
- Persists task-specific knowledge across sessions and machines
- Requires zero additional infrastructure dependencies
- Remains human-readable and editable
- Supports cross-environment sync via existing tools (git)
- Scales to 10,000+ tasks without performance degradation
- Works with any AI agent or development tool

## Decision

**Adopt file-based storage with task memory files at `backlog/memory/task-{id}.md`**

### Storage Structure

```
backlog/
├── tasks/
│   └── task-368.md           # Task definition (existing)
└── memory/
    ├── task-368.md            # Active task memory
    ├── task-369.md
    ├── archive/               # Archived memories
    │   ├── task-100.md
    │   └── task-200.md
    └── .gitkeep
```

### File Format

Each memory file is markdown-formatted with structured sections:

```markdown
# Task Memory: task-368

**Created**: 2025-12-09T10:30:00Z
**Last Updated**: 2025-12-09T14:22:00Z

## Context

[Task description and background]

## Key Decisions

- 2025-12-09 10:35 - Chose file-based storage over database
- 2025-12-09 11:20 - Use CLAUDE.md @import for context injection

## Approaches Tried

### Approach: Embedded storage in task files
**Result**: ❌ Rejected
**Reason**: Complex parsing, format rigidity

## Open Questions

- How to handle memory >1MB? (Add compression/truncation?)

## Resources

- [Links to external documentation]

## Notes

[Append-only section for freeform notes]
```

## Rationale

### Why File-Based Storage?

1. **Simplicity**: Pure file I/O operations, no database setup or management
2. **Git-Native Sync**: Standard `git push/pull` works out-of-box
3. **Human Readability**: Markdown format readable in any text editor
4. **Tool Agnostic**: Any tool with filesystem access can read/write
5. **Greppable**: Standard Unix tools (`grep`, `rg`, `find`) work natively
6. **Zero Dependencies**: No external services, databases, or daemons required
7. **IDE-Friendly**: Shows in file tree, supports search, syntax highlighting

### Why Separate memory/ Directory?

- **Logical Separation**: Task definitions vs. task context
- **Lifecycle Independence**: Archive memories without deleting tasks
- **Clear Boundaries**: Git operations can target memory separately
- **Organizational Clarity**: Developers immediately understand memory vs. task

### Why Markdown Format?

- **Universal Support**: Every editor, IDE, and AI agent understands markdown
- **Structured Yet Flexible**: Section headers provide structure, content remains freeform
- **Version Control Friendly**: Git diffs are meaningful
- **Documentation Standard**: Consistent with project documentation practices

## Consequences

### Positive

- ✅ **Simple Implementation**: File I/O only, no complex database operations
- ✅ **Git-Native Sync**: Works with existing git workflows, no additional tooling
- ✅ **Human-Readable**: Developers can read/edit with any text editor
- ✅ **Agent-Agnostic**: Any tool can read markdown (AI agents, scripts, humans)
- ✅ **Performance**: File system operations < 50ms for 10,000+ files
- ✅ **Scalability**: Directory sharding strategy available if needed
- ✅ **Backup-Friendly**: Standard file backup tools work
- ✅ **Search-Friendly**: `grep`, `rg`, IDE search all work natively

### Negative

- ⚠️ **No Atomic Transactions**: Multiple concurrent writes could conflict
- ⚠️ **Manual Archival**: Requires cleanup strategy (mitigated by lifecycle hooks)
- ⚠️ **Large Files**: No automatic compression (mitigated by 1MB archival threshold)

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Concurrent write conflicts | Medium | Low | Single developer per task + file locking |
| Memory file size growth | Medium | Medium | Automatic archival at 1MB threshold |
| Performance at 10,000+ tasks | Medium | Low | Directory sharding if needed |
| Accidental deletion | High | Low | Git history + archive retention |

## Alternatives Considered

### Alternative 1: Embedded in Task Files

Store memory within task definition files using YAML frontmatter or markdown sections.

**Rejected because**:
- Complex parsing required
- Risk of corrupting task definitions
- Format rigidity limits flexibility
- Lifecycle coupling (can't archive memory independently)

### Alternative 2: SQLite Database

Use SQLite database for structured storage.

**Rejected because**:
- Adds dependency
- Not human-readable without tools
- Git sync requires binary file handling
- Schema migrations add complexity
- Overkill for append-mostly data

### Alternative 3: External Service (Cloud DB)

Use external database or cloud storage service.

**Rejected because**:
- Network dependency
- Requires authentication/credentials
- Privacy/security concerns
- Offline work not possible
- Vendor lock-in risk

### Alternative 4: Git Notes

Use Git's native notes feature for task metadata.

**Rejected because**:
- Limited discoverability (not in working tree)
- Complex CLI operations
- Not file-system visible to agents
- Poor IDE integration

## Implementation Considerations

### Performance Characteristics

- **Read**: O(1) - direct file path access
- **Write**: O(1) - append or overwrite single file
- **List Active**: O(n) - directory scan, n = active tasks
- **Search**: O(n) - grep across files, n = total memory files

### Storage Requirements

- **Typical memory file**: 50-200 KB
- **1,000 tasks**: ~50-200 MB
- **10,000 tasks**: ~500 MB - 2 GB (acceptable for modern systems)

### Cleanup Strategy

- **Active memories**: Remain in `backlog/memory/`
- **Completed task memories**: Move to `backlog/memory/archive/`
- **Archived task memories**: Delete after confirmation
- **Large memories (>1MB)**: Automatically archived with compression option

## Success Criteria

1. **Operational**: Memory create/read/append operations complete in <50ms
2. **Scalability**: No performance degradation up to 10,000 tasks
3. **Reliability**: Zero data loss incidents
4. **Usability**: Developers can read/edit files without tools
5. **Sync**: Git operations work without conflicts >95% of time

## References

- [Gregor Hohpe - Architecture as Selling Options](https://architectelevator.com/architecture/architecture-options/)
- [Task Memory System Architecture](../architecture/task-memory-system.md)
- [Flowspec Constitution](../../memory/constitution.md)
- [Backlog.md Specification](https://github.com/jpoley/backlog.md)

## Notes

This ADR establishes the foundation for the Task Memory system. Future ADRs will address:
- ADR-002: Context injection into AI agents
- ADR-003: Lifecycle triggers and automation
- ADR-004: Cross-environment synchronization

**Implementation tracked in**: task-375 (TaskMemoryStore Component)
