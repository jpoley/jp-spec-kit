# Migrating from tasks.md to Backlog.md

Complete guide for migrating existing Flowspec projects from tasks.md format to Backlog.md task management.

## Table of Contents

- [Why Migrate?](#why-migrate)
- [Before You Begin](#before-you-begin)
- [Migration Methods](#migration-methods)
- [Manual Migration](#manual-migration)
- [Automated Migration (Coming Soon)](#automated-migration-coming-soon)
- [Validation](#validation)
- [Rollback](#rollback)
- [FAQ](#faq)

## Why Migrate?

### tasks.md Limitations

**Static Checklist**:
- No status tracking beyond checked/unchecked
- No assignees or team collaboration
- No visual boards or progress tracking
- No AI integration capabilities

**Backlog.md Benefits**:
- ✅ Visual Kanban boards (terminal + web UI)
- ✅ Task lifecycle management (todo → in_progress → done)
- ✅ Team collaboration (assignees, labels, priorities)
- ✅ AI-powered task management via MCP
- ✅ Dependencies and blocking relationships
- ✅ Git-native (all data in repository)

### When to Migrate

**Recommended**:
- Starting a new feature with multiple user stories
- Working in a team that needs task assignment
- Using Claude Code or other AI assistants
- Wanting visual progress tracking

**Keep tasks.md**:
- Solo project with simple task list
- No need for status tracking or collaboration
- Prefer minimal tooling

## Before You Begin

### Prerequisites

- ✅ Backlog.md installed: `npm install -g backlog.md`
- ✅ Backlog initialized in project: `backlog init`
- ✅ Git repository clean (commit current work)
- ✅ Backup created (see below)

### Create Backup

```bash
# Backup entire specs directory
cp -r specs specs.backup

# Or backup specific feature
cp -r specs/001-auth-feature specs/001-auth-feature.backup

# Verify backup
ls -la specs.backup/
```

### Understand Your Current Structure

```bash
# View your tasks.md
cat specs/001-auth-feature/tasks.md

# Typical format:
# Phase 1: Setup
# - [ ] T001 Create project structure
# - [ ] T002 Initialize database
#
# Phase 2: User Story 1 (Login)
# - [ ] T012 [P] [US1] Create User model
# - [ ] T013 [US1] Implement login endpoint
```

## Migration Methods

### Method 1: Manual Migration (Recommended for Learning)

Best for: First migration, small projects (<50 tasks)

**Time**: 10-30 minutes for 20 tasks
**Pros**: Learn the structure, ensure quality
**Cons**: Time-consuming for large projects

### Method 2: Automated Migration (Coming Soon)

Best for: Large projects, multiple features

**Command** (future):
```bash
specify backlog migrate --feature 001-auth-feature
```

**Time**: <1 minute for any size
**Pros**: Fast, consistent, handles edge cases
**Cons**: Not yet available

## Manual Migration

### Step 1: Initialize Backlog.md

```bash
# Navigate to project
cd your-project

# Initialize if not already done
backlog init

# Verify backlog directory created
ls -la backlog/
```

### Step 2: Parse Your tasks.md

Open `specs/001-auth-feature/tasks.md` and identify:

1. **Phases**: Setup, Foundational, User Stories, Polish
2. **Task IDs**: T001, T012, etc.
3. **Markers**: [P] = parallelizable, [US1] = user story
4. **Status**: [ ] = todo, [x] = done

### Step 3: Create Backlog Tasks

For each task in tasks.md, create a Backlog task:

**Example tasks.md entry**:
```markdown
- [ ] T012 [P] [US1] Create User model in src/models/user.py
```

**Create Backlog task**:
```bash
# Method A: Using CLI
backlog task create "Create User model in src/models/user.py" \
  --labels "US1,parallelizable,implementation" \
  --status "To Do" \
  --priority "high"

# This creates: backlog/tasks/task-1-create-user-model-in-src-models-user-py.md

# Method B: Manually create file
cat > backlog/tasks/task-012-create-user-model.md <<'EOF'
---
status: todo
assignees: []
labels: [US1, parallelizable, implementation]
priority: high
dependencies: []
---

## Description
Create User model in src/models/user.py

## Implementation Details
- Define User schema with authentication fields
- Add password hashing with bcrypt
- Create database migration

## Acceptance Criteria
- [ ] User model includes email, password_hash, created_at
- [ ] Password hashing implemented
- [ ] Migration creates users table successfully
EOF
```

### Step 4: Map Task Metadata

**Task ID Mapping**:
```
T001 → task-001-*.md
T012 → task-012-*.md
T042 → task-042-*.md
```

**Status Mapping**:
```
tasks.md          → Backlog.md
- [ ] (unchecked) → status: todo
- [x] (checked)   → status: done
```

**Label Mapping**:
```
tasks.md    → Backlog.md labels
[P]         → parallelizable
[US1]       → US1
[US2]       → US2
Phase 1     → setup
Phase 2     → foundational
Phase 3+    → implementation
Last phase  → polish
```

**Priority Mapping**:
```
Phase         → Priority
Setup (P1)    → high
Foundational  → high
US1 (P0/P1)   → high
US2 (P2)      → medium
US3 (P3)      → low
Polish        → medium
```

### Step 5: Set Dependencies

**Rule 1**: Setup tasks have no dependencies

```yaml
# task-001-create-project-structure.md
dependencies: []
```

**Rule 2**: Foundational tasks depend on all setup tasks

```yaml
# task-005-database-schema.md
dependencies: [task-001, task-002, task-003]
```

**Rule 3**: User Story tasks depend on foundational tasks

```yaml
# task-012-user-model.md (US1)
dependencies: [task-005]  # Depends on database schema
```

**Rule 4**: Tasks within a user story depend on previous task (unless [P])

```yaml
# task-013-login-endpoint.md (US1, not parallelizable)
dependencies: [task-012]  # Depends on User model

# task-014-signup-endpoint.md (US1, marked [P])
dependencies: [task-005]  # Parallel to task-012, depends on foundational only
```

### Step 6: Migrate Completed Tasks

For tasks already checked off in tasks.md:

```bash
# Find completed tasks
grep "\[x\]" specs/001-auth-feature/tasks.md

# Example output:
# - [x] T001 Create project structure
# - [x] T005 Setup database schema

# Create with done status
backlog task create "Create project structure" \
  --status "Done" \
  --labels "setup"

backlog task create "Setup database schema" \
  --status "Done" \
  --labels "foundational"
```

### Step 7: Verify Migration

```bash
# View all tasks
backlog board

# Check task count
ls backlog/tasks/ | wc -l
# Should match number of tasks in tasks.md

# Verify user stories
backlog board --filter US1
backlog board --filter US2

# Check specific task
backlog task view task-012
```

### Step 8: Update tasks.md (Optional)

Add migration notice to tasks.md:

```bash
cat >> specs/001-auth-feature/tasks.md <<'EOF'

---

**Note**: Tasks migrated to Backlog.md on 2025-11-24
- View tasks: `backlog board`
- Manage tasks: `backlog browser`
- This file preserved for reference
EOF
```

Or deprecate entirely:

```bash
# Rename to indicate deprecated
mv specs/001-auth-feature/tasks.md specs/001-auth-feature/tasks.md.deprecated

# Create pointer file
cat > specs/001-auth-feature/tasks.md <<'EOF'
# Tasks Migrated to Backlog.md

Tasks for this feature are now managed in Backlog.md.

## View Tasks
```bash
backlog board --filter 001-auth-feature
backlog browser
```

## Original tasks.md
See `tasks.md.deprecated` for the original checklist.
EOF
```

## Automated Migration (Coming Soon)

**Future Command**:
```bash
specify backlog migrate --feature 001-auth-feature
```

**What It Will Do**:

1. **Parse tasks.md**:
   - Extract all tasks with IDs, descriptions, markers
   - Identify phases and user stories
   - Detect completed tasks (checked boxes)

2. **Generate Backlog Tasks**:
   - Create `backlog/tasks/task-*.md` files
   - Set status (todo/done) based on checkboxes
   - Apply labels from [US*] and [P] markers
   - Build dependency graph from phases

3. **Create Backup**:
   - Backup `tasks.md` to `tasks.md.backup`
   - Backup `backlog/` to `backlog.backup/` if exists

4. **Generate Report**:
   ```
   Migration Summary:
   ✅ Migrated 42 tasks
   ✅ 8 tasks marked as done
   ✅ 34 tasks marked as todo
   ✅ Dependencies created: 67
   ✅ Labels applied: US1 (15), US2 (12), US3 (10)
   ```

5. **Options**:
```bash
# Dry run (show what would happen)
specify backlog migrate --feature 001-auth --dry-run

# Keep tasks.md
specify backlog migrate --feature 001-auth --keep-tasks-md

# Force overwrite existing backlog
specify backlog migrate --feature 001-auth --force

# Migrate all features
specify backlog migrate --all
```

## Validation

### Checklist

After migration, verify:

- [ ] All tasks from tasks.md are in backlog/tasks/
- [ ] Task IDs match (T001 → task-001, etc.)
- [ ] Completed tasks have status: done
- [ ] User story labels applied (US1, US2, etc.)
- [ ] Parallelizable tasks have "parallelizable" label
- [ ] Dependencies set correctly
- [ ] Priorities assigned based on phase
- [ ] `backlog board` displays all tasks
- [ ] Filtering by user story works (`backlog board --filter US1`)

### Validation Commands

```bash
# Count tasks
echo "tasks.md tasks: $(grep -c '^\s*-\s*\[.\]' specs/001-auth-feature/tasks.md)"
echo "Backlog tasks: $(ls backlog/tasks/ | wc -l)"

# List completed tasks
echo "tasks.md done: $(grep -c '^\s*-\s*\[x\]' specs/001-auth-feature/tasks.md)"
echo "Backlog done: $(grep -r 'status: done' backlog/tasks/ | wc -l)"

# Check for specific user story
echo "tasks.md US1: $(grep -c '\[US1\]' specs/001-auth-feature/tasks.md)"
echo "Backlog US1: $(grep -r 'labels:.*US1' backlog/tasks/ | wc -l)"

# Verify no missing tasks
comm -3 \
  <(grep '^\s*-\s*\[.\]\s*T[0-9]' specs/001-auth-feature/tasks.md | sed 's/.*T\([0-9]\+\).*/\1/' | sort) \
  <(ls backlog/tasks/ | grep -o 'task-[0-9]\+' | sed 's/task-//' | sort)
# Should output nothing if all tasks migrated
```

### Visual Verification

```bash
# Open board
backlog board

# Check that:
# - All columns have tasks
# - User stories are separable by label
# - Dependencies make sense
# - No orphaned tasks

# Open web UI for detailed check
backlog browser
```

## Rollback

If migration fails or you want to revert:

### Rollback Steps

```bash
# 1. Remove Backlog tasks
rm -rf backlog/tasks/*

# 2. Restore tasks.md if modified
cp specs/001-auth-feature.backup/tasks.md specs/001-auth-feature/tasks.md

# 3. Restore backlog if it existed before
if [ -d backlog.backup ]; then
  rm -rf backlog/
  mv backlog.backup backlog/
fi

# 4. Verify git status
git status

# 5. Discard changes if needed
git checkout backlog/
git checkout specs/001-auth-feature/tasks.md
```

### Partial Rollback

Keep some migrated tasks, remove others:

```bash
# Remove specific tasks
rm backlog/tasks/task-012*.md
rm backlog/tasks/task-013*.md

# Or remove by label
for task in backlog/tasks/*; do
  if grep -q "labels:.*bug" "$task"; then
    rm "$task"
  fi
done
```

## FAQ

### Q: Do I have to migrate all features at once?

**A**: No! Migrate feature by feature. You can have some features using tasks.md and others using Backlog.md.

```bash
# Feature 001: Uses Backlog.md
specs/001-auth-feature/  (no tasks.md, uses backlog/)

# Feature 002: Still uses tasks.md
specs/002-api-feature/tasks.md
```

### Q: Can I go back to tasks.md after migrating?

**A**: Yes, but you'll lose Backlog.md benefits (status tracking, assignees, etc.). You can regenerate tasks.md from backlog:

```bash
# Extract task titles from backlog
for task in backlog/tasks/*.md; do
  TITLE=$(grep "^# " "$task" | sed 's/^# //')
  STATUS=$(grep "^status:" "$task" | cut -d: -f2 | xargs)

  if [ "$STATUS" = "done" ]; then
    echo "- [x] $TITLE"
  else
    echo "- [ ] $TITLE"
  fi
done > specs/001-auth-feature/tasks.md
```

### Q: What happens to manual edits in tasks.md?

**A**: During manual migration, manual edits should be incorporated into the Backlog task descriptions. In automated migration (future), there will be options to:
- Skip tasks with manual edits
- Include edits as task notes
- Prompt for each conflict

### Q: How do I handle tasks without IDs (T001, etc.)?

**A**: Assign sequential IDs:

```bash
# In tasks.md, add IDs
- [ ] Create database schema  → - [ ] T001 Create database schema
- [ ] Setup User model        → - [ ] T002 Setup User model
```

Or let Backlog.md auto-assign:

```bash
backlog task create "Create database schema"
# Assigns next available ID: task-1, task-2, etc.
```

### Q: Can I keep both tasks.md and Backlog.md in sync?

**A**: Not recommended. Bidirectional sync creates complexity and conflicts. Choose one as source of truth:

- **Backlog.md as source**: Migrate, deprecate tasks.md
- **tasks.md as source**: Don't migrate, use tasks.md only

For hybrid: Use tasks.md as blueprint, Backlog.md for execution (no sync).

### Q: What about tasks.md in the template?

**A**: Flowspec templates will eventually generate both:

- `tasks.md` - Reference blueprint (optional)
- Backlog.md tasks - Execution tracker (primary)

### Q: How do I migrate if I have custom task format?

**A**: Adjust the mapping:

**Custom format**:
```markdown
- [ ] [HIGH] [BACKEND] Create User model
```

**Map to Backlog.md**:
```yaml
labels: [backend]
priority: high
```

For complex custom formats, wait for automated migration (coming soon) which will support custom parsers.

### Q: Should I delete tasks.md after migration?

**A**: Three options:

1. **Deprecate**: Rename to `tasks.md.deprecated`, keep for reference
2. **Delete**: Remove entirely, use Backlog.md only
3. **Keep**: Add note that Backlog.md is source of truth

Recommended: **Deprecate** (option 1) - preserves history without confusion.

### Q: Can I migrate just completed tasks?

**A**: Yes:

```bash
# Extract only completed tasks
grep "\[x\]" specs/001-auth-feature/tasks.md | while read line; do
  TITLE=$(echo "$line" | sed 's/^.*\] //')
  backlog task create "$TITLE" --status "Done"
done
```

This creates a history of completed work in Backlog.md.

### Q: What if migration fails halfway?

**A**: Backlog.md tasks are independent files. If migration fails:

1. Delete partial tasks: `rm backlog/tasks/*`
2. Restore backup: `cp -r specs.backup/001-auth-feature specs/`
3. Try again with smaller batches
4. Report issue on GitHub if automated migration

---

## Migration Examples

### Example 1: Simple Feature (20 tasks)

**Before** (tasks.md):
```markdown
## Phase 1: Setup
- [ ] T001 Create project structure
- [ ] T002 Initialize database

## Phase 2: User Story 1 (Login)
- [ ] T012 [US1] Create User model
- [ ] T013 [US1] Create login endpoint
```

**After** (Backlog.md):
```bash
backlog/tasks/
├── task-001-create-project-structure.md
├── task-002-initialize-database.md
├── task-012-create-user-model.md
└── task-013-create-login-endpoint.md
```

**Time**: 10 minutes manual migration

### Example 2: Complex Feature (100 tasks, 3 user stories)

**Before**: Large tasks.md with phases, user stories, dependencies

**Migration**:
```bash
# Will use automated migration (when available)
specify backlog migrate --feature 002-complex-feature

# Estimated time: <1 minute
```

### Example 3: Completed Project (all tasks done)

**Use Case**: Migrate for historical record

```bash
# Migrate all as "Done"
grep "^\s*-\s*\[.\]" specs/001-auth-feature/tasks.md | while read line; do
  TITLE=$(echo "$line" | sed 's/^.*\] T[0-9]\+ //')
  backlog task create "$TITLE" --status "Done" --labels "historical"
done
```

## Next Steps After Migration

1. **Try the board**:
```bash
backlog board
backlog browser
```

2. **Configure MCP** (for AI integration):
```bash
claude mcp add backlog --scope user -- backlog mcp start
```

3. **Update team** (if collaborative):
- Share migration details
- Train team on Backlog.md commands
- Update onboarding docs

4. **Set up automation** (optional):
- CI/CD task completion
- Slack notifications for blocked tasks
- Daily standup board views

---

**Need Help?**

- See [Backlog.md User Guide](backlog-user-guide.md) for usage
- Check [Command Reference](../reference/backlog-commands.md) for all commands
- Open issue on [GitHub](https://github.com/jpoley/flowspec/issues) for migration problems

**Status**: Manual migration available now. Automated migration coming in v0.1.0.
