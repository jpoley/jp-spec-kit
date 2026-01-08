# Constitution Pre-flight Check

**CRITICAL**: This command requires constitution validation before execution (unless `--skip-validation` is provided).

## Step 0.5: Check Constitution Status

Before executing this workflow command, validate the project's constitution:

### 1. Check Constitution Exists

```bash
# Look for constitution file
if [ -f "memory/constitution.md" ]; then
  echo "[Y] Constitution found"
else
  echo "⚠️ No constitution found"
  echo ""
  echo "To create one:"
  echo "  1. Run: flowspec init --here"
  echo "  2. Then: Edit memory/constitution.md to customize"
  echo ""
  echo "Proceeding without constitution..."
fi
```

If no constitution exists:
- Warn the user
- Suggest creating one with `flowspec init --here`
- Continue with command (constitution is recommended but not required)

### 2. If Constitution Exists, Check Validation Status

```bash
# Detect tier from TIER comment (default: Medium if not found)
TIER=$(grep -o "TIER: \(Light\|Medium\|Heavy\)" memory/constitution.md | cut -d' ' -f2)
TIER=${TIER:-Medium}  # Default to Medium if not found

# Count NEEDS_VALIDATION markers
MARKER_COUNT=$(grep -c "NEEDS_VALIDATION" memory/constitution.md || echo 0)

# Extract section names from NEEDS_VALIDATION markers
SECTIONS=$(grep "NEEDS_VALIDATION" memory/constitution.md | sed 's/.*NEEDS_VALIDATION: /  - /')

echo "Constitution tier: $TIER"
echo "Unvalidated sections: $MARKER_COUNT"
```

### 3. Apply Tier-Based Enforcement

#### Light Tier - Warn Only

If `TIER = Light` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution has N unvalidated sections:
$SECTIONS

Consider editing memory/constitution.md to customize your constitution.

Proceeding with command...
```

Then continue with the command.

#### Medium Tier - Warn and Confirm

If `TIER = Medium` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution Validation Recommended

Your constitution has N unvalidated sections:
$SECTIONS

Medium tier projects should validate their constitution before workflow commands.

Options:
  1. Continue anyway (y/N)
  2. Edit memory/constitution.md to customize
  3. Run flowspec constitution validate to check status

Continue without validation? [y/N]: _
```

Wait for user response:
- If user responds `y` or `yes` -> Continue with command
- If user responds `n`, `no`, or empty/Enter -> Stop and show:
  ```text
  Command cancelled. Edit memory/constitution.md to customize your constitution.
  ```

#### Heavy Tier - Block Until Validated

If `TIER = Heavy` and `MARKER_COUNT > 0`:

```text
[X] Constitution Validation Required

Your constitution has N unvalidated sections:
$SECTIONS

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Edit memory/constitution.md to customize your constitution
  2. Run flowspec constitution validate to verify
  3. Remove all NEEDS_VALIDATION markers

Or use --skip-validation to bypass (not recommended).

Command blocked until constitution is validated.
```

**DO NOT PROCEED** with the command. Exit and wait for user to resolve.

### 4. Skip Validation Flag

If the command was invoked with `--skip-validation`:

```bash
# Check for skip flag in arguments
if [[ "$ARGUMENTS" == *"--skip-validation"* ]]; then
  echo "⚠️ Skipping constitution validation (--skip-validation)"
  # Remove the flag from arguments and continue
  ARGUMENTS="${ARGUMENTS/--skip-validation/}"
fi
```

When skip flag is present:
- Log warning
- Skip all validation checks
- Continue with command
- Note: For emergency use only

### 5. Fully Validated Constitution

If `MARKER_COUNT = 0`:

```text
[Y] Constitution validated
```

Continue with command normally.

## Summary: When to Block vs Warn

| Tier | Unvalidated Sections | Action |
|------|---------------------|--------|
| Light | 0 | [Y] Continue |
| Light | >0 | ⚠️ Warn, continue |
| Medium | 0 | [Y] Continue |
| Medium | >0 | ⚠️ Warn, ask confirmation, respect user choice |
| Heavy | 0 | [Y] Continue |
| Heavy | >0 | [X] Block, require validation |
| Any | >0 + `--skip-validation` | ⚠️ Warn, continue |

## Integration Example

```markdown
---
description: Your command description
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

<!-- NOTE: INCLUDE directives do not work in Claude command files -->
<!-- Constitution check and workflow state validation are loaded via @import in CLAUDE.md -->

## Execution Instructions

[Rest of your command implementation...]
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `flowspec init --here` | Initialize constitution if missing |
| Edit `memory/constitution.md` | Direct constitution customization |
| `flowspec constitution validate` | Check validation status and show report |
| `flowspec constitution show` | Display current constitution |
