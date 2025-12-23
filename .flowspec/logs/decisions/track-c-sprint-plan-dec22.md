# Track C: Task Memory Sprint Plan
**Date**: 2025-12-22
**Tasks**: task-368 (parent), task-377 (Claude Code integration), task-386 (@import injection)

## Executive Summary

Task Memory is **85% complete**. Core infrastructure is fully implemented and tested:
- Storage layer (TaskMemoryStore) ✓
- Lifecycle management (LifecycleManager) ✓
- Context injection (ContextInjector) ✓
- CLI hooks integration ✓
- Unit tests passing ✓

**Remaining work**: Token-aware truncation integration, E2E testing, documentation.

**Estimated completion time**: 5-7 hours total.

---

## Architecture Overview

### Component Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│              Claude Code Session Start                   │
│         (.claude/hooks/session-start.sh)                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              ContextInjector                             │
│   • estimate_tokens()                                    │
│   • truncate_memory_content()                           │
│   • update_active_task_with_truncation()                │
│   • Updates backlog/CLAUDE.md with @import              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              backlog/CLAUDE.md                           │
│   ## Active Task Context                                │
│   @import ../memory/task-377.md                         │
│   (or task-377.truncated.md if >2000 tokens)            │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Claude Code Agent                           │
│   • Automatically loads task context                    │
│   • No manual intervention needed                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Task Status Changes                         │
│         (backlog task edit XXX -s "...")                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│         Post-Tool-Use Hook (Claude Code)                 │
│   (.claude/hooks/post-tool-use-task-memory-lifecycle)   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              LifecycleManager                            │
│   • on_state_change()                                   │
│   • State transitions: To Do → In Progress → Done       │
│   • Calls ContextInjector for CLAUDE.md updates         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              TaskMemoryStore                             │
│   • create() - new memory from template                 │
│   • archive() - move to archive/ on Done                │
│   • restore() - restore from archive on reopen          │
│   • delete() - permanent deletion                       │
└─────────────────────────────────────────────────────────┘
```

### State Transition Matrix

| From State   | To State     | Memory Operation          | CLAUDE.md Action        |
|--------------|--------------|---------------------------|-------------------------|
| To Do        | In Progress  | Create memory file        | Add @import            |
| In Progress  | Done         | Archive memory            | Clear @import          |
| Done         | In Progress  | Restore from archive      | Add @import            |
| Done         | Archive      | Delete permanently        | N/A                    |
| In Progress  | To Do        | Delete memory             | Clear @import          |

---

## Current Implementation Status

### ✓ Completed Components

#### 1. TaskMemoryStore (`src/flowspec_cli/memory/store.py`)
- **Lines**: 481 total
- **Key Features**:
  - File-based storage in `backlog/memory/`
  - Archive support in `backlog/memory/archive/`
  - Template-based memory creation
  - YAML frontmatter for metadata
  - Path traversal protection
  - Section-based content append
- **Test Coverage**: 100% (tests/test_memory_store.py)

#### 2. LifecycleManager (`src/flowspec_cli/memory/lifecycle.py`)
- **Lines**: 292 total
- **Key Features**:
  - State transition handling (6 transitions)
  - CLAUDE.md integration
  - Automatic memory sync to backlog on completion
  - Graceful error handling
  - Auto-creates CLAUDE.md if missing
- **Test Coverage**: 100% (tests/test_memory_lifecycle.py - 504 lines, 40+ tests)

#### 3. ContextInjector (`src/flowspec_cli/memory/injector.py`)
- **Lines**: 358 total
- **Key Features**:
  - @import directive management
  - Active Task Context section in CLAUDE.md
  - Token estimation (4 chars/token approximation)
  - Content truncation (preserves header + recent context)
  - Regex-based section replacement
  - Multiple rapid transition handling
- **Test Coverage**: 100% (tests/test_memory_injector.py - 246 lines, 12 tests)
- **Token Truncation Strategy**:
  1. Always preserve header (task ID, metadata)
  2. Always preserve Context section (recent work)
  3. Truncate from Notes section first (oldest content)
  4. Truncate from Key Decisions if still too large
  5. Add truncation notice if content cut

#### 4. CLI Hooks Integration
- **session-start.sh** (`.claude/hooks/session-start.sh`, lines 99-121):
  - Detects active tasks via `backlog task list`
  - Injects first active task memory into CLAUDE.md
  - Displays "Task memory available" notification
  - Fail-silent Python integration (no session blocking)
- **post-tool-use hook** (`.claude/hooks/post-tool-use-task-memory-lifecycle.py`, 273 lines):
  - Intercepts `backlog task edit` commands
  - Parses status changes from command
  - Infers old status from memory existence
  - Triggers LifecycleManager state transitions
  - Fail-open principle (never blocks CLI)

#### 5. E2E Test Infrastructure
- **test_memory_lifecycle_e2e.py** (193+ lines):
  - Full project structure setup
  - Complete lifecycle testing
  - CLAUDE.md integration tests
  - Template system validation

---

## Remaining Work Breakdown

### task-377: AC#2 - Token-aware injection (2-3 hours)

**Problem**: ContextInjector has truncation logic but it's not wired up to LifecycleManager.

**Current Behavior**:
```python
# lifecycle.py line 273
self.injector.update_active_task(task_id)  # No truncation!
```

**Required Behavior**:
```python
# lifecycle.py line 273
self.injector.update_active_task_with_truncation(task_id)  # Token-aware!
```

**Implementation Steps**:
1. Modify `LifecycleManager._update_claude_md()`:
   ```python
   # Replace line 273
   self.injector.update_active_task_with_truncation(task_id)
   ```

2. Update session-start.sh hook (line 113):
   ```python
   # Replace
   injector.update_active_task(os.environ.get("FIRST_TASK_ID", ""))
   # With
   injector.update_active_task_with_truncation(os.environ.get("FIRST_TASK_ID", ""))
   ```

3. Add unit tests for token truncation:
   ```python
   def test_lifecycle_uses_token_truncation(manager, tmp_project):
       """Verify LifecycleManager triggers token-aware injection."""
       task_id = "task-375"
       
       # Create large memory file (>2000 tokens)
       manager.store.create(task_id, task_title="Test")
       large_content = "X" * 10000  # ~2500 tokens
       manager.store.append(task_id, large_content)
       
       # Trigger state change
       manager.on_state_change(task_id, "To Do", "In Progress")
       
       # Verify truncated file created
       truncated_path = manager.injector.get_memory_path(f"{task_id}.truncated")
       assert truncated_path.exists()
       
       # Verify import points to truncated version
       claude_md = (tmp_project / "backlog" / "CLAUDE.md").read_text()
       assert f"@import ../memory/{task_id}.truncated.md" in claude_md
   ```

4. Test with real large file:
   - Create 5000+ character memory file
   - Verify truncation happens
   - Verify truncation notice appears
   - Verify original file unchanged

**Files to Modify**:
- `src/flowspec_cli/memory/lifecycle.py` (1 line change)
- `.claude/hooks/session-start.sh` (1 line change)
- `tests/test_memory_lifecycle.py` (add 2-3 tests)
- `tests/test_memory_injector.py` (add truncation edge case tests)

**Acceptance Criteria**:
- [x] estimate_tokens() implemented
- [ ] update_active_task_with_truncation() called by LifecycleManager
- [ ] session-start hook uses truncation
- [ ] Unit tests verify max 2000 tokens
- [ ] Large memory files trigger truncation
- [ ] Truncated files are .truncated.md
- [ ] Original memory files unchanged

---

### task-377: AC#6 - E2E tests for Claude Code integration (2 hours)

**Dependencies**: AC#2 must complete first (needs working truncation).

**Test Scenarios**:

1. **Session start with active task** (happy path):
   ```python
   def test_session_start_injects_active_task():
       # Setup: Create task, set to In Progress
       # Action: Simulate session-start hook
       # Assert: CLAUDE.md has @import for task
   ```

2. **Memory exceeding 2000 tokens**:
   ```python
   def test_session_start_truncates_large_memory():
       # Setup: Create task with >2000 token memory
       # Action: Run session-start hook
       # Assert: .truncated.md file created
       # Assert: CLAUDE.md imports .truncated.md
       # Assert: Truncation notice in content
   ```

3. **Multiple active tasks** (only first injected):
   ```python
   def test_session_start_multiple_active_tasks():
       # Setup: 3 tasks in "In Progress"
       # Action: Run session-start hook
       # Assert: Only task-1 imported (not task-2, task-3)
   ```

4. **No active tasks** (graceful no-op):
   ```python
   def test_session_start_no_active_tasks():
       # Setup: All tasks "To Do" or "Done"
       # Action: Run session-start hook
       # Assert: No @import in CLAUDE.md
       # Assert: No errors logged
   ```

5. **Memory file missing but task active**:
   ```python
   def test_session_start_task_active_no_memory():
       # Setup: Task "In Progress" but no memory file
       # Action: Run session-start hook
       # Assert: @import added anyway (file may be created later)
       # Assert: No crash or error
   ```

6. **CLAUDE.md @import loads automatically** (manual test):
   ```bash
   # Create real task
   backlog task create "Test memory injection" -s "In Progress"
   
   # Add content to memory
   echo "## Context\nTesting @import injection" >> backlog/memory/task-XXX.md
   
   # Start new Claude Code session
   # In Claude: "What task am I working on?"
   # Expected: Claude knows task-XXX context
   ```

**Test Implementation**:
- Extend `tests/e2e/test_memory_injection_e2e.py`
- Add subprocess tests for session-start hook
- Add manual test documentation in task notes
- Verify hook exit codes (always 0, fail-open)

**Acceptance Criteria**:
- [ ] Automated tests for scenarios 1-5
- [ ] Manual Claude Code test documented
- [ ] All tests pass
- [ ] Coverage >90% for injection path

---

### task-386: AC#2 - LifecycleManager integration (30 minutes)

**Same as task-377 AC#2** - these overlap completely. LifecycleManager needs to call `update_active_task_with_truncation()`.

**Implementation**: See task-377 AC#2 above.

---

### task-386: AC#3 - Test @import with Claude Code (30 minutes)

**Dependencies**: task-386 AC#2 (LifecycleManager integration)

**Manual Test Procedure**:

```bash
# 1. Create test task
backlog task create "Test @import injection in Claude Code" \
  -s "In Progress" \
  -d "Verify that task memory is automatically loaded into Claude's context"

