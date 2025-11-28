---
description: Evaluate if SDD workflow is appropriate for a feature. Output: Full SDD workflow (complex), Spec-light mode (medium), Skip SDD (simple).
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command evaluates feature complexity to determine the appropriate development workflow. It assesses multiple dimensions and provides a clear recommendation: Full SDD, Spec-light, or Skip SDD.

### Assessment Process

Guide the user through a structured complexity assessment by asking the following questions. Based on their responses, calculate a complexity score and recommend the appropriate workflow.

#### 1. Scope and Size Assessment

**Question 1: Estimated Lines of Code (LOC)**
```
How many lines of code do you estimate this feature will require?

Options:
A. < 100 lines (Small: Simple utility, configuration change, minor fix)
B. 100-500 lines (Medium: New component, API endpoint, service integration)
C. 500-2000 lines (Large: New module, complex feature, multi-component)
D. > 2000 lines (Very Large: New subsystem, major architectural change)

Score: A=1, B=2, C=3, D=4
```

**Question 2: Number of Modules/Components Affected**
```
How many modules, services, or components will this feature touch?

Options:
A. 1 module (Single-file change, isolated component)
B. 2-3 modules (Multiple related components, service + client)
C. 4-6 modules (Cross-cutting change, multiple services)
D. 7+ modules (System-wide change, architectural refactor)

Score: A=1, B=2, C=3, D=4
```

#### 2. Integration and Dependency Assessment

**Question 3: External Integrations**
```
How many external systems, APIs, or services will this feature integrate with?

Options:
A. 0 integrations (Pure internal logic, no external dependencies)
B. 1-2 integrations (Single third-party API, simple database)
C. 3-4 integrations (Multiple APIs, complex data flows)
D. 5+ integrations (Complex orchestration, multi-system coordination)

Score: A=1, B=2, C=3, D=4
```

**Question 4: Data Complexity**
```
What is the complexity of data modeling and persistence requirements?

Options:
A. No persistence (In-memory only, stateless)
B. Simple persistence (Single table, basic CRUD)
C. Moderate persistence (Multiple tables, relationships, migrations)
D. Complex persistence (Complex schemas, data migrations, legacy compatibility)

Score: A=1, B=2, C=3, D=4
```

#### 3. Team and Process Assessment

**Question 5: Team Coordination Requirements**
```
How many people will need to collaborate on this feature?

Options:
A. Solo developer (One person, clear ownership)
B. 2-3 developers (Small team, pair programming)
C. 4-6 developers (Medium team, requires coordination)
D. 7+ developers (Large team, complex orchestration)

Score: A=1, B=2, C=3, D=4
```

**Question 6: Cross-Functional Requirements**
```
Which roles/disciplines are required for this feature?

Options:
A. Engineering only (Pure technical implementation)
B. Engineering + Design (UI/UX considerations)
C. Engineering + Design + Product (Requires product decisions)
D. Full cross-functional (Engineering, Design, Product, Security, Legal, etc.)

Score: A=1, B=2, C=3, D=4
```

#### 4. Risk and Uncertainty Assessment

**Question 7: Technical Uncertainty**
```
How well understood is the technical approach?

Options:
A. Well-known pattern (Standard implementation, proven approach)
B. Some unknowns (Minor research needed, 1-2 spikes)
C. Significant unknowns (Multiple spikes, proof of concept needed)
D. High uncertainty (New technology, R&D required, multiple experiments)

Score: A=1, B=2, C=3, D=4
```

**Question 8: Business Impact and Risk**
```
What is the business impact if this feature fails or has bugs?

Options:
A. Low impact (Internal tool, non-critical feature)
B. Medium impact (Affects user experience, non-critical functionality)
C. High impact (Revenue-affecting, critical user journey)
D. Critical impact (Security, compliance, data integrity, revenue-critical)

Score: A=1, B=2, C=3, D=4
```

### Scoring and Recommendation Logic

**Total Score Calculation**: Sum all 8 question scores (range: 8-32)

**Complexity Classification**:
- **Simple** (8-12 points): Low complexity, well-understood problem
- **Medium** (13-20 points): Moderate complexity, some coordination needed
- **Complex** (21-32 points): High complexity, significant effort and coordination

**Workflow Recommendations**:

#### Simple Features (8-12 points) → **Skip SDD**
```
✅ RECOMMENDATION: Skip Spec-Driven Development

This feature is simple enough to proceed directly to implementation.

Suggested Approach:
1. Write a brief task description in backlog.md with acceptance criteria
2. Move task to "In Progress" and implement directly
3. Focus on code quality and testing
4. Quick code review before merging

Example Features:
- Bug fixes with clear root cause
- Configuration changes
- Simple utility functions
- Minor UI tweaks
- Documentation updates

Why Skip SDD?
- Overhead of specification would slow down delivery
- Problem and solution are well-understood
- Minimal coordination required
- Low risk if approach changes during implementation
```

#### Medium Features (13-20 points) → **Spec-Light Mode**
```
✅ RECOMMENDATION: Spec-Light Mode

This feature requires some planning but not full SDD workflow.

Suggested Approach:
1. Create lightweight specification (1-2 pages):
   - Problem statement and context
   - High-level solution approach
   - Key acceptance criteria
   - Integration points and dependencies
   - Testing approach
2. Optional: Quick technical spike if unknowns exist
3. Brief architecture review (async or 30-min sync)
4. Implement with standard code review
5. Integration testing before merge

Skip These SDD Phases:
- ❌ /jpspec:research (Business validation)
- ❌ /jpspec:plan (Full architectural planning)
- ❌ /jpspec:validate (Dedicated validation phase)

Use These SDD Phases:
- ✅ /jpspec:specify (Lightweight spec only)
- ✅ /jpspec:implement (Direct implementation)

Example Features:
- New API endpoint with moderate complexity
- UI component with business logic
- Service integration with 1-2 external APIs
- Database schema additions
- Feature flags and A/B tests

Why Spec-Light?
- Captures key decisions without excessive documentation
- Enables team alignment without process overhead
- Maintains flexibility during implementation
- Reduces coordination overhead
```

