# Agent Architecture Diagrams

This document provides visual representations of the JP Spec Kit agent ecosystem, showing all 16 workflow agents, 13 AI coding platforms, 9 MCP servers, and how they interconnect across the SDD workflow.

## Quick Reference

| Category | Count | Description |
|----------|-------|-------------|
| Workflow Agents | 16 | SDD workflow specialists (5 inner loop, 11 outer loop) |
| AI Coding Platforms | 13 | Supported IDE/CLI integrations |
| MCP Servers | 9 | Tool integrations via Model Context Protocol |
| Workflow States | 9 | Task progression states |
| Slash Commands | 7 | `/jpspec:*` workflow commands |

---

## 1. Complete Workflow State Machine

### Mermaid Diagram

```mermaid
stateDiagram-v2
    [*] --> ToDo: Task Created

    ToDo --> Assessed: /jpspec:assess
    Assessed --> Specified: /jpspec:specify
    Specified --> Researched: /jpspec:research
    Specified --> Planned: /jpspec:plan (skip research)
    Researched --> Planned: /jpspec:plan
    Planned --> InImpl: /jpspec:implement
    InImpl --> Validated: /jpspec:validate
    Validated --> Deployed: /jpspec:operate

    Deployed --> Done: Manual close
    Validated --> Done: Manual close
    InImpl --> Done: Manual close

    InImpl --> Planned: Rework
    Validated --> InImpl: Rework
    Deployed --> Validated: Rollback

    Done --> [*]

    state ToDo {
        [*] --> waiting
    }
    state Assessed {
        [*] --> complexity_evaluated
    }
    state Specified {
        [*] --> requirements_captured
    }
    state Researched {
        [*] --> research_complete
    }
    state Planned {
        [*] --> architecture_defined
    }
    state InImpl {
        [*] --> coding
    }
    state Validated {
        [*] --> qa_passed
    }
    state Deployed {
        [*] --> in_production
    }
```

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SDD WORKFLOW STATE MACHINE                            │
└─────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   TO DO     │ ◄── Task Created
                              └──────┬──────┘
                                     │ /jpspec:assess
                                     ▼
                              ┌─────────────┐
                              │  ASSESSED   │ ◄── Complexity evaluated
                              └──────┬──────┘
                                     │ /jpspec:specify
                                     ▼
                              ┌─────────────┐
                              │  SPECIFIED  │ ◄── PRD + Tasks created
                              └──────┬──────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │ /jpspec:plan   │ /jpspec:research
                    │ (skip research)│                │
                    ▼                ▼                │
              ┌─────────────┐ ┌─────────────┐        │
              │   PLANNED   │ │ RESEARCHED  │────────┘
              └──────┬──────┘ └──────┬──────┘
                     │               │ /jpspec:plan
                     │               ▼
                     │        ┌─────────────┐
                     └───────►│   PLANNED   │ ◄── ADRs created
                              └──────┬──────┘
                                     │ /jpspec:implement
                                     ▼
                              ┌──────────────────┐
        ┌──── Rework ◄────────│IN IMPLEMENTATION│ ◄── Code written
        │                     └──────┬──────────┘
        │                            │ /jpspec:validate
        │                            ▼
        │                     ┌─────────────┐
        │     ┌─ Rework ◄─────│  VALIDATED  │ ◄── QA + Security passed
        │     │               └──────┬──────┘
        │     │                      │ /jpspec:operate
        │     │                      ▼
        │     │               ┌─────────────┐
        │     │  Rollback ◄───│  DEPLOYED   │ ◄── In production
        │     │               └──────┬──────┘
        │     │                      │ Manual
        │     │                      ▼
        │     │               ┌─────────────┐
        └─────┴──────────────►│    DONE     │ ◄── Work complete
                              └─────────────┘