# 2. Capture task ID
TASK_ID=$(backlog task list --plain -s "In Progress" | head -n1 | grep -oP '^task-\d+')
echo "Testing with: $TASK_ID"

# 3. Add test content to memory
cat >> backlog/memory/$TASK_ID.md << 'CONTENT'
## Context

This is a test task to verify @import injection works correctly.

## Key Decisions

- Decision 1: Use @import directive in backlog/CLAUDE.md
- Decision 2: Load memory automatically on session start
- Decision 3: Max 2000 tokens per task

## Notes

Lorem ipsum dolor sit amet, consectetur adipiscing elit...
[Add ~2500 tokens of content here to test truncation]
CONTENT

# 4. Verify CLAUDE.md updated
cat backlog/CLAUDE.md | grep "@import"
# Expected: @import ../memory/task-XXX.md (or .truncated.md)

# 5. Check for truncation (if >2000 tokens)
ls -lh backlog/memory/$TASK_ID.truncated.md 2>/dev/null
# If exists: truncation occurred

# 6. Start new Claude Code session
# In new session, ask Claude:
# "What task am I currently working on? Summarize the key decisions."

# Expected output:
# Claude should mention task-XXX, the test context, and key decisions

# 7. Test truncation notice
# If truncated, Claude should mention content was truncated