#### Complex Features (21-32 points) → **Full SDD Workflow**
```
✅ RECOMMENDATION: Full Spec-Driven Development Workflow

This feature requires comprehensive planning and coordination.

Suggested Approach:
1. /jpspec:specify - Comprehensive PRD with:
   - Problem statement and business context
   - User stories and acceptance criteria
   - Success metrics and KPIs
   - Risk assessment (DVF+V framework)

2. /jpspec:research - Market and technical validation:
   - Competitive analysis
   - Technical feasibility assessment
   - Business viability evaluation

3. /jpspec:plan - Architectural planning:
   - System architecture and component design
   - Platform and infrastructure design
   - ADRs for key decisions
   - Integration patterns

4. /jpspec:implement - Phased implementation:
   - Parallel frontend/backend development
   - Comprehensive code review
   - Integration testing

5. /jpspec:validate - Quality assurance:
   - QA testing and validation
   - Security review
   - Documentation review

6. /jpspec:operate - Production deployment:
   - CI/CD pipeline setup
   - Observability and monitoring
   - Deployment and rollout

Example Features:
- New product capabilities or user journeys
- System-wide architectural changes
- Multi-team integration projects
- High-stakes business-critical features
- Complex data migrations
- Security or compliance initiatives

Why Full SDD?
- High coordination overhead requires clear specifications
- Multiple stakeholders need alignment
- High business risk requires validation
- Complex architecture needs documented decisions
- Long implementation timeline benefits from phased approach
```

### Output Format

After collecting all assessment responses, provide a comprehensive recommendation:

```markdown
# Feature Complexity Assessment

## Feature: [Feature Name]

## Assessment Results

### Scope and Size
- Lines of Code: [Answer] (Score: X)
- Modules Affected: [Answer] (Score: X)

### Integration and Dependencies
- External Integrations: [Answer] (Score: X)
- Data Complexity: [Answer] (Score: X)

### Team and Process
- Team Size: [Answer] (Score: X)
- Cross-Functional Needs: [Answer] (Score: X)

### Risk and Uncertainty
- Technical Uncertainty: [Answer] (Score: X)
- Business Impact: [Answer] (Score: X)

## Complexity Score: X/32

**Classification: [Simple/Medium/Complex]**

## Recommendation: [Skip SDD / Spec-Light Mode / Full SDD Workflow]

[Include detailed recommendation text from above]

## Next Steps

[Provide specific actionable steps based on recommendation]

## Notes

- This assessment is a guideline, not a strict rule
- Use your judgment based on team context and project needs
- You can always upgrade to a more rigorous workflow if complexity increases
- Consider organizational standards and compliance requirements
```

### Integration with `specify init`

When users run `specify init`, offer to run this assessment first:

```
Before initializing, would you like to assess if Spec-Driven Development is appropriate for this feature?

[Y/n]:
```

If yes, run the assessment and recommend next steps based on results.

### Validation and Calibration

Encourage teams to calibrate this assessment tool:
- Track assessment scores vs actual complexity
- Adjust thresholds based on team experience
- Document exceptions and rationale
- Refine questions based on domain-specific needs

### Example Scenarios

#### Example 1: Simple Bug Fix
```
Feature: Fix button alignment on login page

Q1: LOC? A (20 lines CSS)
Q2: Modules? A (1 component)
Q3: Integrations? A (None)
Q4: Data? A (No persistence)
Q5: Team? A (Solo)
Q6: Cross-functional? A (Engineering only)
Q7: Technical? A (Well-known)
Q8: Business impact? A (Low)

Total: 8/32 (Simple)
→ Skip SDD, implement directly
```

#### Example 2: New API Endpoint
```
Feature: Add user preferences API endpoint

Q1: LOC? B (200 lines)
Q2: Modules? B (API + DB + Client)
Q3: Integrations? B (Database + Cache)
Q4: Data? C (New tables + migrations)
Q5: Team? B (2 developers)
Q6: Cross-functional? A (Engineering only)
Q7: Technical? A (Standard REST API)
Q8: Business impact? B (User experience)

Total: 15/32 (Medium)
→ Spec-Light Mode
```

#### Example 3: Payment Integration
```
Feature: Integrate Stripe payment processing

Q1: LOC? C (1000+ lines)
Q2: Modules? C (Payment service, UI, webhooks, admin)
Q3: Integrations? C (Stripe, database, email, analytics)
Q4: Data? D (Complex transactions, PCI compliance)
Q5: Team? C (4-5 developers)
Q6: Cross-functional? D (Eng, Product, Legal, Security)
Q7: Technical? C (Multiple spikes needed)
Q8: Business impact? D (Revenue-critical, PCI compliance)

Total: 27/32 (Complex)
→ Full SDD Workflow
```

## Final Notes

**This assessment is a tool, not a mandate.** Consider:
- Organizational standards and compliance requirements
- Team experience and maturity
- Time constraints and deadlines
- Stakeholder expectations
- Domain-specific risk factors

**When in doubt, err on the side of more planning** - it's easier to streamline a workflow than to add planning after issues arise.

**Continuous improvement** - Regularly review assessment outcomes and adjust thresholds based on your team's experience.
