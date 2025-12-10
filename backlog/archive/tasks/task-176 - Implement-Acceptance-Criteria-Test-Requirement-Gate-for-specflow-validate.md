---
id: task-176
title: 'Implement Acceptance Criteria Test Requirement Gate for /specflow:validate'
status: To Do
assignee: []
created_date: '2025-11-30 20:06'
updated_date: '2025-11-30 20:08'
labels:
  - workflow-artifacts
  - critical
dependencies: []
priority: high
---

<!-- AC:END -->

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Implement a quality gate requiring runnable tests that map to acceptance criteria before the Validate phase can proceed. Every AC must have corresponding test coverage.

## Test Requirements

### Test Mapping Structure
Tests must be traceable to acceptance criteria:

```python
# tests/test_feature.py
import pytest

class TestUserAuthentication:
    """Tests for PRD: user-authentication"""
    
    @pytest.mark.ac("AC1: User can register with email and password")
    def test_user_registration_with_email(self):
        """AC1: User can register with email and password"""
        # Test implementation
        pass
    
    @pytest.mark.ac("AC2: Password must be minimum 8 characters")
    def test_password_minimum_length(self):
        """AC2: Password must be minimum 8 characters"""
        pass
```

### Test Coverage Manifest
Generate `./tests/ac-coverage.json` mapping ACs to tests:

```json
{
  "feature": "user-authentication",
  "prd_path": "./docs/prd/user-authentication.md",
  "acceptance_criteria": [
    {
      "id": "AC1",
      "description": "User can register with email and password",
      "tests": [
        "tests/test_auth.py::TestUserAuthentication::test_user_registration_with_email"
      ],
      "coverage": "covered"
    },
    {
      "id": "AC2", 
      "description": "Password must be minimum 8 characters",
      "tests": [
        "tests/test_auth.py::TestUserAuthentication::test_password_minimum_length"
      ],
      "coverage": "covered"
    }
  ],
  "summary": {
    "total_acs": 5,
    "covered": 5,
    "uncovered": 0,
    "coverage_percent": 100
  }
}
```

### Validation Rules
1. All ACs from PRD must have at least one mapped test
2. All mapped tests must pass (exit code 0)
3. Coverage report must be generated as artifact

## Acceptance Criteria
- [ ] AC1: Create pytest marker @pytest.mark.ac("AC description") for test-to-AC mapping
- [ ] AC2: Implement AC coverage scanner that parses PRD and matches to test markers
- [ ] AC3: Generate ac-coverage.json manifest after test run
- [ ] AC4: Add AC coverage check to /specflow:implement exit gate
- [ ] AC5: Block transition to validate if any AC lacks test coverage
- [ ] AC6: Add --ac-coverage flag to specify CLI for manual coverage check
- [ ] AC7: Support multiple test frameworks (pytest, jest, go test) via plugins
- [ ] AC8: Report uncovered ACs with specific guidance on what tests to add

## Dependencies
- task-172 (Workflow Artifacts Specification)
- task-173 (PRD Requirement Gate) - PRD contains ACs to validate against
<!-- SECTION:NOTES:END -->
