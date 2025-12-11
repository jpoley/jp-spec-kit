# ADR-006: Spec-Light Mode for Medium Features

## Status
Accepted

## Date
2024-06-11

## Author
Jane Doe

## Context
User feedback (Böckeler) noted that full SDD workflow creates "a LOT of markdown files" which can be overwhelming for medium-complexity features. We need a streamlined option that maintains quality while reducing overhead.

## Decision
Implement Spec-Light Mode with:

1. **`--light` flag on `specify init`**: Creates `.flowspec-light-mode` marker file
2. **Simplified templates**: `spec-light.md` (combined stories + AC) and `plan-light.md` (high-level only)
3. **Skipped phases**: Research, analyze, detailed data models, API contracts
4. **Maintained requirements**: Constitutional compliance, test-first, PR workflow

### Complexity Assessment
| Score | Recommendation |
|-------|----------------|
| 1-3 | Skip SDD entirely |
| 4-6 | Use Light Mode |
| 7-10 | Use Full Mode |

## Alternatives Considered

1. **No light mode**: Keep full workflow only
   - Rejected: Overhead discourages SDD adoption

2. **Configuration file**: Per-project settings for complexity
   - Rejected: Too complex, marker file is simpler

3. **Automatic detection**: Infer mode from feature size
   - Rejected: Hard to detect reliably, explicit choice is clearer

## Consequences

### Positive
- ~60% faster workflow for medium features (see [user guide](../guides/when-to-use-light-mode.md) for details)
- Lower barrier to SDD adoption
- Explicit mode choice (marker file)
- Easy upgrade path to full mode

### Negative
- Risk of using light mode for complex features
- Two template sets to maintain
- Users must choose mode upfront

## Implementation
- `src/specify_cli/__init__.py`: Add `--light` flag
- `templates/spec-light-template.md`: Combined spec template
- `templates/plan-light-template.md`: High-level plan template
- `docs/guides/when-to-use-light-mode.md`: User guide
- `.flowspec-light-mode`: Marker file in project root
