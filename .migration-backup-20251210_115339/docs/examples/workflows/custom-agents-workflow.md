# Custom Agents Workflow Example

## Overview

This configuration demonstrates how to add organization-specific custom agents to the standard SDD workflow. It includes 9 custom agents across planning, implementation, and validation phases.

**Key Concept**: Extend the workflow with specialized agents for your organization's unique needs.

## Custom Agents Included

### Planning & Governance Agents

1. **Legal Counsel** (`@legal-counsel`)
   - Terms of Service review
   - Privacy policy compliance
   - Intellectual property review
   - Regulatory compliance

2. **Compliance Officer** (`@compliance-officer`)
   - SOC2/GDPR/HIPAA compliance
   - Data retention policy review
   - Audit requirements

3. **Data Scientist** (`@data-scientist`)
   - ML/AI requirements analysis
   - Data pipeline requirements
   - Dataset feasibility

4. **ML Architect** (`@ml-architect`)
   - ML pipeline architecture
   - Feature store design
   - Model serving architecture

5. **Performance Engineer** (`@performance-engineer`)
   - Performance budget definition
   - Caching strategy
   - Load testing strategy

### Implementation Agents

6. **ML Engineer** (`@ml-engineer`)
   - Model training pipeline
   - Feature engineering
   - Model deployment

### Validation & Quality Agents

7. **Accessibility Specialist** (`@accessibility-specialist`)
   - WCAG 2.1 AA compliance
   - Screen reader testing
   - ARIA attributes review

### Operations & DevRel Agents

8. **Developer Advocate** (`@developer-advocate`)
   - SDK documentation review
   - Code examples validation
   - Developer experience

9. **MLOps Engineer** (`@ml-ops-engineer`)
   - Model deployment to production
   - Model monitoring
   - A/B testing infrastructure

## Workflow Diagram

```
To Do
  ↓ /jpspec:assess
Assessed
  ↓ /jpspec:specify (+ data-scientist)
Specified
  ↓ /jpspec:legal-review (CUSTOM - legal-counsel, compliance-officer)
Legal Reviewed
  ↓ /jpspec:research (optional, + data-scientist)
Researched
  ↓ /jpspec:plan (+ ml-architect)
Planned
  ↓ /jpspec:performance-design (CUSTOM - performance-engineer)
Performance Designed
  ↓ /jpspec:implement (+ ml-engineer)
In Implementation
  ↓ /jpspec:accessibility-test (CUSTOM - accessibility-specialist)
Accessibility Tested
  ↓ /jpspec:validate (+ performance-engineer)
Validated
  ↓ /jpspec:devrel-review (CUSTOM - developer-advocate)
Documentation Reviewed
  ↓ /jpspec:operate (+ ml-ops-engineer)
Deployed
  ↓ manual
Done
```

## Custom Workflows Added

### 1. Legal Review Workflow

**Command**: `/jpspec:legal-review`

**When**: After specification, before research/planning

**Purpose**: Ensure legal and compliance requirements are identified early

**Agents**:
- **legal-counsel** - Legal compliance review
- **compliance-officer** - Regulatory compliance

**Approval Gate**: `KEYWORD[LEGAL_APPROVED]`

**Artifacts**:
- `docs/legal/{feature}-legal-review.md` - Legal review report

**Example Artifact**:
```markdown
# Legal Review: User Data Export Feature

## Review Date
2025-12-01

## Legal Counsel
Jane Doe, Corporate Legal

## Compliance Officer
John Smith, Compliance

## Requirements Reviewed
- [x] GDPR Article 20 (Right to data portability)
- [x] CCPA data export requirements
- [x] Terms of Service update needed
- [x] Privacy policy update needed

## Legal Risks Identified
1. **Medium Risk**: User data may include third-party data (e.g., comments from other users)
   - **Mitigation**: Exclude third-party data from export, document in privacy policy

2. **Low Risk**: Export format not specified in ToS
   - **Mitigation**: Update ToS to specify JSON format

## Compliance Requirements
- Data export must complete within 30 days (GDPR requirement)
- Export must include all personal data
- Audit log required for export requests

## Approval
**LEGAL_APPROVED** - 2025-12-01

All legal requirements identified and documented. Proceed with implementation.
```

### 2. Performance Design Workflow

**Command**: `/jpspec:performance-design`

**When**: After planning, before implementation

**Purpose**: Define performance budgets and optimization strategy

**Agents**:
- **performance-engineer** - Performance architecture

**Artifacts**:
- `docs/performance/{feature}-budget.md` - Performance budget

