# ADR-007: Hook Configuration Schema

**Status**: Proposed
**Date**: 2025-12-02
**Author**: @software-architect
**Context**: Agent Hooks Feature (task-199, task-200, task-210)

---

## Context

The event model (ADR-005) defines workflow events, and the execution model (ADR-006) defines how hooks run securely. This ADR defines how users **configure** hooks declaratively.

**Requirements**:
1. **Declarative**: Users define what hooks do, not how to implement them
2. **Readable**: Non-developers can understand hook configurations
3. **Extensible**: Support future features (webhooks, conditional execution) without breaking changes
4. **Validatable**: Configuration errors caught early with JSON Schema validation
5. **Version-Stable**: Configuration format changes follow semantic versioning

**User Personas**:
- **Sarah (Backend Engineer)**: Wants hooks for automated testing after implementation
- **Marcus (Platform Engineer)**: Needs webhooks to CI/CD pipelines
- **Elena (Product Manager)**: Wants Slack notifications when specs are created

---

## Decision

Use **YAML format** for hook configuration with JSON Schema validation.

### 1. Configuration File Location

**Path**: `.specify/hooks/hooks.yaml`

**Rationale**:
- `.specify/` directory already exists (created by `specify init`)
- `hooks/` subdirectory contains both config and scripts
- `hooks.yaml` vs `config.yaml` is more specific and discoverable

**Directory Structure**:
```
.specify/
├── hooks/
│   ├── hooks.yaml          # Hook configuration (this ADR)
│   ├── run-tests.sh        # Example hook script
│   ├── update-changelog.py # Example hook script
│   └── audit.log           # Execution audit log
├── plan-template.md
└── spec-template.md
```

### 2. YAML Schema Definition

**Complete Example**:
```yaml
# .specify/hooks/hooks.yaml
version: "1.0"

# Global defaults applied to all hooks
defaults:
  timeout: 30  # seconds
  working_directory: "."
  shell: "/bin/bash"
  fail_mode: "continue"  # continue | stop
  enabled: true

# Hook definitions
hooks:
  # Example 1: Run tests after implementation
  - name: "run-tests"
    description: "Run test suite after implementation completes"
    events:
      - type: "implement.completed"
    script: "run-tests.sh"
    timeout: 300  # 5 minutes
    env:
      PYTEST_ARGS: "-v --cov=src"
    fail_mode: "stop"  # Block workflow if tests fail

  # Example 2: Update changelog when spec created
  - name: "update-changelog"
    description: "Add feature to CHANGELOG.md when spec created"
    events:
      - type: "spec.created"
      - type: "spec.updated"
    script: "update-changelog.py"
    env:
      CHANGELOG_PATH: "./CHANGELOG.md"

  # Example 3: Notify Slack on high-priority task completion
  - name: "notify-slack"
    description: "Send Slack notification on task completion"
    events:
      - type: "task.completed"
        filter:
          priority: ["high", "critical"]
          labels_any: ["backend", "frontend"]
    command: |
      curl -X POST "${SLACK_WEBHOOK_URL}" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"✅ Task ${TASK_ID} completed: ${TASK_TITLE}\"}"
    timeout: 10
    fail_mode: "continue"

  # Example 4: Disabled hook (can be re-enabled without deletion)
  - name: "deploy-staging"
    description: "Trigger staging deployment on validation"
    enabled: false  # Temporarily disabled
    events:
      - type: "validate.completed"
    script: "deploy-staging.sh"
```

### 3. Schema Field Specification

#### Top-Level Fields

**`version`** (required):
- Type: `string`
- Pattern: `^\d+\.\d+$` (e.g., "1.0", "2.1")
- Description: Configuration schema version
- Purpose: Enable backward compatibility and migration warnings

**`defaults`** (optional):
- Type: `object`
- Description: Default values applied to all hooks
- Fields: `timeout`, `working_directory`, `shell`, `fail_mode`, `enabled`

**`hooks`** (required):
- Type: `array`
- Description: List of hook definitions
- Constraints: At least one hook, unique hook names

#### Hook Definition Fields

**Required Fields**:

**`name`** (required):
- Type: `string`
- Pattern: `^[a-z0-9-]+$` (lowercase alphanumeric + hyphens)
- Description: Unique identifier for hook
- Examples: `run-tests`, `notify-slack`, `update-docs`

**`events`** (required):
- Type: `array` (at least one event matcher)
- Description: Event matchers that trigger this hook
- See "Event Matcher Schema" below

**Execution Method** (one required):