```

---

## 2. Agent-to-Workflow Mapping

### Mermaid Diagram

```mermaid
flowchart TB
    subgraph OUTER["OUTER LOOP (11 Agents) - Governance & Safety"]
        direction TB
        WA[workflow-assessor]
        PRM[product-requirements-manager]
        RES[researcher]
        BV[business-validator]
        SA[software-architect]
        PE[platform-engineer]
        QG[quality-guardian]
        SBD[secure-by-design-engineer]
        TW[tech-writer]
        RM[release-manager]
        SRE[sre-agent]
    end

    subgraph INNER["INNER LOOP (5 Agents) - Developer Velocity"]
        direction TB
        FE[frontend-engineer]
        BE[backend-engineer]
        AI[ai-ml-engineer]
        FCR[frontend-code-reviewer]
        BCR[backend-code-reviewer]
    end

    subgraph WORKFLOWS["/jpspec Commands"]
        direction LR
        A[assess] --> S[specify] --> R[research] --> P[plan] --> I[implement] --> V[validate] --> O[operate]
    end

    WA --> A
    PRM --> S
    RES --> R
    BV --> R
    SA --> P
    PE --> P
    FE --> I
    BE --> I
    AI --> I
    FCR --> I
    BCR --> I
    QG --> V
    SBD --> V
    TW --> V
    RM --> V
    SRE --> O
```

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         AGENT-TO-WORKFLOW MAPPING                               │
└─────────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║  OUTER LOOP AGENTS (11) - Governance, Safety, Reliability                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐             ║
║  │ workflow-       │   │ product-        │   │ researcher      │             ║
║  │ assessor        │   │ requirements-   │   │                 │             ║
║  │ @workflow-      │   │ manager         │   │ @researcher     │             ║
║  │ assessor        │   │ @pm-planner     │   │                 │             ║
║  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘             ║
║           │                     │                     │                       ║
║           ▼                     ▼                     ▼                       ║
║      /jpspec:assess       /jpspec:specify      /jpspec:research              ║
║                                                       │                       ║
║  ┌─────────────────┐                          ┌──────┴────────┐              ║
║  │ business-       │                          │ software-     │              ║
║  │ validator       │                          │ architect     │              ║
║  │ @business-      │──────────────────────────│ @software-    │              ║
║  │ validator       │                          │ architect     │              ║
║  └─────────────────┘                          └───────┬───────┘              ║
║                                                       │                       ║
║  ┌─────────────────┐                          ┌───────┴───────┐              ║
║  │ platform-       │                          │               │              ║
║  │ engineer        │──────────────────────────┤ /jpspec:plan  │              ║
║  │ @platform-      │                          │               │              ║
║  │ engineer        │                          └───────────────┘              ║
║  └─────────────────┘                                                         ║
║                                                                               ║
║  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐             ║
║  │ quality-        │   │ secure-by-      │   │ tech-writer    │             ║
║  │ guardian        │   │ design-engineer │   │                │             ║
║  │ @quality-       │   │ @secure-by-     │   │ @tech-writer   │             ║
║  │ guardian        │   │ design-engineer │   │                │             ║
║  └────────┬────────┘   └────────┬────────┘   └───────┬────────┘             ║
║           │                     │                     │                       ║
║           └─────────────────────┼─────────────────────┘                       ║
║                                 ▼                                             ║
║  ┌─────────────────┐     /jpspec:validate    ┌─────────────────┐             ║
║  │ release-manager │            │            │ sre-agent       │             ║
║  │ @release-       │────────────┘            │ @sre-agent      │             ║
║  │ manager         │                         └────────┬────────┘             ║
║  └─────────────────┘                                  │                       ║
║                                                       ▼                       ║
║                                                /jpspec:operate               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║  INNER LOOP AGENTS (5) - Developer Velocity                                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐             ║
║  │ frontend-       │   │ backend-        │   │ ai-ml-engineer  │             ║
║  │ engineer        │   │ engineer        │   │                 │             ║
║  │ @frontend-      │   │ @backend-       │   │ @ai-ml-engineer │             ║
║  │ engineer        │   │ engineer        │   │                 │             ║
║  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘             ║
║           │                     │                     │                       ║
║           └─────────────────────┼─────────────────────┘                       ║
║                                 ▼                                             ║
║                          /jpspec:implement                                    ║
║                                 ▲                                             ║
║           ┌─────────────────────┼─────────────────────┐                       ║
║           │                     │                     │                       ║
║  ┌────────┴────────┐   ┌────────┴────────┐                                   ║
║  │ frontend-code-  │   │ backend-code-   │                                   ║
║  │ reviewer        │   │ reviewer        │                                   ║
║  │ @frontend-code- │   │ @backend-code-  │                                   ║
║  │ reviewer        │   │ reviewer        │                                   ║
║  └─────────────────┘   └─────────────────┘                                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. MCP Server Integrations

### Mermaid Diagram

```mermaid
flowchart TB
    subgraph MCP["MCP SERVERS (9)"]
        direction TB
        GH[github<br/>GitHub API]
        SER[serena<br/>LSP Code Understanding]
        PW[playwright-test<br/>Browser Automation]
        TR[trivy<br/>Container/IaC Security]
        SG[semgrep<br/>SAST Scanning]
        SH[shadcn-ui<br/>UI Components]
        CD[chrome-devtools<br/>Browser DevTools]
        BL[backlog<br/>Task Management]
        SEC[jpspec-security<br/>Security Scanner]
    end

    subgraph AGENTS["WORKFLOW AGENTS"]
        direction TB
        IMPL[Implementation Agents]
        QA[Quality Agents]
        SECAG[Security Agents]
        SRE[SRE Agent]
    end

    GH --> IMPL
    GH --> SRE
    SER --> IMPL
    PW --> QA
    PW --> SECAG
    TR --> SECAG
    TR --> SRE
    SG --> SECAG
    SH --> IMPL
    CD --> QA
    BL --> IMPL
    BL --> QA
    SEC --> SECAG
