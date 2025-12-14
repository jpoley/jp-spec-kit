# Telemetry Feedback Prompt UI Design

**Task**: task-366 (Acceptance Criteria #5)
**Created**: 2025-12-14
**Status**: Design Complete

## Overview

This document describes the UI design for the telemetry feedback prompt that appears during `specify init` to collect user consent for anonymous usage analytics.

## Design Goals

1. **Transparency**: Clearly explain what data is collected
2. **Privacy-First**: Default to disabled, require explicit opt-in
3. **Non-Intrusive**: Single prompt during init, easy to skip
4. **Accessible**: Works in terminal environments without rich formatting

## User Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    specify init myproject                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ ✓ Created project structure                                 │
│ ✓ Initialized constitution.md                               │
│ ✓ Added .claude/commands/                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TELEMETRY PROMPT                          │
│                                                              │
│  Help improve Flowspec?                                      │
│                                                              │
│  We collect anonymous usage data:                            │
│  • Role selections (dev/pm/qa)                              │
│  • Commands used                                             │
│  • Agent invocations                                         │
│                                                              │
│  Data is stored locally in .flowspec/telemetry.jsonl        │
│  No personal info collected. View anytime with:             │
│    specify telemetry view                                    │
│                                                              │
│  Enable telemetry? [y/N]: _                                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
        User types 'y'                  User types 'n' or Enter
              │                               │
              ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│ ✓ Telemetry enabled     │    │ Telemetry disabled.         │
│                         │    │ Change anytime:             │
│ View: specify telemetry │    │   specify telemetry enable  │
│ Clear: specify telemetry│    └─────────────────────────────┘
│        clear            │
└─────────────────────────┘
```

## Terminal Output Design

### Prompt Message (ANSI-aware)

```python
TELEMETRY_PROMPT = """
╭─────────────────────────────────────────────────────────────╮
│                    Help improve Flowspec?                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  We collect anonymous usage data:                            │
│  • Role selections (dev/pm/qa)                              │
│  • Commands used (/flow:implement, etc.)                    │
│  • Agent invocations                                         │
│                                                              │
│  Privacy:                                                    │
│  • Data stored locally in .flowspec/telemetry.jsonl         │
│  • All identifiers are SHA-256 hashed                       │
│  • No personal information collected                        │
│  • View/clear anytime: specify telemetry view|clear         │
│                                                              │
╰─────────────────────────────────────────────────────────────╯

Enable telemetry? [y/N]: """
```

### Plain Text Fallback (NO_COLOR / dumb terminal)

```
Help improve Flowspec?

We collect anonymous usage data:
- Role selections (dev/pm/qa)
- Commands used (/flow:implement, etc.)
- Agent invocations

Privacy:
- Data stored locally in .flowspec/telemetry.jsonl
- All identifiers are SHA-256 hashed
- No personal information collected
- View/clear anytime: specify telemetry view|clear

Enable telemetry? [y/N]:
```

## Configuration Storage

### flowspec_workflow.yml

```yaml
telemetry:
  enabled: false  # Default disabled
  consent_date: null  # ISO timestamp when user consented
  version: "1.0"  # Telemetry schema version
```

### Environment Variable Override

```bash
# Disable telemetry globally (overrides config)
export FLOWSPEC_TELEMETRY_DISABLED=1

# Enable debug output
export FLOWSPEC_TELEMETRY_DEBUG=1
```

## CLI Commands

### Enable/Disable

```bash
# Enable telemetry
specify telemetry enable

# Disable telemetry
specify telemetry disable
```

### View Telemetry Data

```bash
# View recent events (last 50)
specify telemetry view

# View all events
specify telemetry view --all

# View events for specific role
specify telemetry view --role dev

# JSON output
specify telemetry view --json
```

### Clear Telemetry Data

```bash
# Clear all telemetry data
specify telemetry clear

# Confirmation prompt
Are you sure you want to delete all telemetry data? [y/N]:
```

## Implementation Notes

### Privacy-First Defaults

1. **Opt-In Only**: Telemetry is disabled by default
2. **Local Storage**: All data stays in `.flowspec/telemetry.jsonl`
3. **PII Hashing**: All potentially identifying data is SHA-256 hashed
4. **No Network**: v1 does not transmit data anywhere

### Data Collected

| Field | Description | Hashed |
|-------|-------------|--------|
| event_type | Event category (role.selected, agent.invoked) | No |
| role | Selected role (dev, pm, qa) | No |
| command | Command name (/flow:implement) | No |
| agent | Agent name (backend-engineer) | No |
| timestamp | ISO timestamp | No |
| project | Project identifier | Yes |
| user | Username from context | Yes |
| path | File paths | Yes (home dir removed) |

### Hash Function

```python
def hash_pii(value: str, salt: str = "") -> str:
    """Hash PII value with optional salt."""
    combined = f"{salt}{value}".encode("utf-8")
    return hashlib.sha256(combined).hexdigest()[:12]
```

## Accessibility

1. **Screen Reader**: All text is plain, no visual-only information
2. **Color Blind**: Box drawing uses characters, not color
3. **Keyboard**: Standard input, no special keys required
4. **Terminal Size**: Wraps gracefully on narrow terminals

## Future Considerations (v2)

1. **Remote Upload**: Optional anonymous data sharing (requires additional consent)
2. **Dashboard**: Web UI for viewing aggregated analytics
3. **Insights**: Role-specific recommendations based on usage patterns

## Related Tasks

- task-403: Core telemetry module (implemented)
- task-405: Event integration (implemented)
- task-406: CLI feedback prompt implementation (future)
- task-407: CLI viewer implementation (future)
