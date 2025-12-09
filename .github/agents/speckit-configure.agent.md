---
name: "speckit-configure"
description: "Configure or reconfigure workflow settings including role selection and validation modes"
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Grep"
  - "Glob"
  - "mcp__backlog__*"
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command allows users to reconfigure project settings including role selection and workflow validation modes. It can be used to change your primary role or update workflow transition settings.

### Overview

The `/speckit:configure` command:
1. Re-prompts for role selection (optional)
2. Re-prompts for validation mode on each workflow transition (optional)
3. Regenerates or updates `specflow_workflow.yml` with new settings
4. Optionally reconfigures constitution tier (with `--constitution` flag)
5. Preserves all existing project files and structure

### Argument Parsing

Parse `$ARGUMENTS` for optional flags:

| Flag | Description |
|------|-------------|
| `--role {pm\|arch\|dev\|sec\|qa\|ops\|all}` | Change role directly (non-interactive) |
| `--constitution` | Also prompt to change constitution tier |
| `--all` | Reset all configurations (role + validation modes + constitution) |
| `--validation-mode {none\|keyword\|pull-request}` | Set all transitions to this mode (non-interactive) |
| `--no-prompts` | Use defaults for all options (role: current, validation: NONE) |

Environment variable override:
- `SPECFLOW_PRIMARY_ROLE`: Override role selection (e.g., `export SPECFLOW_PRIMARY_ROLE=dev`)

### Step 1: Verify Project Context

Before proceeding, verify this is a valid jp-spec-kit project:

```bash
# Check for project markers
if [ ! -f "specflow_workflow.yml" ] && [ ! -f "jpspec_workflow.yml" ] && [ ! -d ".claude" ]; then
  echo "Error: This doesn't appear to be a jp-spec-kit project"
  echo "Run '/speckit:init' first to initialize the project"
  exit 1
fi
```

If no workflow config exists but `.claude/` directory does, this is a valid project that just needs configuration.

### Step 2: Display Current Configuration

Show the current configuration to help user make informed decisions:

```
╔══════════════════════════════════════════════════════════════╗
║         Current Configuration                                 ║
╚══════════════════════════════════════════════════════════════╝

🎭 ROLE SETTINGS

Current Role: {icon} {display_name} ({role_id})
Show All Commands: {true | false}

To view role-specific commands, see:
  {PM: /pm:*}
  {Arch: /arch:*}
  {Dev: /dev:*}
  {Sec: /sec:*}
  {QA: /qa:*}
  {Ops: /ops:*}
  {All: all commands}

📋 WORKFLOW VALIDATION MODES

{List current validation modes if jpspec_workflow.yml exists}
{Or: "Not yet configured" if no workflow file}
```

### Step 3: Role Selection Prompt

If `--role` flag is NOT provided and `--no-prompts` is NOT set:

**Precedence order**:
1. `SPECFLOW_PRIMARY_ROLE` environment variable (highest priority)
2. `--role` flag from command line
3. Interactive prompt
4. Current role (no change)

Display role selection prompt:

```
╔══════════════════════════════════════════════════════════════╗
║  Select Your Primary Role                                     ║
╚══════════════════════════════════════════════════════════════╝

Current: {icon} {current_display_name}

Choose your role to personalize command suggestions and agent handoffs:

  1. 📋 Product Manager (PM)
     • Focus: Requirements & specifications
     • Commands: /pm:assess, /pm:define, /pm:discover
     • Agents: @product-requirements-manager, @workflow-assessor

  2. 🏗️  Architect (Arch)
     • Focus: System design & architecture decisions
     • Commands: /arch:design, /arch:decide, /arch:model
     • Agents: @software-architect, @platform-engineer

  3. 💻 Developer (Dev)
     • Focus: Implementation & code development
     • Commands: /dev:build, /dev:debug, /dev:refactor
     • Agents: @frontend-engineer, @backend-engineer, @ai-ml-engineer

  4. 🔒 Security Engineer (Sec)
     • Focus: Security scanning & vulnerability management
     • Commands: /sec:scan, /sec:triage, /sec:fix, /sec:audit
     • Agents: @secure-by-design-engineer

  5. ✅ QA Engineer (QA)
     • Focus: Testing & quality validation
     • Commands: /qa:test, /qa:verify, /qa:review
     • Agents: @quality-guardian, @release-manager

  6. 🚀 SRE/DevOps (Ops)
     • Focus: Deployment & operations
     • Commands: /ops:deploy, /ops:monitor, /ops:respond, /ops:scale
     • Agents: @sre-agent

  7. 🌐 All Roles
     • Full access to all commands and agents
     • No filtering or personalization

  8. Keep Current ({current_display_name})

Enter selection [1-8] (default: 8): _
```