**`script`** (conditional):
- Type: `string`
- Description: Path to executable script (relative to `.specify/hooks/`)
- Constraints: Must exist in `.specify/hooks/`, no path traversal (`..`)
- Examples: `run-tests.sh`, `update-changelog.py`

**`command`** (conditional):
- Type: `string`
- Description: Inline shell command
- Examples: `pytest tests/`, `curl -X POST ...`

**`webhook`** (v2 feature):
- Type: `object`
- Description: HTTP webhook configuration
- Fields: `url`, `method`, `headers`, `payload`, `retry`

**Optional Fields**:

**`description`** (optional):
- Type: `string`
- Description: Human-readable description of hook purpose
- Max Length: 500 characters

**`timeout`** (optional):
- Type: `integer`
- Default: 30 (from defaults)
- Range: 1-600 seconds (10 minutes max)
- Description: Maximum execution time before SIGTERM

**`working_directory`** (optional):
- Type: `string`
- Default: "." (project root)
- Description: Working directory for script execution
- Constraints: Must be subdirectory of project root

**`shell`** (optional):
- Type: `string`
- Default: "/bin/bash"
- Description: Shell to use for command execution
- Examples: `/bin/bash`, `/bin/zsh`, `/usr/bin/python3`

**`env`** (optional):
- Type: `object` (key-value pairs)
- Description: Environment variables passed to script
- Example: `PYTEST_ARGS: "-v --cov=src"`

**`fail_mode`** (optional):
- Type: `string`
- Enum: `["continue", "stop"]`
- Default: "continue"
- Description: How to handle hook failures
  - `continue`: Log error, workflow continues
  - `stop`: Block workflow, exit with error

**`enabled`** (optional):
- Type: `boolean`
- Default: true
- Description: Enable/disable hook without removing configuration

#### Event Matcher Schema

**Simple Matcher**:
```yaml
events:
  - type: "task.completed"
```

**Wildcard Matcher**:
```yaml
events:
  - type: "task.*"          # All task events
  - type: "*.completed"     # All completion events
```

**Filtered Matcher**:
```yaml
events:
  - type: "task.status_changed"
    filter:
      status_to: "Done"                      # Exact match
      priority: ["high", "critical"]         # Any of these values
      labels_any: ["backend", "frontend"]    # At least one label matches
      labels_all: ["security", "reviewed"]   # All labels must be present
```

**Filter Field Types**:
- **Exact Match**: `status_to: "Done"` - Field must equal value
- **Array Match (OR)**: `priority: ["high", "critical"]` - Field must be one of these
- **Array Match (ANY)**: `labels_any: ["a", "b"]` - At least one label present
- **Array Match (ALL)**: `labels_all: ["a", "b"]` - All labels must be present

**Multiple Events** (OR semantics):
```yaml
events:
  - type: "spec.created"
  - type: "spec.updated"
```
Hook runs if EITHER event matches.

### 4. JSON Schema Validation

**Location**: `src/specify_cli/hooks/schemas/hooks-config.schema.json`

**Schema Definition**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Flowspec Hooks Configuration",
  "type": "object",
  "required": ["version", "hooks"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Configuration schema version"
    },
    "defaults": {
      "type": "object",
      "properties": {
        "timeout": {"type": "integer", "minimum": 1, "maximum": 600},
        "working_directory": {"type": "string"},
        "shell": {"type": "string"},
        "fail_mode": {"type": "string", "enum": ["continue", "stop"]},
        "enabled": {"type": "boolean"}
      }
    },
    "hooks": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name", "events"],
        "oneOf": [
          {"required": ["script"]},
          {"required": ["command"]},
          {"required": ["webhook"]}
        ],
        "properties": {
          "name": {
            "type": "string",
            "pattern": "^[a-z0-9-]+$"
          },
          "description": {
            "type": "string",
            "maxLength": 500
          },
          "events": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["type"],
              "properties": {
                "type": {
                  "type": "string",
                  "pattern": "^[a-z*]+\\.[a-z_*]+$"
                },
                "filter": {
                  "type": "object",
                  "additionalProperties": true
                }
              }
            }
          },
          "script": {
            "type": "string"
          },
          "command": {
            "type": "string"
          },
          "timeout": {
            "type": "integer",
            "minimum": 1,
            "maximum": 600
          },
          "working_directory": {
            "type": "string"
          },
          "shell": {
            "type": "string"
          },
          "env": {
            "type": "object",
            "additionalProperties": {"type": "string"}
          },
          "fail_mode": {
            "type": "string",
            "enum": ["continue", "stop"]
          },
          "enabled": {
            "type": "boolean"
          }
        }
      }
    }
  }
}
```

### 5. Configuration Validation

**Validation Command**:
```bash
# Validate hooks configuration
specify hooks validate

