# Malformed Task Test Fixtures

This directory contains examples of malformed task files that break Backlog.md parsing.

**DO NOT copy these files to `backlog/tasks/`** - they will break the task list!

## Purpose

These fixtures are used for:
1. Testing the task validator (`src/utils/task-validator.ts`)
2. Documenting known failure patterns
3. Regression testing to ensure the validator catches these issues

## Files

| File | Problem |
|------|---------|
| `task-011 - [P] Add data visualization.md` | `[P]` in filename and YAML title breaks parsing |

## Adding New Fixtures

When you encounter a new malformed task pattern that breaks Backlog.md:

1. Move the offending file here (away from `backlog/tasks/`)
2. Add a comment in the file explaining the problem
3. Update this README
4. Add a test case in the validator tests

## Related

- `docs/how-to-fix-malformed-tasks.md` - Diagnosis and fix guide
- `src/utils/task-validator.ts` - TypeScript validator
