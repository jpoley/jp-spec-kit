# Problem Sizing Assessment Guide

## Overview

The `/flow:assess` command helps teams determine the appropriate development workflow based on feature complexity. This guide explains when to use Spec-Driven Development (SDD), when to use lightweight approaches, and how to make informed workflow decisions.

## The Problem

Not every feature requires the full Spec-Driven Development workflow. Small bug fixes and simple features can be over-engineered with excessive planning, while complex features risk failure without proper specification. The assessment command helps you find the right balance.

## Decision Framework

### Three Workflow Tiers

| Workflow | Complexity | Score Range | Best For |
|----------|-----------|-------------|----------|
| **Skip SDD** | Simple | 8-12 points | Bug fixes, minor changes, well-understood problems |
| **Spec-Light** | Medium | 13-20 points | New features with moderate complexity, some coordination |
| **Full SDD** | Complex | 21-32 points | Major features, architectural changes, high-risk initiatives |

## Assessment Dimensions

The assessment evaluates 8 key dimensions, each scored 1-4 points:

### 1. Scope and Size (Questions 1-2)

**Lines of Code Estimate**
- Helps gauge implementation effort
- Proxy for overall complexity
- Consider all affected code, not just new code

**Modules/Components Affected**
- Cross-cutting changes increase coordination needs
- More modules = more integration points
- Consider ripple effects across codebase

### 2. Integration and Dependencies (Questions 3-4)

**External Integrations**
- Each external system adds failure modes
- API integration requires contracts and testing
- More integrations = more moving parts

**Data Complexity**
- Database changes have long-term consequences
- Migrations add risk and coordination needs
- Schema design requires upfront planning

### 3. Team and Process (Questions 5-6)

**Team Coordination Requirements**
- More developers = more communication overhead
- Larger teams benefit from clear specifications
- Parallel work requires well-defined interfaces

**Cross-Functional Requirements**
- Product, Design, Legal, Security involvement
- Multiple perspectives require alignment
- Stakeholder coordination benefits from written specs

### 4. Risk and Uncertainty (Questions 7-8)

**Technical Uncertainty**
- Unknown technical approaches require spikes
- New technologies need proof-of-concept
- High uncertainty benefits from research phase

**Business Impact and Risk**
- Revenue-critical features need validation
- Compliance requirements demand documentation
- High-stakes decisions require written rationale

## Workflow Recommendations

### Skip SDD (Simple Features)

**Characteristics:**
- Single developer can own the work
- Problem and solution are well-understood
- Low risk if approach changes
- Minimal stakeholder coordination
- Clear acceptance criteria

**Examples:**
- Fix typo in documentation
- Update dependency version
- Add logging statement
- Change configuration value
- Fix alignment issue in UI

**Workflow:**
```
1. Create task in backlog.md with clear acceptance criteria
2. Implement with TDD (write tests first)
3. Quick peer review
4. Merge and deploy
```

**Why Skip SDD?**
- Specification overhead exceeds implementation time
- Writing docs takes longer than fixing the issue
- Clear problem with obvious solution
- Flexibility to adjust during implementation

### Spec-Light Mode (Medium Features)

**Characteristics:**
- 2-4 developers collaborating
- Some unknowns, but manageable
- Moderate business impact
- Few external dependencies
- Moderate coordination needs

**Examples:**
- New REST API endpoint
- React component with business logic
- Database schema addition
- Third-party API integration
- Feature flag implementation

**Workflow:**
```
1. Lightweight specification (1-2 pages):
   - Problem statement
   - High-level approach
   - Key acceptance criteria
   - Integration points
   - Testing strategy

2. Optional spike for unknowns (1-2 days max)

3. Brief architecture review:
   - Async review (Slack/PR)
   - Or 30-minute sync call

4. Implementation:
   - TDD approach
   - Standard code review
   - Integration testing

5. Deploy with monitoring
```

**Use These SDD Phases:**
- ✅ `/flow:specify` - Create lightweight spec
- ✅ `/flow:implement` - Direct implementation
- ✅ Code review (part of implement)

**Skip These SDD Phases:**
- ❌ `/flow:research` - No market research needed
- ❌ `/flow:plan` - No full architectural planning
- ❌ `/flow:validate` - No dedicated QA phase

**Why Spec-Light?**
- Captures key decisions without excessive documentation
- Enables alignment without process overhead
- Maintains flexibility during implementation
- Documents integration points for coordination
- Reduces risk without slowing down delivery

### Full SDD Workflow (Complex Features)