**Role Mapping**:
- Input 1 → "pm"
- Input 2 → "arch"
- Input 3 → "dev"
- Input 4 → "sec"
- Input 5 → "qa"
- Input 6 → "ops"
- Input 7 → "all"
- Input 8 → Keep current role (no change)

Validate input is in range 1-8. If invalid, reprompt.

**Environment Variable Detection**:
If `SPECFLOW_PRIMARY_ROLE` is set, show:
```
Role auto-selected from environment variable:
  SPECFLOW_PRIMARY_ROLE={role}
  New Role: {icon} {display_name}

(Override with --role flag if needed)
```

**Non-Interactive Mode**:
If `--role` flag is provided:
```
Role updated via --role flag:
  Previous: {old_icon} {old_display_name}
  New: {new_icon} {new_display_name}
```

If `--no-prompts` is set and no `--role` flag:
```
Keeping current role (--no-prompts specified):
  Current: {icon} {display_name}
```

### Step 4: Update specflow_workflow.yml with New Role

Update the `roles.primary` field in `specflow_workflow.yml`:

```yaml
roles:
  primary: "{selected_role}"  # Update this field
  show_all_commands: false
  definitions:
    # ... existing role definitions remain unchanged
```

**IMPORTANT**:
- Preserve all other fields in the file
- Only update `roles.primary`
- If `specflow_workflow.yml` doesn't exist, create it with default structure
- If legacy `jpspec_workflow.yml` exists, migrate to `specflow_workflow.yml` v2.0 format

### Step 5: Workflow Validation Mode Configuration (Optional)

If `--all` flag is provided OR user explicitly requests workflow reconfiguration:

Display the interactive validation mode configuration:

```
╔══════════════════════════════════════════════════════════════╗
║  Workflow Transition Validation Configuration                 ║
╚══════════════════════════════════════════════════════════════╝

For each workflow transition, choose a validation mode:
  - NONE: No gate, proceed immediately (default)
  - KEYWORD: Require user to type approval keyword
  - PULL_REQUEST: Require PR to be merged

1. To Do → Assessed (after /jpspec:assess)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > _

2. Assessed → Specified (after /jpspec:specify, produces PRD)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > _

3. Specified → Researched (after /jpspec:research)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > _

4. Researched → Planned (after /jpspec:plan, produces ADRs)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > _

5. Planned → In Implementation (after /jpspec:implement)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > _

6. In Implementation → Validated (after /jpspec:validate)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > _

7. Validated → Deployed (after /jpspec:operate)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > _
```

If user selects KEYWORD (option 2), prompt for the approval keyword:
```
   Enter approval keyword [APPROVED]: _
```

### Step 6: Constitution Reconfiguration (Optional)

If `--constitution` or `--all` flag is provided:

1. Prompt for constitution tier:
   ```
   Select a constitution tier for your project:
     1. light - Minimal controls for startups/hobby projects
     2. medium - Standard controls for typical business projects
     3. heavy - Enterprise controls for regulated environments

   Current tier: {current_tier}
   Enter tier number (1-3) [keep current]: _
   ```

2. If constitution already exists, warn user:
   ```
   Warning: Existing constitution at memory/constitution.md will be replaced.
   This will NOT preserve any custom modifications.

   Continue? [y/N]: _
   ```

3. Copy the selected tier template to `memory/constitution.md`

4. Suggest running `/speckit:constitution` for full customization:
   ```
   Constitution template installed.

   For full customization with auto-detected tech stack, run:
     /speckit:constitution --tier {selected_tier}
   ```

### Step 7: Display Summary

Output a summary of the changes:

