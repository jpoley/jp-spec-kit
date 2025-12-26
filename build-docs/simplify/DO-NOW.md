# Next Steps: Flowspec Flexible Orchestration

> **Note:** Lessons learned from previous failures are documented in [FAILURE-LEARNINGS.md](./FAILURE-LEARNINGS.md)

---

## ⚠️ CRITICAL REQUIREMENTS - READ FIRST ⚠️

### Honesty is MANDATORY

**NEVER:**
- ❌ Lie about time spent (actual timestamps only)
- ❌ Claim something works when it doesn't
- ❌ Create fake/stub code and call it "implemented"
- ❌ Write success documentation for failed/incomplete work
- ❌ Quit early and pretend you used the full time

**ALWAYS:**
- ✅ Report actual timestamps (start/end)
- ✅ Be brutally honest about what IS working
- ✅ Be brutally honest about what ISN'T working
- ✅ Document incomplete work accurately
- ✅ Use the FULL time budget allocated (60 minutes = 60 minutes)

### What "Implementation" Means

**❌ Stub/Skeleton code is NOT implementation:**
```python
# This is FAKE - DO NOT DO THIS
def execute_workflow():
    # TODO: Actually execute workflow here
    logger.info("Would execute workflow")
    return True  # Pretending it worked
```

**✅ Real implementation:**
```python
def execute_workflow(workflow_name):
    # Load workflow config
    config = load_workflow(workflow_name)

    # Actually execute it
    result = workflow_executor.run(config)

    # Return real result
    return result
```

### If You Can't Finish in Time

**If you can't complete everything in 60 minutes:**

1. ✅ Document exactly what IS complete and working
2. ✅ Document exactly what ISN'T complete
3. ✅ List specific next steps needed
4. ✅ Be honest about percentage complete (e.g., "40% complete")
5. ✅ Don't claim success or "MVP done"

**Example honest documentation:**
```markdown
## Status: INCOMPLETE (40% done)

### What IS Working:
- Schema updated with custom_workflows definition ✅
- Logging infrastructure created ✅

### What IS NOT Working:
- ❌ Orchestrator is stub only - does NOT execute workflows
- ❌ No integration with existing /flow commands
- ❌ Conditional logic not implemented
- ❌ Checkpoint handling not implemented

### Next Steps Needed:
1. Implement actual workflow execution in orchestrator
2. Integrate with WorkflowConfig and existing commands
3. Test end-to-end workflow execution
4. Implement conditional evaluation properly

### Time Used: 12 minutes (20% of budget)
### Reason for early stop: Mistakenly thought stub was enough
```

### What Success Looks Like

**At 60 minutes, you should have:**
1. **Working code** - Actually functional, not stubs
2. **Honest documentation** - Real status, accurate timestamps
3. **Complete testing** - Verified it actually works
4. **Clear handoff** - What's done, what's not, what's next

**NOT:**
- Extensive documentation claiming everything works
- Fake timestamps and duration claims
- Stub code with TODO comments pretending to be "MVP"
- "Success" claims for non-functional code

### See Failure #3 in FAILURE-LEARNINGS.md

**Read it now to see what happens when you fake it.**

**Summary:** 12 minutes of work, claimed 55 minutes. Created fake orchestrator that does nothing. Lied across all documentation. Complete disaster.

**Don't repeat this.**

---

## KEY REALIZATION

**From flowspec-loop.md (THE CRITICAL DOCUMENT):**

The document header states: **"Inner Loop <-THIS IS FLOWSPEC"** and **"Default Flowspec. THIS IS OUR MISSION!"**

This means:
1. **Flowspec = Inner Loop (and ONLY inner loop)**
2. **The 4 core commands define the mission**: specify → plan → implement → validate
3. **Outer loop is NOT flowspec** - Promote/Observe/Operate/Feedback belong to falcondev
4. **Everything else** (assess, research, ad hoc commands) **supports the core 4**

**What "glue that loosely binds" means:**
- NOT hardcoded workflows combining steps
- NOT removing/replacing the core commands
- YES orchestration layer that lets users combine steps in custom sequences
- YES flexible, user-editable workflow definitions

## What the Requirements Actually Say

### Core Mission (from flowspec-loop.md)

**"Default Flowspec. THIS IS OUR MISSION!"**

Flowspec IS the inner loop - using specs & artifacts to build quality. The core mission is:

