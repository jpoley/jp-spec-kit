# ADR-004: Task Memory Cross-Environment Sync Strategy

**Status**: Accepted
**Date**: 2025-12-09
**Decision Makers**: Architecture Team, Enterprise Software Architect

## Context

Task Memory must travel with tasks across machines and environments. Developers work on:
- **Desktop workstation** (primary development)
- **Laptop** (travel, meetings)
- **Remote servers** (SSH, dev containers)
- **CI/CD environments** (automated testing)

### Requirements

1. **Cross-machine sync**: Memory available on all developer machines
2. **Offline-first**: Sync works without network connectivity
3. **Zero additional infrastructure**: No external services
4. **Conflict resolution**: Handle concurrent edits gracefully
5. **Transparent operations**: Sync using familiar tools (git)

### Sync Scenarios

| Scenario | Frequency | Complexity |
|----------|-----------|------------|
| Single developer, multiple machines | High | Low (rare conflicts) |
| Team collaboration, task handoff | Medium | Medium (sequential edits) |
| Concurrent edits on same task | Low | High (true conflicts) |
| CI/CD environment access | High | Low (read-only) |

## Decision

**Use git-based sync with markdown conflict resolution strategy**

### Sync Mechanism

Standard git operations work out-of-box:

```bash
# Developer on Machine A
backlog task edit task-368 -s "In Progress"
# ... work, memory appended ...
git add backlog/memory/task-368.md
git commit -m "task-368: Tried approach X"
git push

# Developer on Machine B (or same developer, different machine)
git pull
# Memory now available with latest context
```

### Conflict Resolution Strategy

**Philosophy**: Append-mostly data structure minimizes conflicts

#### Conflict Types

**1. Rare: Concurrent Appends (90% of conflicts)**

Developer A and Developer B both append notes simultaneously.

```markdown
# Git merge creates:
<<<<<<< HEAD (Machine A)
- Tried approach X, failed because of Z
- Investigated library performance
=======
- Decided to use library Y after research
- Added caching layer
>>>>>>> branch (Machine B)
```

**Resolution**: Keep both (append-only nature)

```markdown
# Resolved version:
- Tried approach X, failed because of Z
- Investigated library performance
- Decided to use library Y after research
- Added caching layer
```

**2. Uncommon: Structural Edits (10% of conflicts)**

Developer edits section headers or reformats existing content.

**Resolution**: Standard git merge tools (manual resolution required)

#### Conflict Probability Analysis

| Factor | Impact on Conflicts | Mitigation |
|--------|---------------------|------------|
| Append-only format | ↓ Low conflict rate | Most edits don't overlap |
| Single developer per task | ↓ Rare concurrent edits | Task ownership clear |
| Markdown format | ↑ Merge-friendly | Line-based diffs work well |
| Small file size (<200KB) | ↓ Easier to resolve | Human-readable resolution |

**Expected conflict rate**: <5% of syncs (based on append-mostly nature)

## Rationale

### Why Git-Based Sync?

1. **Zero additional infrastructure**: Git already used for code
2. **Offline-first**: Commit locally, sync when connected
3. **Transparent operations**: Familiar git workflow
4. **Tool agnostic**: Works with any git client
5. **Version history**: Full audit trail of memory changes
6. **Branching support**: Memory follows git branches naturally

### Why Markdown Format (for sync)?

1. **Line-based diffs**: Git merge tools work well
2. **Human-readable conflicts**: Easy to understand and resolve
3. **Append-mostly structure**: Sections accumulate, rarely edited
4. **No binary data**: Merge tools understand format

### Why Not Alternative Approaches?

**Dedicated sync service**:
- ❌ Additional infrastructure
- ❌ Network dependency
- ❌ Authentication/credentials
- ❌ Privacy concerns

**Conflict-free replicated data types (CRDTs)**:
- ❌ Complex implementation
- ❌ Overkill for low conflict rate
- ❌ Not human-readable
- ❌ Limited tool support

**Last-write-wins**:
- ❌ Data loss risk
- ❌ No merge of concurrent changes
- ❌ Defeats append-only benefit

## Consequences

### Positive

- ✅ **Zero additional infrastructure**: Uses existing git setup
- ✅ **Works offline**: Commit locally, sync later
- ✅ **Transparent**: Standard git operations
- ✅ **Version history**: Full audit trail via git log
- ✅ **Low conflict rate**: Append-only minimizes conflicts (<5%)
- ✅ **Human-resolvable**: Conflicts easy to understand and fix

### Negative

- ⚠️ **Rare conflicts require manual resolution**: ~5% of syncs
- ⚠️ **Git knowledge required**: Developers must understand git merge
- ⚠️ **No automatic conflict resolution**: Manual intervention needed

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Merge conflicts | Medium | Low (5%) | Append-only format, resolution guide |
| Lost context (no sync) | High | Low | Git hooks reminder, docs |
| Binary files in memory | High | Very Low | Linting, guidelines, pre-commit hooks |
| Large memory files | Medium | Low | 1MB archival threshold |

## Alternatives Considered

### Alternative 1: Dedicated Sync Service

Use cloud service (Dropbox, Google Drive, custom API).

**Rejected because**:
- Additional infrastructure cost
- Network dependency (breaks offline-first)
- Authentication complexity
- Privacy/security concerns
- Vendor lock-in