```
╔══════════════════════════════════════════════════════════════╗
║         Configuration Update Complete                         ║
╚══════════════════════════════════════════════════════════════╝

🎭 ROLE CONFIGURATION

{If role changed:}
Previous Role: {old_icon} {old_display_name}
New Role: {new_icon} {new_display_name}
Updated: {YYYY-MM-DD HH:MM:SS}

This role determines:
  • Which commands appear prominently in your IDE
  • Which agents are auto-loaded for handoffs
  • Default workflow entry points

Role-specific commands: {/pm:* | /arch:* | /dev:* | /sec:* | /qa:* | /ops:* | all commands}

{If role unchanged:}
Role: {icon} {display_name} (no change)

📋 VALIDATION MODES {If configured}

Transition               Mode
─────────────────────────────────────
assess                   {MODE}
specify                  {MODE}
research                 {MODE}
plan                     {MODE}
implement                {MODE}
validate                 {MODE}
operate                  {MODE}

📁 FILES UPDATED

  ✓ specflow_workflow.yml (role updated)
  {✓ specflow_workflow.yml (validation modes) - if configured}
  {✓ memory/constitution.md (if --constitution)}

🎯 NEXT STEPS

1. Review the updated configuration:
   cat specflow_workflow.yml

2. Commit the configuration changes:
   git add specflow_workflow.yml
   git commit -s -m "chore: update role to {role_display_name}"

3. Start using role-specific commands:
   {PM role: /pm:assess <feature>}
   {Arch role: /arch:design <component>}
   {Dev role: /dev:build <feature>}
   {Sec role: /sec:scan}
   {QA role: /qa:verify}
   {Ops role: /ops:deploy}
   {All roles: Access all commands}

💡 TIPS

• Override role per session: export SPECFLOW_PRIMARY_ROLE=<role>
• See all commands: Set show_all_commands: true in specflow_workflow.yml
• Reconfigure anytime: /speckit:configure
• Change just role: /speckit:configure --role <new_role>
• Reset validation modes: /speckit:configure --all
```

### Non-Interactive Modes

**Change role only** (fast):
```bash
/speckit:configure --role dev
# Output: Role updated to 💻 Developer
```

**Set all validation modes**:
```bash
/speckit:configure --validation-mode none
# Sets all transitions to NONE
```

**No prompts mode**:
```bash
/speckit:configure --no-prompts
# Uses current role, NONE for all validations
```

**Full reconfiguration**:
```bash
/speckit:configure --all
# Prompts for role, validation modes, and constitution
```

### Error Handling

- **Not in project directory**: Show error and suggest `/speckit:init`
- **Invalid role value**: Show valid options (pm, arch, dev, sec, qa, ops, all)
- **Invalid validation mode**: Show valid options (none, keyword, pull-request)
- **Invalid constitution tier**: Show valid options (light, medium, heavy)
- **User cancels**: Exit gracefully with message
- **No specflow_workflow.yml**: Create new one with selected role
- **Invalid SPECFLOW_PRIMARY_ROLE env var**: Show warning and fall back to prompt

### Migration from jpspec_workflow.yml

If project has `jpspec_workflow.yml` but not `specflow_workflow.yml`:

```
Detected legacy jpspec_workflow.yml (v1.x)

This command will migrate to specflow_workflow.yml v2.0 with roles support.

Migration will:
  ✓ Create specflow_workflow.yml with v2.0 schema
  ✓ Preserve all workflow definitions and states
  ✓ Add roles section with your selected role
  ✓ Keep jpspec_workflow.yml as backup

Continue? [Y/n]: _
```

If user confirms, perform migration and keep old file.

### Quality Checks

Before completing:
- [ ] specflow_workflow.yml exists with v2.0 schema
- [ ] roles.primary is set to valid role value
- [ ] If validation modes configured, all 7 transitions have valid modes
- [ ] Validation modes are one of: NONE, KEYWORD["..."], PULL_REQUEST
- [ ] Summary clearly shows role change (if changed)
- [ ] Summary shows validation modes (if configured)
- [ ] Next steps are role-appropriate and actionable

## Important Notes

1. **Role switching**: Changing role only affects command visibility and agent suggestions
2. **Non-destructive**: Only modifies workflow configuration, not project files
3. **Git-safe**: Previous config preserved in git history
4. **Idempotent**: Can be run multiple times safely
5. **Quick role change**: Use `--role` flag for instant role switching
6. **Environment override**: `SPECFLOW_PRIMARY_ROLE` env var takes precedence
7. **Backwards compatible**: Migrates legacy jpspec_workflow.yml to specflow_workflow.yml
8. **No network requests**: All operations are local and fast