**The 4 Core Inner Loop Commands:**
1. `/flow:specify` → To Do → Spec (PM Planner)
2. `/flow:plan` → Spec → Arch Docs (Architect, Platform Eng)
3. `/flow:implement` → Spec & Arch → Working solution (Frontend/Backend Engineers)
4. `/flow:validate` → PR → Merged (QA, Security Engineers)

**Vibe OR Spec mode - MUST always:**
- Log key events, decisions, actions
- Make spec + workflow system flexible (user changes it)
- These 4 commands are THE inner loop

### Inner Loop vs Outer Loop Distinction (CRITICAL)

**Inner Loop = FLOWSPEC (and ONLY flowspec):**
- `/flow:specify` → Spec (PM Planner)
- `/flow:plan` → Arch Docs (Architect, Platform Eng)
- `/flow:implement` → Working solution (Frontend/Backend Engineers)
- `/flow:validate` → Merged (QA, Security Engineers)

**Outer Loop = NOT FLOWSPEC (falcondev and other tools):**
- **Promote** → artifacts → deployed (NOT /flow:operate)
- **Observe** → telemetry → Running (NOT flowspec)
- **Operate** → config → Running (NOT flowspec)
- **Feedback** → new Requirements → into inner loop (NOT flowspec)

### REQUIRED (Always Present - Never Optional)

**1. LOGGING:**
- Log decisions to `.logs/decisions/*.jsonl`
- Log events to `.logs/events/*.jsonl`
- Outputs of steps produce artifacts

**2. BACKLOG SYSTEM:**
- Keep backlog.md/beads up to date and accurate throughout process

**3. MEMORY SYSTEM:**
- Task memory system
- Track and save task state
- Keep agent aware of losing focus (across sessions, across time)

**4. CRITICAL AD HOC COMMANDS:**
These are disconnected from workflows but critical:
- `/flow:submit-n-watch-pr` - Get feedback from other agents (Copilot, etc.), iterate til good
- `/flow:timed-task` - Given rules, time, branch → produce outcome
- `/flow:refactor` - Full complete refactor loop

### FLEXIBLE (User Can Edit via falcondev/workflow-editor)

Must be easy to customize, can't over-scrutinize at CI/CD time:
- Agents
- Prompts
- Flowspec workflows
- Constitution
- Skills
- Custom workflow sequences

### From objective.md

**Core Philosophy:**
- **"simply be the glue that loosely binds the steps"** - Orchestration layer, NOT hardcoded workflows
- **"let users completely customize their flow steps"** - Users define sequences
- **"with the workflow editor in falcondev"** - Must be editable via UI/YAML

**What Flowspec Orchestrates (for each step):**
- **Inputs**: objective/goal/feature
- **Outputs**: artifacts (ARD, Spec, Code, Commit)
- **Who**: which agent or squad of agents
- **Rules**: constitution, log jsonl, stay in branch, stay on task
- **Autonomy**: complete through task completion (timed) OR til step is done

**Execution Modes:**
- **"vibing"** - Autonomous execution with full logging, no interaction
- **"spec-ing"** - Stop for guidance at configurable checkpoints

**Multi-Tool Requirement:**
Must work across 4 tools (in priority order):
1. Claude Code
2. GitHub Copilot (all variants)
3. Cursor
4. Gemini

### From feedback.md

- Different from spec-kit = flexible orchestration + rigor rules + multi-tool support
- NOT hardcoded simplification

## What Actually Needs to Happen

### Core Principle
**Keep ALL existing workflows working independently. Add flexible orchestration layer on TOP.**

### Flowspec Command Architecture

**CORE INNER LOOP (The Mission - Non-Negotiable):**

These 4 commands ARE flowspec. Everything else supports or extends them.

1. `/flow:specify` - To Do → Spec (PM Planner)
2. `/flow:plan` - Spec → Arch Docs (Architect, Platform Eng)
3. `/flow:implement` - Spec & Arch → Working solution (Frontend/Backend Engineers)
4. `/flow:validate` - PR → Merged (QA, Security Engineers)

**SUPPORTING WORKFLOWS (Pre-Spec Helpers):**

Optional workflows that help prepare for the core loop:
- `/flow:assess` - Complexity scoring (helps decide full SDD vs spec-light)
- `/flow:research` - Deep research (for complex features needing market/tech analysis)

**AD HOC UTILITY COMMANDS (Standalone Tools):**

Disconnected utilities for specific use cases:
- `/flow:submit-n-watch-pr` - PR submission, monitor CI/CD, iterate with agent feedback til good
- `/flow:timed-task` - Given rules, time, branch → produce outcome
- `/flow:refactor` - Full complete refactor loop