**Example Artifact**:
```markdown
# Performance Budget: Search Results Page

## Page Load Metrics
- **First Contentful Paint (FCP)**: < 1.5s (target: 1.0s)
- **Largest Contentful Paint (LCP)**: < 2.5s (target: 2.0s)
- **Time to Interactive (TTI)**: < 3.5s (target: 3.0s)
- **Cumulative Layout Shift (CLS)**: < 0.1 (target: 0.05)

## API Performance
- **Search API Response Time**: < 200ms p95 (target: 150ms)
- **Faceting API Response Time**: < 100ms p95 (target: 80ms)

## Caching Strategy
- **Search Results**: Redis cache, 5-minute TTL
- **Facet Counts**: Materialized view, updated every 10 minutes
- **CDN**: Cloudflare, cache static assets for 24 hours

## Database Queries
- **Max Query Time**: < 100ms (target: 50ms)
- **Elasticsearch Query**: < 50ms p95
- **PostgreSQL Query**: < 30ms p95

## Load Testing
- **Target RPS**: 1000 requests/second
- **Concurrent Users**: 10,000
- **Test Duration**: 30 minutes
```

### 3. Accessibility Testing Workflow

**Command**: `/jpspec:accessibility-test`

**When**: After implementation, before validation

**Purpose**: Ensure WCAG 2.1 AA compliance

**Agents**:
- **accessibility-specialist** - WCAG testing

**Artifacts**:
- `docs/accessibility/{feature}-wcag-report.md` - Accessibility report

**Example Artifact**:
```markdown
# Accessibility Report: User Profile Form

## WCAG 2.1 AA Compliance

### Perceivable (Pass)
- [x] 1.1.1 Non-text Content - All images have alt text
- [x] 1.3.1 Info and Relationships - Semantic HTML used
- [x] 1.4.3 Contrast (Minimum) - All text meets 4.5:1 ratio

### Operable (Pass)
- [x] 2.1.1 Keyboard - All functions keyboard accessible
- [x] 2.1.2 No Keyboard Trap - Tab navigation works correctly
- [x] 2.4.3 Focus Order - Logical focus order maintained

### Understandable (Pass)
- [x] 3.1.1 Language of Page - lang="en" set
- [x] 3.3.1 Error Identification - Validation errors clearly identified
- [x] 3.3.2 Labels or Instructions - All form fields labeled

### Robust (Pass)
- [x] 4.1.2 Name, Role, Value - ARIA attributes correct

## Screen Reader Testing
- **NVDA (Windows)**: Pass
- **JAWS (Windows)**: Pass
- **VoiceOver (macOS)**: Pass

## Keyboard Navigation
- **Tab Order**: Logical and complete
- **Skip Links**: Working
- **Focus Indicators**: Visible at 3:1 contrast

## Issues Found
None - Full WCAG 2.1 AA compliance achieved.

## Approval
WCAG 2.1 AA compliant - Approved for production.
```

### 4. DevRel Review Workflow

**Command**: `/jpspec:devrel-review`

**When**: After validation, before deployment

**Purpose**: Ensure developer-facing features have excellent documentation

**Agents**:
- **developer-advocate** - Developer experience

**Artifacts**:
- `docs/devrel/{feature}-developer-guide.md` - Developer guide

## Usage

### 1. Create Custom Agent Definitions

Create agent definition files in `.agents/` directory:

```bash
mkdir -p .agents

# Legal Counsel
cat > .agents/legal-counsel.md <<EOF
# Legal Counsel Agent

## Identity
@legal-counsel

## Description
Corporate Legal Counsel specializing in technology and privacy law

## Responsibilities
- Review Terms of Service implications
- Assess privacy policy compliance (GDPR, CCPA)
- Evaluate intellectual property concerns
- Identify regulatory compliance requirements

## Expertise
- GDPR, CCPA, HIPAA compliance
- Software licensing (MIT, Apache, GPL)
- Terms of Service contracts
- Data processing agreements
EOF

# Similar files for other custom agents...
```

### 2. Copy Workflow Configuration

```bash
cp docs/examples/workflows/custom-agents-workflow.yml jpspec_workflow.yml
specify workflow validate
```

### 3. Run Custom Workflows

```bash
/jpspec:assess
/jpspec:specify
# Includes data-scientist agent

/jpspec:legal-review
# Review docs/legal/{feature}-legal-review.md
# Type LEGAL_APPROVED to proceed

/jpspec:plan
# Includes ml-architect agent

/jpspec:performance-design
# Creates performance budget

/jpspec:implement
# Includes ml-engineer agent

/jpspec:accessibility-test
# WCAG compliance testing

/jpspec:validate
# Includes performance-engineer for load testing

/jpspec:devrel-review
# Developer documentation review

/jpspec:operate
# Includes ml-ops-engineer

backlog task edit task-123 -s Done
```

## When to Add Custom Agents

### Use Cases by Industry

**Financial Services**:
- **Compliance Officer** - SOC2, PCI-DSS
- **Risk Management Specialist** - Financial risk assessment
- **Fraud Detection Engineer** - Anti-fraud systems