# Output:
# ✓ Schema validation passed
# ✓ All hook scripts exist
# ✓ No duplicate hook names
# ✓ All event types recognized
# ⚠ Warning: Hook 'deploy' has timeout of 600s (max allowed)
```

**Validation Checks**:

1. **JSON Schema Validation**: Configuration structure matches schema
2. **Script Existence**: All `script` paths exist in `.specify/hooks/`
3. **Unique Names**: No duplicate hook names
4. **Event Type Recognition**: All event types are documented types
5. **Path Safety**: No path traversal in script paths
6. **Timeout Limits**: Timeouts within 1-600s range
7. **Shell Availability**: Configured shells exist on system

**Implementation**:
```python
from jsonschema import validate, ValidationError

def validate_hooks_config(config_path: Path) -> ValidationResult:
    """Validate hooks configuration against schema and runtime constraints."""

    # Load configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # JSON Schema validation
    schema = load_json_schema("hooks-config.schema.json")
    try:
        validate(instance=config, schema=schema)
    except ValidationError as e:
        return ValidationResult(valid=False, errors=[f"Schema error: {e.message}"])

    errors = []
    warnings = []

    # Check hook names are unique
    hook_names = [hook["name"] for hook in config["hooks"]]
    if len(hook_names) != len(set(hook_names)):
        errors.append("Duplicate hook names found")

    # Check scripts exist
    for hook in config["hooks"]:
        if "script" in hook:
            script_path = Path(".specify/hooks") / hook["script"]
            if not script_path.exists():
                errors.append(f"Hook '{hook['name']}' script not found: {hook['script']}")

            # Check for path traversal
            if ".." in hook["script"]:
                errors.append(f"Hook '{hook['name']}' script path traversal detected")

    # Check event types are recognized
    valid_event_types = load_valid_event_types()
    for hook in config["hooks"]:
        for event_matcher in hook["events"]:
            event_type = event_matcher["type"]
            if "*" not in event_type and event_type not in valid_event_types:
                warnings.append(f"Hook '{hook['name']}' uses unrecognized event type: {event_type}")

    # Check timeout limits
    for hook in config["hooks"]:
        timeout = hook.get("timeout", config.get("defaults", {}).get("timeout", 30))
        if timeout > 600:
            warnings.append(f"Hook '{hook['name']}' timeout {timeout}s exceeds recommended max (600s)")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
```

### 6. Configuration Loading

**Loading Priority**:
1. Project-local: `.specify/hooks/hooks.yaml`
2. Global defaults: `~/.specify/hooks/hooks.yaml` (v2 feature)
3. Built-in defaults: Empty hooks list

**Implementation**:
```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import yaml

@dataclass
class HookConfig:
    name: str
    events: List[Dict[str, Any]]
    script: Optional[str] = None
    command: Optional[str] = None
    description: Optional[str] = None
    timeout: int = 30
    working_directory: str = "."
    shell: str = "/bin/bash"
    env: Dict[str, str] = field(default_factory=dict)
    fail_mode: str = "continue"
    enabled: bool = True

@dataclass
class HooksConfig:
    version: str
    hooks: List[HookConfig]
    defaults: Dict[str, Any]

def load_hooks_config(config_path: Path) -> HooksConfig:
    """Load and parse hooks configuration with defaults."""

    if not config_path.exists():
        # No hooks configured
        return HooksConfig(version="1.0", hooks=[], defaults={})

    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    # Validate against schema
    validation_result = validate_hooks_config_schema(raw_config)
    if not validation_result.valid:
        raise ConfigurationError(f"Invalid hooks.yaml: {validation_result.errors}")

    # Apply defaults to hooks
    defaults = raw_config.get("defaults", {})
    hooks = []

    for hook_data in raw_config.get("hooks", []):
        # Merge hook-specific config with defaults
        hook_config = {**defaults, **hook_data}
        hooks.append(HookConfig(**hook_config))

    return HooksConfig(
        version=raw_config["version"],
        hooks=hooks,
        defaults=defaults
    )
