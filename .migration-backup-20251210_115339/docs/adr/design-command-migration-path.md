# Design: Command Migration Path

**Status**: Proposed
**Date**: 2025-12-09
**Author**: Enterprise Software Architect
**Related Tasks**: task-359
**Dependencies**: [ADR: Role-Based Command Namespaces](./ADR-role-based-command-namespaces.md)

---

## Executive Summary

This document outlines the migration strategy for transitioning from flat command namespaces (`/jpspec:*`, `/speckit:*`) to role-based hierarchical namespaces (`/pm:*`, `/dev:*`, `/sec:*`, `/qa:*`, `/ops:*`) over a **12-month deprecation period**.

### Goals

1. **Zero Downtime**: Old commands continue to work during entire transition
2. **Clear Communication**: Users understand what's changing and why
3. **Gradual Adoption**: Teams can migrate at their own pace
4. **Minimal Disruption**: Existing workflows, scripts, and documentation remain functional
5. **Complete Migration**: By Month 12, all users have migrated to new commands

---

## Backwards Compatibility Strategy

### Approach: Alias-Based Transition

Old commands become **aliases** that redirect to new commands with deprecation warnings.

**Example**:
```bash
User types: /jpspec:assess feature-x

System executes: /pm:assess feature-x

System displays warning:
⚠️  /jpspec:assess is deprecated and will be removed in 8 months.
Please use /pm:assess instead.
Migration guide: https://jpspec.dev/docs/migration
```

### Implementation: Command Forwarding

#### Option 1: Symbolic Links (File System)

Create symlinks from old locations to new:

```bash
# Old command redirects to new
.claude/commands/jpspec/assess.md → .claude/commands/pm/assess.md
```

**Pros**: Simple, filesystem-native
**Cons**: Platform-dependent (Windows requires special handling)

**Verdict**: ❌ Too platform-specific

---

#### Option 2: Include-Based Forwarding (Chosen)

Old command files include new command with deprecation metadata:

```markdown
# .claude/commands/jpspec/assess.md (OLD LOCATION)
---
description: "[DEPRECATED] Use /pm:assess - Assess SDD workflow suitability"
deprecated: true
deprecation_date: "2025-12-09"
removal_date: "2026-12-09"
replacement: "/pm:assess"
replacement_path: ".claude/commands/pm/assess.md"
---

⚠️ **DEPRECATED COMMAND**

This command is deprecated and will be removed on **2026-12-09**.

Please use **`/pm:assess`** instead.

Migration guide: https://jpspec.dev/docs/migration

---

{{INCLUDE:.claude/commands/pm/assess.md}}
```

**Pros**:
- Platform-independent
- Allows deprecation warnings in command definition
- Works with include resolution in both Claude Code and Copilot

**Cons**:
- Duplicate file management during transition

**Verdict**: ✅ **SELECTED**

---

## Deprecation Timeline (12 Months)

### Phase 1: Soft Deprecation (Months 0-6)

**Goal**: Awareness and education

**Actions**:
1. ✅ Release new role-based namespaces alongside old commands
2. ✅ Old commands work perfectly with deprecation notice
3. ✅ All documentation updated to show new commands first
4. ✅ Migration guide published with examples
5. ✅ Announcement blog post and changelog entry

**User Experience**:
```bash
$ /jpspec:assess user-auth

⚠️  Deprecation Warning

Command: /jpspec:assess
Status: DEPRECATED (soft)
Replacement: /pm:assess
Removal Date: 2026-12-09 (8 months)

This command still works but will be removed.
Update your workflows: https://jpspec.dev/docs/migration

───────────────────────────────────────────────────────────

[Command executes normally]
```

**Metrics to Track**:
- New command adoption rate (target: 40% by Month 6)
- Migration guide page views
- User feedback on clarity of warnings

---

### Phase 2: Hard Deprecation (Months 6-9)

**Goal**: Urgency and migration

**Actions**:
1. ✅ Warnings become more prominent (colored, bold)
2. ✅ Countdown timer added ("3 months until removal")
3. ✅ Auto-migration script released (`specify migrate-commands`)
4. ✅ Email to active users with migration checklist
5. ✅ In-tool migration prompt on first use after Month 6

