---
name: sdd-methodology
description: Use when explaining or applying Spec-Driven Development workflow, guiding through SDD phases, or helping with workflow decisions. Invoked for methodology guidance, workflow optimization, and best practices.
---

# SDD Methodology Skill

You are an expert in Spec-Driven Development (SDD), a methodology for AI-assisted software development. You guide teams through structured workflow phases to deliver high-quality software.

## When to Use This Skill

- Explaining SDD workflow phases
- Guiding through workflow transitions
- Helping with methodology decisions
- Optimizing team workflows
- Onboarding new team members to SDD
- Troubleshooting workflow issues

## SDD Workflow Overview

```
┌─────────┐   ┌─────────┐   ┌──────────┐   ┌────────┐   ┌───────────┐   ┌──────────┐
│  Assess │ → │ Specify │ → │ Research │ → │  Plan  │ → │ Implement │ → │ Validate │
└─────────┘   └─────────┘   └──────────┘   └────────┘   └───────────┘   └──────────┘
     ↓             ↓              ↓            ↓              ↓              ↓
  Assessed     Specified     Researched    Planned    In Implementation  Validated

Note: Deployment/operations is "outer loop" - handled by external CI/CD pipelines, not SDD workflow.
```

## Workflow Phases

### 1. Assess (`/flow:assess`)
**Purpose**: Evaluate if SDD workflow is appropriate for a feature.

**Outputs**:
- Assessment report in `docs/assess/`
- Recommendation: Full SDD, Spec-Light, or Skip SDD

**Criteria for Full SDD**:
- Complex feature (>3 days estimated)
- Multiple stakeholders
- Architectural impact
- Security implications
- External integrations

### 2. Specify (`/flow:specify`)
**Purpose**: Create product requirements document.

**Outputs**:
- PRD in `docs/prd/`
- User stories
- Acceptance criteria
- Success metrics

**Best Practices**:
- Focus on "what" not "how"
- Include user personas
- Define MVP scope
- Identify risks and mitigations

### 3. Research (`/flow:research`)
**Purpose**: Technical research and business validation.

**Outputs**:
- Research report in `docs/research/`
- Technology recommendations
- Feasibility analysis
- Market validation (if applicable)

**Activities**:
- Spike prototypes
- Performance benchmarks
- Third-party evaluations
- Competitive analysis

### 4. Plan (`/flow:plan`)
**Purpose**: Create architecture and implementation plan.

**Outputs**:
- ADRs in `docs/adr/`
- Platform design in `docs/platform/`
- Task breakdown in backlog

**Deliverables**:
- System architecture diagrams
- API specifications
- Database schema
- Infrastructure requirements

### 5. Implement (`/flow:implement`)
**Purpose**: Execute the implementation plan.

**Process**:
1. Assign tasks from backlog
2. Implement with TDD/BDD
3. Create pull requests
4. Code review
5. Merge to main

**Best Practices**:
- One task per PR
- All tests passing
- Documentation updated
- No new technical debt

### 6. Validate (`/flow:validate`)
**Purpose**: Quality assurance and security review.

**Outputs**:
- QA report in `docs/qa/`
- Security report in `docs/security/`
- Test coverage report

**Checklist**:
- [ ] All acceptance criteria met
- [ ] Test coverage >= 80%
- [ ] Security scan clean
- [ ] Performance benchmarks passed
- [ ] Documentation complete

## Workflow State Transitions

> **Note**: Deployment and operations are "outer loop" concerns handled by external CI/CD pipelines.
> Use `/ops:*` commands (`/ops:monitor`, `/ops:respond`, `/ops:scale`) for operational tasks.

| Current State | Valid Commands | Next State |
|---------------|----------------|------------|
| To Do | `/flow:assess` | Assessed |
| Assessed | `/flow:specify` | Specified |
| Specified | `/flow:research`, `/flow:plan` | Researched, Planned |
| Researched | `/flow:plan` | Planned |
| Planned | `/flow:implement` | In Implementation |
| In Implementation | `/flow:validate` | Validated |
| Validated | (external CI/CD) | Deployed |

## SDD Principles

### 1. Specification First
- Define requirements before coding
- Use acceptance criteria as contracts
- Document decisions as ADRs

### 2. Incremental Delivery
- Small, atomic tasks
- Continuous integration
- Frequent deployments

### 3. Quality Built-In
- TDD/BDD approach
- Automated testing
- Security by design

### 4. Continuous Improvement
- Retrospectives after each phase
- Metrics-driven optimization
- Knowledge sharing

## Common Anti-Patterns

### Avoid These:
1. **Skipping Assess**: Jumping to implementation without evaluation
2. **Vague Specs**: Requirements without acceptance criteria
3. **Big Bang Implementations**: Large PRs with multiple features
4. **Testing Afterthought**: Writing tests after implementation
5. **Documentation Debt**: Leaving docs for "later"

### Instead, Do This:
1. Always assess complexity first
2. Write testable acceptance criteria
3. One task = one PR
4. TDD from the start
5. Document as you go

## Workflow Configuration

SDD workflow is configured in `flowspec_workflow.yml`:

```yaml
states:
  - name: "To Do"
    description: "Task created, not started"
  - name: "Assessed"
    description: "Complexity evaluated"
  # ... more states

workflows:
  assess:
    command: "/flow:assess"
    input_states: ["To Do"]
    output_state: "Assessed"
    agents: ["workflow-assessor"]
  # ... more workflows
```

## Getting Help

- Workflow troubleshooting: `docs/guides/workflow-troubleshooting.md`
- State mapping: `docs/guides/workflow-state-mapping.md`
- Customization: `docs/guides/workflow-customization.md`
