# Workflow Troubleshooting Guide

This guide provides solutions for common issues when working with Flowspec workflow configuration.

## Quick Diagnostics

Before troubleshooting specific errors, run these diagnostic commands:

```bash
# 1. Check workflow configuration validity
flowspec workflow validate

# 2. Check current task state
backlog task view task-123

# 3. Check which workflows are valid for current state
# (This information is in flowspec_workflow.yml)
cat flowspec_workflow.yml | grep -A 3 "input_states.*Planned"

# 4. Verify flowspec_workflow.yml exists
ls -la flowspec_workflow.yml

# 5. Check YAML syntax
python -c "import yaml; yaml.safe_load(open('flowspec_workflow.yml'))"
```

## Configuration Issues

### Error: "flowspec_workflow.yml not found"

**Symptom**:
```
[ERROR] WorkflowConfigNotFoundError: flowspec_workflow.yml not found
Searched locations:
  - /home/user/project/flowspec_workflow.yml
  - /home/user/project/memory/flowspec_workflow.yml
  - /home/user/project/.specify/flowspec_workflow.yml
```

**Causes**:
1. Configuration file missing
2. Working in wrong directory
3. File named incorrectly (e.g., `flowspec-workflow.yml` instead of `flowspec_workflow.yml`)

**Solutions**:

**Solution 1: Create default configuration**
```bash
# Copy from Flowspec templates
cp ~/.local/share/flowspec-cli/templates/flowspec_workflow.yml ./flowspec_workflow.yml

# Or create in memory/ directory
mkdir -p memory
cp ~/.local/share/flowspec-cli/templates/flowspec_workflow.yml memory/flowspec_workflow.yml
```

**Solution 2: Check current directory**
```bash
# Ensure you're in project root
pwd
# Should be: /path/to/your/project

# If not, navigate to project root
cd /path/to/your/project
```

**Solution 3: Check filename**
```bash
# Look for incorrectly named files
ls -la | grep -i workflow

# Rename if found
mv flowspec-workflow.yml flowspec_workflow.yml
```

---

### Error: "Configuration validation errors"

**Symptom**:
```
[ERROR] WorkflowConfigValidationError: Workflow config validation failed
Errors:
  - states: 'To Do' is a required property
  - workflows.implement.output_state: 'Implemented' is not one of ['To Do', 'Specified', ...]
```

**Causes**:
1. Invalid YAML syntax
2. Missing required fields
3. State name typos
4. Schema version mismatch

**Solutions**:

**Solution 1: Check YAML syntax**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('flowspec_workflow.yml'))"

# Common YAML errors:
# - Inconsistent indentation (use spaces, not tabs)
# - Missing colons after keys
# - Unquoted strings with special characters
```

**Solution 2: Verify required fields**
```yaml
# Required top-level fields
version: "1.1"

states:
  - "To Do"  # Required
  - "Done"   # Required
  # ... other states

workflows:
  # At least one workflow required

transitions:
  # At least one transition required
```

**Solution 3: Fix state name typos**
```bash
# Find all state references
grep -n "output_state\|input_states" flowspec_workflow.yml

# Verify state names match states list exactly (case-sensitive)
grep -A 20 "^states:" flowspec_workflow.yml
```

**Solution 4: Check schema version**
```yaml
# Ensure version matches Flowspec's expected version
version: "1.1"  # Current version
```

---

### Error: "State transition errors"

**Symptom**:
```
[ERROR] Cannot execute 'implement' from state 'Specified'.
Valid input states: ['Planned']
```

**Causes**:
1. Trying to run workflow from wrong state
2. Missing intermediate workflow step
3. Incorrect workflow customization

**Solutions**:

**Solution 1: Check current state and run correct workflow**
```bash
# View current task state
backlog task view task-123

# If state is "Specified", run planning first
/flow:plan
# Then run implementation
/flow:implement
```

**Solution 2: Check workflow sequence**
```yaml
# Verify input_states in flowspec_workflow.yml
workflows:
  implement:
    input_states: ["Planned"]  # implement requires "Planned" state
    output_state: "In Implementation"
```

**Solution 3: Manually change state (if necessary)**
```bash
# Only if you're certain this is correct
backlog task edit task-123 -s "Planned" \
  --notes "Manual state change: Planning was done outside workflow"
