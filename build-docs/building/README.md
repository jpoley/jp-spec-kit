# Building Directory (DEPRECATED)

This directory has been flattened into `build-docs/` root level.

## Migration Map

The contents were moved as follows:

| Original Location | New Location |
|-------------------|--------------|
| `building/assess/` | `build-docs/assess/` |
| `building/audit/` | `build-docs/audit/` |
| `building/case-studies/` | `build-docs/case-studies/` |
| `building/design/` | `build-docs/design/` |
| `building/evaluations/` | `build-docs/evaluations/` |
| `building/qa/` | `build-docs/qa/` |
| `building/research/` | `build-docs/research/` |
| `building/upstream-contributions/` | `build-docs/upstream-contributions/` |
| `MARKETPLACE.md` | `prd/MARKETPLACE.md` |
| `backlog-*.md` | `platform/` |
| `claude-review.md` | `evaluations/` |
| `copilot-next.md` | `prd/` |
| `decision-tracker.md` | `adr/` |
| `dev-setup-recovery-plan.md` | `runbooks/` |
| `fix-dogfood.md` | `runbooks/` |
| `flowspec-*-spec.md` | `specs/` |
| `flowspec-workflow-reference.md` | `reference/` |
| `git-workflow-objectives.md` | `prd/` |
| `implementation-summary-*.md` | `reports/` |
| `prd-*.md` | `prd/` |

## Rationale

Per `doc-rules.md`, everything in `build-docs/` is for builders, so the nested `building/` directory was redundant. Flattening provides a cleaner structure.
