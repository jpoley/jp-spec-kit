---
id: task-343
title: Publish Phase 1 Release (v1.0.0) to Docker Hub
status: To Do
assignee: []
created_date: '2025-12-09 01:02'
labels:
  - release
  - devcontainer
  - publishing
dependencies:
  - task-340
  - task-341
  - task-342
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Publish first stable release of AI Coding Agents devcontainer image to Docker Hub.

Release checklist:
- All variants built and pushed to `jpoley/specflow-agents`
- Tags: `latest`, `1.0.0`, `1.0`, `1`, variant-specific tags (`minimal`, `python`, `node`)
- Docker Hub README published and formatted correctly
- GitHub release created with changelog and SBOM attachments
- Examples repository made public with working samples
- Announcement in jp-spec-kit README and blog post (if applicable)

Pre-release validation:
- All security scans passing
- All platform tests passing
- Documentation reviewed and approved

Depends on: task-340 (Documentation), task-341 (Security), task-342 (Testing)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 4 variants published to Docker Hub: jpoley/specflow-agents:{latest,minimal,python,node}
- [ ] #2 Semantic version tags published: 1.0.0, 1.0, 1
- [ ] #3 Docker Hub README published and displays correctly on hub.docker.com
- [ ] #4 GitHub release v1.0.0 created with changelog and SBOM attachments
- [ ] #5 Examples repository public at github.com/jpoley/specflow-agents-examples with 3+ samples
- [ ] #6 jp-spec-kit README updated with link to Docker Hub image
- [ ] #7 Announcement posted (blog, Twitter, or internal docs)
- [ ] #8 All pre-release validation passed: security scans, platform tests, documentation review
<!-- AC:END -->