**User Experience**:
```bash
$ /jpspec:assess user-auth

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  DEPRECATION WARNING (3 MONTHS UNTIL REMOVAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command: /jpspec:assess
Status: DEPRECATED (hard)
Replacement: /pm:assess
Removal Date: 2026-09-09 (3 months)

ACTION REQUIRED:
Run: specify migrate-commands --dry-run
to update all your workflows automatically.

Migration guide: https://jpspec.dev/docs/migration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Command executes normally]
```

**Auto-Migration Tool**:
```bash
# Scan for deprecated command usage
specify migrate-commands --dry-run

# Output:
Found 12 deprecated commands in your project:

File: .github/workflows/ci.yml
  Line 45: /jpspec:assess → /pm:assess
  Line 67: /jpspec:specify → /pm:specify

File: docs/guides/quickstart.md
  Line 23: /jpspec:implement → /dev:implement

Run without --dry-run to apply changes automatically.
```

**Metrics to Track**:
- New command adoption rate (target: 80% by Month 9)
- Auto-migration tool usage
- Support ticket volume

---

### Phase 3: Final Warning (Months 9-12)

**Goal**: Final push for stragglers

**Actions**:
1. ✅ Critical warnings with countdown
2. ✅ Commands still work but highly discouraged
3. ✅ Telemetry identifies users still on old commands
4. ✅ Personal outreach to heavy users
5. ✅ "Last chance" blog post and email

**User Experience**:
```bash
$ /jpspec:assess user-auth

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 CRITICAL: COMMAND REMOVAL IN 30 DAYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command: /jpspec:assess
Status: WILL BE REMOVED IN 30 DAYS
Replacement: /pm:assess
Removal Date: 2026-12-09

URGENT ACTION REQUIRED:
This command will STOP WORKING in 30 days.

Auto-migrate now:
  specify migrate-commands

Need help? Contact support: support@jpspec.dev

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Command executes normally but logs usage for outreach]
```

**Metrics to Track**:
- New command adoption rate (target: 95% by Month 12)
- Remaining users identified for outreach

---

### Phase 4: Removal (Month 12+)

**Goal**: Clean removal with helpful error

**Actions**:
1. ✅ Old command files deleted
2. ✅ Helpful error message with migration path
3. ✅ Release notes clearly document breaking change
4. ✅ Support team briefed on migration issues

**User Experience**:
```bash
$ /jpspec:assess user-auth

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ COMMAND NOT FOUND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Command: /jpspec:assess
Status: REMOVED (as of 2026-12-09)

This command has been replaced by /pm:assess

Update your command:
  OLD: /jpspec:assess user-auth
  NEW: /pm:assess user-auth

Migration guide: https://jpspec.dev/docs/migration
Auto-migrate: specify migrate-commands

Need help? support@jpspec.dev

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Complete Command Mapping

### Product Manager Commands
| Old Command | New Command | Deprecation Phase |
|-------------|-------------|-------------------|
| `/jpspec:assess` | `/pm:assess` | Month 0 |
| `/jpspec:specify` | `/pm:specify` | Month 0 |
| `/jpspec:research` | `/pm:research` | Month 0 |

### Developer Commands
| Old Command | New Command | Deprecation Phase |
|-------------|-------------|-------------------|
| `/jpspec:plan` | `/dev:plan` | Month 0 |
| `/jpspec:implement` | `/dev:implement` | Month 0 |
| `/jpspec:operate` | `/dev:operate` | Month 0 |
| `/jpspec:init` | `/dev:init` | Month 0 |
| `/jpspec:reset` | `/dev:reset` | Month 0 |
| `/jpspec:prune-branch` | `/dev:prune-branch` | Month 0 |
| `/speckit:implement` | `/dev:implement-light` | Month 3 |
| `/speckit:plan` | `/dev:plan-light` | Month 3 |

### Security Commands
| Old Command | New Command | Deprecation Phase |
|-------------|-------------|-------------------|
| `/jpspec:security_fix` | `/sec:fix` | Month 0 |
| `/jpspec:security_report` | `/sec:report` | Month 0 |
| `/jpspec:security_triage` | `/sec:triage` | Month 0 |
| `/jpspec:security_web` | `/sec:scan-web` | Month 0 |
| `/jpspec:security_workflow` | `/sec:workflow` | Month 0 |

### QA Commands
| Old Command | New Command | Deprecation Phase |
|-------------|-------------|-------------------|
| `/jpspec:validate` | `/qa:validate` | Month 0 |
| `/speckit:checklist` | `/qa:checklist` | Month 3 |
| `/speckit:analyze` | `/qa:analyze` | Month 3 |

### Utility Commands (No Change)
| Command | Status | Notes |
|---------|--------|-------|
| `/speckit:constitution` | Unchanged | Used by all roles |
| `/speckit:tasks` | Unchanged | Backlog management |
| `/speckit:clarify` | Unchanged | Requirements clarification |
| `/speckit:specify` | Unchanged | Lightweight specification |

---

## User Migration Guide

### Quick Migration (< 5 minutes)

**For users who trust automation**:

```bash
# 1. Scan your project for deprecated commands
specify migrate-commands --dry-run

