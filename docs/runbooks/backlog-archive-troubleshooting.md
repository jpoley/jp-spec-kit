# Backlog Archive Troubleshooting Runbook

This runbook provides solutions for common issues with the backlog archive system.

## Quick Diagnostics

```bash
# Check script exists and is executable
ls -la scripts/bash/archive-tasks.sh

# Verify backlog CLI is installed
backlog --version

# Test dry-run
./scripts/bash/archive-tasks.sh --dry-run

# Check for Done tasks
backlog task list -s Done --plain
```

## Common Error Messages

### "backlog CLI not found"

**Symptom:** Script exits with code 1, shows "backlog CLI not found"

**Cause:** The `backlog.md` CLI is not installed or not in PATH

**Solution:**
```bash
# Install backlog CLI
npm install -g backlog.md

# Verify installation
backlog --version

# If still not found, check PATH
which backlog
echo $PATH
```

### "Invalid date format"

**Symptom:** Script exits with code 1 when using `--done-by`

**Cause:** Date is not in ISO 8601 format (YYYY-MM-DD)

**Solution:**
```bash
# Correct format
./scripts/bash/archive-tasks.sh --done-by 2025-12-01

# Wrong formats
./scripts/bash/archive-tasks.sh --done-by 12/01/2025  # Wrong
./scripts/bash/archive-tasks.sh --done-by "Dec 1, 2025"  # Wrong
```

### "No tasks to archive" (Exit code 2)

**Symptom:** Script exits with code 2, no tasks archived

**Cause:** No tasks match the filter criteria

**Diagnosis:**
```bash
# Check if any Done tasks exist
backlog task list -s Done --plain

# If empty, no tasks have status "Done"
backlog task list --plain  # Show all tasks
```

**Solution:**
- Ensure tasks have status "Done" before archiving
- Use `--all` flag to archive tasks regardless of status
- Check date filter isn't too restrictive

### "Partial failures" (Exit code 3)

**Symptom:** Script exits with code 3, some tasks failed to archive

**Cause:** One or more tasks couldn't be archived (permission, file issues)

**Diagnosis:**
```bash
# Run with verbose output
./scripts/bash/archive-tasks.sh 2>&1 | tee archive.log

# Check which tasks failed in output
grep "Failed" archive.log
```

**Solution:**
1. Check task file permissions: `ls -la backlog/tasks/`
2. Verify archive directory exists: `mkdir -p backlog/archive`
3. Check disk space: `df -h .`
4. Retry failed tasks individually

## Workflow Issues

### GitHub Actions Workflow Not Triggering

**Symptom:** Push with "archive-backlog" keyword doesn't trigger workflow

**Diagnosis:**
```bash
# Check workflow is enabled
gh workflow list

# Check recent runs
gh run list --workflow=backlog-archive.yml
```

**Solutions:**
1. Verify keyword is exactly `archive-backlog`, `Archive Backlog`, or `ARCHIVE-BACKLOG`
2. Ensure push is to `main` branch
3. Check workflow file exists: `ls .github/workflows/backlog-archive.yml`
4. Enable workflow if disabled: Actions → Backlog Archive → Enable

### Scheduled Run Not Executing

**Symptom:** Weekly scheduled run didn't happen

**Cause:** GitHub may skip scheduled runs on inactive repositories

**Solutions:**
1. Make any commit to keep repository active
2. Check Actions → Filter by "Scheduled" for run history
3. Manually trigger to verify workflow works

### Workflow Commits Not Appearing

**Symptom:** Workflow runs but no commit in history

**Diagnosis:**
1. Check workflow run logs for "No changes to commit"
2. Verify dry-run wasn't enabled
3. Check if there were tasks to archive

**Solutions:**
1. Ensure dry-run is false for production runs
2. Verify Done tasks exist before running
3. Check workflow has `contents: write` permission

## Hook Issues

### Hook Not Running After /flow:validate

**Symptom:** Archive preview doesn't appear after validation

**Diagnosis:**
```bash
# Check hook exists and is executable
ls -la .claude/hooks/post-workflow-archive.sh

# Test hook manually
echo '{"event_type":"validate.completed"}' | .claude/hooks/post-workflow-archive.sh
```

**Solutions:**
1. Make hook executable: `chmod +x .claude/hooks/post-workflow-archive.sh`
2. Check hook is in `.claude/hooks/` directory
3. Verify event type matches expected trigger

### Hook Timing Out

**Symptom:** Hook logs show "timed out after 30s"

**Cause:** Archive script taking too long (large backlog)

**Solution:**
```bash
# Increase timeout in hook
# Edit .claude/hooks/post-workflow-archive.sh
TIMEOUT=60  # Increase from 30
```

## Performance Issues

### Archive Taking Too Long

**Symptom:** Script runs slowly for large backlogs

**Solutions:**

1. **Use date filtering:**
   ```bash
   # Archive old tasks first
   ./scripts/bash/archive-tasks.sh --done-by 2025-01-01
   ```

2. **Archive in batches:**
   ```bash
   # First batch
   ./scripts/bash/archive-tasks.sh --done-by 2025-06-01
   # Second batch
   ./scripts/bash/archive-tasks.sh --done-by 2025-12-01
   ```

3. **Run during off-hours:**
   - Use scheduled workflow for weekly archiving
   - Avoid running during active development

### Too Many Files in Archive

**Symptom:** Archive directory growing large

**Solutions:**

1. **Create yearly subdirectories:**
   ```bash
   mkdir -p backlog/archive/2024
   mv backlog/archive/task-0* backlog/archive/2024/
   ```

2. **Compress old archives:**
   ```bash
   cd backlog/archive
   tar -czf 2024-archive.tar.gz task-{001..100}*
   rm task-{001..100}*
   ```

## Recovery Procedures

### Recovering Archived Tasks

If you need to restore an archived task:

```bash
# Move task back to active directory
mv backlog/archive/task-042*.md backlog/tasks/

# Update status if needed
backlog task edit 42 -s "To Do"
```

### Fixing Corrupted Archive

If archive directory has issues:

```bash
# Verify task files are valid
for f in backlog/archive/*.md; do
  if ! head -1 "$f" | grep -q "^---$"; then
    echo "Invalid: $f"
  fi
done

# Remove corrupted files (after backup)
cp -r backlog/archive backlog/archive.backup
rm backlog/archive/corrupted-file.md
```

### Resetting Archive State

For a complete reset:

```bash
# Backup current archive
mv backlog/archive backlog/archive.old

# Create fresh archive directory
mkdir -p backlog/archive

# Optionally restore valid files
for f in backlog/archive.old/*.md; do
  if head -1 "$f" | grep -q "^---$"; then
    cp "$f" backlog/archive/
  fi
done
```

## Escalation Path

If issues persist after trying solutions above:

1. **Check GitHub Issues**: Search existing issues for similar problems
2. **Review Logs**: Collect full output from failed runs
3. **Create Issue**: File issue with:
   - Error message
   - Steps to reproduce
   - Environment (OS, CLI versions)
   - Relevant log output

## Related Documentation

- [Backlog Archive User Guide](../guides/backlog-archive.md)
- [Backlog Archive Workflow Guide](../guides/backlog-archive-workflow.md)
- [Backlog Archive Hook Guide](../guides/backlog-archive-hook.md)
- [Backlog User Guide](../guides/backlog-user-guide.md)
