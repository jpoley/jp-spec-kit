# When to Use Spec-Light Mode

## Overview

Spec-Light Mode is a streamlined SDD workflow for medium-complexity features that reduces documentation overhead and total workflow time by ~60%, while maintaining constitutional compliance and quality gates.

## When to Use Light Mode

Use `flowspec init --light` when:

| Criteria | Light Mode | Full Mode |
|----------|------------|-----------|
| Feature complexity | Medium (4-6/10) | High (7+/10) |
| Estimated dev time | 1-3 days | 4+ days |
| Team size | 1-2 developers | 3+ developers |
| External dependencies | Few/none | Multiple |
| API surface | Internal/simple | Public/complex |

## What's Different

### Skipped in Light Mode
- `/flow:research` phase
- `/flow:analyze` phase
- Detailed data models
- API contracts
- Quickstart documentation

### Still Required
- Constitutional compliance
- Test-first development
- Code review
- PR workflow
- Security considerations

## Files Created

### Light Mode
```
docs/
├── spec-light.md       # Combined user stories + AC
├── plan-light.md       # High-level approach
└── tasks.md           # Standard task list
```

### Full Mode
```
docs/
├── prd/
│   ├── spec.md         # Detailed specification
│   └── research.md     # Market/technical research
├── adr/
│   └── ADR-xxx.md      # Architecture decisions
├── platform/
│   └── data-model.md   # Detailed data models
└── tasks.md
```

## Usage

```bash
# Initialize with light mode
flowspec init my-feature --light

# Check if project is light mode
ls .flowspec-light-mode

# The marker file indicates light mode is active
```

## Upgrading from Light to Full Mode

If a feature becomes more complex than expected:

1. Delete `.flowspec-light-mode` marker
2. Run `/flow:specify` to create full spec
3. Run `/flow:research` if needed
4. Run `/flow:plan` for detailed planning

## Downgrading from Full Mode to Light Mode

Downgrading from full mode to light mode is **not supported**. Once you have upgraded to full mode and generated the additional documentation and files, reverting to light mode is not recommended, as it may result in loss of important information and constitutional compliance. If you need a simpler workflow, start a new feature using light mode.

## Time Savings

| Phase | Full Mode | Light Mode | Savings |
|-------|-----------|------------|---------|
| Specify | 30 min | 15 min | 50% |
| Research | 45 min | Skipped | 100% |
| Plan | 30 min | 15 min | 50% |
| Implement | Same | Same | 0% |
| Validate | 30 min | 20 min | 33% |
| **Total** | **135 min** | **50 min** | **~60%** |

## Best Practices

1. **Start with assessment**: Run `/flow:assess` first to confirm light mode is appropriate
2. **Don't force it**: If complexity grows, upgrade to full mode
3. **Document out-of-scope**: Be explicit about what's not included
4. **Maintain quality**: Light mode ≠ lower quality, just less documentation

## Constitution Compliance

Light mode still enforces:
- No direct commits to main
- Test-first development
- Security review for sensitive code
- PR-based workflow
- DCO sign-off