**Characteristics:**
- 5+ developers or multiple teams
- Significant unknowns or new technologies
- High business impact or risk
- Multiple external integrations
- Cross-functional coordination

**Examples:**
- Payment processing integration
- Authentication/authorization system
- Multi-tenant architecture
- Data migration project
- Compliance initiative (PCI, SOC2, HIPAA)
- New product capability

**Workflow:**
```
1. /flow:specify
   - Comprehensive PRD
   - User stories and use cases
   - DVF+V risk assessment
   - Success metrics

2. /flow:research
   - Market analysis
   - Competitive landscape
   - Technical feasibility
   - Business validation

3. /flow:plan
   - System architecture
   - Platform design
   - ADRs for key decisions
   - Integration patterns

4. /flow:implement
   - Parallel dev (frontend/backend)
   - Comprehensive code review
   - Integration testing

5. /flow:validate
   - QA and testing
   - Security review
   - Documentation review

6. /flow:operate
   - CI/CD setup
   - Monitoring and alerting
   - Phased rollout
```

**Why Full SDD?**
- High coordination overhead requires clear specs
- Multiple stakeholders need alignment
- Business risk requires validation
- Complex architecture needs documented decisions
- Long timeline benefits from phased approach
- Compliance requirements demand documentation

## Running the Assessment

### Command Usage

```bash
# Interactive assessment
/flow:assess

# With feature context
/flow:assess "Integrate Stripe payment processing"

# As part of project initialization
flowspec init
# (Will prompt: "Run complexity assessment? [Y/n]")
```

### Assessment Process

The command will guide you through 8 questions:

```
Feature Complexity Assessment
=============================

Feature: [Your feature name]

Question 1/8: Estimated Lines of Code (LOC)

How many lines of code do you estimate this feature will require?

A. < 100 lines (Small: Simple utility, configuration change, minor fix)
B. 100-500 lines (Medium: New component, API endpoint, service integration)
C. 500-2000 lines (Large: New module, complex feature, multi-component)
D. > 2000 lines (Very Large: New subsystem, major architectural change)

Your answer [A/B/C/D]:
```

After completing all 8 questions, you'll receive:
- **Complexity score** (8-32 points)
- **Classification** (Simple/Medium/Complex)
- **Workflow recommendation** (Skip SDD / Spec-Light / Full SDD)
- **Specific next steps**

## Calibration and Tuning

### Team Calibration

Different teams may need different thresholds. Calibrate based on:

**Team Experience:**
- Junior teams: Lower thresholds (more planning)
- Senior teams: Higher thresholds (less planning)

**Domain Complexity:**
- Regulated industries (healthcare, finance): Lower thresholds
- Internal tools: Higher thresholds

**Organizational Culture:**
- Move-fast culture: Higher thresholds
- Safety-critical culture: Lower thresholds

### Tracking and Improvement

Track assessment accuracy:

```markdown
## Assessment Log

| Feature | Predicted | Actual | Notes |
|---------|-----------|--------|-------|
| Payment API | Complex (26) | Complex | Accurate, saved time |
| UI Refresh | Simple (10) | Medium | Underestimated scope |
| Bug Fix #123 | Simple (8) | Simple | Accurate |
```

Adjust thresholds based on patterns:
- Consistently over-estimating? Raise thresholds
- Consistently under-estimating? Lower thresholds
- Domain-specific patterns? Add custom questions

## When to Override the Assessment

The assessment is a guideline, not a mandate. Override when:

### Upgrade to More Rigor

Even if assessment says "Simple", upgrade if:
- **Regulatory requirements** demand documentation
- **Organizational policy** requires approvals
- **Stakeholder request** for detailed planning
- **Team learning** opportunity (training juniors)
- **Architecture precedent** that needs documentation

### Downgrade to Less Rigor

Even if assessment says "Complex", downgrade if:
- **Proven pattern** already documented elsewhere
- **Time-critical** emergency fix or opportunity
- **Spike/POC** to validate before full commitment
- **Team expertise** in this exact problem domain

### Document Your Override

If you override, document why:

```markdown
## Assessment Override

**Assessment Score:** 24/32 (Complex) → Full SDD recommended
**Override Decision:** Spec-Light Mode
**Rationale:**
- Team implemented identical pattern 3 times before
- Well-documented architecture in ADR-042
- Time-sensitive market opportunity
- Can leverage existing test infrastructure

**Risk Mitigation:**
- Daily standups for coordination
- Architecture review after spike
- Extra attention to integration testing
```

## Integration with Backlog.md

