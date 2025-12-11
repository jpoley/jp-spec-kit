# Feature Specification: File-Friendly Timestamp in Specify-Backup Path

**Feature Branch**: `300-backup-timestamp`
**Created**: 2025-12-07
**Status**: Draft
**Backlog Task**: task-300
**Input**: User description: "we need to add a file friendly timestamp in the specify-backup path"

---

## 1. Executive Summary

### Problem Statement (Customer Opportunity Focus)

When users run `specify upgrade-tools`, the backup directory `.specify-backup/` is created without a timestamp. Each subsequent upgrade operation **overwrites** the previous backup, eliminating the user's ability to:

- Roll back to earlier template versions
- Compare changes between upgrade iterations
- Recover from failed upgrades that corrupt the most recent backup

### Proposed Solution (Outcome-Driven)

Add a file-system-safe timestamp to the backup directory name using the format:
```
.specify-backup-YYYYMMDD-HHMMSS/
```

Example: `.specify-backup-20251207-143052/`

### Success Metrics (North Star + Key Outcomes)

| Metric | Target |
|--------|--------|
| **North Star**: Backup preservation rate | 100% of backups preserved across upgrades |
| **User recovery capability** | Users can access any previous backup |
| **Timestamp uniqueness** | No backup name collisions |

### Business Value and Strategic Alignment

- **Reduced support burden**: Users can self-service rollbacks
- **Improved upgrade confidence**: Safe experimentation with upgrades
- **Data safety**: Protection against cascading failures

---

## 2. User Stories and Use Cases

### User Story 1 - Preserve Multiple Backup Versions (Priority: P1)

As a developer using JP Flowspec, I want each upgrade to create a uniquely named backup directory so that I can access previous versions of my templates after multiple upgrades.

**Why this priority**: Core functionality - without this, the entire backup system is unreliable.

**Independent Test**: Run `specify upgrade-tools` twice and verify two separate backup directories exist.

**Acceptance Scenarios**:

1. **Given** a project with existing templates, **When** I run `specify upgrade-tools`, **Then** a backup directory with timestamp is created (e.g., `.specify-backup-20251207-143052/`)
2. **Given** a project with an existing timestamped backup, **When** I run `specify upgrade-tools` again, **Then** a new backup with a different timestamp is created alongside the previous one

---

### User Story 2 - Console Output Shows Timestamped Path (Priority: P1)

As a developer, I want the console output to display the exact timestamped backup path so I know where my backup is stored.

**Why this priority**: Essential UX - users must know backup location.

**Independent Test**: Run upgrade and verify console shows full timestamped path.

**Acceptance Scenarios**:

1. **Given** running `specify upgrade-tools`, **When** backup completes, **Then** console displays `saved to .specify-backup-YYYYMMDD-HHMMSS`
2. **Given** upgrade fails, **When** error is displayed, **Then** console shows exact backup path for recovery

---

### User Story 3 - Rollback from Specific Backup (Priority: P2)

As a developer who needs to rollback, I want to easily identify which backup corresponds to which upgrade attempt by looking at the timestamp in the directory name.

**Why this priority**: Secondary value - relies on P1 features.

**Independent Test**: List backup directories and verify timestamps are human-readable and sortable.

**Acceptance Scenarios**:

1. **Given** multiple backup directories exist, **When** I list the project directory, **Then** backups are sortable chronologically by name
2. **Given** a backup directory name, **When** I parse the timestamp, **Then** it clearly indicates the date and time of the backup

---

### Edge Cases

- **What happens when** two upgrades occur within the same second? → Timestamp includes seconds, collisions extremely unlikely; if collision occurs, append counter.
- **How does system handle** timezone differences? → Use local system time consistently.
- **What happens with** non-ASCII file systems? → Format uses only ASCII characters (digits, hyphens), universally compatible.

---

## 3. DVF+V Risk Assessment

### Value Risk (Desirability)

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Users don't need multiple backups | Low | Existing pattern in git (reflog) proves value |
| Disk space concerns | Medium | Document cleanup guidance for old backups |

**Validation Plan**: User feedback on current overwrite behavior confirms pain point.

### Usability Risk (Experience)

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Timestamp format confusing | Low | Use ISO 8601-inspired format (familiar) |
| Directory clutter | Medium | Consider future --cleanup flag |

**Validation Plan**: Format aligns with common conventions (git stash, backup tools).

### Feasibility Risk (Technical)

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cross-platform timestamp issues | Low | Python datetime is cross-platform |
| Timezone handling | Low | Use local time, document behavior |

**Validation Plan**: Minimal code change (~5 lines), well-understood Python APIs.

### Business Viability Risk (Organizational)

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Breaking change concerns | None | Additive change, backwards compatible |
| Documentation updates | Low | Minimal doc changes required |

**Validation Plan**: No breaking changes, purely additive improvement.

---

## 4. Functional Requirements

### Core Features and Capabilities

