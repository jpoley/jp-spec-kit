---
id: task-293
title: LLM Customization Accuracy Tests
status: To Do
assignee:
  - '@adare'
created_date: '2025-12-04 16:20'
updated_date: '2026-01-06 18:52'
labels:
  - constitution-cleanup
dependencies:
  - task-244
priority: high
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Verify LLM customization generates correct repo facts with 90%+ accuracy
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test Python project: detects pytest, ruff, GitHub Actions
- [ ] #2 Test TypeScript project: detects jest, eslint, prettier, npm/pnpm
- [ ] #3 Test Go project: detects go test, golangci-lint, Go modules
- [ ] #4 Test multi-language project: detects all languages correctly
- [ ] #5 Test edge case: empty repo with only README
- [ ] #6 Accuracy target: 90%+ correct detections
<!-- AC:END -->