```

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MCP SERVER INTEGRATIONS                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                              MCP SERVERS (9)                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ DEVELOPMENT & CODE                                                      │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                         │ │
│  │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │ │
│  │  │    github       │   │    serena       │   │   shadcn-ui     │       │ │
│  │  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤       │ │
│  │  │ GitHub API:     │   │ LSP-grade code  │   │ UI component    │       │ │
│  │  │ repos, issues,  │   │ understanding & │   │ library access  │       │ │
│  │  │ PRs, search,    │   │ safe semantic   │   │ and install     │       │ │
│  │  │ workflows       │   │ edits           │   │                 │       │ │
│  │  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘       │ │
│  │           │                     │                     │                 │ │
│  │           └─────────────────────┼─────────────────────┘                 │ │
│  │                                 ▼                                       │ │
│  │                    Implementation Agents                                │ │
│  │                    (frontend, backend, ai-ml)                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ SECURITY & COMPLIANCE                                                   │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                         │ │
│  │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │ │
│  │  │    semgrep      │   │     trivy       │   │ jpspec-security │       │ │
│  │  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤       │ │
│  │  │ SAST code       │   │ Container/IaC   │   │ JP Spec Kit     │       │ │
│  │  │ scanning for    │   │ security scans  │   │ Security:       │       │ │
│  │  │ vulnerabilities │   │ and SBOM        │   │ scan, triage,   │       │ │
│  │  │                 │   │ generation      │   │ fix with AI     │       │ │
│  │  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘       │ │
│  │           │                     │                     │                 │ │
│  │           └─────────────────────┼─────────────────────┘                 │ │
│  │                                 ▼                                       │ │
│  │                     Security Agents                                     │ │
│  │                     (secure-by-design-engineer)                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ TESTING & QUALITY                                                       │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                         │ │
│  │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │ │
│  │  │ playwright-test │   │ chrome-devtools │   │    backlog      │       │ │
│  │  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤       │ │
│  │  │ Browser auto-   │   │ Chrome DevTools │   │ Task management │       │ │
│  │  │ mation for E2E  │   │ Protocol for    │   │ create, update, │       │ │
│  │  │ testing         │   │ inspection &    │   │ search tasks    │       │ │
│  │  │                 │   │ performance     │   │ with kanban     │       │ │
│  │  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘       │ │
│  │           │                     │                     │                 │ │
│  │           └─────────────────────┼─────────────────────┘                 │ │
│  │                                 ▼                                       │ │
│  │                       Quality Agents                                    │ │
│  │                       (quality-guardian)                                │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Supported AI Coding Platforms

### Mermaid Diagram

```mermaid
flowchart TB
    subgraph CLI["CLI-Based (6)"]
        direction TB
        CL[Claude Code<br/>.claude/]
        GE[Gemini CLI<br/>.gemini/]
        QW[Qwen Code<br/>.qwen/]
        OC[opencode<br/>.opencode/]
        CX[Codex CLI<br/>.codex/]
        AQ[Amazon Q CLI<br/>.amazonq/]
    end

    subgraph IDE["IDE-Based (7)"]
        direction TB
        CP[GitHub Copilot<br/>.github/]
        CU[Cursor<br/>.cursor/]
        WS[Windsurf<br/>.windsurf/]
        KC[Kilo Code<br/>.kilocode/]
        AU[Auggie<br/>.augment/]
        CB[CodeBuddy<br/>.codebuddy/]
        RO[Roo Code<br/>.roo/]
    end

    subgraph WORKFLOW["SDD Workflow"]
        direction LR
        W1[assess] --> W2[specify] --> W3[plan] --> W4[implement] --> W5[validate] --> W6[operate]
    end

    CLI --> WORKFLOW
    IDE --> WORKFLOW
