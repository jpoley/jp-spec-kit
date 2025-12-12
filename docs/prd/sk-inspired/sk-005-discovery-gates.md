# SK-005: Discovery Gates (Mandatory Interviews)

**Inspired by:** [spec-kitty](https://github.com/Priivacy-ai/spec-kitty) discovery interview system
**Priority:** P2 - Medium Impact
**Complexity:** Low (estimated 3-5 days implementation)
**Dependencies:** None

---

## 1. Problem Statement

Flowspec's workflow commands (`/flow:specify`, `/flow:plan`, etc.) allow AI agents to generate artifacts immediately based on initial descriptions. This leads to:

- **Assumption drift** - Agent makes assumptions user didn't intend
- **Missing context** - Critical requirements not captured
- **Rework cycles** - Artifacts need repeated revision
- **Scope creep** - Agent adds features not requested
- **Unclear priorities** - No explicit discussion of trade-offs

**How Spec-Kitty Solves This:**

Spec-kitty implements **discovery gates** - mandatory structured interviews before any artifact creation:

```
WAITING_FOR_DISCOVERY_INPUT

Before proceeding, please answer:
1. What are the core user personas?
2. What is the primary success metric?
3. Are there regulatory constraints?
```

The workflow **halts** until all questions are answered and an intent summary is confirmed.

---

## 2. Solution Overview

Add discovery gates to flowspec's `/flow:specify` and `/flow:plan` commands. Before creating artifacts, the agent conducts a structured interview proportional to feature complexity.

### Key Concepts

**Scope-Proportional Questioning:**
- Trivial features (hello world, simple fixes): 1-2 questions max
- Simple features (minor UI additions): 2-3 questions
- Complex features (new subsystems): 3-5 questions
- Critical features (auth, payments, security): 5+ questions with full rigor

**User Acceleration Signals:**
- "just testing" / "quick prototype" → Minimize questions, use defaults
- "production ready" / "enterprise" → Full rigor, all questions

**Blocking Marker:**
```
WAITING_FOR_DISCOVERY_INPUT

[Questions appear here]
```

Workflow halts until user provides answers.

**Intent Summary Confirmation:**
After discovery, agent paraphrases understanding for explicit confirmation before proceeding.

---

## 3. User Stories

### US-1: Discovery Interview for Specify
**As a** developer starting a new feature
**I want** the agent to ask clarifying questions before writing the PRD
**So that** the specification reflects my actual intent

**Acceptance Criteria:**
- [ ] `/flow:specify` starts with discovery questions, not immediate spec writing
- [ ] Questions are proportional to feature complexity
- [ ] `WAITING_FOR_DISCOVERY_INPUT` marker shown after questions
- [ ] Agent waits for all answers before proceeding
- [ ] Intent summary shown for confirmation before spec creation

### US-2: Discovery Interview for Plan
**As a** developer about to plan implementation
**I want** the agent to clarify technical decisions before writing the plan
**So that** the architecture matches my constraints and preferences

**Acceptance Criteria:**
- [ ] `/flow:plan` conducts technical discovery interview
- [ ] Questions about stack, constraints, patterns
- [ ] Agent doesn't assume technology choices
- [ ] Intent summary includes confirmed tech decisions

### US-3: Skip Discovery for Quick Tasks
**As a** developer doing a quick prototype
**I want to** skip detailed discovery
**So that** I can move fast on trivial tasks

**Acceptance Criteria:**
- [ ] Saying "quick prototype" or "just testing" triggers minimal questions
- [ ] Agent acknowledges acceleration and uses sensible defaults
- [ ] Artifacts still created but with default assumptions noted
- [ ] `--skip-discovery` flag for CLI invocation

### US-4: No Clarification Markers in Final Artifacts
**As a** developer reviewing generated artifacts
**I want** artifacts to have no unresolved placeholders
**So that** I know the spec is complete

**Acceptance Criteria:**
- [ ] No `[NEEDS CLARIFICATION: ...]` markers in final artifacts
- [ ] Any unresolved questions block artifact completion
- [ ] Clear indication of what needs clarification if blocked

---

## 4. Technical Design

### 4.1 Discovery Question Bank

Create domain-specific question banks for each workflow command:

```yaml
# templates/discovery/specify-questions.yml

questions:
  # Core questions (always asked)
  core:
    - id: user_personas
      question: "Who are the primary users of this feature? (e.g., end users, admins, API consumers)"
      why: "Ensures we design for the right audience"
      required: true

    - id: success_metric
      question: "What's the primary success metric? How will we know this feature is successful?"
      why: "Defines what 'done' means beyond just shipping code"
      required: true

  # Complexity-triggered questions
  complex:
    - id: regulatory
      question: "Are there regulatory or compliance requirements? (GDPR, HIPAA, PCI-DSS, etc.)"
      why: "Compliance affects architecture and data handling"
      triggers:
        - keywords: ["auth", "payment", "health", "finance", "personal data"]
        - complexity_score: >= 7

    - id: scalability
      question: "What's the expected scale? (users, requests/sec, data volume)"
      why: "Scale requirements affect architecture choices"
      triggers:
        - keywords: ["enterprise", "high traffic", "millions"]
        - complexity_score: >= 6

    - id: integrations
      question: "What external systems does this need to integrate with?"
      why: "Integration points often define architecture"
      triggers:
        - keywords: ["api", "integration", "connect", "sync"]

  # Critical feature questions
  critical:
    - id: security_model
      question: "What's the security model? Who can access what data?"
      why: "Security can't be bolted on later"
      triggers:
        - keywords: ["auth", "security", "permission", "access control"]
        - labels: ["security"]

    - id: failure_modes
      question: "What happens when this fails? What's the fallback behavior?"
      why: "Error handling is often underspecified"
      triggers:
        - keywords: ["critical", "payment", "transaction"]

# Acceleration signals
acceleration:
  skip_keywords:
    - "just testing"
    - "quick prototype"
    - "spike"
    - "experiment"
    - "proof of concept"
    - "skip questions"

  full_rigor_keywords:
    - "production"
    - "enterprise"
    - "mission critical"
    - "customer facing"
```

### 4.2 Discovery Engine Implementation

```python
# src/specify_cli/discovery/engine.py

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import yaml
import re

@dataclass
class DiscoveryQuestion:
    id: str
    question: str
    why: str
    required: bool = False
    answer: Optional[str] = None

@dataclass
class DiscoverySession:
    questions: List[DiscoveryQuestion]
    answers: Dict[str, str]
    intent_summary: Optional[str] = None
    confirmed: bool = False
    skipped: bool = False

class DiscoveryEngine:
    """Manages discovery interviews before artifact creation."""

    def __init__(self, questions_file: Path):
        self.questions_config = yaml.safe_load(questions_file.read_text())

    def should_skip_discovery(self, description: str) -> bool:
        """Check if user wants to skip discovery."""
        skip_keywords = self.questions_config.get("acceleration", {}).get("skip_keywords", [])
        description_lower = description.lower()
        return any(kw in description_lower for kw in skip_keywords)

    def should_use_full_rigor(self, description: str) -> bool:
        """Check if full rigor is warranted."""
        rigor_keywords = self.questions_config.get("acceleration", {}).get("full_rigor_keywords", [])
        description_lower = description.lower()
        return any(kw in description_lower for kw in rigor_keywords)

    def select_questions(
        self,
        description: str,
        complexity_score: int = 5,
        labels: List[str] = None
    ) -> List[DiscoveryQuestion]:
        """Select questions based on description and complexity."""
        labels = labels or []
        description_lower = description.lower()

        selected = []

        # Always include core questions
        for q in self.questions_config.get("questions", {}).get("core", []):
            selected.append(DiscoveryQuestion(
                id=q["id"],
                question=q["question"],
                why=q["why"],
                required=q.get("required", False)
            ))

        # Add complexity-triggered questions
        for q in self.questions_config.get("questions", {}).get("complex", []):
            if self._should_include(q, description_lower, complexity_score, labels):
                selected.append(DiscoveryQuestion(
                    id=q["id"],
                    question=q["question"],
                    why=q["why"],
                    required=q.get("required", False)
                ))

        # Add critical questions
        for q in self.questions_config.get("questions", {}).get("critical", []):
            if self._should_include(q, description_lower, complexity_score, labels):
                selected.append(DiscoveryQuestion(
                    id=q["id"],
                    question=q["question"],
                    why=q["why"],
                    required=q.get("required", False)
                ))

        # Limit questions based on complexity
        max_questions = self._get_max_questions(complexity_score)
        return selected[:max_questions]

    def _should_include(
        self,
        question: Dict,
        description: str,
        complexity_score: int,
        labels: List[str]
    ) -> bool:
        """Check if a question should be included based on triggers."""
        triggers = question.get("triggers", [])

        for trigger in triggers:
            # Keyword trigger
            if "keywords" in trigger:
                if any(kw in description for kw in trigger["keywords"]):
                    return True

            # Complexity trigger
            if "complexity_score" in trigger:
                condition = trigger["complexity_score"]
                if condition.startswith(">="):
                    threshold = int(condition[2:].strip())
                    if complexity_score >= threshold:
                        return True

            # Label trigger
            if "labels" in trigger:
                if any(lbl in labels for lbl in trigger["labels"]):
                    return True

        return False

    def _get_max_questions(self, complexity_score: int) -> int:
        """Get maximum questions based on complexity."""
        if complexity_score <= 2:
            return 2  # Trivial
        elif complexity_score <= 4:
            return 3  # Simple
        elif complexity_score <= 6:
            return 5  # Medium
        else:
            return 10  # Complex/Critical

    def format_discovery_prompt(
        self,
        questions: List[DiscoveryQuestion],
        context: str = ""
    ) -> str:
        """Format questions as a discovery prompt."""
        prompt = """## Discovery Interview

Before creating artifacts, let's ensure we capture your intent correctly.

"""
        if context:
            prompt += f"**Context:** {context}\n\n"

        prompt += "Please answer the following questions:\n\n"

        for i, q in enumerate(questions, 1):
            prompt += f"**{i}. {q.question}**\n"
            prompt += f"   *Why this matters:* {q.why}\n\n"

        prompt += """
---

WAITING_FOR_DISCOVERY_INPUT

Please provide your answers above. Once complete, I'll summarize your intent for confirmation before proceeding.
"""
        return prompt

    def format_intent_summary(
        self,
        description: str,
        answers: Dict[str, str]
    ) -> str:
        """Format intent summary for confirmation."""
        summary = f"""## Intent Summary

Based on your answers, here's my understanding of what we're building:

**Feature:** {description}

**Key Details:**
"""
        for q_id, answer in answers.items():
            summary += f"- **{q_id.replace('_', ' ').title()}:** {answer}\n"

        summary += """

---

**Does this accurately capture your intent?** (yes/no/adjust)

If yes, I'll proceed with creating the specification.
If no, please tell me what needs to change.
"""
        return summary
```

### 4.3 Command Template Integration

Update `/flow:specify` command template to include discovery:

```markdown
---
description: Create or update feature specifications with discovery interview
---

# /flow:specify

Create a feature specification through structured discovery and documentation.

## Discovery Phase

Before writing any artifacts, conduct a discovery interview:

1. **Assess Complexity**
   - Parse the feature description for complexity signals
   - Check for acceleration signals ("just testing", "production ready")
   - Determine question count (2-10 based on complexity)

2. **Conduct Interview**
   - Present selected questions with "Why this matters" context
   - End with: `WAITING_FOR_DISCOVERY_INPUT`
   - Wait for user responses

3. **Confirm Intent**
   - Summarize understanding in plain language
   - Ask for explicit confirmation
   - If "no" or "adjust", refine understanding

## Artifact Creation (After Discovery Confirmed)

Only after discovery is confirmed:

1. Create PRD using mission template
2. Create backlog tasks
3. Generate acceptance criteria

## CRITICAL RULES

- **NEVER** write PRD or create tasks until discovery is complete and confirmed
- **NEVER** include `[NEEDS CLARIFICATION: ...]` in final artifacts
- If user says "skip questions", use minimal discovery (2 questions max) and note assumptions
- Always show intent summary before proceeding

## Example Flow

```
User: /flow:specify Add user authentication with OAuth

Agent: ## Discovery Interview

Before creating artifacts, let's ensure we capture your intent correctly.

**1. Who are the primary users of this feature?**
   *Why this matters:* Ensures we design for the right audience

**2. What OAuth providers do you need to support?**
   *Why this matters:* Affects implementation complexity and dependencies

**3. What's the security model for user sessions?**
   *Why this matters:* Security can't be bolted on later

---

WAITING_FOR_DISCOVERY_INPUT

User: 1. End users of our SaaS platform
      2. Google and GitHub OAuth
      3. JWT tokens with 24h expiry, refresh tokens for remember me

Agent: ## Intent Summary

Based on your answers, here's my understanding:

**Feature:** User authentication with OAuth

**Key Details:**
- **Users:** End users of SaaS platform
- **OAuth Providers:** Google, GitHub
- **Session Security:** JWT with 24h expiry + refresh tokens

**Does this accurately capture your intent?** (yes/no/adjust)

User: yes

Agent: [Proceeds to create PRD and tasks]
```
```

### 4.4 Clarification Marker Validation

Add validation to ensure no clarification markers in final artifacts:

```python
# src/specify_cli/validation/artifact_validator.py

import re
from pathlib import Path
from typing import List, Tuple

CLARIFICATION_PATTERNS = [
    r'\[NEEDS CLARIFICATION:.*?\]',
    r'\[TODO:.*?\]',
    r'\[TBD\]',
    r'\[PLACEHOLDER\]',
    r'\?\?\?',
    r'XXX',
]

def validate_no_clarifications(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check that a file has no unresolved clarification markers.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    content = file_path.read_text()
    issues = []

    for pattern in CLARIFICATION_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append(f"Found clarification marker: {match}")

    return len(issues) == 0, issues

def validate_artifacts_directory(dir_path: Path) -> Dict[str, List[str]]:
    """Validate all artifacts in a directory."""
    results = {}

    for md_file in dir_path.glob("**/*.md"):
        is_valid, issues = validate_no_clarifications(md_file)
        if not is_valid:
            results[str(md_file)] = issues

    return results
```

---

## 5. User Experience Examples

### Example 1: Standard Feature

```
User: /flow:specify Add shopping cart functionality

Agent: ## Discovery Interview

Before creating the specification, let me understand your requirements:

**1. Who are the primary users of this feature?**
   *Why this matters:* Ensures we design for the right audience

**2. What's the primary success metric?**
   *Why this matters:* Defines what 'done' means

**3. What payment providers need to be supported?**
   *Why this matters:* Integration requirements affect architecture

**4. What happens when payment fails?**
   *Why this matters:* Error handling is often underspecified

---

WAITING_FOR_DISCOVERY_INPUT

User: 1. E-commerce customers
      2. Conversion rate from cart to purchase
      3. Stripe only for now
      4. Show error, keep items in cart, allow retry

Agent: ## Intent Summary

**Feature:** Shopping cart functionality

**Key Details:**
- **Users:** E-commerce customers
- **Success Metric:** Cart-to-purchase conversion rate
- **Payment:** Stripe integration
- **Failure Handling:** Show error, preserve cart, allow retry

**Does this accurately capture your intent?** (yes/no/adjust)

User: yes

Agent: Creating specification...
[Creates PRD and tasks]
```

### Example 2: Quick Prototype (Accelerated)

```
User: /flow:specify Add a hello world endpoint, just testing the framework

Agent: ## Quick Discovery

You've indicated this is a quick prototype. I'll keep this brief:

**1. Any specific framework preference?**

---

WAITING_FOR_DISCOVERY_INPUT

User: FastAPI

Agent: ## Intent Summary

**Feature:** Hello world endpoint (prototype)
**Framework:** FastAPI
**Assumptions:** No authentication, no persistence, minimal error handling

**Proceed with these defaults?** (yes/adjust)

User: yes

Agent: [Creates minimal spec with noted assumptions]
```

### Example 3: Critical Feature (Full Rigor)

```
User: /flow:specify Add payment processing for enterprise customers

Agent: ## Discovery Interview - Full Rigor

This appears to be a critical, enterprise feature. I'll ask comprehensive questions:

**1. Who are the primary users?**
**2. What's the primary success metric?**
**3. What payment methods need support?**
**4. What's the expected transaction volume?**
**5. What compliance requirements apply? (PCI-DSS, regional regulations)**
**6. What's the security model for payment data?**
**7. What happens on payment failure?**
**8. Are there retry/reconciliation requirements?**

---

WAITING_FOR_DISCOVERY_INPUT

[Full interview continues...]
```

---

## 6. Implementation Plan

### Phase 1: Core Engine (Day 1-2)
1. Create `src/specify_cli/discovery/` module
2. Implement `DiscoveryEngine` class
3. Create question banks for specify and plan
4. Unit tests

### Phase 2: Command Integration (Day 2-3)
1. Update `/flow:specify` template with discovery
2. Update `/flow:plan` template with technical discovery
3. Add `--skip-discovery` flag
4. Integration tests

### Phase 3: Validation (Day 3-4)
1. Implement clarification marker validation
2. Add validation to artifact creation
3. Block artifact save if markers present
4. Error messages and guidance

### Phase 4: Documentation (Day 4-5)
1. Update CLAUDE.md with discovery workflow
2. Add examples to command help
3. Update user guide

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Discovery questions asked | 2-10 (complexity proportional) |
| Artifacts with clarification markers | 0% |
| User satisfaction with intent capture | Track via feedback |
| Rework cycles reduced | Measure before/after |

---

## 8. Configuration

Users can customize discovery behavior in `.specify/config.yml`:

```yaml
discovery:
  enabled: true
  min_questions: 2
  max_questions: 10
  skip_for_complexity_under: 3  # Skip for trivial tasks
  require_confirmation: true
  custom_questions_file: ".specify/discovery-questions.yml"
```

---

## 9. References

- [spec-kitty discovery gates documentation](https://github.com/Priivacy-ai/spec-kitty/blob/main/templates/commands/specify.md)
- [spec-kitty WAITING_FOR_DISCOVERY_INPUT pattern](https://raw.githubusercontent.com/Priivacy-ai/spec-kitty/main/templates/commands/specify.md)
