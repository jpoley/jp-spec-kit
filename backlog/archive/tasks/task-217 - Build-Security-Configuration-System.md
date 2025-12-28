---
id: task-217
title: Build Security Configuration System
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-28 20:18'
labels:
  - security
  - config
  - on-hold
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement .flowspec/security-config.yml configuration file support with scanner selection, rulesets, and AI settings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Parse security-config.yml with schema validation
- [ ] #2 Support scanner enable/disable (Semgrep, CodeQL)
- [ ] #3 Configurable severity thresholds (fail_on)
- [ ] #4 Path exclusion patterns
- [ ] #5 AI triage confidence threshold settings
- [ ] #6 Custom Semgrep rule directory support
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Build Security Configuration System

### Overview
Implement .flowspec/security-config.yml configuration file support for scanner selection, rulesets, path exclusions, and AI settings.

### Step-by-Step Implementation

#### Step 1: Define Configuration Schema (1.5 hours)
**File**: `src/specify_cli/security/config_schema.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ScannerConfig(BaseModel):
    enabled: bool = True
    rulesets: List[str] = ["auto"]
    timeout_seconds: Optional[int] = 300

class SecurityConfig(BaseModel):
    version: str = "1.0"
    
    # Scanner configuration
    scanners: Dict[str, ScannerConfig] = {
        "semgrep": ScannerConfig(rulesets=["auto", "p/owasp-top-ten"]),
        "codeql": ScannerConfig(enabled=False)
    }
    
    # Severity thresholds
    fail_on: List[str] = ["critical", "high"]
    warn_on: List[str] = ["medium"]
    
    # Path configuration
    include_paths: List[str] = ["src/", "lib/"]
    exclude_paths: List[str] = ["tests/", "vendor/", "docs/"]
    
    # AI triage settings
    ai_triage: dict = {
        "enabled": True,
        "model": "claude-sonnet-4",
        "confidence_threshold": 0.7
    }
    
    # Custom rules
    custom_rules_dir: Optional[str] = ".flowspec/security-rules/"
```

#### Step 2: Implement Configuration Loader (2 hours)
**File**: `src/specify_cli/security/config.py`

```python
def load_security_config(path: str = ".flowspec/security-config.yml") -> SecurityConfig:
    """Load security configuration with fallback to defaults."""
    if not Path(path).exists():
        return SecurityConfig()  # Use defaults
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    return SecurityConfig(**data)

def merge_with_cli_args(config: SecurityConfig, args: Namespace) -> SecurityConfig:
    """Merge config file with CLI arguments (CLI takes precedence)."""
    if args.fail_on:
        config.fail_on = args.fail_on.split(",")
    if args.exclude:
        config.exclude_paths.extend(args.exclude)
    return config
```

#### Step 3: Integrate Configuration into Scan Command (2 hours)

1. Load config at scan start
2. Apply scanner enable/disable
3. Apply path inclusions/exclusions
4. Apply severity thresholds
5. Pass AI settings to triage

#### Step 4: Add Configuration Management Commands (2 hours)

```bash
# Initialize config file
specify security config init

# Validate config
specify security config validate

# Show effective config (with CLI overrides)
specify security config show

# Set specific values
specify security config set scanners.semgrep.enabled=false
```

#### Step 5: Create Default Template (1 hour)
**File**: `templates/security-config-template.yml`

#### Step 6: Testing (1.5 hours)
- Config parsing tests
- CLI override tests
- Path exclusion tests
- Invalid config handling

### Dependencies
- Security scan command (task-210)

### Estimated Effort
**Total**: 10 hours (1.25 days)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**ON HOLD (Dec 2025)**: Security scanning features may move to dedicated security repo.
<!-- SECTION:NOTES:END -->