```

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       SUPPORTED AI CODING PLATFORMS (13)                        │
└─────────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════╗
║  CLI-BASED PLATFORMS (6) - Requires CLI installation                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐             ║
║  │  Claude Code    │   │   Gemini CLI    │   │   Qwen Code     │             ║
║  │  ─────────────  │   │  ─────────────  │   │  ─────────────  │             ║
║  │  Folder: .claude│   │  Folder: .gemini│   │  Folder: .qwen  │             ║
║  │  Config: CLAUDE │   │  Requires CLI   │   │  Requires CLI   │             ║
║  │         .md     │   │  install        │   │  install        │             ║
║  └─────────────────┘   └─────────────────┘   └─────────────────┘             ║
║                                                                               ║
║  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐             ║
║  │    opencode     │   │   Codex CLI     │   │  Amazon Q CLI   │             ║
║  │  ─────────────  │   │  ─────────────  │   │  ─────────────  │             ║
║  │  Folder:        │   │  Folder: .codex │   │  Folder:        │             ║
║  │  .opencode      │   │  Requires CLI   │   │  .amazonq       │             ║
║  │  Requires CLI   │   │  install        │   │  Requires CLI   │             ║
║  └─────────────────┘   └─────────────────┘   └─────────────────┘             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════════╗
║  IDE-BASED PLATFORMS (7) - Built into IDE, no CLI required                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐             ║
║  │ GitHub Copilot  │   │     Cursor      │   │    Windsurf     │             ║
║  │  ─────────────  │   │  ─────────────  │   │  ─────────────  │             ║
║  │  Folder: .github│   │  Folder: .cursor│   │  Folder:        │             ║
║  │  VS Code/IDE    │   │  Cursor IDE     │   │  .windsurf      │             ║
║  │  extension      │   │  native         │   │  Codeium IDE    │             ║
║  └─────────────────┘   └─────────────────┘   └─────────────────┘             ║
║                                                                               ║
║  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐             ║
║  │   Kilo Code     │   │   Auggie CLI    │   │   CodeBuddy     │             ║
║  │  ─────────────  │   │  ─────────────  │   │  ─────────────  │             ║
║  │  Folder:        │   │  Folder:        │   │  Folder:        │             ║
║  │  .kilocode      │   │  .augment       │   │  .codebuddy     │             ║
║  │  IDE extension  │   │  CLI available  │   │  CLI available  │             ║
║  └─────────────────┘   └─────────────────┘   └─────────────────┘             ║
║                                                                               ║
║                        ┌─────────────────┐                                    ║
║                        │    Roo Code     │                                    ║
║                        │  ─────────────  │                                    ║
║                        │  Folder: .roo   │                                    ║
║                        │  IDE extension  │                                    ║
║                        └─────────────────┘                                    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 5. Complete System Overview

### Mermaid Diagram

```mermaid
flowchart TB
    subgraph USER["USER"]
        DEV[Developer]
    end

    subgraph PLATFORMS["AI CODING PLATFORMS (13)"]
        direction LR
        P1[Claude Code]
        P2[Copilot]
        P3[Cursor]
        P4[...]
    end

    subgraph WORKFLOW["SDD WORKFLOW COMMANDS"]
        direction LR
        C1["/jpspec:assess"]
        C2["/jpspec:specify"]
        C3["/jpspec:research"]
        C4["/jpspec:plan"]
        C5["/jpspec:implement"]
        C6["/jpspec:validate"]
        C7["/jpspec:operate"]
    end

    subgraph AGENTS["WORKFLOW AGENTS (16)"]
        direction TB
        subgraph OUTER["Outer Loop (11)"]
            A1[workflow-assessor]
            A2[pm-planner]
            A3[researcher]
            A4[business-validator]
            A5[software-architect]
            A6[platform-engineer]
            A7[quality-guardian]
            A8[secure-by-design]
            A9[tech-writer]
            A10[release-manager]
            A11[sre-agent]
        end
        subgraph INNER["Inner Loop (5)"]
            A12[frontend-engineer]
            A13[backend-engineer]
            A14[ai-ml-engineer]
            A15[frontend-reviewer]
            A16[backend-reviewer]
        end
    end

    subgraph MCP["MCP SERVERS (9)"]
        direction TB
        M1[github]
        M2[serena]
        M3[playwright-test]
        M4[trivy]
        M5[semgrep]
        M6[shadcn-ui]
        M7[chrome-devtools]
        M8[backlog]
        M9[jpspec-security]
    end

    subgraph ARTIFACTS["OUTPUT ARTIFACTS"]
        direction TB
        AR1[Assessment Reports]
        AR2[PRDs & Tasks]
        AR3[Research Reports]
        AR4[ADRs]
        AR5[Source Code & Tests]
        AR6[QA & Security Reports]
        AR7[Deployments]
    end

    DEV --> PLATFORMS
    PLATFORMS --> WORKFLOW
    WORKFLOW --> AGENTS
    AGENTS --> MCP
    AGENTS --> ARTIFACTS