**Healthcare**:
- **HIPAA Compliance Officer** - HIPAA Privacy/Security rules
- **Clinical Informaticist** - Medical domain expertise
- **PHI Security Specialist** - Protected Health Information

**E-commerce**:
- **Conversion Optimization Specialist** - A/B testing, UX
- **Payment Security Engineer** - PCI-DSS compliance
- **Localization Specialist** - Multi-region support

**SaaS/Platform**:
- **Developer Advocate** - SDK documentation, DX
- **API Product Manager** - API design, versioning
- **Multi-Tenancy Specialist** - Tenant isolation

**AI/ML Products**:
- **Data Scientist** - Model requirements
- **ML Architect** - ML pipeline design
- **MLOps Engineer** - Model deployment
- **AI Ethics Specialist** - Bias detection, fairness

## How to Add a Custom Agent

### Step 1: Identify the Need

Ask:
- What specialized knowledge does this feature require?
- Are existing agents covering all aspects?
- Is this a one-off need or recurring pattern?

### Step 2: Define the Agent

Create `.agents/{agent-name}.md`:

```markdown
# {Agent Name} Agent

## Identity
@{agent-identity}

## Description
{Role title and expertise area}

## Responsibilities
- {Responsibility 1}
- {Responsibility 2}
- {Responsibility 3}

## Expertise
- {Expertise area 1}
- {Expertise area 2}

## Decision Authority
- {What this agent can approve/reject}

## Escalation
- {When to escalate to human expert}
```

### Step 3: Add to Workflow

Edit `jpspec_workflow.yml`:

```yaml
workflows:
  {workflow-name}:
    agents:
      # ... existing agents
      - name: "{agent-name}"
        identity: "@{agent-identity}"
        description: "{description}"
        responsibilities:
          - "{responsibility 1}"
          - "{responsibility 2}"
```

### Step 4: Classify Agent Loop

```yaml
agent_loops:
  inner:  # Fast iteration
    agents:
      - "{agent-name}"  # If agent does coding/reviews

  outer:  # Governance
    agents:
      - "{agent-name}"  # If agent does planning/compliance
```

### Step 5: Test

```bash
specify workflow validate

# Run the workflow
/{workflow-command}
# Verify custom agent participates
```

## Best Practices

### 1. Clear Responsibilities

**Good**:
```yaml
- name: "legal-counsel"
  responsibilities:
    - "Review Terms of Service implications"
    - "Assess GDPR compliance"
    - "Evaluate data retention policies"
```

**Bad**:
```yaml
- name: "legal-counsel"
  responsibilities:
    - "Legal stuff"
    - "Compliance"
```

### 2. Avoid Overlapping Responsibilities

Don't create agents that duplicate existing agent duties:

**Bad**:
```yaml
- name: "security-tester"
  responsibilities:
    - "Security testing"  # Overlaps with secure-by-design-engineer
```

**Good**: Extend existing agent or create specialized sub-role:
```yaml
- name: "penetration-tester"
  responsibilities:
    - "Offensive security testing"  # Specialized, not duplicate
    - "Red team exercises"
```

### 3. Define Decision Authority

Specify what the agent can approve:

```yaml
- name: "compliance-officer"
  description: "Compliance Officer"
  responsibilities:
    - "SOC2 compliance verification"
  decision_authority:
    - "Can approve/reject deployments based on compliance"
    - "Can require additional audits"
```

### 4. Establish Escalation Paths

Document when to involve humans:

```markdown
## Escalation
- Legal risk rated "High" or "Critical" → Escalate to General Counsel
- Regulatory uncertainty → Escalate to Compliance Committee
- Intellectual property concerns → Escalate to IP Attorney
```

### 5. Reuse Agents Across Workflows

If an agent is needed in multiple phases, reuse them:

```yaml
workflows:
  specify:
    agents:
      - name: "data-scientist"  # Define requirements

  research:
    agents:
      - name: "data-scientist"  # Assess feasibility

  validate:
    agents:
      - name: "data-scientist"  # Validate model performance
```

## Comparison to Standard Workflow

| Aspect | Standard Workflow | Custom Agents Workflow |
|--------|-------------------|------------------------|
| **Agent Count** | 16 | 25 (16 standard + 9 custom) |
| **Workflow Count** | 7 | 11 (7 standard + 4 custom) |
| **State Count** | 9 | 13 (9 standard + 4 custom) |
| **Time to Deploy** | ~1-2 weeks | ~2-4 weeks (more reviews) |
| **Specialization** | General SDD | Industry-specific |
| **Best For** | Standard web apps | Regulated industries, ML/AI, APIs |

## Related Examples

- [Minimal Workflow](./minimal-workflow.md) - Simplest workflow
- [Security Audit Workflow](./security-audit-workflow.md) - Enhanced security
- [Parallel Workflows](./parallel-workflows.md) - Multi-track development
