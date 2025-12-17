# Backlog.md Troubleshooting Guide

Comprehensive troubleshooting for common issues with Backlog.md integration in Flowspec.

## Table of Contents

- [Installation Issues](#installation-issues)
- [MCP Integration Issues](#mcp-integration-issues)
- [Task Management Issues](#task-management-issues)
- [Web UI Issues](#web-ui-issues)
- [Git Integration Issues](#git-integration-issues)
- [Performance Issues](#performance-issues)
- [Migration Issues](#migration-issues)
- [AI Integration Issues](#ai-integration-issues)

## Installation Issues

### Problem: `backlog: command not found`

**Symptoms**: Running `backlog` in terminal shows "command not found"

**Solution**:

1. **Install Backlog.md**:
```bash
npm install -g backlog.md
```

2. **Verify installation**:
```bash
which backlog
# Should show: /usr/local/bin/backlog or similar

backlog --version
# Should show: v1.20.1 or higher
```

3. **Check PATH**:
```bash
echo $PATH
# Should include npm global bin directory

# Find npm global bin
npm bin -g
# Add to PATH if missing (in ~/.bashrc or ~/.zshrc):
export PATH="$(npm bin -g):$PATH"
```

4. **Alternative: Use pnpm**:
```bash
pnpm add -g backlog.md
```

---

### Problem: Node.js not installed

**Symptoms**: `npm: command not found`

**Solution**:

**macOS**:
```bash
brew install node
```

**Ubuntu/Debian**:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows**:
Download from https://nodejs.org

**Verify**:
```bash
node --version  # v18.0.0 or higher
npm --version   # 8.0.0 or higher
```

---

### Problem: Permission denied during installation

**Symptoms**: `EACCES` error when running `npm install -g`

**Solution**:

**Option 1: Fix npm permissions** (recommended):
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g backlog.md
```

**Option 2: Use sudo** (not recommended):
```bash
sudo npm install -g backlog.md
```

**Option 3: Use nvm**:
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install Node via nvm
nvm install 18
nvm use 18

# Install backlog.md
npm install -g backlog.md
```

## MCP Integration Issues

### Problem: MCP server not connecting to Claude Code

**Symptoms**: Claude can't list tasks, MCP tools unavailable

**Solution**:

1. **Verify MCP configured**:
```bash
cat ~/.config/claude-code/.mcp.json
# Should contain:
# {
#   "mcpServers": {
#     "backlog": { ... }
#   }
# }
```

2. **Re-add MCP server**:
```bash
# Remove existing
claude mcp remove backlog

# Add again
claude mcp add backlog --scope user -- backlog mcp start
```

3. **Restart Claude Code completely**:
- Quit Claude Code entirely (Cmd+Q or close all windows)
- Restart Claude Code
- Wait for MCP servers to load (~10 seconds)

4. **Test MCP connection**:
Ask Claude:
```
List all available MCP servers
```
Should see "backlog" in the list.

5. **Check MCP logs**:
```bash
# View Claude Code logs
tail -f ~/.local/state/claude-code/logs/mcp-backlog.log

# Look for:
# ✅ "MCP server started"
# ❌ "Connection failed" or "Server error"
```

---

### Problem: MCP server crashes or times out

**Symptoms**: "MCP server disconnected" or timeout errors

**Solution**:

1. **Check Backlog.md version**:
```bash
backlog --version
# Update if < v1.20.0
npm update -g backlog.md
```

2. **Test MCP server manually**:
```bash
backlog mcp start --log-level debug

# Should output:
# MCP server started on port 6421
# Listening for connections...
```

3. **Check port availability**:
```bash
lsof -i :6421
# If port in use, kill process:
kill <PID>
```

4. **Increase timeout** (in `.mcp.json`):
```json
{
  "mcpServers": {
    "backlog": {
      "command": "backlog",
      "args": ["mcp", "start"],
      "env": {},
      "timeout": 30000
    }
  }
}
```

---

### Problem: Claude can't create or update tasks

**Symptoms**: Claude says "I don't have permission" or "Task creation failed"

**Solution**:

1. **Verify backlog initialized**:
```bash
ls -la backlog/
# Should exist with config.yml
```

2. **Check file permissions**:
```bash
ls -la backlog/tasks/
# Should be writable by current user

# Fix if needed:
chmod -R u+w backlog/
```

3. **Test CLI directly**:
```bash
backlog task create "Test task"
# If this works, MCP should work too
```

4. **Check MCP tool availability**:
Ask Claude:
```
What MCP tools are available from the backlog server?
```
Should list: `backlog_create_task`, `backlog_update_task`, etc.

## Task Management Issues

### Problem: Tasks not showing in board

**Symptoms**: `backlog board` shows empty or missing tasks

**Solution**:

1. **Check tasks directory**:
```bash
ls -la backlog/tasks/
# Should contain task-*.md files
```

2. **Verify task file format**:
```bash
cat backlog/tasks/task-001*.md

# Must have valid frontmatter:
# ---
# status: todo
# assignees: []
# labels: []
# ---
```

3. **Check for YAML errors**:
```bash
# Install yq if needed
brew install yq  # macOS
sudo apt install yq  # Linux

# Validate each task
for task in backlog/tasks/*.md; do
  echo "Checking $task"
  head -n 20 "$task" | yq eval '.' -
done
```

4. **Re-initialize if corrupted**:
```bash
# Backup first
cp -r backlog backlog.backup

# Re-initialize
backlog init --force
```

---

### Problem: Task status not updating

**Symptoms**: Status changes don't reflect in board

**Solution**:

1. **Refresh board**:
```bash
# In board view, press 'r' for refresh
# Or re-run:
backlog board
```

2. **Check Git status**:
```bash
git status backlog/tasks/

# If not tracked:
git add backlog/tasks/
git commit -m "Track backlog tasks"
```

3. **Verify file changes**:
```bash
# Check if file actually changed
git diff backlog/tasks/task-012*.md

# Should show:
# -status: todo
# +status: in_progress
```

4. **Clear cache** (if using web UI):
```bash
# Stop web server
pkill -f "backlog browser"

# Clear browser cache
# Then restart:
backlog browser
```

---

### Problem: Dependencies not enforcing blocking

**Symptoms**: Can move tasks even though dependencies incomplete

**Solution**:

Backlog.md **displays** dependencies but doesn't **enforce** blocking. This is by design.

**Workaround - Manual checking**:
```bash
#!/bin/bash
# scripts/check-dependencies.sh
TASK_ID=$1

# Get dependencies
DEPS=$(grep "dependencies:" "backlog/tasks/task-$TASK_ID"*.md | \
       sed 's/.*: \[\(.*\)\]/\1/' | tr ',' ' ')

# Check each dependency
for dep in $DEPS; do
  STATUS=$(grep "status:" "backlog/tasks/$dep"*.md | cut -d: -f2 | xargs)
  if [ "$STATUS" != "done" ]; then
    echo "⚠️ Cannot start task-$TASK_ID: $dep is $STATUS"
    exit 1
  fi
done

echo "✅ All dependencies met for task-$TASK_ID"
```

**Use in workflow**:
```bash
./scripts/check-dependencies.sh 12
# Only proceed if exit code 0
```

## Web UI Issues

### Problem: Web UI won't open

**Symptoms**: `backlog browser` fails or browser doesn't open

**Solution**:

1. **Check port availability**:
```bash
lsof -i :6420

# If in use:
kill <PID>
# Or use different port:
backlog browser --port 6421
```

2. **Disable auto-open and open manually**:
```bash
backlog browser --no-open

# Then manually open:
# http://localhost:6420
```

3. **Update config**:
```bash
# Edit backlog/config.yml
auto_open_browser: false
default_port: 6421
```

4. **Check for errors**:
```bash
backlog browser --verbose
# Look for error messages
```

---

### Problem: Web UI shows "Connection refused"

**Symptoms**: Browser shows connection error

**Solution**:

1. **Verify server running**:
```bash
ps aux | grep "backlog browser"
# Should show running process
```

2. **Check firewall**:
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Linux
sudo ufw status

# Allow if blocked:
sudo ufw allow 6420
```

3. **Try localhost explicitly**:
```
http://127.0.0.1:6420
```

4. **Restart server**:
```bash
pkill -f "backlog browser"
backlog browser
```

---

### Problem: Drag-and-drop not working in web UI

**Symptoms**: Can't move tasks between columns

**Solution**:

1. **Check browser compatibility**:
   - Use Chrome, Firefox, or Safari (modern versions)
   - Disable browser extensions that might interfere

2. **Clear browser cache**:
   - Cmd/Ctrl + Shift + R (hard refresh)

3. **Try incognito/private mode**:
   - Rules out extension conflicts

4. **Use CLI as fallback**:
```bash
backlog task edit task-12 --field status --value "In Progress"
```

## Git Integration Issues

### Problem: Backlog changes not tracked by Git

**Symptoms**: `git status` doesn't show backlog/ changes

**Solution**:

1. **Check .gitignore**:
```bash
cat .gitignore
# Make sure backlog/ is NOT ignored

# If it is, remove the line:
sed -i '/backlog/d' .gitignore
```

2. **Add backlog to Git**:
```bash
git add backlog/
git commit -m "Track backlog tasks"
```

3. **Verify tracking**:
```bash
git ls-files backlog/
# Should list all backlog files
```

---

### Problem: Merge conflicts in backlog/

**Symptoms**: Git conflicts when pulling or merging

**Solution**:

1. **View conflicts**:
```bash
git status
# Shows conflicted files in backlog/

cat backlog/tasks/task-012-example.md
# Look for conflict markers:
# <<<<<<< HEAD
# =======
# >>>>>>> branch
```

2. **Resolve task conflicts**:

Tasks are markdown files with YAML frontmatter. Conflicts usually in:
- **Status**: Keep most recent status
- **Assignee**: Keep theirs if they took ownership
- **Labels**: Merge both sets

**Example resolution**:
```yaml
# Conflict:
# <<<<<<< HEAD
# status: done
# =======
# status: in_progress
# >>>>>>> feature-branch

# Resolution (keep most complete):
status: done
```

3. **Automated resolution** for status conflicts:
```bash
# Script to keep latest status
git checkout --theirs backlog/tasks/*.md
```

4. **After resolution**:
```bash
git add backlog/
git commit -m "Resolve backlog conflicts"
```

---

### Problem: Auto-commit not working

**Symptoms**: Task changes not auto-committed

**Solution**:

Check config:
```yaml
# backlog/config.yml
auto_commit: true  # Must be true
remote_operations: true
```

If still not working, use manual commits:
```bash
git add backlog/
git commit -m "Update task status"
```

## Performance Issues

### Problem: Slow board loading with 1000+ tasks

**Symptoms**: `backlog board` takes >5 seconds to load

**Solution**:

1. **Use filtering**:
```bash
# Instead of viewing all tasks
backlog board --filter US1

# Or by status
backlog board --status todo
```

2. **Archive completed tasks**:
```bash
# Archive tasks older than 30 days
backlog task archive --status done --before $(date -d '30 days ago' +%Y-%m-%d)

# Archived tasks move to backlog/archive/
```

3. **Use list for bulk operations**:
```bash
# Instead of board for viewing
backlog list --format table
```

4. **Split into multiple projects**:
```bash
# Separate backlogs for different phases
backlog-mvp/
backlog-v2/
backlog-v3/
```

---

### Problem: Search is slow

**Symptoms**: `backlog search` takes >10 seconds

**Solution**:

1. **Use specific search**:
```bash
# Search titles only (faster)
backlog search "login" --title

# Instead of full content search
```

2. **Index large projects**:
```bash
# Create search index (if supported)
backlog index rebuild
```

3. **Use grep for simple searches**:
```bash
# Faster for simple text search
grep -r "authentication" backlog/tasks/
```

## Migration Issues

### Problem: Task IDs don't match after migration

**Symptoms**: T001 in tasks.md becomes task-1 in Backlog.md

**Solution**:

**Manual ID assignment**:
```bash
# Rename task files to match IDs
mv backlog/tasks/task-1*.md backlog/tasks/task-001*.md
mv backlog/tasks/task-2*.md backlog/tasks/task-002*.md
# etc.
```

**Script for bulk rename**:
```bash
#!/bin/bash
for task in backlog/tasks/task-[0-9]*.md; do
  BASE=$(basename "$task")
  # Extract number
  NUM=$(echo "$BASE" | sed 's/task-\([0-9]\+\).*/\1/')
  # Pad to 3 digits
  PADDED=$(printf "%03d" $NUM)
  # Rename
  NEW=$(echo "$BASE" | sed "s/task-$NUM/task-$PADDED/")
  mv "$task" "backlog/tasks/$NEW"
done
```

---

### Problem: Completed tasks marked as todo

**Symptoms**: Tasks checked off in tasks.md show as todo in Backlog.md

**Solution**:

**Fix manually**:
```bash
# Find tasks that should be done
grep "\[x\]" specs/001-feature/tasks.md

# Update corresponding Backlog tasks
backlog task edit task-001 --field status --value done
backlog task edit task-005 --field status --value done
```

**Bulk update**:
```bash
# Extract completed task IDs from tasks.md
DONE_IDS=$(grep "\[x\].*T[0-9]" specs/001-feature/tasks.md | \
           sed 's/.*T\([0-9]\+\).*/\1/')

# Update each in Backlog.md
for id in $DONE_IDS; do
  # Find file matching ID
  TASK_FILE=$(ls backlog/tasks/ | grep "task-0*$id")
  if [ -n "$TASK_FILE" ]; then
    # Update status
    sed -i 's/status: todo/status: done/' "backlog/tasks/$TASK_FILE"
  fi
done
```

---

### Problem: Lost metadata during migration

**Symptoms**: Labels, priorities, or descriptions missing

**Solution**:

1. **Restore from backup**:
```bash
# If you created backup before migration
cp specs/001-feature.backup/tasks.md specs/001-feature/tasks.md
```

2. **Re-migrate carefully**:
Follow [Migration Guide](backlog-migration.md) step-by-step

3. **Add missing metadata manually**:
```bash
# Edit task to add labels
backlog task edit task-012
# Add to frontmatter:
# labels: [US1, backend, parallelizable]
```

## AI Integration Issues

### Problem: Claude doesn't understand task context

**Symptoms**: Claude creates tasks with wrong labels or priorities

**Solution**:

1. **Provide context in prompt**:
```text
Bad:  "Create a task for login"
Good: "Create a task for implementing login endpoint.
       This is part of User Story 1 (US1), backend work,
       high priority, depends on User model (task-012)"
```

2. **Use spec files as context**:
```text
You: "Read spec.md for this feature, then create tasks for US1"
Claude: [Reads spec, creates tasks with appropriate context]
```

3. **Set defaults in config**:
```yaml
# backlog/config.yml
default_labels: [backend, feature]
default_priority: medium
```

---

### Problem: Claude can't find tasks

**Symptoms**: "Task not found" when asking about tasks

**Solution**:

1. **Use exact task IDs**:
```text
Bad:  "Show me the login task"
Good: "Show me task-012"
```

2. **List tasks first**:
```text
You: "List all tasks labeled with US1"
Claude: [Shows list with IDs]
You: "Show me details for task-012"
Claude: [Shows details]
```

3. **Verify MCP working**:
```text
You: "What MCP tools do you have for backlog?"
Claude: [Should list backlog_* tools]
```

---

### Problem: Task updates don't persist

**Symptoms**: Claude says task updated but changes not saved

**Solution**:

1. **Check file permissions**:
```bash
ls -la backlog/tasks/
# Should be writable

chmod u+w backlog/tasks/*.md
```

2. **Verify Git not blocking**:
```bash
git status backlog/
# If locked, unlock:
rm .git/index.lock
```

3. **Manual verification**:
```bash
# After Claude updates, check:
cat backlog/tasks/task-012*.md
# Verify status field updated
```

## Getting Help

### When to Report an Issue

Report if you encounter:
- Bugs in Backlog.md tool
- MCP integration failures
- flowspec integration problems
- Documentation errors

### How to Report

**For Backlog.md tool issues**:
https://github.com/MrLesk/Backlog.md/issues

**For Flowspec integration issues**:
https://github.com/jpoley/flowspec/issues

**Include in report**:
```bash
# System info
uname -a
node --version
backlog --version

# Backlog config
cat backlog/config.yml

# MCP config (if relevant)
cat ~/.config/claude-code/.mcp.json

# Error logs
tail -50 ~/.local/state/claude-code/logs/mcp-backlog.log

# Steps to reproduce
# 1. ...
# 2. ...

# Expected vs actual behavior
```

### Community Help

- **Discord**: [Flowspec community](https://discord.gg/...)
- **GitHub Discussions**: https://github.com/jpoley/flowspec/discussions
- **Stack Overflow**: Tag with `flowspec` and `backlog-md`

### Quick Diagnostic

Run this to collect diagnostic info:

```bash
#!/bin/bash
# scripts/backlog-diagnostic.sh

echo "=== Backlog.md Diagnostic ==="
echo ""

echo "Node version:"
node --version

echo ""
echo "Backlog.md version:"
backlog --version

echo ""
echo "Backlog config:"
cat backlog/config.yml

echo ""
echo "Task count:"
ls backlog/tasks/*.md 2>/dev/null | wc -l

echo ""
echo "Git status:"
git status backlog/

echo ""
echo "MCP config:"
cat ~/.config/claude-code/.mcp.json 2>/dev/null | grep -A5 backlog

echo ""
echo "Recent errors:"
tail -20 ~/.local/state/claude-code/logs/mcp-backlog.log 2>/dev/null || echo "No MCP logs found"
```

---

**Last Updated**: 2025-11-24
**Status**: Actively maintained