```

---

### Error: "Circular dependencies detected"

**Symptom**:
```
[ERROR] CYCLE_DETECTED: Cycle detected in state transitions: Planned -> In Implementation -> Planned.
Workflows must be acyclic (DAG).
```

**Causes**:
1. Rework transitions create a cycle
2. Invalid custom workflow configuration
3. Multiple paths creating unintended cycle

**Solutions**:

**Solution 1: Review transition graph**
```bash
# Extract all transitions
grep -A 5 "^  - name:" flowspec_workflow.yml | grep -E "from:|to:|via:"

# Look for cycles:
# from: A, to: B
# from: B, to: C
# from: C, to: A  <- Cycle!
```

**Solution 2: Use "rework" via, not separate transition**
```yaml
# Correct: Rework transitions are allowed
transitions:
  - name: "rework_to_planned"
    from: "In Implementation"
    to: "Planned"
    via: "rework"  # Special "rework" via allows backward transition

# Incorrect: Regular workflow creating cycle
transitions:
  - name: "plan"
    from: "In Implementation"
    to: "Planned"
    via: "plan"  # This creates an invalid cycle
```

**Solution 3: Remove or fix circular transition**
```bash
# Edit flowspec_workflow.yml
vim flowspec_workflow.yml

# Remove the transition creating the cycle
# Or change it to use via: "rework"

# Validate
flowspec workflow validate
```

---

### Error: "Unreachable states"

**Symptom**:
```
[ERROR] UNREACHABLE_STATE: State 'Security Audited' is not reachable from initial state 'To Do'.
Add a transition path or remove this state.
```

**Causes**:
1. Added custom state but no transitions to it
2. Deleted workflow but kept state
3. Misconfigured transitions

**Solutions**:

**Solution 1: Add missing transition**
```yaml
# Ensure there's a path from an existing state to the unreachable state
states:
  - "Validated"
  - "Security Audited"  # Unreachable

workflows:
  security-audit:
    input_states: ["Validated"]  # Add this
    output_state: "Security Audited"

transitions:
  - name: "security_audit"
    from: "Validated"
    to: "Security Audited"
    via: "security-audit"  # Add this transition
```

**Solution 2: Remove unused state**
```yaml
# If state is not needed, remove it
states:
  - "Validated"
  # Remove "Security Audited" if not used
  - "Deployed"
```

**Solution 3: Check complete path from "To Do"**
```
To Do → Assessed → Specified → Planned → ... → Security Audited
                                                 ^
                                                 Must have complete path
```

---

## Runtime Issues

### Error: "Agent not found"

**Symptom**:
```
[WARNING] UNKNOWN_AGENT: Workflow 'implement' references unknown agent 'custom-engineer'.
This may be a custom agent or typo.
```

**Causes**:
1. Typo in agent name
2. Custom agent not defined
3. Agent definition file missing

**Solutions**:

**Solution 1: Fix typo**
```yaml
# Check agent name spelling
workflows:
  implement:
    agents:
      - name: "frontend-engineer"  # Correct
      # Not: "frontend-enigneer" (typo)
```

**Solution 2: Create custom agent definition**
```bash
# Create .agents/ directory
mkdir -p .agents

# Create agent definition
cat > .agents/custom-engineer.md <<EOF
# Custom Engineer Agent

## Identity
@custom-engineer

## Description
Custom engineering role

## Responsibilities
- Custom engineering tasks
EOF
```

**Solution 3: Use known agent names**
```bash
# Check known agents in validator.py
grep -A 30 "KNOWN_AGENTS" src/specify_cli/workflow/validator.py

# Use agents from this list, or accept the warning for custom agents
```

---

### Error: "Invalid input state for workflow"

**Symptom**:
```
[ERROR] WorkflowStateError: Cannot execute 'validate' from state 'Planned'.
Valid input states: ['In Implementation']
```

**Causes**:
1. Skipped a workflow step
2. Task state manually changed incorrectly
3. Workflow customization error

**Solutions**:

**Solution 1: Run missing workflow step**
```bash
# Check what workflow should run from current state
cat flowspec_workflow.yml | grep -B 5 "input_states.*Planned"

# Run the correct workflow
/flow:implement  # Moves from Planned → In Implementation
/flow:validate   # Now this will work
```

**Solution 2: Check task state is correct**
```bash
# Verify current state
backlog task view task-123

