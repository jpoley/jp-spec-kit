# CLAUDE.md Update - Meta-Workflows Section

**Action Required**: Add this section to CLAUDE.md after the "## Slash Commands" heading.

```markdown
## Slash Commands

### Meta-Workflows (Simplified - Recommended)

**New in v0.3.x**: Meta-workflows consolidate multiple phases into single commands.

```bash
# 3 Commands for Complete Workflow
/flow:meta-research    # Plan It   (assess + specify + research + plan)
/flow:meta-build       # Create It (implement + validate)
/flow:meta-run         # Deploy It (operate)
```

**Benefits**:
- ✅ **Simplicity**: 3 commands vs. 8 for common path (62.5% reduction)
- ✅ **Quality Gates**: Automatic enforcement (coverage, security, AC)
- ✅ **Atomic**: Build ensures implementation + validation together
- ✅ **Flexible**: Granular commands still available for advanced use

**Quick Reference**: See `docs/reference/meta-workflow-quick-reference.md`
**Migration Guide**: See `docs/guides/meta-workflow-migration.md`

### Granular Workflow Commands (Advanced)

**Power users can still use all 8 granular commands for fine-grained control:**

```bash
# 8 Granular Commands (all still available)
/flow:assess    # Evaluate SDD workflow suitability
/flow:specify   # Create/update feature specs
/flow:research  # Research and validation
/flow:plan      # Execute planning workflow
/flow:implement # Implementation with code review
/flow:validate  # QA, security, docs validation
/flow:operate   # SRE operations (CI/CD, K8s)
```
```

---

## Integration Instructions

1. Open `CLAUDE.md`
2. Find the `## Slash Commands` section (around line 27)
3. Replace the existing workflow commands section with the content above
4. Save the file

This update:
- Highlights meta-workflows as the recommended approach
- Maintains documentation for all granular commands
- Provides clear links to additional resources
- Shows the value proposition (62.5% reduction in commands)
