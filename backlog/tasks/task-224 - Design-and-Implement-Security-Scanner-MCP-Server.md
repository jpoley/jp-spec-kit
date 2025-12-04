---
id: task-224
title: Design and Implement Security Scanner MCP Server
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 02:16'
updated_date: '2025-12-04 16:32'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create MCP server exposing security scanning capabilities for tool composition. Enables other agents to query security findings, cross-repo dashboards, and IDE integrations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design MCP server schema with tools and resources
- [ ] #2 Implement security_scan tool
- [ ] #3 Implement security_triage tool
- [ ] #4 Implement security_fix tool
- [ ] #5 Expose security://findings resource
- [ ] #6 Expose security://status resource
- [ ] #7 Expose security://config resource
- [ ] #8 Add MCP server to .mcp.json configuration
- [ ] #9 Write MCP server documentation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
CORRECTED IMPLEMENTATION PLAN:

MCP server exposes data and invokes skills - NO LLM API calls.

## What to Build

1. MCP Server Skeleton (Pure Python)
   - Implement security_scan tool (runs Semgrep via subprocess)
   - Implement security_triage tool (returns skill invocation instruction)
   - Implement security_fix tool (returns skill invocation instruction)
   - Implement security://findings resource (returns JSON data)
   - Implement security://status resource (returns computed stats)

2. Scanner Integration (subprocess only)
   - Run Semgrep via subprocess.run()
   - Parse Semgrep JSON output
   - Write findings to docs/security/findings.json
   - NO AI processing

3. Skill Invocation Instructions
   - security_triage returns: { action: invoke_skill, skill: .claude/skills/security-triage.md }
   - security_fix returns: { action: invoke_skill, skill: .claude/skills/security-fix.md }
   - AI coding tool executes skills using its own LLM access

## What NOT to Build

- ❌ LLM API integration (no import anthropic)
- ❌ API key handling
- ❌ AI triage engine in MCP server
- ❌ Prompt execution in MCP server

## Testing

- Test Semgrep subprocess execution
- Test MCP tool returns correct instructions
- Test MCP resources return correct data
- Do NOT test AI inference (that's skill tests)

## Dependencies

- mcp-python (MCP protocol)
- subprocess (Python stdlib)
- json (Python stdlib)
- NO anthropic package
- NO openai package

CRITICAL: ZERO API KEYS. ZERO LLM SDK CALLS.
<!-- SECTION:PLAN:END -->