# 8. Document results
backlog task edit ${TASK_ID#task-} --notes \
  "Manual Claude Code test results: [PASS/FAIL with details]"
```

**Acceptance Criteria**:
- [ ] Task memory loads automatically in new Claude session
- [ ] Claude can summarize task context
- [ ] Truncation works for >2000 token files
- [ ] Truncation notice visible to Claude
- [ ] Test results documented in task notes

---

### task-386: AC#7 - Document @import mechanism (1-2 hours)

**Can run in parallel with other work.**

**Documentation Plan**:

#### 1. Create `docs/guides/task-memory-injection.md`

**Outline**:
```markdown
# Task Memory @import Injection

## Overview
Task Memory is automatically loaded into Claude Code sessions via the @import directive.

## How It Works
1. When task moves to "In Progress", memory file created
2. session-start.sh hook detects active tasks
3. ContextInjector updates backlog/CLAUDE.md with @import
4. Claude Code loads memory automatically on session start
5. Task context available without manual intervention

## Token Limits
- Max 2000 tokens per task memory
- Truncation preserves: header, Context, Key Decisions
- Oldest content truncated first (Notes section)
- Truncation notice added when content cut
- Original memory file unchanged

## File Locations
- Active memory: `backlog/memory/task-XXX.md`
- Truncated copy: `backlog/memory/task-XXX.truncated.md`
- Injection point: `backlog/CLAUDE.md` (Active Task Context section)
- Archive: `backlog/memory/archive/` (for Done tasks)

## Lifecycle Integration
- To Do → In Progress: Create memory + inject @import
- In Progress → Done: Archive memory + clear @import
- Done → In Progress: Restore memory + inject @import

## Manual Operations
```bash
# View active task memory
flowspec memory show task-375

# Edit memory manually
flowspec memory edit task-375

# Clear and restart memory
flowspec memory clear task-375

# Force re-inject into CLAUDE.md
flowspec memory inject task-375
```

## Troubleshooting

**Memory not loading in Claude?**
- Check `backlog/CLAUDE.md` has @import directive
- Verify memory file exists: `ls backlog/memory/task-*.md`
- Restart Claude Code session
- Check session-start hook ran: look for "Task memory available" message

**Memory file too large?**
- Check for `.truncated.md` file
- Verify truncation notice in content
- Reduce Notes section size
- Move old content to task notes (archived in backlog)

**Multiple tasks active?**
- Only first task injected automatically
- Use `flowspec memory inject task-XXX` for others
- Consider completing tasks before starting new ones

## Architecture Diagram
[Include diagram from this report]
```

#### 2. Update `docs/guides/backlog-user-guide.md`

Add section:
```markdown
## Task Memory Integration

When you start working on a task, Flowspec automatically creates a memory file
to track context, decisions, and notes. This memory is injected into Claude
Code sessions so the agent always has context about your current work.

See [Task Memory @import Injection](task-memory-injection.md) for details.
```

#### 3. Add comments to `backlog/CLAUDE.md` template

```markdown
## Active Task Context

<!-- 
This section is automatically managed by Flowspec task memory.
Do not edit manually - use `flowspec memory` commands instead.

The @import directive below loads task context into Claude Code sessions.
Maximum 2000 tokens per task. Content truncated if needed.
-->

@import ../memory/task-42.md
```

#### 4. Update main `README.md`

Add to features section:
```markdown
- **Task Memory**: Automatic context injection into Claude Code sessions
  - Memory files track implementation context, decisions, and notes
  - Auto-loads into agent context via @import directive
  - Token-aware truncation (max 2000 tokens per task)
  - Persists across sessions and machines (via git)
```

**Files to Create/Modify**:
- `docs/guides/task-memory-injection.md` (new, ~200 lines)
- `docs/guides/backlog-user-guide.md` (add 1 section)
- `backlog/CLAUDE.md` (add template comments)
- `README.md` (add feature bullet)

**Acceptance Criteria**:
- [ ] Comprehensive guide created
- [ ] User guide updated
- [ ] Template comments added
- [ ] README updated
- [ ] All cross-references valid

---

## Dependency Graph

```
task-368 (parent)
├── task-377 (Claude Code integration)
│   ├── AC#2: Token-aware injection ←──┐
│   │   (BLOCKS)                       │ SAME WORK
│   └── AC#6: E2E tests                │
│       (depends on AC#2)               │
│                                       │
└── task-386 (@import injection)       │
    ├── AC#2: LifecycleManager ────────┘
    │   (depends on nothing)
    ├── AC#3: Manual Claude test
    │   (depends on AC#2)
    └── AC#7: Documentation
        (can run in parallel)
```

**Critical Path**: task-377 AC#2 → task-377 AC#6 → task-386 AC#3

**Parallel Work**: task-386 AC#7 (documentation) can happen anytime

---

## Work Breakdown by Effort

### High Priority (Blocks Other Work)
1. **task-377 AC#2 / task-386 AC#2**: Token-aware injection integration
   - **Effort**: 30 min (code) + 1 hour (tests) = 1.5 hours
   - **Blocks**: All remaining work
   - **Files**: 2 changes, 5-10 new tests

### Medium Priority (Dependent Work)
2. **task-377 AC#6**: E2E tests for Claude Code integration
   - **Effort**: 2 hours (automated) + 30 min (manual) = 2.5 hours
   - **Depends on**: AC#2
   - **Files**: Extend existing E2E tests

3. **task-386 AC#3**: Manual Claude Code testing
   - **Effort**: 30 minutes
   - **Depends on**: AC#2
   - **Deliverable**: Test procedure + results in task notes

### Low Priority (Can Parallelize)
4. **task-386 AC#7**: Documentation
   - **Effort**: 1-2 hours
   - **Depends on**: Nothing (can start anytime)
   - **Files**: 1 new guide + 3 updates

---

## Risk Assessment

### Low Risk
- Core infrastructure complete and tested
- Token truncation logic already implemented
- Integration is simple (1-line changes)
- Fail-open design prevents blocking

### Medium Risk
- Manual Claude Code testing requires real session
  - **Mitigation**: Detailed test procedure documented
- Token estimation is approximation (4 chars/token)
  - **Mitigation**: Conservative limit (2000 tokens = ~8000 chars)
  - **Mitigation**: Truncation notice alerts user

### No High Risks Identified

---

## Completion Estimate

**Sequential Path** (if working alone):
1. AC#2 (token integration): 1.5 hours
2. AC#6 (E2E tests): 2.5 hours
3. AC#3 (manual test): 0.5 hours
4. AC#7 (documentation): 1.5 hours

**Total**: 6 hours

**Parallel Path** (if documentation delegated):
1. AC#2 + AC#7 (parallel): 1.5 hours
2. AC#6: 2.5 hours  
3. AC#3: 0.5 hours

**Total**: 4.5 hours

**Recommended Approach**: Sequential (documentation quality benefits from seeing implementation work)

---

## Quality Gates

Before marking tasks Done:

### task-377 Completion Checklist
- [ ] LifecycleManager uses update_active_task_with_truncation()
- [ ] session-start hook uses update_active_task_with_truncation()
- [ ] Unit tests verify token truncation
- [ ] E2E tests pass (6 scenarios)
- [ ] Manual Claude Code test documented with results
- [ ] All tests green
- [ ] Code reviewed (self-review minimum)

### task-386 Completion Checklist
- [ ] LifecycleManager integration complete (same as task-377 AC#2)
- [ ] Manual Claude Code test passed and documented
- [ ] Documentation created (task-memory-injection.md)
- [ ] Related docs updated (3 files)
- [ ] Cross-references validated
- [ ] All links work

### task-368 Completion Checklist
- [ ] All child tasks (task-377, task-386) Done
- [ ] All 8 acceptance criteria met
- [ ] Architecture documented
- [ ] User-facing documentation complete
- [ ] E2E tests passing
- [ ] No regressions in unit tests

---

## Next Steps (Recommended Order)

1. **Implement token-aware integration** (task-377 AC#2, task-386 AC#2):
   - Modify LifecycleManager._update_claude_md()
   - Update session-start.sh hook
   - Write unit tests for truncation
   - Test with large memory file

2. **Create E2E tests** (task-377 AC#6):
   - Extend test_memory_injection_e2e.py
   - Cover 6 test scenarios
   - Verify all tests pass

3. **Manual Claude Code test** (task-386 AC#3):
   - Follow documented test procedure
   - Capture results
   - Add notes to task

4. **Write documentation** (task-386 AC#7):
   - Create task-memory-injection.md guide
   - Update related docs
   - Validate cross-references

5. **Final validation**:
   - Run full test suite
   - Check all acceptance criteria
   - Mark tasks Done

---

## Files Summary

### Files to Modify (5)
1. `src/flowspec_cli/memory/lifecycle.py` (1 line)
2. `.claude/hooks/session-start.sh` (1 line)
3. `tests/test_memory_lifecycle.py` (add 3-5 tests)
4. `tests/test_memory_injector.py` (add 2-3 tests)
5. `tests/e2e/test_memory_injection_e2e.py` (extend)

### Files to Create (1)
1. `docs/guides/task-memory-injection.md` (~200 lines)

### Files to Update (3)
1. `docs/guides/backlog-user-guide.md` (add section)
2. `backlog/CLAUDE.md` (add comments)
3. `README.md` (add feature)

---

## Conclusion

Task Memory is nearly complete with solid architecture and comprehensive test coverage. The remaining work is primarily:
1. Wiring up existing token truncation logic (30 min)
2. Testing the integration (3 hours)
3. Documentation (1.5 hours)

**All components are in place** - this is assembly and validation work, not new feature development.

**Confidence Level**: High. No major technical risks identified.
