---
id: task-352
title: Create rollback procedure and automation
status: To Do
assignee: []
created_date: '2025-12-09 01:03'
labels:
  - infrastructure
  - cicd
  - reliability
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement automated rollback capability to quickly revert to previous known-good image in case of critical issues.

**Rollback Scenarios**:
1. Critical vulnerability discovered in published image
2. Image functionality broken (e.g., CLIs not working)
3. User reports of widespread issues

**Implementation**:

1. **Rollback Manifest Generation** (automated in pipeline):
   ```json
   {
     "current_digest": "sha256:abc123...",
     "current_tags": ["latest", "v1.2.3"],
     "previous_digest": "sha256:def456...",
     "rollback_command": "docker pull jpoley/specflow-agents@sha256:def456... && ..."
   }
   ```

2. **Rollback Procedure** (manual):
   ```bash
   # 1. Identify previous good image
   PREVIOUS_DIGEST="sha256:def456..."

   # 2. Pull previous image
   docker pull jpoley/specflow-agents@$PREVIOUS_DIGEST

   # 3. Re-tag as latest
   docker tag jpoley/specflow-agents@$PREVIOUS_DIGEST \
     jpoley/specflow-agents:latest

   # 4. Push updated latest tag
   docker push jpoley/specflow-agents:latest
   ```

3. **Automated Rollback Script**:
   ```bash
   scripts/rollback-docker-image.sh <previous-digest>
   ```

4. **Verification**:
   - Pull latest and verify digest matches previous
   - Run health checks
   - Test in devcontainer

**Recovery Time Objective (RTO)**: < 15 minutes

**Testing**:
1. Simulate rollback in test environment
2. Document rollback runbook
3. Train team on rollback procedure

**Communication**:
- Notify users of rollback via GitHub Discussions
- Update Docker Hub description with status
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rollback manifest generated and uploaded for every build
- [ ] #2 Rollback procedure documented in runbook
- [ ] #3 Rollback script created and tested
- [ ] #4 Rollback can be executed in < 15 minutes
- [ ] #5 Rollback verified to restore functionality
- [ ] #6 Communication template created for rollback notifications
<!-- AC:END -->
