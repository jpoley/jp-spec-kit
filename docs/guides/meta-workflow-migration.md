# Meta-Workflow Migration Guide

**Version**: 1.0.0
**Date**: 2025-12-26

## Overview

Flowspec now supports **meta-workflows** - simplified commands that consolidate multiple workflow phases into high-level operations. This guide helps you migrate from granular workflows to meta-workflows.

## What Changed?

### Before: 8 Granular Commands

```bash
# Old workflow - 8 separate commands
/flow:assess
/flow:specify
/flow:research      # Optional
/flow:plan
/flow:implement
/flow:validate
/flow:operate
/flow:submit-n-watch-pr  # Optional
```

### After: 3 Meta-Workflows + 8 Granular Commands

```bash
# New meta-workflows (recommended for most users)
/flow:meta-research    # assess + specify + research + plan
/flow:meta-build       # implement + validate
/flow:meta-run         # operate

# Granular commands still available (for power users)
/flow:assess           # Still works!
/flow:specify          # Still works!
# ... all 8 commands still work
```

## Key Benefits

✅ **Simplicity**: 3 commands instead of 8 for common path
✅ **Backward Compatible**: All existing commands still work
✅ **Flexible**: Choose meta or granular based on your needs
✅ **Atomic**: Build ensures implementation + validation together
✅ **Quality Gates**: Automatic enforcement of coverage/security/AC thresholds

## Migration Scenarios

### Scenario 1: New Feature Development

**Before**:
```bash
git checkout -b feature/user-authentication
/flow:assess
/flow:specify
/flow:research  # If complex
/flow:plan
/flow:implement
/flow:validate
/flow:operate
```

**After**:
```bash
git checkout -b feature/user-authentication
/flow:meta-research     # Replaces assess+specify+research+plan
/flow:meta-build        # Replaces implement+validate
/flow:meta-run          # Replaces operate
```

**Time Saved**: ~50% fewer commands, automatic orchestration

### Scenario 2: Iterative Development

**Before**:
```bash
# Make code changes
/flow:implement
# Fix tests
/flow:implement
# Fix security issues
/flow:validate
```

**After - Option A (Meta-workflow)**:
```bash
# Make code changes
/flow:meta-build   # Re-runs implement + validate
```

**After - Option B (Granular - More Control)**:
```bash
# Make code changes
/flow:implement    # Just re-implement
# Fix security issues
/flow:validate     # Just re-validate
```

**Best Practice**: Use granular commands for iteration, meta-workflows for full runs

### Scenario 3: Debugging Workflow Phases

**Before**:
```bash
# Specify failed, need to fix PRD
/flow:specify

# Plan failed, need to update ADRs
/flow:plan
```

**After (Same)**:
```bash
# Still use granular commands for debugging
/flow:specify
/flow:plan
```

**Best Practice**: Granular commands are still best for debugging specific phases

## Decision Matrix

### When to Use Meta-Workflows

✅ **Use `/flow:meta-research`** when:
- Starting a new feature from "To Do" state
- Want complete planning in one command
- Don't need to review intermediate artifacts
- Prefer simplicity over control

✅ **Use `/flow:meta-build`** when:
- Starting implementation from "Planned" state
- Want atomic implementation + validation
- Want automatic quality gate enforcement
- Confident in your code (minimal iteration expected)

✅ **Use `/flow:meta-run`** when:
- Deploying a validated feature
- Want operational artifacts generated automatically
- Following full SDD workflow

### When to Use Granular Commands

🔧 **Use granular commands** when:
- Re-running a single phase after fixes
- Debugging specific workflow issues
- Reviewing artifacts between phases
- Need fine-grained control
- Custom orchestration requirements
- Learning flowspec (easier to understand each step)

## Configuration Customization

You can customize meta-workflows in `flowspec_workflow.yml`:

### Example: Skip Research by Default

```yaml
meta_workflows:
  research:
    sub_workflows:
      - workflow: "research"
        required: false
        condition: "complexity_score >= 9"  # Changed from 7
```

### Example: Lower Test Coverage Threshold

```yaml
meta_workflows:
  build:
    quality_gates:
      - type: "test_coverage"
        threshold: 70  # Changed from 80
```

