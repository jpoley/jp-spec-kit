# Task-6 Testing Guide: /flow:tasks Command Update

## Quick Start Testing

### Prerequisites
- jp-spec-kit installed and configured
- `specify` CLI available in PATH
- Claude Code with access to slash commands

### Test 1: Basic Task Generation (Recommended First Test)

**Setup:**
```bash
# Create a test feature directory
mkdir -p /tmp/jp-spec-test-feature
cd /tmp/jp-spec-test-feature

# Create minimal spec.md
cat > spec.md << 'EOF'
# User Authentication Feature

## User Story 1: User Registration
**Priority**: P1
**As a** new user
**I want to** register an account
**So that** I can access the application

## User Story 2: User Login
**Priority**: P1
**As a** registered user
**I want to** log in with my credentials
**So that** I can access my account
EOF

# Create minimal plan.md
cat > plan.md << 'EOF'
# User Authentication - Implementation Plan

## Feature Name
User Authentication System

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- bcrypt

## Project Structure
```
src/
  models/
    user.py
  services/
    auth_service.py
  api/
    auth.py
tests/
  test_auth.py
```

## Libraries
- fastapi - Web framework
- sqlalchemy - ORM
- pydantic - Data validation
- bcrypt - Password hashing
EOF
```

**Execute:**
```bash
# Open Claude Code in this directory
cd /tmp/jp-spec-test-feature

# Run the slash command
/flow:tasks
```

**Expected AI Workflow:**
1. AI runs `scripts/bash/check-prerequisites.sh --json` to get FEATURE_DIR
2. AI reads spec.md and plan.md
3. AI generates tasks.md with checklist format
4. AI runs `specify tasks generate --source /tmp/jp-spec-test-feature`
5. AI reports both output paths and statistics

**Verify Output:**
```bash
# Check intermediate tasks.md exists
ls -lh tasks.md

# Check tasks.md format (should have checklist format)
grep -E "^- \[ \] T[0-9]{3}" tasks.md

# Check backlog directory created
ls -la backlog/

# Check individual task files created
ls -la backlog/tasks/

# Count task files
ls backlog/tasks/*.md | wc -l

# Inspect a task file
cat backlog/tasks/task-001*.md
```

**Expected Results:**
- ✅ `tasks.md` exists with checklist format tasks
- ✅ `backlog/tasks/` directory contains individual task files
- ✅ Each task file has YAML frontmatter
- ✅ Task IDs are sequential (task-001, task-002, etc.)
- ✅ Labels include user story tags (US1, US2)
- ✅ File paths are preserved in task descriptions

### Test 2: Verify Task Format Compliance

**Command:**
```bash
cd /tmp/jp-spec-test-feature

# Check all tasks have proper format
for file in backlog/tasks/*.md; do
  echo "=== $file ==="
  head -20 "$file"
  echo ""
done
```

**Validate Each Task Has:**
- ✅ YAML frontmatter with `---` delimiters
- ✅ `id: task-NNN` field
- ✅ `title: ...` field
- ✅ `status: To Do` field (or other valid status)
- ✅ `assignee: []` field (can be empty)
- ✅ `created_date: 'YYYY-MM-DD HH:MM'` field
- ✅ `labels: [...]` field (array of labels)
- ✅ `dependencies: [...]` field (array of task IDs)
- ✅ Markdown body with task description

### Test 3: Dependency Graph Validation

**Command:**
```bash
cd /tmp/jp-spec-test-feature

# Run with dry-run to see dependency analysis
specify tasks generate --source . --dry-run
```

**Expected Output:**
```
Source: /tmp/jp-spec-test-feature
Output: /tmp/jp-spec-test-feature/backlog
Format: backlog
DRY RUN MODE - No files will be created

Tasks Parsed         10
User Stories         2

Tasks by Phase:
  Phase 1: Setup        2 tasks
  Phase 2: Foundational 1 tasks
  Phase 3: User Story 1 3 tasks
  Phase 4: User Story 2 3 tasks
  Final Phase           1 tasks

Tasks by Story:
  No Story              3 tasks
  US1                   3 tasks
  US2                   3 tasks
  US3                   1 tasks

Execution Order: T001, T002, T003... (10 total)

Parallel Batches: 4
Critical Path Length: 7
```

### Test 4: Error Handling

**Test 4a: Missing spec.md**
```bash
mkdir -p /tmp/jp-spec-test-empty
cd /tmp/jp-spec-test-empty

# Try to generate without spec.md
specify tasks generate --source .
```

**Expected:** Error message about missing spec.md or tasks.md

**Test 4b: Invalid tasks.md format**
```bash
mkdir -p /tmp/jp-spec-test-invalid
cd /tmp/jp-spec-test-invalid

# Create invalid tasks.md
cat > tasks.md << 'EOF'
# Tasks

- Create something (missing checkbox, ID, etc.)
- [ ] Do another thing (missing task ID)
EOF

# Try to generate
specify tasks generate --source .
```