# 2. Review suggested changes

# 3. Apply changes automatically
specify migrate-commands

# 4. Verify changes
git diff

# 5. Commit
git add .
git commit -m "chore: migrate to role-based command namespaces"
```

### Manual Migration

**For users who prefer control**:

1. **Find deprecated commands**:
```bash
grep -r "/jpspec:" .github/ docs/ scripts/
```

2. **Replace using mapping table** (see above)

3. **Update documentation**:
   - README.md
   - Quickstart guides
   - CI/CD workflows (.github/workflows/)
   - Scripts (scripts/*)

4. **Test workflows**:
```bash
# Test that new commands work
/pm:assess test-feature
/dev:plan test-feature
/qa:validate
```

---

## Auto-Migration Tool (`specify migrate-commands`)

### Features

1. **Dry-run mode**: Preview changes without applying
2. **File type detection**: Handles .md, .yml, .yaml, .sh, .py
3. **Context-aware replacement**: Only replaces in command contexts
4. **Git integration**: Creates commit with detailed message
5. **Rollback support**: Can revert if issues found

### Usage

```bash
# Basic usage
specify migrate-commands

# Preview changes
specify migrate-commands --dry-run

# Migrate specific files
specify migrate-commands --files ".github/workflows/*"

# Exclude certain files
specify migrate-commands --exclude "vendor/*"

# Auto-commit changes
specify migrate-commands --commit
```

### Implementation Sketch

```python
def migrate_commands(
    dry_run: bool = False,
    files: Optional[str] = None,
    exclude: Optional[str] = None,
    commit: bool = False
) -> MigrationResult:
    """
    Migrate deprecated commands to role-based namespaces.

    Algorithm:
    1. Discover all files matching pattern (default: **/*.{md,yml,yaml,sh,py})
    2. Exclude vendor, node_modules, .git
    3. For each file:
       a. Load content
       b. Search for deprecated command patterns
       c. Replace with new commands (context-aware)
       d. Track changes
    4. Display summary
    5. If --commit, create git commit
    """

    # Command mapping
    MIGRATIONS = {
        r'/jpspec:assess\b': '/pm:assess',
        r'/jpspec:specify\b': '/pm:specify',
        r'/jpspec:research\b': '/pm:research',
        r'/jpspec:plan\b': '/dev:plan',
        r'/jpspec:implement\b': '/dev:implement',
        r'/jpspec:operate\b': '/dev:operate',
        r'/jpspec:validate\b': '/qa:validate',
        r'/jpspec:security_fix\b': '/sec:fix',
        r'/jpspec:security_report\b': '/sec:report',
        r'/jpspec:security_triage\b': '/sec:triage',
        r'/jpspec:security_web\b': '/sec:scan-web',
        r'/jpspec:security_workflow\b': '/sec:workflow',
        r'/speckit:checklist\b': '/qa:checklist',
        r'/speckit:analyze\b': '/qa:analyze',
        r'/speckit:implement\b': '/dev:implement-light',
        r'/speckit:plan\b': '/dev:plan-light',
    }

    # Context patterns (only replace within these contexts)
    CONTEXTS = [
        r'```bash\n(.*?)\n```',          # Code blocks
        r'`([^`]+)`',                     # Inline code
        r'^\s*(\S+)',                     # Command at line start
    ]

    result = MigrationResult()

    for file_path in discover_files(files, exclude):
        changes = apply_migrations(file_path, MIGRATIONS, CONTEXTS, dry_run)
        result.add_file(file_path, changes)

    if not dry_run and commit:
        create_migration_commit(result)

    return result