# If state is wrong, fix it
backlog task edit task-123 -s "In Implementation"
```

**Solution 3: Verify workflow configuration**
```yaml
# Check if input_states matches expected progression
workflows:
  validate:
    input_states: ["In Implementation"]  # Must be in this state

# If you want validate to accept "Planned", add it:
workflows:
  validate:
    input_states: ["Planned", "In Implementation"]
```

---

## Customization Issues

### Error: "Custom workflow not working"

**Symptom**:
- Custom workflow doesn't appear in `/flow:` commands
- Custom state not available in backlog
- Transitions not working as expected

**Causes**:
1. Workflow not properly defined
2. Missing transitions
3. Configuration not reloaded

**Solutions**:

**Solution 1: Verify workflow definition**
```yaml
# Complete workflow definition required
workflows:
  my-custom-workflow:
    command: "/flow:my-custom-workflow"  # Required
    description: "Custom workflow description"  # Required
    agents:  # Required (at least one)
      - name: "custom-agent"
        identity: "@custom-agent"
        description: "Custom agent"
        responsibilities:
          - "Custom responsibility"
    input_states: ["Previous State"]  # Required
    output_state: "Next State"  # Required
```

**Solution 2: Add transitions**
```yaml
# Workflow alone is not enough - need transitions
transitions:
  - name: "my_custom_transition"
    from: "Previous State"
    to: "Next State"
    via: "my-custom-workflow"  # Must match workflow name
    description: "Custom transition"
    validation: "NONE"
```

**Solution 3: Reload configuration**
```bash
# Restart Claude Code to reload configuration
# Or use reload command if available
flowspec workflow validate --reload

# Verify changes are reflected
flowspec workflow validate
```

---

### Error: "Performance issues with workflow config"

**Symptom**:
- Slow `/flowspec` command execution
- Long delays when checking states
- High memory usage

**Causes**:
1. Very large workflow configuration (50+ states, 100+ transitions)
2. Circular dependencies causing infinite loops
3. Complex validation logic

**Solutions**:

**Solution 1: Simplify workflow**
```yaml
# Remove unused states
states:
  - "To Do"
  - "Specified"
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Done"
  # Remove intermediate states if not needed

# Combine workflows
# Instead of: specify → plan → design → implement
# Use: specify → plan → implement
```

**Solution 2: Fix circular dependencies**
```bash
# Check for cycles
flowspec workflow validate

# Remove circular transitions
# Use "rework" via for backward transitions only
```

**Solution 3: Optimize agent assignments**
```yaml
# Reduce agent count per workflow if possible
workflows:
  implement:
    agents:
      - name: "full-stack-engineer"  # One agent instead of 5
    # Instead of: frontend, backend, reviewer1, reviewer2, architect
```

---

## Validation Command Issues

### Error: "flowspec workflow validate fails"

**Symptom**:
```bash
flowspec workflow validate
# Command not found or fails
```

**Causes**:
1. Flowspec not installed
2. Old version without workflow commands
3. Path issue

**Solutions**:

**Solution 1: Install/update Flowspec**
```bash
# Install latest version
uv tool install . --force

# Verify installation
flowspec --version

# Should be v0.0.136 or later for workflow support
```

**Solution 2: Check PATH**
```bash
# Verify specify is in PATH
which specify

# If not found, add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use full path
~/.local/bin/flowspec workflow validate
```

**Solution 3: Run validation manually**
```bash
# Fallback: Validate YAML syntax manually
python -c "
import yaml
import sys

try:
    config = yaml.safe_load(open('flowspec_workflow.yml'))
    assert 'states' in config
    assert 'workflows' in config
    assert 'transitions' in config
    print('✓ Configuration structure valid')
except Exception as e:
    print(f'✗ Validation failed: {e}')
    sys.exit(1)
"
```

---

## Recovery and Rollback

### Rolling Back Configuration Changes

**If workflow changes cause issues:**

**Step 1: Check Git history**
```bash
# See recent changes to workflow config
git log --oneline flowspec_workflow.yml

# View specific change
git show <commit-hash>:flowspec_workflow.yml
```

**Step 2: Restore previous version**
```bash
# Restore from Git
git checkout HEAD~1 flowspec_workflow.yml