```

---

## Consequences

### Positive

1. **Readability**: YAML is human-readable, familiar to developers (CI/CD configs)
2. **Validation**: JSON Schema catches errors early, before hook execution
3. **Extensibility**: New fields can be added without breaking existing configs
4. **Defaults**: Global defaults reduce repetition in hook definitions
5. **Filtering**: Event matchers with filters enable precise hook targeting

### Negative

1. **YAML Pitfalls**: YAML has gotchas (tabs vs spaces, unquoted values, multiline)
   - Mitigation: Provide example configs, use YAML linters in docs
2. **Schema Complexity**: JSON Schema verbose and hard to maintain
   - Mitigation: Generate schema from Pydantic models (v2), keep examples updated
3. **Filter Semantics**: Array match types (any/all) may confuse users
   - Mitigation: Clear documentation, explicit field names (`labels_any` vs `labels_all`)

### Neutral

1. **YAML vs TOML**: YAML chosen over TOML for better array/object nesting
   - Trade-off: YAML more expressive but more complex
2. **Single File**: All hooks in one file vs directory of files
   - Trade-off: Simpler discovery but harder to modularize (acceptable for v1)

---

## Alternatives Considered

### Alternative 1: TOML Configuration

**Approach**: Use TOML instead of YAML.

**Example**:
```toml
version = "1.0"

[defaults]
timeout = 30
fail_mode = "continue"

[[hooks]]
name = "run-tests"
events = ["implement.completed"]
script = "run-tests.sh"
timeout = 300
```

**Rejected Because**:
- TOML verbose for nested arrays (events with filters)
- Less familiar to developers (YAML more common in CI/CD)
- Harder to represent complex event matchers

**Advantages of TOML**:
- Fewer syntax pitfalls than YAML
- Explicit typing (no "Norway problem")

### Alternative 2: Python Configuration

**Approach**: Configuration is Python code.

**Example**:
```python
# .specify/hooks/hooks.py
from specify_hooks import Hook, Event

hooks = [
    Hook(
        name="run-tests",
        events=[Event.IMPLEMENT_COMPLETED],
        script="run-tests.sh",
        timeout=300,
    ),
]
```

**Rejected Because**:
- Ties configuration to Python (not tool-agnostic)
- Harder to validate statically (requires Python interpreter)
- Security risk (arbitrary code execution on config load)
- Less declarative (users can add logic, reduces clarity)

### Alternative 3: JSON Configuration

**Approach**: Use JSON instead of YAML.

**Example**:
```json
{
  "version": "1.0",
  "hooks": [
    {
      "name": "run-tests",
      "events": [{"type": "implement.completed"}],
      "script": "run-tests.sh"
    }
  ]
}
```

**Rejected Because**:
- No comments (YAML supports comments)
- Verbose (trailing commas, quotes on keys)
- Less human-friendly for hand-editing

**Advantages of JSON**:
- Universal parsing support
- Strict syntax (fewer ambiguities)

### Alternative 4: Directory-Based Configuration

**Approach**: Each hook is a separate file.

**Example**:
```
.specify/hooks/
├── run-tests/
│   ├── hook.yaml
│   └── script.sh
├── update-changelog/
│   ├── hook.yaml
│   └── script.py
```

**Rejected for v1 Because**:
- Increases file system overhead (many files)
- Harder to get overview of all hooks
- More complex discovery logic

**Advantages**:
- Better organization for large hook collections
- Scripts co-located with configs

**Note**: Could revisit for v2 with `specify hooks init <hook-name>` scaffolding.

---

## Implementation Guidance

### Configuration Parser

**Location**: `src/specify_cli/hooks/config_parser.py`

**Key Functions**:
```python
import yaml
from pathlib import Path
from typing import Optional

def load_hooks_config(config_path: Path) -> HooksConfig:
    """Load hooks configuration with validation."""
    if not config_path.exists():
        return HooksConfig.empty()

    with open(config_path) as f:
        raw_config = yaml.safe_load(f)

    # Validate
    validate_hooks_config_schema(raw_config)

    # Parse into dataclasses
    return parse_hooks_config(raw_config)

def validate_hooks_config_schema(config: dict) -> ValidationResult:
    """Validate configuration against JSON schema."""
    schema = load_json_schema("hooks-config.schema.json")
    try:
        jsonschema.validate(instance=config, schema=schema)
        return ValidationResult(valid=True)
    except jsonschema.ValidationError as e:
        return ValidationResult(valid=False, errors=[e.message])

def parse_hooks_config(raw_config: dict) -> HooksConfig:
    """Parse raw config dict into typed dataclasses."""
    defaults = raw_config.get("defaults", {})

    hooks = []
    for hook_data in raw_config.get("hooks", []):
        # Apply defaults
        merged = {**defaults, **hook_data}

        # Validate execution method
        if not any(key in merged for key in ["script", "command", "webhook"]):
            raise ConfigurationError(f"Hook '{merged['name']}' missing execution method")

        hooks.append(HookConfig(**merged))

    return HooksConfig(
        version=raw_config["version"],
        hooks=hooks,
        defaults=defaults
    )
