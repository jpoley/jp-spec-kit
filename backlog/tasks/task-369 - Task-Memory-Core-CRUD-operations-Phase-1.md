---
id: task-369
title: 'Task Memory: Core CRUD operations (Phase 1)'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:56'
updated_date: '2025-12-15 02:17'
labels:
  - infrastructure
  - cli
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement foundational memory file operations: create, read, update, delete with YAML metadata validation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 backlog memory create initializes memory file with template
- [x] #2 backlog memory show displays memory content
- [x] #3 backlog memory edit opens memory in $EDITOR
- [x] #4 backlog memory clear removes content (preserves metadata)
- [x] #5 Memory files use YAML frontmatter for metadata
- [x] #6 Unit tests for all CRUD operations
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Task Memory CRUD operations for Phase 1:

## Summary
- **AC#1**: Added `create` command alias for `init` to initialize memory files with YAML frontmatter template
- **AC#2**: Verified `show` command displays memory content (already implemented)
- **AC#3**: Implemented `edit` command to open memory in $EDITOR with fallback to vim/nano
- **AC#4**: Updated `clear` command to preserve YAML frontmatter metadata while resetting content
- **AC#5**: Migrated template to YAML frontmatter format (task_id, created, updated)
- **AC#6**: Created comprehensive test suite with 21 new tests in test_memory_crud.py

## Implementation Details

### YAML Frontmatter Support
- Added `_parse_frontmatter()` method to extract metadata from YAML frontmatter
- Added `_serialize_frontmatter()` method to construct files with YAML frontmatter
- Updated `append()` method to update frontmatter timestamps
- Updated template at `templates/memory/default.md` to use YAML frontmatter

### New Commands
- `specify memory create` (alias for init) - initializes memory with template
- `specify memory edit` - opens memory in $EDITOR with auto-creation
- Updated `specify memory clear` - preserves metadata, resets content

### Clear Method Behavior Change
**Before**: Deleted the entire memory file
**After**: Preserves YAML frontmatter (task_id, created, updated), resets all content sections to empty template

### Test Coverage
Created `tests/test_memory_crud.py` with 21 unit tests covering:
- Create/init command functionality (4 tests)
- Show command functionality (3 tests)  
- Edit command functionality (4 tests)
- Clear command metadata preservation (3 tests)
- YAML frontmatter parsing/serialization (4 tests)
- Edge cases and error handling (3 tests)

All 111 memory-related tests pass.

## Files Modified
- `src/specify_cli/memory/store.py` - Added YAML frontmatter methods, updated append/clear
- `src/specify_cli/memory/cli.py` - Added edit command, updated clear command, added create alias
- `templates/memory/default.md` - Migrated to YAML frontmatter format
- `tests/test_memory_crud.py` - New test file with 21 tests
- `tests/test_memory_cli.py` - Updated fixture template to use YAML frontmatter
<!-- SECTION:NOTES:END -->
