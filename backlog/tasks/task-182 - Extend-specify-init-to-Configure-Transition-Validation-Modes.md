---
id: task-182
title: Extend specify init to Configure Transition Validation Modes
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-11-30 21:34'
updated_date: '2025-12-04 17:07'
labels:
  - workflow-artifacts
  - critical
  - 'workflow:Specified'
dependencies: []
priority: high
---

<!-- AC:END -->

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary
Extend the `specify init` command to ask users about their preferred validation mode for each workflow transition, storing the configuration in jpspec_workflow.yml.

## Interactive Init Flow

```bash
$ specify init my-project

Initializing my-project...
✓ Created directory structure
✓ Created templates

== Workflow Transition Validation Configuration ==

For each workflow transition, choose a validation mode:
- NONE: No gate, proceed immediately (default)
- KEYWORD: Require user to type approval keyword
- PULL_REQUEST: Require PR to be merged

1. Assess → Specified (after /jpspec:assess)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > 1

2. Specified → Researched (after /jpspec:specify, produces PRD)
   [1] NONE (default)
   [2] KEYWORD - Enter keyword: PRD_APPROVED
   [3] PULL_REQUEST
   > 2
   Enter approval keyword: PRD_APPROVED

3. Researched → Planned (after /jpspec:research)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > 1

4. Planned → In Implementation (after /jpspec:plan, produces ADRs)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > 3

5. In Implementation → Validated (after /jpspec:implement)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > 1

6. Validated → Deployed (after /jpspec:validate)
   [1] NONE (default)
   [2] KEYWORD
   [3] PULL_REQUEST
   > 2
   Enter approval keyword: DEPLOY_APPROVED

7. Deployed → Done (manual completion)
   [1] NONE (default)
   [2] KEYWORD
   > 1

Configuration saved to jpspec_workflow.yml
```

## Generated Configuration

```yaml
# jpspec_workflow.yml
version: "1.0"

transitions:
  - name: assess
    from: "To Do"
    to: "Assessed"
    validation: NONE

  - name: specify  
    from: "Assessed"
    to: "Specified"
    validation: KEYWORD["PRD_APPROVED"]

  - name: research
    from: "Specified"
    to: "Researched"
    validation: NONE

  - name: plan
    from: "Researched"
    to: "Planned"
    validation: PULL_REQUEST

  - name: implement
    from: "Planned"
    to: "In Implementation"
    validation: NONE

  - name: validate
    from: "In Implementation"
    to: "Validated"
    validation: NONE

  - name: operate
    from: "Validated"
    to: "Deployed"
    validation: KEYWORD["DEPLOY_APPROVED"]

  - name: complete
    from: "Deployed"
    to: "Done"
    validation: NONE
```

## Non-Interactive Mode

Support flags for CI/automation:

```bash
# All NONE (fastest)
specify init my-project --validation-mode none

# All KEYWORD with default keywords
specify init my-project --validation-mode keyword

# All PULL_REQUEST (strictest)
specify init my-project --validation-mode pull-request

# Skip validation questions entirely (use defaults)
specify init my-project --no-validation-prompts
```

## Acceptance Criteria
- [ ] AC1: Add validation mode prompts to specify init command
- [ ] AC2: Support NONE selection (default, press Enter)
- [ ] AC3: Support KEYWORD selection with custom keyword input
- [ ] AC4: Support PULL_REQUEST selection
- [ ] AC5: Generate jpspec_workflow.yml with configured validation modes
- [ ] AC6: Add --validation-mode {none|keyword|pull-request} flag for batch config
- [ ] AC7: Add --no-validation-prompts flag to skip questions (use NONE)
- [ ] AC8: Display summary of configured validation modes at end
- [ ] AC9: Support reconfiguration via `specify config validation`

## CLI Command Updates

```bash
# Initial configuration
specify init my-project

# Reconfigure validation modes
specify config validation

# View current validation configuration
specify config show validation

# Update single transition
specify config validation --transition plan --mode PULL_REQUEST
specify config validation --transition specify --mode KEYWORD["APPROVED"]
```

## Dependencies
- task-172 (Workflow Transition Validation Schema)
- task-175 (Transition Validation Mode Engine)
- task-179 (Directory Scaffolding)
<!-- SECTION:NOTES:END -->
