---
id: task-256
title: 'Implement ADR-006: AI Triage Engine Design'
status: To Do
assignee:
  - '@platform-engineer'
created_date: '2025-12-03 02:31'
labels:
  - architecture
  - security
  - ai
  - implement
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build AI-powered vulnerability triage with classification, risk scoring, clustering, and explanations. See docs/adr/ADR-006-ai-triage-engine-design.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement TriageEngine core logic in src/specify_cli/security/triage/engine.py
- [ ] #2 Implement FindingClassifier interface and default classifier
- [ ] #3 Implement 5 specialized classifiers (SQL Injection, XSS, Path Traversal, Hardcoded Secrets, Weak Crypto)
- [ ] #4 Implement Raptor risk scoring formula: (Impact × Exploitability) / Detection_Time
- [ ] #5 Implement finding clustering by CWE, file, and architectural pattern
- [ ] #6 Implement plain-English explanation generation
- [ ] #7 Benchmark AI triage accuracy >85% on known TP/FP examples
- [ ] #8 Unit tests with mocked LLM responses
<!-- AC:END -->
