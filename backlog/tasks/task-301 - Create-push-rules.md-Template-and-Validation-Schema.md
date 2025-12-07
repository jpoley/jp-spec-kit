---
id: task-301
title: Create push-rules.md Template and Validation Schema
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-07 20:38'
updated_date: '2025-12-07 21:14'
labels:
  - implement
  - backend
  - templates
dependencies:
  - task-300
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the push-rules.md template file that defines mandatory pre-push checks. This file will be:
1. Generated during project setup via `specify init`
2. Validated using a JSON schema
3. Checked explicitly before every PR/push operation

The file must include sections for:
- Rebase policy (always rebase vs main)
- Linting requirements (must pass)
- Testing requirements (must pass)
- Janitor requirements (must run after validation)
- Branch naming conventions
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Template file created at templates/push-rules.md
- [x] #2 JSON schema created for validation
- [x] #3 Validation function implemented in specify_cli
- [x] #4 Unit tests cover schema validation
- [x] #5 Documentation added to docs/guides/
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Phase 1: Template Creation
1. Create `templates/push-rules-template.md` with YAML frontmatter
2. Include all required sections: rebase policy, linting, testing, branch naming, janitor settings
3. Add inline documentation explaining each field

### Phase 2: Schema Validation
1. Create Pydantic model at `src/specify_cli/models/push_rules.py`
2. Define PushRulesConfig with all fields and validation
3. Implement YAML frontmatter parser
4. Add validation error messages with line numbers

### Phase 3: Validation Function
1. Implement `validate_push_rules(path: Path) -> PushRulesConfig` in specify_cli
2. Handle missing file, invalid YAML, schema validation errors
3. Return parsed config or raise descriptive exceptions

### Phase 4: Unit Tests
1. Create `tests/unit/test_push_rules_parser.py`
2. Test valid configurations
3. Test invalid configurations with specific error messages
4. Test edge cases (missing fields, invalid values)
5. Target >80% coverage

### Phase 5: Documentation
1. Create `docs/guides/push-rules-configuration.md`
2. Document all configuration options
3. Add examples for common use cases

### References
- ADR-012: docs/adr/ADR-012-push-rules-enforcement-architecture.md
- Platform Design: docs/platform/push-rules-platform-design.md
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete (2025-12-07)

### Files Created
1. `templates/push-rules-template.md` - Template with full YAML frontmatter
2. `src/specify_cli/push_rules/__init__.py` - Module exports
3. `src/specify_cli/push_rules/models.py` - Pydantic models (PushRulesConfig, RebasePolicy, ValidationCommand, JanitorSettings)
4. `src/specify_cli/push_rules/parser.py` - YAML frontmatter parser and validation
5. `tests/test_push_rules.py` - 48 unit tests (100% pass)
6. `docs/guides/push-rules-configuration.md` - User guide

### Key Features
- Pydantic schema validation with clear error messages
- YAML frontmatter extraction from markdown
- Branch name regex validation
- Configurable lint/test commands with timeouts
- Janitor settings for cleanup automation

### Test Coverage
- 48 tests covering all models and parser functions
- Edge cases: empty files, invalid YAML, regex validation
- Template validation test ensures template is always valid
<!-- SECTION:NOTES:END -->
