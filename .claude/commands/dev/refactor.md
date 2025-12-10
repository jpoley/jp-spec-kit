---
description: Code refactoring guidance for improving code quality and maintainability.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command provides guidance for refactoring code to improve quality, maintainability, and performance while preserving functionality.

### Refactoring Principles

1. **Preserve Behavior**: Refactoring should not change external behavior
2. **Small Steps**: Make incremental changes, test frequently
3. **Have Tests**: Ensure tests exist before refactoring
4. **One Thing at a Time**: Focus on single improvement per commit
5. **Use Version Control**: Commit frequently, easy to revert

### Common Refactoring Patterns

**Extract Function**:
```python
# Before: Long function with multiple responsibilities
def process_order(order):
    # Validate order (10 lines)
    # Calculate total (15 lines)
    # Apply discounts (20 lines)
    # Process payment (25 lines)
    # Send confirmation (10 lines)

# After: Extracted functions
def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    total = apply_discounts(total, order)
    process_payment(total, order)
    send_confirmation(order)
```

**Extract Variable**:
```python
# Before: Complex expression
if (order.items > 0 and order.total > 100 and
    order.customer.is_premium and order.discount == 0):

# After: Named variable
is_eligible_for_discount = (
    order.items > 0 and
    order.total > 100 and
    order.customer.is_premium and
    order.discount == 0
)
if is_eligible_for_discount:
```

**Replace Magic Numbers**:
```python
# Before: Magic numbers
if user.age > 18 and user.age < 65:

# After: Named constants
ADULT_AGE = 18
RETIREMENT_AGE = 65
if ADULT_AGE < user.age < RETIREMENT_AGE:
```

**Consolidate Conditionals**:
```python
# Before: Multiple similar conditions
if status == 'pending':
    return True
if status == 'processing':
    return True
if status == 'review':
    return True
return False

# After: Consolidated
ACTIVE_STATUSES = {'pending', 'processing', 'review'}
return status in ACTIVE_STATUSES
```

**Replace Conditional with Polymorphism**:
```python
# Before: Type checking
def calculate_area(shape):
    if shape.type == 'circle':
        return math.pi * shape.radius ** 2
    elif shape.type == 'rectangle':
        return shape.width * shape.height
    elif shape.type == 'triangle':
        return 0.5 * shape.base * shape.height

# After: Polymorphism
class Circle:
    def area(self):
        return math.pi * self.radius ** 2

class Rectangle:
    def area(self):
        return self.width * self.height

class Triangle:
    def area(self):
        return 0.5 * self.base * self.height
```

### Refactoring Workflow

1. **Identify Code Smells**
   - Duplicated code
   - Long functions/classes
   - Complex conditionals
   - Poor naming
   - Too many parameters

2. **Prioritize Changes**
   - High-impact, low-risk first
   - Focus on pain points
   - Consider team velocity

3. **Plan Refactoring**
   - What pattern to apply
   - What tests are needed
   - How to break into steps

4. **Execute Refactoring**
   - Make one change
   - Run tests
   - Commit
   - Repeat

5. **Verify Improvement**
   - Code is more readable
   - Tests still pass
   - No new bugs introduced
   - Easier to maintain

### Code Smells and Fixes

| Smell | Fix |
|-------|-----|
| Duplicated code | Extract function/class |
| Long function | Extract functions, simplify logic |
| Long parameter list | Introduce parameter object |
| Divergent change | Split class |
| Feature envy | Move method |
| Data clumps | Introduce parameter object |
| Primitive obsession | Create domain classes |
| Large class | Extract class |
| Switch statements | Replace with polymorphism |
| Lazy class | Inline or remove |
| Speculative generality | Remove unused abstraction |
| Temporary field | Extract class |
| Message chains | Hide delegate |
| Middle man | Remove middle man |
| Inappropriate intimacy | Move or extract method |
| Comments | Extract method (code should be self-documenting) |

### Testing During Refactoring

```bash
# Run tests after each change
pytest tests/ -x  # Stop on first failure

# Run specific test file
pytest tests/test_orders.py -v

# Check coverage
pytest tests/ --cov=src --cov-report=html

# Run linter
ruff check .

# Format code
ruff format .
```

### Refactoring Checklist

Before refactoring:
- [ ] Tests exist and pass
- [ ] Code is committed to version control
- [ ] Understand the code's purpose
- [ ] Identify specific smell/issue
- [ ] Plan refactoring approach

During refactoring:
- [ ] Make small, incremental changes
- [ ] Run tests after each change
- [ ] Commit frequently
- [ ] Keep code working at all times

After refactoring:
- [ ] All tests still pass
- [ ] Code is more readable
- [ ] Functionality unchanged
- [ ] No new issues introduced
- [ ] Update documentation if needed

### Best Practices

1. **Have a Safety Net**: Comprehensive tests before refactoring
2. **Refactor Separately**: Don't mix with feature work
3. **Stay Focused**: One improvement at a time
4. **Know When to Stop**: Don't over-engineer
5. **Get Reviews**: Pair programming or code review
6. **Document Why**: Explain reasoning in commits

## Related Commands

- `/dev:build` - Implementation
- `/dev:debug` - Debugging assistance
- `/qa:review` - Code review
- `/arch:decide` - Architectural decisions