The assessment integrates with backlog task management:

```bash
# Create task and run assessment
backlog task create "New feature" --ac "Criterion 1" --ac "Criterion 2"

# Assessment determines workflow
/flow:assess "New feature"

# Based on recommendation, choose approach:

# If Simple: Mark "In Progress" and implement
backlog task edit 1 -s "In Progress"

# If Medium: Create lightweight spec first
backlog task edit 1 -s "Specified"

# If Complex: Follow full SDD workflow
/flow:specify "New feature"
```

## Examples and Case Studies

### Example 1: Database Index Addition

```
Feature: Add index to users.email for faster lookups

Assessment:
- LOC: A (5 lines migration)
- Modules: A (1 migration file)
- Integrations: A (None)
- Data: B (Simple index, no schema change)
- Team: A (Solo)
- Cross-functional: A (Engineering only)
- Technical: A (Standard practice)
- Business Impact: A (Performance optimization)

Score: 9/32 (Simple)
Recommendation: Skip SDD

Approach:
1. Write migration
2. Test on staging
3. Quick PR review
4. Deploy during low-traffic window
```

### Example 2: User Profile Page

```
Feature: Build user profile editing page

Assessment:
- LOC: B (300 lines React + API)
- Modules: B (UI component + API endpoint + validation)
- Integrations: B (Database + image upload)
- Data: B (Update existing user table)
- Team: B (2 developers: frontend + backend)
- Cross-functional: B (Engineering + Design)
- Technical: A (Standard CRUD)
- Business Impact: B (User experience)

Score: 15/32 (Medium)
Recommendation: Spec-Light Mode

Approach:
1. Brief spec (1 page):
   - User flow mockups
   - API contract
   - Validation rules
   - Image upload approach
2. Frontend/backend parallel work
3. Integration testing
4. Standard code review
```

### Example 3: Multi-Tenant Architecture

```
Feature: Add multi-tenancy support across platform

Assessment:
- LOC: D (5000+ lines)
- Modules: D (All services, database, auth, UI)
- Integrations: C (All external APIs, database sharding)
- Data: D (Major schema changes, data migration)
- Team: D (10+ developers)
- Cross-functional: D (Eng, Product, Legal, Security, Customer Success)
- Technical: D (New architecture, multiple POCs)
- Business Impact: D (Foundational capability, revenue-critical)

Score: 31/32 (Complex)
Recommendation: Full SDD Workflow

Approach:
1. /flow:specify - Full PRD with business case
2. /flow:research - Competitive analysis, technical spikes
3. /flow:plan - Architecture blueprint, ADRs
4. Phased implementation:
   - Phase 1: Data model + migration strategy
   - Phase 2: Tenant isolation
   - Phase 3: UI and routing
5. /flow:validate - Security audit, QA
6. /flow:operate - Staged rollout with monitoring
```

## FAQ

**Q: What if I'm not sure about LOC estimate?**
A: Use order of magnitude: < 100, 100-500, 500-2000, > 2000. Ballpark is fine.

**Q: Should I count test code in LOC estimate?**
A: Yes, include all code you'll write (implementation + tests + config).

**Q: What if complexity increases during implementation?**
A: Upgrade your workflow. If a "simple" feature becomes complex, pause and create a spec.

**Q: Can I customize the questions or thresholds?**
A: Yes! Fork the command and adjust for your team's needs. Document your changes.

**Q: What if my team disagrees on the assessment?**
A: Discuss specific questions where opinions differ. Use team's collective experience. When in doubt, err on more planning.

**Q: Do I need to run this for every bug fix?**
A: No. Use judgment. Obvious simple tasks don't need formal assessment.

**Q: Should this assessment be in version control?**
A: Yes! Save assessment results with specs. Helps with retrospectives and calibration.

## References

- [Workflow Architecture Guide](./workflow-architecture.md)
- [Agent Loop Classification](../reference/agent-loop-classification.md)
- [Inner Loop Principles](../reference/inner-loop.md)
- [Outer Loop Principles](../reference/outer-loop.md)
- [Backlog.md User Guide](./backlog-user-guide.md)

## Summary

The `/flow:assess` command helps you:
1. **Make informed decisions** about workflow based on complexity
2. **Avoid over-engineering** simple features with excessive planning
3. **Reduce risk** on complex features through proper specification
4. **Calibrate** your team's planning processes
5. **Document** workflow decisions for future reference

Use it as a starting point, not a rigid rule. Apply team judgment, organizational context, and domain expertise to make the final decision.
