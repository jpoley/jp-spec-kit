---
id: task-223
title: Implement Custom Security Rules System
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 02:16'
updated_date: '2025-12-28 20:18'
labels:
  - security
  - rules
  - on-hold
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to define custom security rules in .flowspec/security-rules/ directory. Support Semgrep custom rules and pattern definitions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create .flowspec/security-rules/ directory structure
- [ ] #2 Support custom Semgrep rule definitions
- [ ] #3 Load and validate custom rules at scan time
- [ ] #4 Document custom rule creation process
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Implement Custom Security Rules System

### Overview
Allow users to define custom Semgrep rules in .flowspec/security-rules/ directory with automatic loading and validation.

### Step-by-Step Implementation

#### Step 1: Create Rules Directory Structure (1 hour)
```
.flowspec/security-rules/
├── python/
│   ├── custom-sql-injection.yml
│   └── api-auth-bypass.yml
├── javascript/
│   └── unsafe-eval.yml
└── README.md
```

#### Step 2: Implement Rule Loader (2 hours)
**File**: `src/specify_cli/security/custom_rules.py`

```python
def load_custom_rules(rules_dir: str = ".flowspec/security-rules/") -> List[str]:
    """Load custom Semgrep rules from directory."""
    if not Path(rules_dir).exists():
        return []
    
    rule_files = []
    for root, dirs, files in os.walk(rules_dir):
        for file in files:
            if file.endswith(('.yml', '.yaml')):
                path = Path(root) / file
                if validate_semgrep_rule(path):
                    rule_files.append(str(path))
                else:
                    logger.warning(f"Invalid rule: {path}")
    
    return rule_files
```

#### Step 3: Integrate with Scan Command (1 hour)
Pass custom rules to Semgrep:
```bash
semgrep --config auto --config .flowspec/security-rules/
```

#### Step 4: Add Rule Validation (2 hours)
```python
def validate_semgrep_rule(rule_file: Path) -> bool:
    """Validate Semgrep rule syntax."""
    result = subprocess.run(
        ["semgrep", "--validate", "--config", str(rule_file)],
        capture_output=True
    )
    return result.returncode == 0
```

#### Step 5: Documentation (2 hours)
**File**: `docs/guides/custom-security-rules.md`

Sections:
1. Semgrep rule syntax overview
2. Creating your first custom rule
3. Rule patterns library (examples)
4. Testing custom rules
5. Contributing rules upstream

Example rule template provided.

#### Step 6: Testing (2 hours)
- Test rule loading
- Test rule validation
- Test rule execution
- Test invalid rule handling

### Dependencies
- Semgrep installed
- Security scan command

### Estimated Effort
**Total**: 10 hours (1.25 days)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**ON HOLD (Dec 2025)**: Security scanning features may move to dedicated security repo.
<!-- SECTION:NOTES:END -->