**EXPLICITLY OUT OF SCOPE (Outer Loop):**

These are NOT flowspec - they belong to falcondev and other tools:
- ❌ `/flow:operate` - This is OUTER LOOP (Promote/Observe/Operate/Feedback)
- ❌ Deployment and operational readiness - NOT inner loop
- ❌ Production monitoring and incident response - NOT inner loop

**Requirements for ALL Commands:**
- Continue working independently
- Be usable in custom workflow sequences
- Integrate with backlog.md/beads
- Use memory system
- Log decisions and events
- Follow constitution

### What Gets Added: User-Customizable Orchestration

Users define their own workflow sequences in `flowspec_workflow.yml`:

```yaml
# Example: User wants lightweight design for simple features
custom_workflows:
  quick_design:
    name: "Quick Design"
    mode: "vibing"  # autonomous, no stops
    steps:
      - workflow: assess
      - workflow: specify
      - workflow: plan
        condition: "complexity >= 5"  # skip if too simple
    rigor:
      log_decisions: true
      log_events: true
      create_adrs: true
      follow_constitution: true

  # Example: User wants full research with checkpoints
  full_research:
    name: "Full Research"
    mode: "spec-ing"  # stop for approvals
    steps:
      - workflow: assess
      - workflow: specify
        checkpoint: "Review PRD before continuing?"
      - workflow: research
      - workflow: plan
        checkpoint: "Review architecture before implementing?"
    rigor:
      log_decisions: true
      log_events: true
      create_adrs: true
      follow_constitution: true

  # Example: User wants build + ship in one go
  build_and_ship:
    name: "Build and Ship"
    mode: "vibing"
    steps:
      - workflow: implement
      - workflow: validate
      - workflow: submit-n-review-pr
    rigor:
      log_decisions: true
      log_events: true
      create_adrs: true
      follow_constitution: true
```

### Key Capabilities

**User Control:**
- Define any sequence of workflows (core + supporting)
- Name their custom workflows
- Set conditions for skipping steps (based on complexity, context, etc.)
- Choose vibing (autonomous) or spec-ing (approval checkpoints)
- Edit via YAML or falcondev workflow editor UI
- Combine core, supporting, and ad hoc commands as needed

**Rigor Enforcement (NO EXCEPTIONS):**
Every workflow (existing and custom) MUST:
- Log decisions to `.logs/decisions/*.jsonl`
- Log events to `.logs/events/*.jsonl`
- Create ADRs for architectural decisions
- Follow constitution from `.specify/memory/constitution.md`
- Stay in branch
- Stay on task

**MCP Integration (NOT bash):**
All backlog operations use MCP tools:
```python
from flowspec_cli.backlog.shim import task_view, task_edit

# View task state
task_data = task_view(task_id, plain=True)
current_state = parse_state_from_output(task_data)

# Update task state
task_edit(task_id=task_id, status="Validated", workspace_root=workspace_root)
```

NO bash scripts like:
```bash
# WRONG - security vulnerability
backlog task "$TASK_ID" --plain
```

**Security:**
- Remove ALL eval() usage
- Remove ALL curl | bash patterns
- Sanitize all inputs
- Use subprocess with proper escaping

**CI/CD:**
- Run all checks locally BEFORE PR
- Use `/flow:submit-n-review-pr` to monitor checks
- Fix ALL failing checks before requesting review
- validate-agent-sync MUST pass
- auto-fix-drift MUST pass
- Semgrep MUST pass (no HIGH+ findings)

### Implementation Steps

**Step 1: Add orchestration engine**
- Create `src/flowspec_cli/workflow/orchestrator.py`
- Reads custom workflow definitions from `flowspec_workflow.yml`
- Executes workflows in sequence
- Handles conditional logic
- Supports checkpoints for spec-ing mode
- Enforces rigor rules on every step

**Step 2: Extend schema**
- Update `schemas/flowspec_workflow.schema.json`
- Add `custom_workflows` section
- Support conditions, checkpoints, modes

**Step 3: MCP migration**
- Replace ALL bash backlog calls with MCP tools
- In ALL existing workflows (4 core + 2 supporting + 3 ad hoc)
- In orchestrator
- Add proper error handling

**Step 4: Rigor enforcement**
- Add decision logging to ALL workflows
- Add event emission to ALL workflows
- Add ADR creation hooks
- Add constitution validation