### Example: Add Custom Sub-Workflow

```yaml
meta_workflows:
  research:
    sub_workflows:
      - workflow: "assess"
        required: true
      - workflow: "specify"
        required: true
      - workflow: "custom-phase"  # Your custom workflow
        required: false
      - workflow: "plan"
        required: true
```

## Cross-Tool Migration

### GitHub Copilot

**Before**:
```
@flowspec /flow:assess for user auth feature
@flowspec /flow:specify
@flowspec /flow:plan
```

**After**:
```
@flowspec /flow:meta-research for user auth feature
```

### Cursor

**Before**:
```
@flowspec /flow:implement the user auth feature
@flowspec /flow:validate
```

**After**:
```
@flowspec /flow:meta-build
```

### Gemini Code

**Before**:
```
flowspec assess
flowspec specify
flowspec plan
```

**After**:
```
flowspec meta-research
```

## Common Pitfalls

### ❌ Pitfall 1: Mixing Meta and Granular in Sequence

**Wrong**:
```bash
/flow:meta-research
/flow:implement      # Don't mix!
/flow:validate
```

**Right - Option A**:
```bash
/flow:meta-research
/flow:meta-build     # Use meta-build instead
```

**Right - Option B**:
```bash
/flow:assess
/flow:specify
/flow:plan
/flow:implement
/flow:validate
```

### ❌ Pitfall 2: Expecting Intermediate States with Meta-Workflows

Meta-workflows skip intermediate states:

**Wrong Expectation**:
```bash
/flow:meta-research
# Task state is now... "Specified"? No, it's "Planned"
```

**Right Understanding**:
```bash
/flow:meta-research
# Task state jumps directly from "To Do" → "Planned"
# (Skips "Assessed", "Specified", "Researched")
```

### ❌ Pitfall 3: Using Meta-Workflows for Partial Re-runs

**Wrong**:
```bash
# Only need to fix tests
/flow:meta-build     # This re-runs BOTH implement and validate
```

**Right**:
```bash
# Only need to fix tests
/flow:implement      # Just re-run implementation
```

## FAQ

### Q: Do I have to use meta-workflows?

**A**: No! Meta-workflows are optional. All 8 granular commands still work. Use what fits your workflow.

### Q: Can I customize meta-workflows?

**A**: Yes! Edit `flowspec_workflow.yml` to change sub-workflows, conditions, quality gates, etc.

### Q: What if a meta-workflow fails halfway through?

**A**: Execution stops, but artifacts created before failure are preserved. Fix the issue and re-run the meta-workflow - it will resume from the beginning but use existing artifacts where possible.

### Q: Can I create my own meta-workflows?

**A**: Yes! Add a new entry to `meta_workflows` in `flowspec_workflow.yml` and create a corresponding command template.

### Q: Do meta-workflows emit events?

**A**: Yes! They emit events for each sub-workflow plus overall meta-workflow events. See `.logs/events/` for details.

### Q: Will this break my existing workflows?

**A**: No! This is a purely additive change. All existing commands work exactly as before.

## Next Steps

1. **Try a meta-workflow**: Start a new feature and use `/flow:meta-research`
2. **Compare**: Note the reduction in commands vs. granular workflow
3. **Customize**: Edit `flowspec_workflow.yml` to fit your preferences
4. **Decide**: Choose your preferred workflow style (meta vs. granular)
5. **Share**: Update team documentation with your recommended approach

## Resources

- [Meta-Workflow Command Reference](../reference/meta-workflow-commands.md)
- [ADR-003: Meta-Workflow Simplification](../adr/003-meta-workflow-simplification.md)
- [Workflow Configuration Guide](./workflow-customization.md)
- [flowspec_workflow.yml](../../flowspec_workflow.yml)

## Support

Questions? Issues? Feedback?
- GitHub Issues: https://github.com/jpoley/flowspec/issues
- Documentation: `docs/guides/`
- Community: Ask in discussions

---

**Remember**: Meta-workflows are designed to make flowspec **more usable, less complicated, and more flexible** while preserving all existing functionality. You choose your own adventure! 🚀
