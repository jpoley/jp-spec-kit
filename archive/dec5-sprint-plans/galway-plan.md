# Galway Task Execution Plan - December 5, 2025

## Status Summary

### Completed Tasks (5)
| Task | Description | Status |
|------|-------------|--------|
| task-190 | Create 5 Core Skills for SDD Workflow | Done |
| task-191 | Create 4 Engineering Subagents | Done |
| task-272 | Migrate speckit commands to subdirectory | Done |
| task-276 | Create command migration script | Done |
| task-281 | Create archive-tasks.sh script | Done |

### Remaining Tasks (13)

#### High Priority (7)
| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| task-278 | Add CI validation for command structure | None | Small |
| task-279 | Update documentation for new architecture | None | Medium |
| task-281.01 | Implement archive-tasks.sh with flexible filtering | task-281 | Small |
| task-282 | Create backlog-archive.yml GitHub workflow | task-281.01 | Medium |
| task-087 | Production Case Studies Documentation | None | Large |
| task-134 | Integrate diagrams and documentation | None | Medium |
| task-204 | Integrate Event Emission into Backlog | None | Large |

#### Medium Priority (4)
| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| task-204.01 | Create git hook for backlog events | task-204 | Small |
| task-204.02 | Create backlog CLI wrapper with events | task-204 | Medium |
| task-283 | Post-workflow-archive.sh hook | task-281.01 | Small |
| task-284 | Documentation for archive-tasks.sh | task-281.01 | Medium |

#### Low Priority (2)
| Task | Description | Dependencies | Effort |
|------|-------------|--------------|--------|
| task-204.03 | Contribute hooks/events upstream | task-204.02 | Large |
| task-285 | CI check for stale Done tasks | None | Small |

---

## Recommended Execution Order

### Wave 1: Quick Wins (Can be parallelized)
Focus on small, independent tasks to build momentum.

1. **task-278** - Add CI validation for command structure
   - Adds pre-commit-dev-setup.sh to CI pipeline
   - Prevents future symlink issues
   - ~30 min effort

2. **task-285** - Add optional CI check for stale Done tasks
   - Low priority but quick win
   - ~30 min effort

### Wave 2: Documentation & Architecture
Complete documentation updates before larger feature work.

3. **task-279** - Update documentation for new architecture
   - Document subdirectory structure
   - Update README, CHANGELOG
   - Create upgrade guide section for migration script
   - ~1-2 hours

4. **task-284** - Documentation for archive-tasks.sh
   - Complete docs for existing script
   - ~1 hour

### Wave 3: Archive System Completion
Finish the archive-tasks feature set.

5. **task-281.01** - Implement archive-tasks.sh with flexible filtering
   - Enhance existing script with filters
   - ~1 hour

6. **task-282** - Create backlog-archive.yml workflow
   - GitHub Actions workflow for archiving
   - Depends on task-281.01
   - ~1-2 hours

7. **task-283** - Post-workflow-archive.sh hook
   - Claude Code hook integration
   - Depends on task-281.01
   - ~30 min

### Wave 4: Event System (Larger Feature)
Implement the event emission system.

8. **task-204** - Integrate Event Emission into Backlog
   - Core event system design
   - ~2-3 hours

9. **task-204.01** - Git hook for backlog events
   - Depends on task-204
   - ~1 hour

10. **task-204.02** - Backlog CLI wrapper with events
    - Depends on task-204
    - ~1-2 hours

### Wave 5: Documentation & Polish

11. **task-134** - Integrate diagrams and documentation
    - Architecture diagrams
    - ~2 hours

12. **task-087** - Production Case Studies Documentation
    - Requires real-world examples
    - ~3-4 hours

### Wave 6: Upstream Contribution (Optional)

13. **task-204.03** - Contribute hooks/events upstream
    - Depends on task-204.02 being stable
    - Large effort, coordinate with upstream

---

## Immediate Next Steps

Start with **Wave 1** tasks in parallel:

```bash
# Task 278: CI validation
backlog task edit task-278 -s "In Progress" -a @galway

# Task 285: Stale Done check (if time permits)
backlog task edit task-285 -s "In Progress" -a @galway
```

### Task 278 Implementation Checklist
- [ ] Add dev-setup-validation job to CI workflow
- [ ] Configure to run on PRs affecting .claude/ or templates/
- [ ] Test with a PR that has correct symlinks
- [ ] Test with a PR that would break symlinks

### Task 285 Implementation Checklist
- [ ] Create script to detect Done tasks older than N days
- [ ] Add optional CI job (off by default)
- [ ] Document usage in scripts/CLAUDE.md

---

## Risk Notes

1. **task-204 family** - Event system is complex; may need design review first
2. **task-087** - Case studies require real customer/usage data
3. **task-204.03** - Upstream contribution depends on their acceptance

## Branch Naming Convention

Follow established pattern:
```
galway-{task-number}-{short-description}
```

Examples:
- `galway-278-ci-validation`
- `galway-279-architecture-docs`
- `galway-282-archive-workflow`
