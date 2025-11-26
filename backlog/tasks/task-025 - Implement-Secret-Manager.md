---
id: task-025
title: Implement Secret Manager
status: In Progress
assignee:
  - '@claude-agent'
created_date: '2025-11-24'
updated_date: '2025-11-26 18:16'
labels:
  - implementation
  - security
  - P0
  - satellite-mode
dependencies:
  - task-023
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement secure credential management with keychain support.

## Phase

Phase 3: Implementation - Core
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Multi-platform keychain integration (keyring library)
- [x] #2 Environment variable support
- [x] #3 `gh` CLI auth integration
- [x] #4 Interactive prompt with save option
- [x] #5 Log filter to prevent token leakage
- [x] #6 Token validation

## Deliverables

- `src/backlog_md/infrastructure/secret_manager.py` - Implementation
- Unit tests (mock keychain)
- Integration tests (real keychain on CI)

## Parallelizable

[P] with task-024
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Phase 1: Setup & Dependencies
1. Add `keyring>=25.0.0` to pyproject.toml dependencies
2. Create `src/specify_cli/satellite/secrets.py` module

### Phase 2: Core SecretManager Class
3. Implement `SecretManager` class with:
   - `__init__(service_name="backlog-satellite")` 
   - Provider credential storage keys: `{provider}-token` pattern
   - Fallback chain: keychain → env_var → gh_cli → prompt

### Phase 3: Credential Retrieval Methods (AC#1, AC#2, AC#3)
4. `get_token(provider: ProviderType) -> str | None`
   - Try keychain via keyring.get_password()
   - Try env vars: GITHUB_TOKEN, JIRA_TOKEN, NOTION_TOKEN
   - For GitHub: Try `gh auth token` subprocess
   - Return None if all fail

5. `store_token(provider: ProviderType, token: str) -> bool`
   - Store in system keychain via keyring.set_password()
   - Handle SecretStorageUnavailableError gracefully

6. `delete_token(provider: ProviderType) -> bool`
   - Remove from keychain via keyring.delete_password()

### Phase 4: Interactive Prompt (AC#4)
7. `prompt_for_token(provider: ProviderType, save: bool = True) -> str`
   - Use getpass for secure input
   - Optionally validate before saving
   - Store if save=True and keychain available

### Phase 5: Token Validation (AC#6)
8. `validate_token_format(provider: ProviderType, token: str) -> bool`
   - GitHub: ghp_*, gho_*, github_pat_*, or 40-char hex
   - Jira: Base64 email:token format check
   - Notion: secret_* or ntn_* prefix

### Phase 6: Log Redaction Filter (AC#5)
9. Implement `TokenRedactionFilter(logging.Filter)` class
   - Track known tokens to redact
   - Replace tokens with [REDACTED:{provider}] in log messages
   - Register via `add_token_to_redact(token, provider)`

### Phase 7: Integration & Exports
10. Add SecretManager to satellite/__init__.py exports
11. Add TokenRedactionFilter to exports

### Testing Strategy
- Unit tests for each retrieval path (mock keyring, env, subprocess)
- Test fallback chain order
- Test token validation patterns
- Test log redaction works correctly
- Integration test with actual keychain (manual)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete:

- Created secrets.py with SecretManager class supporting keychain (keyring), env vars, gh CLI, and interactive prompt
- Added TokenRedactionFilter for log security
- Token format validation for GitHub, Jira, Notion
- 38 unit tests all passing
- User documentation at docs/guides/satellite-credentials.md

PR: https://github.com/jpoley/jp-spec-kit/pull/9
<!-- SECTION:NOTES:END -->
