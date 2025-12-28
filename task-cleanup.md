# Task Cleanup Recommendations

Generated: 2025-12-28

## Summary

| Category | Count |
|----------|-------|
| Already Done | 13 |
| Likely Obsolete | 8 |
| Scope Creep / Deprioritize | 45+ |
| Keep Active | ~30 |

---

## ALREADY DONE - Mark Done & Archive

These tasks have existing implementations in the codebase:

| Task | Title | Evidence |
|------|-------|----------|
| **task-489** | claude-improves-again: Add /flow:intake command | `.claude/commands/flow/intake.md` exists |
| **task-491** | claude-improves-again: Create PRP base template | `templates/docs/prp/prp-base-flowspec.md` exists |
| **task-492** | claude-improves-again: Add /flow:generate-prp command | `.claude/commands/flow/generate-prp.md` exists |
| **task-490** | claude-improves-again: Update CLAUDE.md to prefer INITIAL docs | INITIAL Document Workflow section in CLAUDE.md |
| **task-495** | claude-improves-again: Add context extraction helper skill | `.claude/skills/context-extractor/` exists |
| **task-499** | claude-improves-again: Add /flow:map-codebase command | `.claude/commands/flow/map-codebase.md` exists |
| **task-500** | claude-improves-again: Add Known Gotchas/Prior Failures section | Present in `templates/prd-template.md` |
| **task-501** | claude-improves-again: Add gather-learnings helper skill | `.claude/skills/gather-learnings/` exists |
| **task-541** | Create _rigor-rules.md shared include file | `.claude/commands/flow/_rigor-rules.md` exists |
| **task-542** | Add JSONL decision logging infrastructure | `.flowspec/logs/events/` directory exists with JSONL files |
| **task-496** | claude-improves-again: Add Feature Validation Plan section | Present in `templates/prd-template.md` |
| **task-488** | claude-improves-again: Add INITIAL feature intake template | `templates/docs/initial/initial-feature-template.md` exists |
| **task-494** | claude-improves-again: Add All Needed Context section to /flow:specify | Likely done with context-extractor skill |

**Action**: `backlog task edit <id> -s Done && backlog task archive <id>` for each

---

## LIKELY OBSOLETE - Archive Without Completing

These tasks are no longer relevant due to architecture changes or superseded approaches:

| Task | Title | Reason |
|------|-------|--------|
| **task-467** | claude-improves: Document standalone security skills | Security features moved to MCP server; skills documented in skills themselves |
| **task-309** | Sync .agents/ and .claude/agents/ directories | Agents now symlinked; sync approach abandoned |
| **task-336** | Update documentation for VS Code Copilot support | Copilot prompts now auto-generated from commands |
| **task-204.03** | Contribute hooks/events feature to upstream backlog.md | Backlog.md has own development path; not pursuing upstream |
| **task-226** | Implement Optional AFL++ Fuzzing Support | Security scanning moved to dedicated MCP; fuzzing deprioritized |
| **task-195** | Create Flowspec Plugin Package | Plugin architecture not being pursued |
| **task-081** | Claude Plugin Architecture | Superseded by MCP and skills architecture |
| **task-136** | Add Primary Support for claude-trace Observability Tool | Tool may be deprecated; needs verification |

**Action**: Archive directly without marking Done

---

## SCOPE CREEP - Consider Archiving Entire Feature Sets

These represent large feature sets that may be over-engineered or deprioritized:

### Task Memory System (task-368 and subtasks)
**Status**: In Progress but massive scope (7 phases, 30+ subtasks)
**Recommendation**: Review if this complexity is needed. Consider simplifying to just:
- Basic context file per task
- Manual management
- Skip the elaborate lifecycle/hooks/CLI

Related tasks to potentially archive:
- task-382, task-383, task-387, task-388, task-389, task-390, task-391, task-392, task-393, task-394, task-395, task-397, task-398, task-399, task-402

### Event System / Telemetry (task-485-540+)
**Status**: To Do, very large scope
**Recommendation**: This is a 50+ task initiative for event emission, action registry, DORA metrics. Consider:
- Is this needed for flowspec's core mission?
- Could be a separate project entirely

Related tasks to potentially archive:
- task-485, task-486, task-487, task-504, task-507, task-508, task-509, task-510, task-511, task-512, task-513, task-514, task-530, task-531, task-536, task-537, task-538, task-539, task-540

### Git Workflow Automation (task-505-535)
**Status**: To Do, complex automation
**Recommendation**: Worktree automation, container orchestration, GPG signing for agents - may be over-engineered

Related tasks to potentially archive:
- task-505, task-506, task-515, task-516, task-517, task-518, task-519, task-520, task-521, task-522, task-523, task-524, task-525, task-526, task-527, task-528, task-529, task-532, task-533, task-534, task-535

