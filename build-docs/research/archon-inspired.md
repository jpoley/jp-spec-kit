# Deep Context-Engineering Improvements for **flowspec**
## Based on coleam00/context-engineering-intro and jpoley/flowspec

This document turns ideas from **context-engineering-intro** into **very specific, concrete changes** you can make to **flowspec** to improve context engineering.

The focus is:

- INITIAL-style feature intake docs
- PRP-style “all needed context” bundles
- Enforced All Needed Context in specs
- Per-feature validation loops
- Codebase mapping and examples
- Systematized gotchas/learnings
- Explicit inner vs outer loop metadata

No generalities; every suggestion is phrased as tasks you can actually implement in the repo.

---

## 1. Core patterns from context-engineering-intro

From the structure of `context-engineering-intro`, the core patterns are:

1. A **single INITIAL doc** per feature, with sections like:
   - FEATURE (problem + outcome)
   - EXAMPLES (actual files and behaviors)
   - DOCUMENTATION (docs, ADRs, README links)
   - OTHER CONSIDERATIONS (gotchas, constraints)

2. A **PRP (Product Requirements Prompt)** generated from the INITIAL doc, which explicitly contains:
   - ALL NEEDED CONTEXT (files, docs, examples, gotchas)
   - CODEBASE SNAPSHOT (bounded tree of relevant code)
   - VALIDATION LOOP (exact commands + pass/fail expectations)

3. **Global rules and examples**:
   - A `CLAUDE` doc that lays down global behavior and standards
   - An `examples` directory that is explicitly wired into prompts and specs

Flowspec already has strong global rules, standards, and a spec pipeline, but does *not* yet have:

- INITIAL docs per feature
- PRP files per feature
- An enforced “All Needed Context” section in PRDs
- Per-feature validation recipes captured as first-class artifacts
- Automatic codebase snapshots and example binding
- Automatic inclusion of gotchas/learnings per feature

The following sections are how to bolt those in.

---

## 2. Where flowspec is already strong

Flowspec gives you many of the building blocks that context-engineering-intro assumes:

- **Critical rules**
  - A document that defines non-negotiables:
    - Do not delete tests
    - Always run specific pre-PR checks (formatter, linter, tests)
    - Requirements for task memory and updates

- **Code and test standards**
  - Documents that lay down:
    - How to structure code
    - How to design APIs and error handling
    - How to write tests (fixtures, isolation, negative cases)

- **Task memory**
  - Per-task memory files (for example, under a `backlog/memory` folder) that capture:
    - What and why
    - Constraints
    - Key decisions
    - Blockers
    - Acceptance criteria status

- **Spec pipeline**
  - A command such as `/flow:specify` that:
    - Writes a PRD
    - Uses DVF+V or similar frameworks
    - Integrates with `backlog` tooling and states

- **Workflow states**
  - A lifecycle such as:
    - Assessed → Specified → Implemented → Validated → Merged → Verified

In other words, flowspec has a lot of **global and lifecycle structure**, but it’s missing the **per-feature context bundles** that context-engineering-intro uses (INITIAL and PRP).

---

## 3. Add INITIAL-style feature intake docs

### Problem

flowspec currently starts with commands like `/flow:assess` or `/flow:specify` based on natural language plus backlog tasks. There is no standard, structured **pre-spec** document per feature.

### Goal

Introduce an **INITIAL-style document** that becomes the structured first step before assessing or specifying work.

### Task 1 — Add an INITIAL template

Create a template file such as:

- Path: `templates/docs/initial/initial-feature-template.md`

Suggested content:

- Heading: “FEATURE”
  - Describe the problem, the desired outcome, key constraints, and why this matters.
- Heading: “EXAMPLES”
  - List relevant files under an `examples` directory and what they illustrate.
- Heading: “DOCUMENTATION”
  - Links to PRDs, ADRs, architecture docs, README sections, external specs or RFCs, and any previous tasks.
- Heading: “OTHER CONSIDERATIONS”
  - Known gotchas, previous failures, dependencies on other features, security concerns, performance requirements, etc.

This template is the canonical starting point for any new feature-level change.

### Task 2 — Add a `/flow:init` command

Add a new Claude command file, for example:

- Path: `.claude/commands/flow/init.md`

The behavior of `/flow:init` should be:

- Accept a path argument to an INITIAL doc (defaulting to something like `docs/features/<slug>-initial.md`).
- Parse the sections:
  - FEATURE → use this as the basis for a new backlog task title and description.
  - EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS → seed the initial task memory file.
- Create a new backlog task using your `backlog` CLI or API.
- Create a task memory file such as `backlog/memory/<task-id>.md` and populate:
  - What and Why (from FEATURE)
  - Constraints (from FEATURE + OTHER CONSIDERATIONS)
  - Examples (from EXAMPLES)
  - Docs (from DOCUMENTATION)
  - Initial gotchas (from OTHER CONSIDERATIONS)

### Task 3 — Update CLAUDE instructions to prefer INITIAL docs

In your main CLAUDE configuration document (for example, a `CLAUDE.md` in the repo):

- Add guidance along the lines of:
  - “If there is an INITIAL doc for the current feature, read that document before running `/flow:assess` or `/flow:specify`.”
  - “The INITIAL doc is the primary source of high-level context for the feature.”

This ensures that *all* flowspec work for a feature starts from a consistent, structured intake.

---

## 4. Add PRP-style context bundles for each feature

### Problem

flowspec’s PRD generated by `/flow:specify` is rich, but it does not explicitly enforce an **All Needed Context** bundle that enumerates every file, example, doc, and gotcha, plus a codebase snapshot and validation loop.

### Goal

For each feature or task, create a **PRP-style file** that acts as a single, self-contained context packet.

### Task 4 — Create a PRP base template for flowspec

Add a file such as:

- Path: `templates/docs/prp/prp-base-flowspec.md`

Suggested sections:

- Title: “Product Requirements Prompt (PRP)”
- Section: “ALL NEEDED CONTEXT”
  - Subsection: “Code Files”
    - List of code files and their purpose.
  - Subsection: “Docs / Specs”
    - Links to PRDs, architecture docs, ADRs, external documents.
  - Subsection: “Examples”
    - List of examples and why each is relevant.
  - Subsection: “Known Gotchas”
    - List of pitfalls and known failures.
  - Subsection: “Related Backlog Tasks”
    - List of related task IDs with a brief note.

- Section: “CODEBASE SNAPSHOT”
  - A bounded directory tree for the relevant parts of the codebase (only directories and files relevant to this feature, not a full repo listing).

- Section: “VALIDATION LOOP”
  - Commands to run (pytest invocations, ruff checks, integration scripts).
  - The exact success criteria (what must pass).
  - Any known failure modes to watch out for.

This file becomes the blueprint for all feature-specific PRPs.

### Task 5 — Add a `/flow:generate-prp` command

Create another Claude command file:

- Path: `.claude/commands/flow/generate-prp.md`

Intended behavior:

- Determine the active task (from backlog context or a passed argument).
- Collect:
  - The PRD produced by `/flow:specify` for that task.
  - All docs and specs linked to that task (in a known directory, e.g., `docs/specs`).
  - Relevant examples from `examples` for that feature.
  - Any relevant learnings from a `memory/learnings` folder or similar.
  - A limited directory tree of the relevant code paths (for example, running a tree command over a filtered path).
- Populate `templates/docs/prp/prp-base-flowspec.md` with this material.
- Write the filled-out PRP to a file such as:
  - `docs/prp/<task-id>.md`

The idea: if you give `docs/prp/<task-id>.md` to an LLM as the only context, it should have *everything* needed to work on the feature.

### Task 6 — Make implementation flows PRP-first

Update your implementation-related command(s) (for example, `/flow:implement`):

- When running `/flow:implement`:
  - Check for the presence of a PRP file for the active task (such as `docs/prp/<task-id>.md`).
  - If it exists, load that PRP first and treat it as primary context for the agent.
  - If it does not exist, the command instructions should recommend:
    - “Generate a PRP via `/flow:generate-prp` before doing non-trivial implementation work.”

This makes PRP files part of the normal workflow rather than an optional extra.

---

## 5. Enforce “All Needed Context” in `/flow:specify` PRDs

### Problem

Your spec command produces good product and technical descriptions, but does not enforce a clearly structured **All Needed Context** block that is easy to parse and reuse.

### Goal

Attach a consistent “All Needed Context” section to all PRDs so other commands can parse it.

### Task 7 — Update the `/flow:specify` template