### Alternative 2: CRDTs (Conflict-Free Replicated Data Types)

Use CRDT library (Automerge, Yjs) for automatic conflict resolution.

**Rejected because**:
- High complexity for low conflict rate
- Not human-readable (binary format)
- Limited tooling support
- Overkill for append-mostly data

### Alternative 3: Last-Write-Wins

Simple overwrite strategy, latest write wins.

**Rejected because**:
- Data loss on concurrent edits
- Defeats append-only benefit
- No merge of concurrent context
- Unreliable for collaboration

### Alternative 4: SQLite with Cloud Sync

Use SQLite database with cloud replication (Litestream, rqlite).

**Rejected because**:
- Requires database (ADR-001 chose file-based)
- Cloud service dependency
- Complex conflict resolution
- Not human-readable

## Implementation Considerations

### Conflict Resolution Guide

**For developers** (in user documentation):

```markdown
# Resolving Memory Conflicts

1. **Identify conflict**: Git shows conflict markers in memory file
2. **Understand sections**: Review both versions (HEAD vs incoming)
3. **Append both**: Most conflicts can be resolved by keeping both
4. **Remove markers**: Delete `<<<<<<<`, `=======`, `>>>>>>>` lines
5. **Commit resolution**: `git add` and `git commit`

Example:
# Before (conflict):
<<<<<<< HEAD
- Tried approach X, failed
=======
- Decided on approach Y
>>>>>>> branch

# After (resolved - keep both):
- Tried approach X, failed
- Decided on approach Y
```

### Git Merge Strategy

**Use "union" merge driver** for memory files (optional):

```gitattributes
# .gitattributes
backlog/memory/*.md merge=union
```

Union merge automatically keeps both sides of conflict (useful for append-only files).

**Trade-off**:
- ✅ Automatic resolution of append conflicts
- ⚠️ May create duplicates if edits overlap
- ⚠️ Doesn't work for structural edits

**Recommendation**: Start without union merge, add if conflicts become common

### Sync Reminders

**Git hook reminder** (optional post-commit hook):

```bash
# .git/hooks/post-commit

if git diff --name-only HEAD~1 HEAD | grep -q 'backlog/memory/'; then
    echo "📝 Task memory updated. Remember to push to sync across machines:"
    echo "   git push"
fi
```

### CI/CD Integration

**Read-only access** in CI/CD:

```yaml
# .github/workflows/test.yml
- name: Checkout with task memory
  uses: actions/checkout@v4
  with:
    fetch-depth: 1  # Only need latest memory

- name: Run tests (memory available read-only)
  run: pytest tests/
```

## Success Criteria

1. **Sync reliability**: Memory syncs successfully >95% of time
2. **Conflict rate**: Conflicts occur <5% of syncs
3. **Resolution time**: Average conflict resolution <2 minutes
4. **Offline capability**: All operations work without network
5. **Zero infrastructure**: No additional services required

## Cross-Environment Use Cases

### Use Case 1: Desktop → Laptop

**Scenario**: Developer starts task on desktop, continues on laptop

```bash
# Desktop (evening)
backlog task edit task-368 -s "In Progress"
# ... work, memory created ...
git add backlog/memory/task-368.md backlog/CLAUDE.md
git commit -m "task-368: Initial investigation"
git push

# Laptop (morning)
git pull
# Memory available, developer continues seamlessly
```

**No conflicts** (sequential work)

### Use Case 2: Task Handoff

**Scenario**: Developer A starts, Developer B continues

```bash
# Developer A
backlog task edit task-368 -s "In Progress"
# ... work, memory accumulated ...
git push

# Developer B (different machine)
git pull
backlog task edit task-368 -a @developer-b
# B continues with full context from A's memory
```

**No conflicts** (handoff is sequential)

### Use Case 3: Concurrent Work (rare)

**Scenario**: Two developers work on same task simultaneously

```bash
# Developer A (Machine A)
echo "- Approach X failed" >> backlog/memory/task-368.md
git commit -m "task-368: Document failure"
git push

# Developer B (Machine B, before pulling)
echo "- Library Y selected" >> backlog/memory/task-368.md
git commit -m "task-368: Library decision"
git pull  # ⚠️ CONFLICT

# Resolution: Keep both lines (append-only)
# Resolved file:
# - Approach X failed
# - Library Y selected

git add backlog/memory/task-368.md
git commit -m "Merge memory from both developers"
git push
```

**Conflict occurred but easily resolved** (append both)

## Integration with Other ADRs

- **ADR-001**: Defines file locations that git syncs
- **ADR-002**: CLAUDE.md updates sync alongside memory files
- **ADR-003**: Lifecycle hooks create files that git syncs

## References

- [Git Merge Strategies](https://git-scm.com/docs/git-merge)
- [Gitattributes Merge Drivers](https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver)
- [Task Memory System Architecture](../architecture/task-memory-system.md)
- [ADR-001: Storage Mechanism](./ADR-001-task-memory-storage.md)

## Notes

This ADR establishes the cross-environment sync strategy that makes Task Memory portable. The git-based approach leverages existing infrastructure while the markdown format and append-only structure minimize conflicts.

**Implementation tracked in**:
- task-381 (Git sync documentation)
- task-397 (E2E test: cross-machine sync)

**Future consideration**: If conflict rate exceeds 10%, consider union merge driver or CRDT adoption.
