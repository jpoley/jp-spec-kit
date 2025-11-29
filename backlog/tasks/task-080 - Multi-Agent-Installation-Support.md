---
id: task-080
title: Multi-Agent Installation Support
status: Done
assignee:
  - '@claude-agent-2'
created_date: '2025-11-27 21:53'
updated_date: '2025-11-29 05:47'
labels:
  - specify-cli
  - feature
  - multi-agent
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to install spec-kit for multiple AI coding agents (not just one) during 'specify init'. Teams often use mixed agents (Claude for backend, Copilot for frontend). Implementation: Interactive multi-select with checkboxes, comma-separated --ai flag support (e.g., --ai claude,copilot,cursor). Agent directories are already independent (no conflicts). Feasibility: HIGH, 1-3 days effort.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement parse_agent_list() for comma-separated input
- [x] #2 Create multi-select UI with checkbox interface
- [x] #3 Update init() to accept multiple agents via --ai flag
- [x] #4 Implement download logic for multiple templates
- [x] #5 Update tool checks for multiple CLI-based agents
- [x] #6 Maintain backward compatibility (single agent still works)
- [x] #7 Update documentation with multi-agent examples
- [x] #8 Create tests for multi-agent combinations
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented multi-agent installation support with full backward compatibility.

Key Changes:
- Added parse_agent_list() to parse comma-separated agent input
- Created select_multiple_with_checkboxes() for interactive multi-select UI
- Updated init() command to accept --ai flag with multiple agents
- Modified download_and_extract_two_stage() and download_and_extract_template() to support list of agents
- Enhanced tool checking to validate all selected CLI-based agents
- Updated security notices to show all agent folders
- Added comprehensive test suite (28 new tests, all passing)
- Updated README.md with multi-agent examples

Backward Compatibility:
- Single agent usage still works: --ai claude
- Function signatures support both str and list[str] via type union
- All existing tests pass (294 total tests)

Testing:
- Unit tests for parse_agent_list() edge cases
- Validation tests for agent combinations
- Tool checking tests for CLI vs IDE agents
- Agent folder uniqueness tests
- Backward compatibility tests
<!-- SECTION:NOTES:END -->