Modify the template used by `/flow:specify` (for example under `templates/commands/flow/specify.md`) to include a section like:

- Heading: “All Needed Context”
  - List of code files
  - List of docs/specs
  - List of examples
  - Gotchas and prior failures
  - External systems and APIs involved

In more concrete terms, the PRD should be required to output something like:

- All Needed Context:
  - Code Files:
    - …
  - Docs / Specs:
    - …
  - Examples:
    - …
  - Gotchas / Prior Failures:
    - …
  - External Systems / APIs:
    - …

This structure can then be machine-parsed by other flowspec commands.

### Task 8 — Add a “context extraction” helper

Add a helper script or skill (for example in `.claude/skills` or under `src`):

- Input: the path to a PRD file.
- Behavior:
  - Parse the “All Needed Context” section.
  - Return it as structured data (for example, JSON).
- This helper can then be invoked by:
  - `/flow:implement` to know which files and docs to open.
  - `/flow:generate-prp` to seed the PRP context.
  - `/flow:validate` to confirm tests or commands to run.

---

## 6. Add per-feature validation loops

### Problem

Global rules enforce “run ruff, run pytest” etc, but each feature should have its own recipe of validation commands and expectations.

### Goal

Every PRD and PRP must define a **Feature Validation Plan**.

### Task 9 — Add a “Feature Validation Plan” section

Update both the PRD template and the PRP template to include a section called “Feature Validation Plan” with:

- Subsection: “Commands”
  - Explicit shell commands (pytest with specific paths, integration tests, data migrations, etc).
- Subsection: “Expected Success”
  - Text explaining what passing looks like.
- Subsection: “Known Failure Modes”
  - Patterns of failures to watch for, or regressions previously observed.

This moves validation from “just run tests” to “run these specific commands and look for these specific outcomes.”

### Task 10 — Add a `/flow:validate` command

