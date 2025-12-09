# Team Mode Workflow Guide

## Overview

JP Spec Kit supports both **Solo Mode** (single developer) and **Team Mode** (multiple developers). This guide explains how to configure and work with Team Mode properly to avoid conflicts and ensure smooth collaboration.

## Solo vs Team Mode

### Solo Mode
- **Definition**: Single developer working on the project
- **VS Code Settings**: `.vscode/settings.json` can be committed to the repository
- **Agent Configuration**: Shared via Git
- **Use Case**: Personal projects, prototypes, single-maintainer repositories

### Team Mode
- **Definition**: Multiple developers working on the same project
- **VS Code Settings**: `.vscode/settings.json` must be gitignored (user-specific)
- **Agent Configuration**: Each developer generates their own settings
- **Use Case**: Team projects, open-source repositories, shared codebases

## Detecting Team Mode

The CI/CD pipeline automatically detects team mode by counting unique contributors:

```bash
# Check contributor count
git log --format='%ae' | sort -u | wc -l
```

If the count is greater than 1, the project is in **Team Mode**.

## Team Mode Requirements

### 1. Gitignore Configuration

Add `.vscode/settings.json` to `.gitignore`:

```gitignore
# VS Code user-specific settings (team mode)
.vscode/settings.json
```

This ensures each developer can have their own role preferences and agent configurations.

### 2. Remove Committed Settings

If `.vscode/settings.json` was previously committed, remove it:

```bash
# Remove from Git tracking (but keep local file)
git rm --cached .vscode/settings.json

# Commit the change
git add .gitignore
git commit -m "chore: move .vscode/settings.json to gitignore for team mode"
```

### 3. Generate User-Specific Settings

Each developer should generate their own settings:

```bash
# Generate .vscode/settings.json based on role preference
bash scripts/bash/sync-copilot-agents.sh --with-vscode
```

This creates a user-specific settings file based on the role configuration in `specflow_workflow.yml`.

## Role Selection in Team Mode

Each developer can configure their primary role in `specflow_workflow.yml` (locally, not committed):

```yaml
roles:
  primary: "dev"  # Change to: pm, arch, dev, sec, qa, ops
  show_all_commands: false
```

**Best Practice**: Don't commit changes to `roles.primary` in team mode. Keep it in your local working copy.

## Workflow for Team Members

### Initial Setup (New Team Member)

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd <repo>
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set your role preference** (optional, local only):
   ```bash
   # Edit specflow_workflow.yml (don't commit!)
   # Change roles.primary to your preferred role
   ```

4. **Generate your VS Code settings**:
   ```bash
   bash scripts/bash/sync-copilot-agents.sh --with-vscode
   ```

5. **Verify setup**:
   ```bash
   # Check that .vscode/settings.json exists locally
   ls -la .vscode/settings.json

   # Verify it's gitignored
   git status .vscode/settings.json
   # Should show: "Untracked files" (if new) or nothing (if ignored)
   ```

### Daily Workflow

1. **Pull latest changes**:
   ```bash
   git pull
   ```

2. **Sync agents** (if commands changed):
   ```bash
   bash scripts/bash/sync-copilot-agents.sh
   ```

3. **Work with your role-specific commands**:
   - PM: `@pm-assess`, `@pm-define`, `@pm-discover`
   - Arch: `@arch-design`, `@arch-decide`, `@arch-model`
   - Dev: `@dev-build`, `@dev-debug`, `@dev-refactor`
   - QA: `@qa-test`, `@qa-verify`, `@qa-review`
   - Sec: `@sec-scan`, `@sec-triage`, `@sec-fix`, `@sec-audit`
   - Ops: `@ops-deploy`, `@ops-monitor`, `@ops-respond`, `@ops-scale`

4. **Commit and push**:
   ```bash
   git add <files>
   git commit -m "feat: implement feature X"
   git push
   ```

## CI/CD Validation

The CI/CD pipeline enforces team mode compliance:

### Team Mode Validation Job

```yaml
validate-team-mode:
  runs-on: ubuntu-latest
  steps:
    - name: Check for .vscode/settings.json in team mode
      run: |
        CONTRIBUTOR_COUNT=$(git log --format='%ae' | sort -u | wc -l)

        if [ $CONTRIBUTOR_COUNT -gt 1 ]; then
          # Team mode detected
          if git ls-files --error-unmatch .vscode/settings.json >/dev/null 2>&1; then
            echo "❌ ERROR: .vscode/settings.json is committed in team mode"
            exit 1
          fi
        fi
```