```

---

## Breaking Change Communication Plan

### Announcement Channels

1. **GitHub Release Notes**: Highlight deprecation in release
2. **Documentation Banner**: Prominent banner on docs site
3. **CLI Startup Message**: One-time message on first use after deprecation
4. **Email Campaign**: Monthly updates during deprecation period
5. **Discord/Slack**: Pin announcement in community channels
6. **Blog Post**: Detailed migration guide and rationale

### Announcement Template

**Subject**: JP Spec Kit v2.0 - Role-Based Command Namespaces (Action Required)

**Body**:
```
Hi JP Spec Kit users,

We're excited to announce JP Spec Kit v2.0 with role-based command
namespaces for improved discoverability and developer experience.

What's Changing:
• Commands are now organized by role: /pm, /dev, /sec, /qa, /ops
• Old commands (/jpspec:*, /speckit:*) are deprecated
• 12-month transition period with full backwards compatibility

Action Required:
1. Run: specify migrate-commands --dry-run
2. Review changes
3. Run: specify migrate-commands
4. Update your workflows

Timeline:
• Now - Month 6: Soft deprecation (warnings only)
• Month 6-9: Hard deprecation (urgent warnings)
• Month 9-12: Final warning period
• Month 12+: Old commands removed

Migration Guide: https://jpspec.dev/docs/migration
Questions? support@jpspec.dev

Thanks for using JP Spec Kit!
The JP Spec Team
```

---

## Support and Troubleshooting

### Common Migration Issues

#### Issue 1: Command Not Found After Migration

**Symptom**: `/pm:assess` not recognized

**Solution**:
```bash
# Ensure you're on latest version
specify --version

# Should be v2.0.0 or later
# If not, upgrade:
pip install --upgrade specify-cli
```

---

#### Issue 2: Scripts Break After Migration

**Symptom**: CI/CD workflows fail with "command not found"

**Solution**:
```bash
# 1. Check script for old commands
grep -r "/jpspec:" .github/

# 2. Run migration tool on specific files
specify migrate-commands --files ".github/workflows/*"

# 3. Test locally before pushing
bash .github/workflows/ci.yml
```

---

#### Issue 3: Documentation Out of Sync

**Symptom**: README shows old commands

**Solution**:
```bash
# Migrate all markdown files
specify migrate-commands --files "**/*.md"

# Review changes
git diff

# Commit if looks good
git commit -am "docs: migrate to role-based commands"
```

---

## Rollback Plan

If critical issues arise during migration:

### Emergency Rollback (Month 0-11)

1. **Revert version**: `pip install specify-cli==1.x.x`
2. **Old commands still work**: Aliases remain functional
3. **No data loss**: Migration only affects command names

### Post-Removal Rollback (Month 12+)

1. **No rollback available**: Old commands permanently removed
2. **Support available**: Contact support@jpspec.dev
3. **Migration tool**: Can regenerate old-style commands if needed

---

## Success Criteria

| Milestone | Target Date | Success Metric |
|-----------|-------------|----------------|
| Initial release | Month 0 | New commands available |
| 40% adoption | Month 6 | 40% of users using new commands |
| 80% adoption | Month 9 | 80% of users migrated |
| 95% adoption | Month 11 | Only 5% on old commands |
| Full migration | Month 12 | Old commands removed |

### Measurement

- **Telemetry**: Track command usage (old vs new)
- **Migration tool usage**: How many ran `specify migrate-commands`
- **Support tickets**: Volume and type of migration issues
- **User feedback**: Survey satisfaction with migration process

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Users miss deprecation warnings | Medium | High | Multiple communication channels, prominent warnings |
| Scripts break after removal | High | High | 12-month period, auto-migration tool, clear docs |
| Confusion during transition | Medium | Medium | Clear mapping table, examples, support |
| Legacy documentation persists | High | Low | Auto-migration tool, search/replace in docs |
| Enterprise users slow to migrate | Medium | High | Personal outreach, extended support period |

---

## Related Documents

- [ADR: Role-Based Command Namespaces](./ADR-role-based-command-namespaces.md)
- [ADR: Role Selection During Initialization](./ADR-role-selection-during-initialization.md)
- [Command Mapping Matrix](./ADR-role-based-command-namespaces.md#command-mapping-matrix)

---

**Status**: Awaiting approval
**Reviewers**: @product-requirements-manager, @software-architect
**Next Review Date**: 2025-12-16
