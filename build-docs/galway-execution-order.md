# @galway Execution Order

Generated: 2025-12-14 21:08

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 24 |
| Already Done | 6 |
| To Do | 18 |
| Execution Levels | 2 |

## Focus Areas

- **ci**: 10 tasks
- **github-actions**: 8 tasks
- **documentation**: 6 tasks
- **bug**: 4 tasks
- **testing**: 4 tasks

## Execution Order

Tasks are grouped by execution level. Tasks within the same level have no dependencies on each other and **CAN be executed in parallel**.


### Level 1 (PARALLEL OK)

- **task-087**: Production Case Studies Documentation
  - Labels: `documentation, validation, marketing`
- **task-134**: Integrate diagrams and documentation into project  (deps: task-133)
  - Labels: `documentation, integration`
- **task-278**: Add CI validation for command structure
  - Labels: `ci, validation`
- **task-279**: Update documentation for new architecture
  - Labels: `bug, documentation, branding`
- **task-282**: >- (deps: task-281)
  - Labels: `infrastructure, ci-cd, github-actions`
- **task-284**: Create comprehensive documentation for archive-tas (deps: task-281)
  - Labels: `documentation`
- **task-295**: Validate Fix Generator Quality (>75% accuracy)
  - Labels: `security, qa, validation`
- **task-309**: Sync .agents/ and .claude/agents/ directories
  - Labels: `technical-debt, agents, testing`
- **task-310.03**: Add unit tests for upgrade-tools scenarios
  - Labels: `test, cli, upgrade-tools`
- **task-311.01**: Fix double-dash in version-bump branch name
  - Labels: `bug, ci, github-actions`
- **task-311.02**: Delete branch after PR creation failure
  - Labels: `bug, ci, github-actions`
- **task-311.03**: Enable auto-delete branch on PR merge in GitHub re
  - Labels: `ci, github-actions, config`
- **task-311.04**: Add scheduled workflow to cleanup stale version-bu
  - Labels: `ci, github-actions, cleanup`
- **task-313**: Fix release workflow: Update version files before  (deps: task-312)
  - Labels: `implement, ci, github-actions`
- **task-333**: Test commands in VS Code and VS Code Insiders
  - Labels: `test, copilot, workflow:Planned`
- **task-335**: Add CI check for agent sync drift
  - Labels: `implement, ci, workflow:Planned`
- **task-441**: Test Bookworm Migration End-to-End
  - Labels: `qa, testing, docker`

### Level 2 (SERIAL)

- **task-311**: Fix orphaned chore/version-bump branches not being (deps: task-313)
  - Labels: `bug, ci, github-actions`

## Already Completed (6 tasks)

- **task-312**: Research: Analyze version management workflow orde
- **task-314**: Sync current pyproject.toml version to match lates
- **task-315**: Add release workflow integration tests
- **task-401**: Task Memory: Architecture Decision Record (ADR)
- **task-409**: Telemetry: Comprehensive test suite and privacy ve
- **task-437.06**: Create governance files (CONTRIBUTING, CODE_OF_CON

## Dependency Map

| Task | Depends On | Blocks |
|------|------------|--------|
| task-087 | - | - |
| task-134 | task-133 | - |
| task-278 | - | - |
| task-279 | - | - |
| task-282 | task-281 | - |
| task-284 | task-281 | - |
| task-295 | - | - |
| task-309 | - | - |
| task-310.03 | - | - |
| task-311 | task-313 | - |
| task-311.01 | - | - |
| task-311.02 | - | - |
| task-311.03 | - | - |
| task-311.04 | - | - |
| task-313 | task-312 | task-311, task-314, task-315 |
| task-333 | - | - |
| task-335 | - | - |
| task-441 | - | - |