# Or restore from specific commit
git checkout <commit-hash> flowspec_workflow.yml

# Verify
flowspec workflow validate
```

**Step 3: Create backup before changes**
```bash
# Always backup before editing
cp flowspec_workflow.yml flowspec_workflow.yml.backup.$(date +%Y%m%d_%H%M%S)

# Edit safely
vim flowspec_workflow.yml

# If issues occur, restore
cp flowspec_workflow.yml.backup.* flowspec_workflow.yml
```

---

### Emergency: Reset to Default Configuration

**If configuration is completely broken:**

```bash
# 1. Backup current config (just in case)
mv flowspec_workflow.yml flowspec_workflow.yml.broken

# 2. Copy default configuration
cp ~/.local/share/flowspec-cli/templates/flowspec_workflow.yml ./flowspec_workflow.yml

# Or from project templates
cp flowspec_workflow.yml

# 3. Verify default works
flowspec workflow validate

# 4. Gradually re-add customizations from broken config
diff flowspec_workflow.yml.broken flowspec_workflow.yml
```

---

## Prevention Best Practices

### 1. Always Validate Before Committing

```bash
# Pre-commit checklist
vim flowspec_workflow.yml
flowspec workflow validate
git add flowspec_workflow.yml
git commit -s -m "feat(workflow): add custom phase"
```

### 2. Version Control Workflow Changes

```bash
# Commit workflow changes separately
git add flowspec_workflow.yml
git commit -s -m "feat(workflow): add security audit phase

- Add Security Audited state
- Add security-audit workflow
- Update transitions"

# Don't mix workflow changes with code changes
```

### 3. Test Customizations on Non-Critical Tasks

```bash
# Create test task
backlog task create "Test custom workflow"

# Run through custom workflow
/flow:custom-workflow

# Verify it works before using on real features
```

### 4. Document Customizations

```yaml
# Add comments explaining custom phases
workflows:
  security-audit:
    # CUSTOM: Required for SOC2 compliance
    # Added: 2025-12-01
    # Owner: Security Team
    command: "/flow:security-audit"
    # ...
```

### 5. Keep Workflow Simple

- Start with default configuration
- Add one customization at a time
- Test after each change
- Remove unused states/workflows
- Avoid complex state graphs (keep it DAG)

---

## Getting Help

### 1. Check Documentation

- [Workflow State Mapping](./workflow-state-mapping.md)
- [Workflow Customization Guide](./workflow-customization.md)
- [Workflow Architecture](./workflow-architecture.md)
- [Configuration Examples](../examples/workflows/)

### 2. Check Existing Configurations

```bash
# Compare to working examples
diff flowspec_workflow.yml docs/examples/workflows/minimal-workflow.yml

# Learn from other examples
ls docs/examples/workflows/
cat docs/examples/workflows/security-audit-workflow.yml
```

### 3. Enable Debug Logging

```bash
# If available, enable verbose output
export SPECIFY_DEBUG=1
flowspec workflow validate

# Check for detailed error messages
```

### 4. Report Issues

If none of these solutions work:

1. Create minimal reproduction:
   ```bash
   # Simplify flowspec_workflow.yml to smallest failing case
   # Share anonymized version
   ```

2. Include diagnostic output:
   ```bash
   flowspec workflow validate > workflow-debug.txt 2>&1
   ```

3. Report via GitHub Issues with:
   - Error message
   - Minimal flowspec_workflow.yml
   - Flowspec version (`flowspec --version`)
   - Steps to reproduce

---

## Summary

**Most Common Issues**:
1. **Config not found** → Create `flowspec_workflow.yml` in project root
2. **State transition error** → Run workflows in correct sequence
3. **Circular dependencies** → Use `via: "rework"` for backward transitions
4. **Unreachable states** → Add transitions or remove unused states
5. **Unknown agents** → Accept warning or define custom agents

**Quick Fixes**:
- Run `flowspec workflow validate` to diagnose
- Check current task state with `backlog task view`
- Verify workflow sequence matches configuration
- Restore from Git if changes cause issues
- Reset to default config if completely broken

**Prevention**:
- Always validate before committing
- Test on non-critical tasks first
- Keep configurations simple
- Document custom changes
- Version control all modifications