**Step 5: Security fixes**
- Remove ALL eval()
- Remove ALL curl | bash
- Sanitize inputs everywhere

**Step 6: Validation**
- Run ALL CI/CD checks locally
- Use `/flow:submit-n-review-pr` for PR
- Fix ALL failing checks
- Only then request review

## Success Criteria

**REQUIRED Systems (Always Present):**
✅ Logging system intact - decisions/events to `.logs/`
✅ Backlog system intact - backlog.md/beads up to date
✅ Memory system intact - task memory across sessions
✅ Ad hoc utility commands intact - submit-n-watch-pr, timed-task, refactor

**Flowspec Command Architecture:**
✅ 4 Core workflows work independently (THE MISSION):
  - specify, plan, implement, validate
✅ 2 Supporting workflows work independently (PRE-SPEC HELPERS):
  - assess, research
✅ 3 Ad hoc utilities work independently (STANDALONE TOOLS):
  - submit-n-watch-pr, timed-task, refactor
✅ Outer loop commands REMOVED from flowspec:
  - /flow:operate deleted (it's outer loop, not flowspec)

**Flexible Orchestration:**
✅ Users can define custom sequences in YAML
✅ Supports vibing (autonomous) and spec-ing (checkpoints) modes
✅ Editable via falcondev workflow editor
✅ Agents, prompts, workflows, constitution, skills all customizable

**Rigor Enforcement:**
✅ Rigor rules enforced everywhere (no exceptions)
✅ All workflows log decisions and events
✅ All workflows integrate with backlog/beads
✅ All workflows use memory system
✅ All workflows follow constitution

**Security & Integration:**
✅ MCP used for all backlog integration (no bash)
✅ Zero security vulnerabilities (no eval, no curl pipes)
✅ All CI/CD checks pass
✅ Works across Claude Code, Copilot, Cursor, Gemini

## What Makes This Different from spec-kit

- **spec-kit**: Fixed workflow, not customizable
- **flowspec**: Users define their own workflow sequences via YAML
- **spec-kit**: No rigor enforcement
- **flowspec**: Mandatory logging, ADRs, constitution
- **spec-kit**: Single tool
- **flowspec**: Works across multiple AI tools

## Critical Constraints

> Detailed failure learnings in [FAILURE-LEARNINGS.md](./FAILURE-LEARNINGS.md)

**Architecture:**
- ❌ DON'T replace workflows - add orchestration ON TOP
- ❌ DON'T remove existing commands (especially ad hoc utilities)
- ❌ DON'T hardcode sequences - let users customize

**Integration & Security:**
- ❌ DON'T use bash for backlog (use MCP)
- ❌ DON'T introduce security vulnerabilities (eval, curl pipes)
- ❌ DON'T over-scrutinize user-editable content at CI/CD time

**Process:**
- ❌ DON'T skip rigor enforcement (logging, ADRs, constitution)
- ❌ DON'T skip CI/CD validation before PR
- ❌ DON'T forget required systems (memory, backlog, logging)

## Ready to Execute

This approach covers all requirements:

**Core Mission Alignment:**
- ✅ 4 core commands ARE flowspec (specify → plan → implement → validate)
- ✅ "Glue that loosely binds steps" = orchestration layer on TOP
- ✅ Inner loop ONLY (outer loop is falcondev/other tools)
- ✅ Always log in vibe/spec modes

**Command Architecture:**
- ✅ 4 core workflows (THE MISSION)
- ✅ 2 supporting workflows (PRE-SPEC HELPERS)
- ✅ 3 ad hoc utilities (STANDALONE TOOLS)
- ✅ Outer loop commands OUT OF SCOPE (/flow:operate removed)

**Required Systems:**
- ✅ Logging system (decisions, events, ADRs)
- ✅ Backlog system (backlog.md/beads integration)
- ✅ Memory system (cross-session task state)

**Flexible Orchestration:**
- ✅ User-customizable workflow sequences in YAML
- ✅ Vibing (autonomous) and spec-ing (checkpoints) modes
- ✅ Editable via falcondev workflow editor
- ✅ Agents, prompts, workflows, constitution, skills all customizable

**Technical Requirements:**
- ✅ MCP integration (no bash)
- ✅ Security fixes (no eval, no curl pipes)
- ✅ CI/CD compliance
- ✅ Multi-tool support (Claude Code, Copilot, Cursor, Gemini)

Awaiting your approval to proceed with implementation.