```

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE SYSTEM ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                                 DEVELOPER                                     │
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         AI CODING PLATFORMS (13)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Claude   │ │ Copilot  │ │ Cursor   │ │ Gemini   │ │ Windsurf │ │  ...   │ │
│  │ Code     │ │          │ │          │ │ CLI      │ │          │ │        │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                      SDD WORKFLOW COMMANDS (/jpspec:*)                        │
│                                                                               │
│   assess ──► specify ──► research ──► plan ──► implement ──► validate ──► operate │
│      │          │           │          │           │            │           │
└──────┼──────────┼───────────┼──────────┼───────────┼────────────┼───────────┼───┘
       │          │           │          │           │            │           │
       ▼          ▼           ▼          ▼           ▼            ▼           ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW AGENTS (16)                                  │
│                                                                               │
│  ╔═══════════════════════════════════════════════════════════════════════╗   │
│  ║ OUTER LOOP (11) - Governance & Safety                                 ║   │
│  ║ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           ║   │
│  ║ │ workflow-  │ │ pm-planner │ │ researcher │ │ business-  │           ║   │
│  ║ │ assessor   │ │            │ │            │ │ validator  │           ║   │
│  ║ └────────────┘ └────────────┘ └────────────┘ └────────────┘           ║   │
│  ║ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           ║   │
│  ║ │ software-  │ │ platform-  │ │ quality-   │ │ secure-by- │           ║   │
│  ║ │ architect  │ │ engineer   │ │ guardian   │ │ design-eng │           ║   │
│  ║ └────────────┘ └────────────┘ └────────────┘ └────────────┘           ║   │
│  ║ ┌────────────┐ ┌────────────┐ ┌────────────┐                          ║   │
│  ║ │ tech-      │ │ release-   │ │ sre-agent  │                          ║   │
│  ║ │ writer     │ │ manager    │ │            │                          ║   │
│  ║ └────────────┘ └────────────┘ └────────────┘                          ║   │
│  ╚═══════════════════════════════════════════════════════════════════════╝   │
│                                                                               │
│  ╔═══════════════════════════════════════════════════════════════════════╗   │
│  ║ INNER LOOP (5) - Developer Velocity                                   ║   │
│  ║ ┌────────────┐ ┌────────────┐ ┌────────────┐                          ║   │
│  ║ │ frontend-  │ │ backend-   │ │ ai-ml-     │                          ║   │
│  ║ │ engineer   │ │ engineer   │ │ engineer   │                          ║   │
│  ║ └────────────┘ └────────────┘ └────────────┘                          ║   │
│  ║ ┌────────────┐ ┌────────────┐                                         ║   │
│  ║ │ frontend-  │ │ backend-   │                                         ║   │
│  ║ │ reviewer   │ │ reviewer   │                                         ║   │
│  ║ └────────────┘ └────────────┘                                         ║   │
│  ╚═══════════════════════════════════════════════════════════════════════╝   │
│                                                                               │
└─────────────────────────────────────┬─────────────────────────────────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
           ▼                          ▼                          ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│    MCP SERVERS (9)  │   │  OUTPUT ARTIFACTS   │   │   TASK STATES (9)   │
│                     │   │                     │   │                     │
│  ┌───────────────┐  │   │  • Assessment.md    │   │  • To Do            │
│  │    github     │  │   │  • PRD.md           │   │  • Assessed         │
│  │    serena     │  │   │  • Research.md      │   │  • Specified        │
│  │ playwright    │  │   │  • ADR-*.md         │   │  • Researched       │
│  │    trivy      │  │   │  • src/ tests/      │   │  • Planned          │
│  │   semgrep     │  │   │  • QA-report.md     │   │  • In Implementation│
│  │  shadcn-ui    │  │   │  • Security.md      │   │  • Validated        │
│  │ chrome-devtools│  │   │  • deploy/          │   │  • Deployed         │
│  │   backlog     │  │   │                     │   │  • Done             │
│  │ jpspec-security│  │   │                     │   │                     │
│  └───────────────┘  │   │                     │   │                     │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
```