This validation:
- Counts unique contributors via Git history
- Fails if `.vscode/settings.json` is committed when contributors > 1
- Provides helpful error messages with fix instructions

## Troubleshooting

### Problem: CI/CD failing with ".vscode/settings.json is committed"

**Solution**:
```bash
# Remove from Git
git rm --cached .vscode/settings.json

# Add to .gitignore
echo ".vscode/settings.json" >> .gitignore

# Commit
git add .gitignore
git commit -m "chore: fix team mode - gitignore .vscode/settings.json"
git push
```

### Problem: Agent commands not showing up in VS Code

**Solution**:
```bash
# Regenerate agents
bash scripts/bash/sync-copilot-agents.sh

# Regenerate VS Code settings
bash scripts/bash/sync-copilot-agents.sh --with-vscode

# Reload VS Code window
# Cmd/Ctrl + Shift + P → "Developer: Reload Window"
```

### Problem: Conflicts on .vscode/settings.json

**Solution**:
```bash
# If you accidentally committed it, remove from Git
git rm --cached .vscode/settings.json

# If you pulled someone else's settings, regenerate yours
bash scripts/bash/sync-copilot-agents.sh --with-vscode
```

### Problem: Different team members have different role preferences

**Solution**: This is expected and correct behavior in team mode! Each developer should:
1. Keep their own local `roles.primary` setting
2. Not commit changes to `roles.primary`
3. Generate their own `.vscode/settings.json`

## Migration from Solo to Team Mode

When transitioning from solo to team mode:

### Step 1: Update .gitignore
```bash
echo "" >> .gitignore
echo "# VS Code user-specific settings (team mode)" >> .gitignore
echo ".vscode/settings.json" >> .gitignore
```

### Step 2: Remove from Git
```bash
git rm --cached .vscode/settings.json
git add .gitignore
git commit -m "chore: migrate to team mode - gitignore .vscode/settings.json"
git push
```

### Step 3: Notify Team
Send a message to all team members:

> **Action Required**: We've migrated to team mode. Please run:
> ```bash
> git pull
> bash scripts/bash/sync-copilot-agents.sh --with-vscode
> ```
>
> This will generate your personal VS Code settings based on your role preference.

## Best Practices

### For Project Maintainers

1. **Document team mode** in README.md
2. **Set up CI/CD validation** (already included in `.github/workflows/role-validation.yml`)
3. **Provide onboarding guide** for new team members
4. **Keep `specflow_workflow.yml` in sync** with latest role definitions

### For Team Members

1. **Don't commit `.vscode/settings.json`** in team mode
2. **Don't commit `roles.primary` changes** unless changing the default for everyone
3. **Regenerate agents after pulling** if command templates changed
4. **Respect role boundaries** - if you're a dev, use dev commands
5. **Communicate role changes** if you switch roles on the project

## Role-Based Collaboration

### Example: Feature Development Flow

1. **PM** (@pm-define):
   - Creates PRD in `docs/prd/`
   - Defines user stories and acceptance criteria
   - Creates implementation tasks in backlog

2. **Architect** (@arch-design):
   - Reviews PRD
   - Creates technical design in `docs/adr/`
   - Defines system architecture

3. **Developer** (@dev-build):
   - Reviews design
   - Implements feature according to spec
   - Writes unit tests

4. **QA** (@qa-test):
   - Reviews implementation
   - Runs test suite
   - Validates acceptance criteria

5. **Security** (@sec-scan):
   - Scans for vulnerabilities
   - Reviews security implications
   - Approves or requests fixes

6. **Ops** (@ops-deploy):
   - Deploys to staging
   - Monitors metrics
   - Deploys to production

Each role uses their specific commands, avoiding conflicts and confusion.

## FAQ

### Q: Can I use multiple roles?
**A**: Yes! Set `show_all_commands: true` in `specflow_workflow.yml` to see all commands regardless of role.

### Q: What if I'm the only developer but want team mode?
**A**: You can manually enable team mode by gitignoring `.vscode/settings.json`. This is useful for projects that will grow to multiple contributors.

### Q: Can I override the primary role per-project?
**A**: Yes, but keep changes local. Don't commit `roles.primary` changes in team mode.

### Q: What happens if someone commits .vscode/settings.json?
**A**: The CI/CD pipeline will fail with a clear error message and fix instructions.

## References

- [Role-Based Command Namespaces ADR](../adr/ADR-role-based-command-namespaces.md)
- [Workflow Configuration Guide](./workflow-customization.md)
- [Agent Loop Classification](../reference/agent-loop-classification.md)
- [CI/CD Role Validation](../../.github/workflows/role-validation.yml)
