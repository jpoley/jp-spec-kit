---
id: task-218
title: Write Comprehensive Security Commands Documentation
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-05 16:44'
labels:
  - security
  - documentation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create user documentation, command reference, CI/CD integration guides, and security best practices.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Security Quickstart Guide (docs/guides/security-quickstart.md)
- [x] #2 Command Reference (docs/reference/jpspec-security-commands.md)
- [x] #3 CI/CD Integration Examples (GitHub Actions, GitLab, Jenkins)
- [x] #4 Threat Model and Limitations documentation
- [x] #5 Privacy Policy for AI data usage
- [x] #6 Custom Rule Writing Guide
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Write Comprehensive Security Commands Documentation

### Overview
Create complete user-facing documentation including quickstart, command reference, CI/CD guides, and best practices.

### Step-by-Step Implementation

#### Step 1: Security Quickstart Guide (2 hours)
**File**: `docs/guides/security-quickstart.md`

Sections:
1. Installation verification
2. First scan (5-minute tutorial)
3. Understanding results
4. Fixing your first vulnerability
5. Generating audit report

#### Step 2: Command Reference (3 hours)
**File**: `docs/reference/jpspec-security-commands.md`

Document all commands:
- `specify security scan` (all flags, examples)
- `specify security triage` (all flags, examples)
- `specify security fix` (all flags, examples)
- `specify security audit` (all flags, examples)
- `specify security policy` (subcommands)
- `specify security config` (subcommands)

Format: Command → Description → Syntax → Flags → Examples → Exit Codes

#### Step 3: CI/CD Integration Guide (2 hours)
**File**: `docs/guides/security-cicd-integration.md`

Already exists from platform design, enhance with:
- Step-by-step GitHub Actions setup
- Step-by-step GitLab CI setup
- Jenkins pipeline example
- CircleCI example
- Troubleshooting common CI issues

#### Step 4: Threat Model and Limitations (2 hours)
**File**: `docs/security/threat-model.md`

Sections:
1. What /jpspec:security protects against
2. What it does NOT protect against
3. Known limitations (SAST only, no runtime analysis)
4. Complementary tools (DAST, dependency scanning)
5. Security assumptions

#### Step 5: Privacy Policy for AI (1 hour)
**File**: `docs/security/ai-privacy-policy.md`

Sections:
1. What data is sent to AI models
2. Data retention policies
3. Opt-out instructions
4. GDPR/CCPA compliance
5. Enterprise deployment options (self-hosted models)

#### Step 6: Custom Rule Writing Guide (2 hours)
**File**: `docs/guides/custom-security-rules.md`

Sections:
1. Semgrep rule syntax primer
2. Creating custom rules
3. Testing rules
4. Contributing rules upstream
5. Example rules library

### Dependencies
- All security commands implemented
- Platform design documents

### Estimated Effort
**Total**: 12 hours (1.5 days)
<!-- SECTION:PLAN:END -->