---

## 6. Agent-MCP Integration Matrix

### Which MCP servers each agent type uses:

| Agent | github | serena | playwright | trivy | semgrep | shadcn | devtools | backlog | security |
|-------|:------:|:------:|:----------:|:-----:|:-------:|:------:|:--------:|:-------:|:--------:|
| **workflow-assessor** | | | | | | | | ✓ | |
| **pm-planner** | | | | | | | | ✓ | |
| **researcher** | ✓ | | | | | | | | |
| **business-validator** | ✓ | | | | | | | | |
| **software-architect** | ✓ | ✓ | | | | | | ✓ | |
| **platform-engineer** | ✓ | | | ✓ | | | | ✓ | |
| **frontend-engineer** | ✓ | ✓ | | | | ✓ | ✓ | ✓ | |
| **backend-engineer** | ✓ | ✓ | | | | | | ✓ | |
| **ai-ml-engineer** | ✓ | ✓ | | | | | | ✓ | |
| **frontend-reviewer** | ✓ | ✓ | | | | | ✓ | | |
| **backend-reviewer** | ✓ | ✓ | | | ✓ | | | | |
| **quality-guardian** | | | ✓ | | | | ✓ | ✓ | |
| **secure-by-design** | | | ✓ | ✓ | ✓ | | | | ✓ |
| **tech-writer** | ✓ | | | | | | | | |
| **release-manager** | ✓ | | | | | | | ✓ | |
| **sre-agent** | ✓ | | | ✓ | | | | ✓ | |

### ASCII Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         AGENT-MCP INTEGRATION MATRIX                            │
└─────────────────────────────────────────────────────────────────────────────────┘

                         M C P   S E R V E R S
                    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
                    │ g │ s │ p │ t │ s │ s │ c │ b │ j │
                    │ i │ e │ l │ r │ e │ h │ h │ a │ p │
                    │ t │ r │ a │ i │ m │ a │ r │ c │ s │
                    │ h │ e │ y │ v │ g │ d │ o │ k │ e │
                    │ u │ n │ w │ y │ r │ c │ m │ l │ c │
                    │ b │ a │ r │   │ e │ n │ e │ o │   │
                    │   │   │ i │   │ p │   │   │ g │   │