```

### Event Matcher

**Location**: `src/specify_cli/hooks/matcher.py`

**Key Functions**:
```python
from fnmatch import fnmatch

def match_event(event: Event, event_matcher: dict) -> bool:
    """Check if event matches event matcher."""

    # Match event type (supports wildcards)
    event_type_pattern = event_matcher["type"]
    if not fnmatch(event.event_type, event_type_pattern):
        return False

    # Match filters (if present)
    filters = event_matcher.get("filter", {})
    for field, expected_value in filters.items():
        actual_value = get_nested_field(event.context, field)

        # Handle special filter types
        if field.endswith("_any"):
            # labels_any: At least one label matches
            base_field = field[:-4]  # Remove "_any"
            actual_labels = get_nested_field(event.context, base_field)
            if not any(label in expected_value for label in actual_labels):
                return False

        elif field.endswith("_all"):
            # labels_all: All expected labels present
            base_field = field[:-4]  # Remove "_all"
            actual_labels = get_nested_field(event.context, base_field)
            if not all(label in actual_labels for label in expected_value):
                return False

        elif isinstance(expected_value, list):
            # Array match (OR): actual must be one of expected
            if actual_value not in expected_value:
                return False

        else:
            # Exact match
            if actual_value != expected_value:
                return False

    return True

def match_hooks(hooks_config: HooksConfig, event: Event) -> List[HookConfig]:
    """Return all hooks that match event."""
    matching = []

    for hook in hooks_config.hooks:
        # Skip disabled hooks
        if not hook.enabled:
            continue

        # Check each event matcher (OR semantics)
        for event_matcher in hook.events:
            if match_event(event, event_matcher):
                matching.append(hook)
                break  # Hook matched, don't check other matchers

    return matching
```

---

## Testing Strategy

### Schema Validation Tests

```python
def test_valid_config():
    """Valid configuration passes schema validation."""
    config = {
        "version": "1.0",
        "hooks": [
            {
                "name": "run-tests",
                "events": [{"type": "implement.completed"}],
                "script": "run-tests.sh"
            }
        ]
    }
    result = validate_hooks_config_schema(config)
    assert result.valid

def test_missing_required_field():
    """Missing required field fails validation."""
    config = {
        "version": "1.0",
        "hooks": [{"name": "test"}]  # Missing "events"
    }
    result = validate_hooks_config_schema(config)
    assert not result.valid
    assert "events" in result.errors[0]
```

### Event Matcher Tests

```python
def test_exact_match():
    """Event matcher with exact type match."""
    event = Event(event_type="spec.created")
    matcher = {"type": "spec.created"}
    assert match_event(event, matcher)

def test_wildcard_match():
    """Event matcher with wildcard pattern."""
    event = Event(event_type="task.completed")
    matcher = {"type": "task.*"}
    assert match_event(event, matcher)

def test_filter_array_match():
    """Event matcher with array filter (OR)."""
    event = Event(
        event_type="task.completed",
        context={"priority": "high"}
    )
    matcher = {
        "type": "task.completed",
        "filter": {"priority": ["high", "critical"]}
    }
    assert match_event(event, matcher)

def test_filter_labels_any():
    """Event matcher with labels_any filter."""
    event = Event(
        event_type="task.completed",
        context={"labels": ["backend", "security"]}
    )
    matcher = {
        "type": "task.completed",
        "filter": {"labels_any": ["frontend", "backend"]}
    }
    assert match_event(event, matcher)
```

### Configuration Loading Tests

```python
def test_defaults_applied():
    """Defaults merged into hook configurations."""
    config = {
        "version": "1.0",
        "defaults": {"timeout": 60},
        "hooks": [
            {"name": "test", "events": [{"type": "spec.created"}], "script": "test.sh"}
        ]
    }
    hooks_config = parse_hooks_config(config)
    assert hooks_config.hooks[0].timeout == 60
```

---

## References

- **ADR-005**: Event Model Architecture - Defines event types used in matchers
- **ADR-006**: Hook Execution Model - Defines how hooks execute
- **PRD**: `docs/prd/agent-hooks-prd.md` - Section 3.2 Hook Definition Format
- **task-199**: Design Hook Definition Format (YAML Schema)
- **task-200**: Implement Hook Configuration Parser

---

## Revision History

- **2025-12-02**: Initial decision (v1.0) - @software-architect