**Expected:** Validation errors about task format

**Test 4c: File conflicts**
```bash
cd /tmp/jp-spec-test-feature

# Generate once (should succeed)
specify tasks generate --source .

# Try to generate again without --overwrite (should skip existing)
specify tasks generate --source .

# Generate with --overwrite (should succeed)
specify tasks generate --source . --overwrite
```

## Integration Testing Scenarios

### Scenario 1: Real Feature Spec

Use an actual feature specification from your project:

```bash
# Navigate to a real feature directory
cd ~/projects/my-app/.specify/features/my-feature

# Run the slash command
/flow:tasks
```

### Scenario 2: Complex Dependencies

Test with a spec that has multiple interdependent user stories:

```bash
# Create spec with dependencies
cat > spec.md << 'EOF'
## User Story 1: Database Setup
Priority: P1
Dependencies: None

## User Story 2: User Model
Priority: P1
Dependencies: User Story 1

## User Story 3: Authentication API
Priority: P1
Dependencies: User Story 2

## User Story 4: Frontend Login
Priority: P2
Dependencies: User Story 3
EOF

# Generate tasks
/flow:tasks

# Verify dependencies in task files
grep -r "dependencies:" backlog/tasks/
```

### Scenario 3: Parallel Tasks

Test parallelizable task detection:

```bash
# Create spec with independent features
cat > spec.md << 'EOF'
## User Story 1: User Profile
Independent feature A

## User Story 2: Shopping Cart
Independent feature B (no dependency on US1)
EOF

# Generate and check for [P] markers
/flow:tasks

# Check tasks.md for parallelizable markers
grep "\[P\]" tasks.md
```

## Validation Checklist

After running tests, verify:

### ✅ File Structure
- [ ] `tasks.md` exists in feature directory
- [ ] `backlog/` directory exists
- [ ] `backlog/tasks/` directory contains task files
- [ ] `backlog/config.yml` exists
- [ ] Task filenames follow pattern: `task-NNN - Title.md`

### ✅ Task Format
- [ ] All tasks have valid YAML frontmatter
- [ ] Task IDs are sequential (task-001, task-002, ...)
- [ ] User story labels preserved (US1, US2, ...)
- [ ] Parallelizable markers converted to labels
- [ ] File paths included in descriptions
- [ ] Phase information preserved

### ✅ Metadata Preservation
- [ ] Priority labels (P0, P1, P2) preserved
- [ ] Dependencies correctly inferred and set
- [ ] Labels include appropriate tags (setup, implementation, etc.)
- [ ] Created dates are valid

### ✅ Dependency Graph
- [ ] Setup tasks have no dependencies
- [ ] Foundational tasks depend on setup
- [ ] User story tasks depend on foundational
- [ ] Cross-story dependencies detected
- [ ] No circular dependencies

### ✅ Command Integration
- [ ] `specify tasks generate` command works
- [ ] `--dry-run` flag shows preview
- [ ] `--overwrite` flag works correctly
- [ ] `--source` flag accepts both files and directories
- [ ] Error messages are clear and helpful

### ✅ Backward Compatibility
- [ ] Original tasks.md format still generated
- [ ] Can use tasks.md for reference
- [ ] Backlog.md format is additive, not replacing

## Troubleshooting

### Issue: "No tasks found in file"
**Solution:** Check that tasks.md follows the correct format:
```
- [ ] T001 Task description with file path
```

### Issue: "Invalid dependency graph"
**Solution:** Check for circular dependencies or invalid task IDs in dependencies field

### Issue: "Task file already exists"
**Solution:** Use `--overwrite` flag or delete existing backlog directory

### Issue: specify command not found
**Solution:** Install jp-spec-kit CLI:
```bash
uv tool install /home/jpoley/ps/jp-spec-kit --force
```

## Performance Testing

### Test with Large Task Sets

```bash
# Create a spec with many user stories
python3 << 'EOF'
with open('spec.md', 'w') as f:
    f.write('# Large Feature Spec\n\n')
    for i in range(1, 21):  # 20 user stories
        f.write(f'## User Story {i}: Feature {i}\n')
        f.write(f'Priority: P{(i-1)//5}\n')
        f.write(f'As a user, I want feature {i}\n\n')
EOF

# Generate tasks
time specify tasks generate --source .

# Check task count
ls backlog/tasks/*.md | wc -l
```

**Expected:** Should handle 50+ tasks efficiently (< 5 seconds)

## Reporting Results

After testing, report:

1. **Success Rate**: X/Y tests passed
2. **Issues Found**: List any problems or bugs
3. **Performance**: Time to generate tasks for different sizes
4. **Usability**: Feedback on command clarity and output
5. **Edge Cases**: Any scenarios that need special handling

## Next Steps After Testing

1. ✅ If all tests pass → Mark task-6 as complete
2. ⚠️ If issues found → Document and fix before completion
3. 📝 Update main documentation with new workflow
4. 🧪 Create automated tests (task-7)