A                   │   │   │ g │   │   │   │   │   │   │
G ──────────────────┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
E workflow-assessor │   │   │   │   │   │   │   │ ● │   │
N pm-planner        │   │   │   │   │   │   │   │ ● │   │
T researcher        │ ● │   │   │   │   │   │   │   │   │
S business-validator│ ● │   │   │   │   │   │   │   │   │
  software-architect│ ● │ ● │   │   │   │   │   │ ● │   │
  platform-engineer │ ● │   │   │ ● │   │   │   │ ● │   │
  frontend-engineer │ ● │ ● │   │   │   │ ● │ ● │ ● │   │
  backend-engineer  │ ● │ ● │   │   │   │   │   │ ● │   │
  ai-ml-engineer    │ ● │ ● │   │   │   │   │   │ ● │   │
  frontend-reviewer │ ● │ ● │   │   │   │   │ ● │   │   │
  backend-reviewer  │ ● │ ● │   │   │ ● │   │   │   │   │
  quality-guardian  │   │   │ ● │   │   │   │ ● │ ● │   │
  secure-by-design  │   │   │ ● │ ● │ ● │   │   │   │ ● │
  tech-writer       │ ● │   │   │   │   │   │   │   │   │
  release-manager   │ ● │   │   │   │   │   │   │ ● │   │
  sre-agent         │ ● │   │   │ ● │   │   │   │ ● │   │
                    └───┴───┴───┴───┴───┴───┴───┴───┴───┘

Legend: ● = Uses this MCP server
```

---

## 7. Workflow Command Detail

### Command-Agent-Artifact Summary

| Command | Agents | Input State(s) | Output State | Output Artifacts |
|---------|--------|----------------|--------------|------------------|
| `/jpspec:assess` | workflow-assessor | To Do | Assessed | `docs/assess/{feature}-assessment.md` |
| `/jpspec:specify` | pm-planner | Assessed | Specified | `docs/prd/{feature}.md`, backlog tasks |
| `/jpspec:research` | researcher, business-validator | Specified | Researched | `docs/research/{feature}-*.md` |
| `/jpspec:plan` | software-architect, platform-engineer | Specified, Researched | Planned | `docs/adr/ADR-*.md` |
| `/jpspec:implement` | frontend-eng, backend-eng, ai-ml-eng, reviewers | Planned | In Implementation | `src/`, `tests/` |
| `/jpspec:validate` | quality-guardian, secure-by-design, tech-writer, release-mgr | In Implementation | Validated | `docs/qa/`, `docs/security/` |
| `/jpspec:operate` | sre-agent | Validated | Deployed | `deploy/` |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         JP SPEC KIT - QUICK REFERENCE                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  WORKFLOW AGENTS: 16 total                                                      │
│    • Inner Loop (5): frontend-eng, backend-eng, ai-ml-eng, 2 reviewers          │
│    • Outer Loop (11): assessor, pm, researcher, validator, architect,           │
│                       platform-eng, qa, security, tech-writer, release, sre     │
│                                                                                 │
│  AI PLATFORMS: 13 supported                                                     │
│    • CLI: Claude Code, Gemini, Qwen, opencode, Codex, Amazon Q                  │
│    • IDE: Copilot, Cursor, Windsurf, Kilo, Auggie, CodeBuddy, Roo               │
│                                                                                 │
│  MCP SERVERS: 9 integrations                                                    │
│    • Dev: github, serena, shadcn-ui                                             │
│    • Security: trivy, semgrep, jpspec-security                                  │
│    • Testing: playwright-test, chrome-devtools                                  │
│    • Workflow: backlog                                                          │
│                                                                                 │
│  STATES: To Do → Assessed → Specified → Researched → Planned →                  │
│          In Implementation → Validated → Deployed → Done                        │
│                                                                                 │
│  COMMANDS: /jpspec:assess, specify, research, plan, implement, validate, operate│
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [Agent Loop Classification](./agent-loop-classification.md)
- [Workflow Configuration](../../jpspec_workflow.yml)
- [MCP Configuration](../../.mcp.json)
- [Inner Loop Reference](./inner-loop.md)
- [Outer Loop Reference](./outer-loop.md)
