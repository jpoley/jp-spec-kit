---
description: Debugging assistance for troubleshooting issues and errors.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command provides systematic debugging assistance for troubleshooting code issues, errors, and unexpected behavior.

### Debugging Workflow

1. **Reproduce the Issue**
   - Understand the expected behavior
   - Identify the actual behavior
   - Find minimal reproduction steps

2. **Gather Information**
   - Error messages and stack traces
   - Logs and console output
   - Input data that triggers the issue
   - Environment details (OS, versions, config)

3. **Hypothesis Formation**
   - What could cause this behavior?
   - What are the most likely culprits?
   - What assumptions might be wrong?

4. **Systematic Investigation**
   - Use binary search to narrow down location
   - Add logging/debugging statements
   - Test hypotheses one at a time
   - Eliminate possibilities systematically

5. **Root Cause Identification**
   - Identify the exact source of the issue
   - Understand why it occurs
   - Verify the diagnosis

6. **Fix and Verify**
   - Implement the fix
   - Test the fix works
   - Ensure no regressions
   - Add tests to prevent recurrence

### Common Debugging Techniques

**Logging**:
```python
# Add strategic log statements
import logging
logging.debug(f"Variable state: {var}")
logging.info(f"Entering function with args: {args}")
```

**Print Debugging**:
```python
# Quick diagnostic prints
print(f"DEBUG: Expected {expected}, got {actual}")
```

**Debugger**:
```python
# Use breakpoints
import pdb; pdb.set_trace()  # Python
# Or use IDE debugger with breakpoints
```

**Binary Search**:
- Comment out half the code
- If issue persists, it's in remaining half
- Repeat until isolated

**Rubber Duck Debugging**:
- Explain the problem out loud
- Walk through code line by line
- Often reveals the issue

### Error Analysis

**Read Stack Traces**:
- Start at the bottom (root cause)
- Work up to understand call chain
- Look for your code (not library code)

**Google the Error**:
- Copy exact error message
- Add language/framework name
- Look for similar issues

**Check Recent Changes**:
- What changed since it last worked?
- Use git diff to see changes
- Try reverting recent commits

### Common Issue Patterns

**Null/None/Undefined**:
- Add null checks
- Verify data exists
- Check initialization

**Type Mismatches**:
- Verify data types
- Check implicit conversions
- Add type validation

**Async/Timing Issues**:
- Check promise/await usage
- Verify callback order
- Look for race conditions

**State Issues**:
- Check initialization
- Verify state updates
- Look for shared state

### Debugging Commands

```bash
# View logs
tail -f logs/app.log

# Check process status
ps aux | grep your-app

# Network debugging
curl -v https://api.example.com/endpoint

# Database debugging
# Check query execution plans
EXPLAIN ANALYZE SELECT ...

# Environment debugging
env | grep APP_

# Dependency debugging
npm list | grep package-name
pip show package-name
```

### Documentation

After resolving the issue:
- Document the root cause
- Add comments explaining the fix
- Update relevant documentation
- Create tests to prevent recurrence
- Share learnings with team

## Related Commands

- `/dev:build` - Implementation and coding
- `/dev:refactor` - Code improvement
- `/qa:test` - Testing and verification
