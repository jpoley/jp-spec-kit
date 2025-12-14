# Upstream Contributions

This directory contains design documents, implementation plans, and PR templates for contributions to upstream dependencies.

## Backlog.md Hook System

**Status**: Ready for PR submission
**Target**: https://github.com/MrLesk/Backlog.md
**Tracking Issue**: task-402

### Documents

1. **backlog-hooks-design.md**: Comprehensive design document
   - Architecture overview
   - Implementation details
   - TypeScript code examples
   - Integration points
   - Testing strategy
   - Security considerations

2. **hooks-api.md**: User-facing documentation
   - Quick start guide
   - Hook event reference
   - Configuration options
   - Use cases and examples
   - Troubleshooting guide
   - Best practices

3. **backlog-hooks-pr-template.md**: Pull request template
   - PR description and motivation
   - Features summary
   - Implementation details
   - Testing instructions
   - Backward compatibility notes

### Local Implementation

While the upstream PR is pending, a local implementation is available:

**File**: `src/specify_cli/memory/backlog_hooks.py`

**Usage**:
```python
from specify_cli.memory.backlog_hooks import emit_hook, HookEvent

# Emit a hook event
emit_hook(
    HookEvent.POST_TASK_UPDATE,
    task_id="task-402",
    old_status="To Do",
    new_status="In Progress"
)
```

**Tests**: `tests/test_backlog_hooks.py` (100% coverage)

**Examples**: `docs/examples/hooks/`
- task-memory-integration.sh
- slack-notifications.sh
- metrics-tracking.sh
- jira-sync.sh

### Next Steps

1. **Fork Repository**: Fork https://github.com/MrLesk/Backlog.md
2. **Create Branch**: `git checkout -b feat/hook-system`
3. **Port Implementation**: Convert Python proof-of-concept to TypeScript
4. **Add Tests**: Port tests to Bun test framework
5. **Submit PR**: Use template from `backlog-hooks-pr-template.md`

### Implementation Checklist

Design Phase:
- [x] Design document completed
- [x] API documentation written
- [x] Examples created

Local Implementation:
- [x] Python implementation (`backlog_hooks.py`)
- [x] Unit tests (9 tests, 100% coverage)
- [x] Integration examples
- [x] Linting passed

Upstream Contribution (Pending):
- [ ] Fork backlog.md repository
- [ ] Convert to TypeScript
- [ ] Add Bun tests
- [ ] Submit PR
- [ ] Respond to review feedback
- [ ] Merge and release

### Benefits

Once merged upstream:
- Automatic task memory lifecycle management
- Native hook support in backlog.md
- No wrapper scripts needed
- Better performance (native implementation)
- Wider ecosystem benefits

### Local Usage Until Merge

The local Python implementation can be used immediately:

```bash
# Install example hooks
python -c "from specify_cli.memory.backlog_hooks import install_example_hooks; install_example_hooks()"

# Hooks are now ready to use
backlog task create "Test hooks"
# Check: tail .backlog/hooks.log
```

### Related Tasks

- task-402: Upstream contribution to backlog CLI for hook support
- task-401: Hook integration for automatic memory capture
- task-375: Task Memory system implementation

### Contact

For questions about this contribution:
- Check design documents first
- Review API documentation
- See examples for common patterns
- Open discussion in upstream repository
