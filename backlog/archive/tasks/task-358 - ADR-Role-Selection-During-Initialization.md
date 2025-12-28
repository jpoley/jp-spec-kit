---
id: task-358
title: 'ADR: Role Selection During Initialization'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:10'
updated_date: '2025-12-15 02:17'
labels:
  - architecture
  - adr
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Document architecture decision for how users select their primary role during /flow:init or /flow:reset, and how that affects command auto-loading in VS Code
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define role selection mechanism (interactive prompt during init/reset)
- [x] #2 Document storage location and format (flowspec_workflow.yml or separate file)
- [x] #3 Specify VS Code Copilot integration impact
- [x] #4 Design extensibility for future roles
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Week 1: Core functionality (prompt, storage, env override)
Week 2: IDE integration (VS Code agent metadata)
Week 3: CLI integration (command filtering)
Week 4: Documentation and testing

## Next Steps
- Review and approve ADR
- Implement role selection prompt in init/reset
- Update VS Code agent metadata
- Test integration across platforms
<!-- SECTION:NOTES:END -->
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
# ADR: Role Selection During Initialization

## Deliverable
Created comprehensive ADR at: /home/jpoley/ps/flowspec/docs/adr/ADR-role-selection-during-initialization.md

## Key Design Decisions

### 1. Storage Location
Chose flowspec_workflow.yml extension over separate file or global config:
- Project-scoped (correct abstraction level)
- Git-tracked (team can share)
- Colocated with workflow definitions
- Single source of truth

### 2. Interactive Prompt Design
Created user-friendly role selection interface:
- 6 options: PM, Dev, Sec, QA, Ops, All
- Clear descriptions with icons
- Agent assignments shown
- Default to Developer role

### 3. Configuration Schema
Extended flowspec_workflow.yml with role_config section:
```yaml
role_config:
  primary_role: "dev"
  show_all_commands: false
  roles:
    dev:
      display_name: "Developer"
      icon: "💻"
      auto_load_agents: ["@software-architect", "@frontend-engineer"]
```

### 4. VS Code Copilot Integration
Defined how role affects VS Code experience:
- Handoff priority (role-appropriate agents first)
- Agent visibility (starred agents for selected role)
- Autocomplete filtering (role commands shown first)

### 5. Environment Variable Override
Added FLOWSPEC_PRIMARY_ROLE for per-session role switching:
- Precedence: env var > config file > default
- Enables multi-role users to switch contexts

### 6. Extensibility
Designed for easy role additions:
- Dynamic role discovery from config
- Simple schema extension
- Minimal code changes needed

## Implementation Plan
Week 1: Core functionality (prompt, storage, env override)
Week 2: IDE integration (VS Code agent metadata)
Week 3: CLI integration (command filtering)
Week 4: Documentation and testing

## Next Steps
- Review and approve ADR
- Implement role selection prompt in init/reset
- Update VS Code agent metadata
- Test integration across platforms
<!-- SECTION:NOTES:END -->
