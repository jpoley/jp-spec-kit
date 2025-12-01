---
id: task-137
title: Add Pipecat voice dependencies to pyproject.toml
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 00:59'
labels:
  - implement
  - voice
  - setup
  - phase1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add pipecat-ai with optional extras [daily,deepgram,openai,cartesia] as an optional dependency group named 'voice'. Reference: docs/research/pipecat-voice-integration-summary.md Section 1.2 Dependencies
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 pyproject.toml contains [project.optional-dependencies] voice = ["pipecat-ai[daily,deepgram,openai,cartesia]>=0.0.50"]
- [x] #2 Command `uv sync --extra voice` completes without dependency resolution errors
- [x] #3 Command `python -c "import pipecat"` executes without ImportError
- [x] #4 pipecat version in uv.lock matches constraint (>=0.0.50)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added pipecat-ai with extras [daily,deepgram,openai,cartesia]>=0.0.50 to pyproject.toml.

Verification:
- uv sync --extra voice completes successfully
- pipecat-ai 0.0.96 installed (meets >=0.0.50 constraint)
- Import test passes: python -c "import pipecat" works
- uv.lock contains pipecat-ai version 0.0.96

Changes:
- Modified pyproject.toml to add voice optional dependency group
<!-- SECTION:NOTES:END -->