### Role-Based Commands (task-361-367)
**Status**: To Do, partially implemented
**Recommendation**: Role selection during init may be over-complicated. Current command structure works.

Related tasks to potentially archive:
- task-361, task-364, task-367, task-363, task-365

---

## KEEP ACTIVE - High Value Tasks

These should remain in the backlog:

### Core Improvements
| Task | Title | Priority |
|------|-------|----------|
| **task-310** | Fix upgrade-tools: Reports success but doesn't upgrade | HIGH - user-facing bug |
| **task-310.01** | Fix version detection after upgrade install | HIGH |
| **task-432** | Enforce DCO sign-off in all automated commits | HIGH - compliance |
| **task-543** | Integrate rigor rules into /flow:implement | HIGH - already started |
| **task-544** | Integrate rigor rules into /flow:validate | HIGH |
| **task-545** | Integrate rigor rules into /flow:specify | HIGH |
| **task-572** | Test Workflow Execution E2E | HIGH - in progress |

### Documentation
| Task | Title | Priority |
|------|-------|----------|
| **task-087** | Production Case Studies Documentation | MEDIUM |
| **task-134** | Integrate diagrams and documentation | MEDIUM |
| **task-284** | Create comprehensive documentation for archive-tasks.sh | MEDIUM |
| **task-438** | Documentation: GitHub Setup Features User Guide | MEDIUM |

### Testing
| Task | Title | Priority |
|------|-------|----------|
| **task-293** | LLM Customization Accuracy Tests | HIGH |
| **task-294** | Constitution Enforcement Integration Tests | HIGH |

### Init/Setup Improvements
| Task | Title | Priority |
|------|-------|----------|
| **task-466** | Fix constitution placeholder in memory/constitution.md | HIGH |
| **task-471** | Add CLAUDE.md scaffolding to flowspec init | MEDIUM |
| **task-472** | Improve template placeholder handling | MEDIUM |
| **task-478** | Add .mcp.json template | MEDIUM |
| **task-479** | Add CI check for template-deployment parity | MEDIUM |

---

## NEEDS REVIEW - Unclear Status

| Task | Title | Question |
|------|-------|----------|
| **task-079** | Stack Selection During Init | Is this still wanted? |
| **task-084** | Spec Quality Metrics Command | Still relevant? |
| **task-168** | Add macOS CI Matrix Testing | Worth doing? |
| **task-171** | Research library documentation MCP replacement | Context7 is now used - done? |
| **task-196** | Experiment with Output Styles | Still wanted? |
| **task-197** | Create Custom Statusline | Still wanted? |
| **task-283** | Create post-workflow-archive.sh hook | Still needed? |
| **task-285** | Add optional CI check for stale Done tasks | Archive workflow exists - needed? |
| **task-429** | Create flowspec CLI ASCII logo | Nice to have? |
| **task-430** | Create flowspec-cli to replace specify init | Was this done? CLI is flowspec now |
| **task-435** | Add flowspec remove command | Still wanted? |
| **task-436** | Move underscore partial commands | Underscore commands exist - done differently? |
| **task-444** | Validate CI/CD Pipeline Post-Bookworm Migration | Was this validated? |
| **task-445** | Post-Migration Monitoring and Documentation | Done? |

---

## Quick Actions

### Mark Done & Archive (13 tasks)
```bash
for task in task-488 task-489 task-490 task-491 task-492 task-494 task-495 task-496 task-499 task-500 task-501 task-541 task-542; do
  backlog task edit "$task" -s Done 2>/dev/null
  backlog task archive "$task" 2>/dev/null
  echo "Done & archived: $task"
done
```

### Archive Obsolete (8 tasks)
```bash
for task in task-467 task-309 task-336 task-204.03 task-226 task-195 task-081 task-136; do
  backlog task archive "$task" 2>/dev/null
  echo "Archived: $task"
done
```

### Archive Task Memory Subtasks (if abandoning feature)
```bash
for task in task-382 task-383 task-387 task-388 task-389 task-390 task-391 task-392 task-393 task-394 task-395 task-397 task-398 task-399 task-402; do
  backlog task archive "$task" 2>/dev/null
done
```

### Archive Event System Tasks (if deprioritizing)
```bash
for task in task-485 task-486 task-487 task-504 task-507 task-508 task-509 task-510 task-511 task-512 task-513 task-514 task-530 task-531 task-536 task-537 task-538 task-539 task-540; do
  backlog task archive "$task" 2>/dev/null
done
```

### Archive Git Workflow Tasks (if deprioritizing)
```bash
for task in task-505 task-506 task-515 task-516 task-517 task-518 task-519 task-520 task-521 task-522 task-523 task-524 task-525 task-526 task-527 task-528 task-529 task-532 task-533 task-534 task-535; do
  backlog task archive "$task" 2>/dev/null
done
```