Create a validation command (for example:

- Path: `.claude/commands/flow/validate.md`

Behavior:

- Determine the active task.
- Locate its PRD or PRP file.
- Extract the “Feature Validation Plan” section using your helper.
- Then:

  - Option A (fully automated):
    - Run the commands via a bash skill (if you have one).
    - Parse results and summarize pass/fail.
  - Option B (semi-automated):
    - Print out the commands with clear instructions for the human to run.
    - Ask the user to report results or paste logs.

- Update:
  - The backlog task notes with validation results.
  - The task memory file with:
    - “Current State”
    - “Latest validation run”
    - “Known Issues” if any failures occur

Now, every feature change ends with a reproducible, documented validation trace.

---

## 7. Tighten bindings to examples and codebase mapping

### Problem

Flowspec has an `examples` directory and a structured repo, but these are not systematically integrated into feature docs and flows.

### Goal

For each feature:

- At least one example is referenced in the spec.
- A bounded codebase snapshot is available for the relevant area.

### Task 11 — Require examples in PRDs

Modify `/flow:specify` template to include a specific section, for example:

- Heading: “Examples”
  - List of relevant files under `examples`.
  - For each file:
    - Short explanation of how it relates to the feature (e.g., “Shows expected CLI usage”, “Demonstrates error handling pattern needed here”).

Specs without at least one example reference should be considered incomplete.

### Task 12 — Add a `/flow:map-codebase` helper command

Create a command file such as:

- Path: `.claude/commands/flow/map-codebase.md`

Behavior:

- Accepts one or more paths of interest (for example, directories under `src`).
- Runs a bounded directory tree listing for those paths (limited depth).
- Writes a codebase snapshot into either:
  - The PRP for that task under “CODEBASE SNAPSHOT”, or
  - A separate file such as `docs/feature-maps/<task-id>.md` that the PRP and PRD reference.

The goal is to ensure that every feature has a short, readable map of the code area it touches.

---

## 8. Make gotchas and learnings a first-class channel

### Problem

Global learnings and gotchas exist as memory documents, but they aren’t automatically linked into each feature’s specs and PRPs.

### Goal

Automatically pull relevant learnings into every feature’s context bundle.

### Task 13 — Add a “Known Gotchas / Prior Failures” section

Ensure both the PRD template and the PRP template include a section like:

- Heading: “Known Gotchas / Prior Failures”
  - Space for:
    - Links to learning documents.
    - Brief descriptions of what went wrong previously.
    - Task IDs of prior related failures.

This forces each feature doc to explicitly enumerate prior lessons.

### Task 14 — Implement a “gather learnings” helper

Add a script or skill (for example, in `.claude/skills`) that:

- Reads the learning files from a `memory/learnings` directory or equivalent.
- Matches entries based on:
  - Relevant file paths.
  - Keywords or tags.
  - A simple metadata system if you define one (e.g., YAML front matter with a “tags” field).
- Returns a curated list of relevant learnings that can be inserted into:
  - The “Known Gotchas / Prior Failures” section of the PRD.
  - The corresponding section of the PRP.

This helper can be called during `/flow:specify` and `/flow:generate-prp` to ensure gotchas are always front and center.

---

## 9. Operationalize inner vs outer loop behavior

### Problem

Flowspec already models **inner loop** vs **outer loop** behaviors in your thinking and documents, but feature specs and commands do not explicitly declare that classification.

### Goal

Make loop classification explicit in both feature docs and commands.

### Task 15 — Add a “Loop Classification” section to PRDs and PRPs

Add to both templates a section such as:

- Heading: “Loop Classification”
  - Subheading: “Inner Loop Responsibilities”
    - Description of tasks that are fast, implementation-focused (e.g., refactoring, local changes, small tests).
  - Subheading: “Outer Loop Responsibilities”
    - Description of tasks that are planning-focused (e.g., problem framing, spec writing, risk analysis, approvals).

This makes it obvious what parts of the workflow should be handled by inner-loop tools or agents versus outer-loop ones.

### Task 16 — Add loop metadata to flow commands

In each `.claude/commands/flow/...` file, add a simple metadata marker near the top such as:

- A label field like `loop: Inner` or `loop: Outer`
- Or a clear comment that identifies the loop role

Examples:

- `/flow:specify` → outer loop
- `/flow:implement` → inner loop
- `/flow:validate` → spans both, but you can tag it explicitly

This annotation allows you to:

- Quickly reason about which agents or UI contexts should handle which commands.
- Potentially wire different models or safety rules to different loop types.

---

## 10. Summary of concrete deliverables

A concise mapping of everything above into deliverables:

- **INITIAL intake**
  - New template: `templates/docs/initial/initial-feature-template.md`
  - New command: `/flow:init` to turn INITIAL docs into backlog tasks and task memory
  - CLAUDE instructions updated to load INITIAL docs first

- **PRP context bundles**
  - New template: `templates/docs/prp/prp-base-flowspec.md`
  - New command: `/flow:generate-prp` to produce `docs/prp/<task-id>.md`
  - Implementation commands updated to be PRP-first

- **All Needed Context in PRDs**
  - `/flow:specify` template extended with a structured “All Needed Context” section
  - Helper/skill to parse that section into structured data

- **Per-feature validation loops**
  - PRD and PRP templates extended with a “Feature Validation Plan”
  - New `/flow:validate` command that runs or guides the validation loop and writes results to task memory and backlog

- **Examples and codebase mapping**
  - Specs required to reference at least one relevant entry from `examples`
  - New `/flow:map-codebase` command to generate bounded directory trees and feature maps

- **Gotchas and learnings**
  - PRD and PRP templates extended with a “Known Gotchas / Prior Failures” section
  - New helper/skill to gather relevant learnings from memory files based on paths/tags

- **Loop semantics**
  - PRD and PRP templates extended with a “Loop Classification” section
  - All flow commands annotated with inner vs outer loop metadata

---

## 11. What this concretely buys you in flowspec

Implementing these changes will:

- Turn each feature into a **single, portable context bundle** (PRP) that fully describes:
  - What needs to be done
  - What files and docs are relevant
  - What examples to learn from
  - What historical failures to avoid
  - How to validate success

- Make **spec-driven development** materially more robust:
  - No more guessing which docs or examples matter for a feature
  - Agents always see the same structured context
  - Validation is repeatable and traceable

- Make it easier to layer in:
  - Different LLMs or agents for inner vs outer loop
  - Different safety and compliance rules for planning vs execution
  - Future automation that walks the INITIAL → PRD → PRP → implementation → validation pipeline end-to-end

In short: these changes turn flowspec from “structured spec workflow” into a **context-engineering framework** that can safely and reliably orchestrate multi-step, multi-agent work on a codebase.