- **FR-001**: System MUST generate backup directory names with format `.specify-backup-YYYYMMDD-HHMMSS`
- **FR-002**: System MUST use local system time for timestamp generation
- **FR-003**: System MUST NOT overwrite existing backup directories
- **FR-004**: System MUST display the full timestamped backup path in console output
- **FR-005**: System MUST preserve all existing backup functionality (what gets backed up)

### Timestamp Format Specification

| Component | Format | Example |
|-----------|--------|---------|
| Year | YYYY | 2025 |
| Month | MM | 12 |
| Day | DD | 07 |
| Hour (24h) | HH | 14 |
| Minute | mm | 30 |
| Second | SS | 52 |
| **Full Format** | `.specify-backup-YYYYMMDD-HHMMSS` | `.specify-backup-20251207-143052` |

### File System Safety

The format uses only:
- ASCII digits (0-9)
- Hyphens (-)
- Period prefix (.)

This ensures compatibility across:
- Windows (NTFS, FAT32)
- macOS (APFS, HFS+)
- Linux (ext4, btrfs, etc.)

---

## 5. Non-Functional Requirements

### Performance Requirements

- **NFR-001**: Timestamp generation MUST add < 1ms to backup operation
- **NFR-002**: No additional I/O beyond current backup implementation

### Compatibility Requirements

- **NFR-003**: Works on Python 3.11+ (existing requirement)
- **NFR-004**: Works on Windows, macOS, Linux
- **NFR-005**: Directory name under 255 characters (filesystem limit)

### Maintainability Requirements

- **NFR-006**: Timestamp format documented in code comments
- **NFR-007**: Existing test patterns followed

---

## 6. Task Breakdown (Backlog Tasks)

**Implementation task created:**

- **task-300**: Add file-friendly timestamp to specify-backup directory path
  - Priority: Medium
  - Labels: backend, implement, size-s
  - Assignee: @pm-planner

**Acceptance Criteria** (from task-300):
1. Backup directory includes ISO 8601-like timestamp (YYYYMMDD-HHMMSS format)
2. Timestamp is file-system safe (no colons or special characters)
3. Multiple consecutive upgrades create separate backup directories
4. Backup directory name displayed correctly in console output
5. Existing tests pass and new tests cover timestamp format
6. Documentation updated to reflect new backup naming

---

## 7. Discovery and Validation Plan

### Learning Goals and Hypotheses

| Hypothesis | Validation Method | Success Criteria |
|------------|-------------------|------------------|
| Users need backup history | Feedback from issue/feature request | User confirms pain point |
| Timestamp format is intuitive | Code review | Reviewers understand format |
| Implementation is minimal | LoC count | < 10 lines changed |

### Go/No-Go Decision Points

- **Go**: If implementation fits within existing backup flow
- **No-Go**: If timestamp generation causes platform-specific issues (unlikely)

---

## 8. Acceptance Criteria and Testing

### Acceptance Test Scenarios

| # | Scenario | Expected Result |
|---|----------|-----------------|
| 1 | Fresh project upgrade | `.specify-backup-YYYYMMDD-HHMMSS/` created |
| 2 | Second upgrade | New timestamped backup, first preserved |
| 3 | Console output | Shows full timestamped path |
| 4 | Failed upgrade | Error message shows correct backup path |

### Definition of Done

- [ ] Implementation complete
- [ ] Unit tests pass
- [ ] Existing tests unaffected
- [ ] Console output updated
- [ ] Code reviewed
- [ ] Documentation updated (CHANGELOG.md minimum)

### Test Coverage Requirements

- New timestamp format helper function: 100% coverage
- Backup path generation: existing tests + new timestamp tests

---

## 9. Dependencies and Constraints

### Technical Dependencies

| Dependency | Purpose |
|------------|---------|
| Python `datetime` module | Timestamp generation (stdlib, no new deps) |
| `pathlib.Path` | Directory path construction (already used) |

### Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Timezone edge cases | Low | Low | Document local time usage |
| Filename length limits | None | Low | Total length well under 255 |

---

## 10. Success Metrics (Outcome-Focused)

### North Star Metric

**Backup Preservation Rate**: Percentage of upgrade operations that preserve previous backups.

| Current | Target | Measurement |
|---------|--------|-------------|
| 0% (overwrites) | 100% (all preserved) | Count unique backup directories after multiple upgrades |

### Leading Indicators

- Console output shows timestamped path
- No test regressions

### Lagging Indicators

- Zero user complaints about lost backups
- Users successfully performing rollbacks

### Measurement Approach

- Manual verification during code review
- Automated tests verify multiple backup directories created

---

## Implementation Notes

### Code Location

`src/specify_cli/__init__.py` line ~3675:

```python
# Current implementation
backup_dir = project_path / ".specify-backup"

# New implementation
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_dir = project_path / f".specify-backup-{timestamp}"
```

### Affected Console Messages

Update messages at lines ~3686, ~3710, ~3715 to reference `backup_dir.name` (already dynamic).

---

*PRD created by PM Planner agent via /flow:specify*
