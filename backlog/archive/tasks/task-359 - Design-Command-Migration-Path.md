---
id: task-359
title: 'Design: Command Migration Path'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:10'
updated_date: '2025-12-15 02:17'
labels:
  - architecture
  - design
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design migration strategy from flat flowspec/* and speckit/* namespaces to role-based namespaces with clear deprecation timeline and user migration guide
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Backwards compatibility strategy documented (alias approach)
- [x] #2 Deprecation timeline defined with milestones
- [x] #3 User migration guide outlined with examples
- [x] #4 Breaking change communication plan defined
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
# Design: Command Migration Path

## Deliverable
Created comprehensive migration design at: /home/jpoley/ps/flowspec/docs/adr/design-command-migration-path.md

## Key Design Decisions

### 1. Alias-Based Transition Strategy
Chose include-based forwarding over symlinks:
- Platform-independent (works on Windows)
- Allows inline deprecation warnings
- Works with both Claude Code and VS Code Copilot
- Maintains backwards compatibility

### 2. 12-Month Deprecation Timeline
Four-phase approach:
- Phase 1 (Months 0-6): Soft deprecation - awareness
- Phase 2 (Months 6-9): Hard deprecation - urgency
- Phase 3 (Months 9-12): Final warning - last chance
- Phase 4 (Month 12+): Removal - helpful errors

### 3. Auto-Migration Tool
Designed `specify migrate-commands` with features:
- Dry-run mode for preview
- Context-aware replacement (only in code/command contexts)
- Multi-file type support (.md, .yml, .sh, .py)
- Git integration with auto-commit
- Rollback support

### 4. Complete Command Mapping
Documented migration paths for all commands:
- 3 PM commands
- 8 Dev commands
- 5 Security commands
- 3 QA commands
- 4 unchanged utility commands

### 5. Breaking Change Communication Plan
Multi-channel approach:
- GitHub release notes
- CLI startup messages
- Email campaigns
- Documentation banners
- Community channels (Discord/Slack)

### 6. Support and Troubleshooting
Documented common issues:
- Command not found after migration
- Scripts breaking in CI/CD
- Documentation out of sync
- Rollback procedures

## Migration Targets
- Month 6: 40% adoption
- Month 9: 80% adoption
- Month 11: 95% adoption
- Month 12: Full migration

## Next Steps
- Review and approve design
- Implement auto-migration tool
- Create announcement templates
- Build support documentation
<!-- SECTION:NOTES:END -->
