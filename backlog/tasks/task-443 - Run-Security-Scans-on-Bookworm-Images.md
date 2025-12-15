---
id: task-443
title: Run Security Scans on Bookworm Images
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-11 04:17'
updated_date: '2025-12-15 02:18'
labels:
  - security
  - docker
  - infrastructure
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Perform comprehensive security scanning on new bookworm-based Docker images and compare against bullseye baseline to quantify security posture improvement
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Run Trivy scan on bookworm test image with HIGH,CRITICAL severity filter
- [ ] #2 Run Trivy scan on current bullseye image (jpoley/flowspec-agents:latest) for baseline comparison
- [ ] #3 Generate security reports in multiple formats: JSON, SARIF, and human-readable text
- [ ] #4 Document CVE count comparison (critical, high, medium, low) in docs/platform/bookworm-security-summary.md
- [ ] #5 Verify reduction in critical and high severity CVEs vs bullseye
- [ ] #6 List specific CVEs resolved by migration (e.g., CVE-2025-0938, CVE-2025-1795)
<!-- AC:END -->
