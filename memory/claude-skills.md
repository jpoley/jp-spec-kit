# Claude Code Skills

JP Spec Kit includes 5 core Skills that Claude automatically invokes based on task context. Skills differ from slash commands in that they are **model-invoked** (automatic) rather than user-invoked (manual).

## How Skills Work

Skills are stored in `.claude/skills/<skill-name>/SKILL.md` with:
- YAML frontmatter: `name` and `description` (critical for automatic discovery)
- Markdown content: instructions, templates, and examples

Claude automatically uses a skill when the task context matches the skill's `description`.

## Core Skills

### 1. PM Planner (`pm-planner`)

**Location**: `.claude/skills/pm-planner/SKILL.md`

**Auto-invoked when**:
- Creating or editing backlog tasks
- Breaking down features into atomic tasks
- Writing acceptance criteria
- Reviewing task quality

**Capabilities**:
- Task creation guidelines (title, description, AC)
- Atomicity rules (single PR scope, testable, independent)
- Task breakdown strategies
- Quality checklist

### 2. Architect (`architect`)

**Location**: `.claude/skills/architect/SKILL.md`

**Auto-invoked when**:
- Making architecture decisions
- Creating ADRs
- Designing system components
- Evaluating technology choices

**Capabilities**:
- ADR format and templates
- Architecture principles (separation of concerns, defense in depth)
- Technology evaluation framework
- Scalability checklist

### 3. QA Validator (`qa-validator`)

**Location**: `.claude/skills/qa-validator/SKILL.md`

**Auto-invoked when**:
- Creating test plans
- Reviewing test coverage
- Defining quality gates
- Writing E2E scenarios

**Capabilities**:
- Test pyramid guidance
- Test plan templates
- AC validation checklist
- Bug report format

### 4. Security Reviewer (`security-reviewer`)

**Location**: `.claude/skills/security-reviewer/SKILL.md`

**Auto-invoked when**:
- Reviewing code for vulnerabilities
- Conducting threat modeling
- Ensuring SLSA compliance
- Performing security assessments

**Capabilities**:
- OWASP Top 10 checklist
- SLSA compliance levels
- STRIDE threat modeling
- Secure coding patterns

### 5. SDD Methodology (`sdd-methodology`)

**Location**: `.claude/skills/sdd-methodology/SKILL.md`

**Auto-invoked when**:
- Explaining SDD workflow
- Guiding through workflow phases
- Helping with methodology decisions
- Onboarding to SDD

**Capabilities**:
- Workflow phase overview
- State transition rules
- SDD principles
- Common anti-patterns

## Creating Custom Skills

To add a new skill:

1. Create directory: `.claude/skills/<skill-name>/`
2. Create `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: my-skill
   description: Use when [context that triggers this skill]
   ---
   ```
3. Add instructions, templates, and examples in Markdown

## Skills vs. Other Claude Code Features

| Feature | Invocation | Use Case |
|---------|------------|----------|
| **Skills** | Automatic (model-invoked) | Domain expertise, templates, guidelines |
| **Slash Commands** | Manual (`/command`) | Explicit workflows, multi-step processes |
| **Subagents** | Manual (Task tool) | Parallel execution, isolated context |
| **Hooks** | Automatic (event-based) | Validation, formatting, safety checks |
