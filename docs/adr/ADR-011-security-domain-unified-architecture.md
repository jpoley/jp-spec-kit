# ADR-011: Security Domain Unified Architecture

**Status:** Proposed
**Date:** 2025-12-04
**Author:** Enterprise Software Architect (Hohpe Principles Expert)
**Context:** Security scanning, triage, and remediation system (22 tasks)
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

Security vulnerabilities in code create **latent risk** that compounds over time:
- Developers face **alert fatigue** from false positives (60-80% of SAST findings)
- Manual triage of findings is **time-consuming** (15-30 minutes per vulnerability)
- Remediation requires **deep security expertise** (scarce resource)
- Compliance audits demand **audit trails** for all security decisions

**The Core Tension:** Security scanning tools produce **high-volume, noisy output** that overwhelms developers, yet **every true positive** represents real business risk.

**Business Impact:**
- **Velocity Tax:** Security reviews delay releases by 2-5 days
- **False Confidence:** Ignored findings hide critical vulnerabilities
- **Compliance Risk:** Missing audit trails expose organization to regulatory penalties
- **Talent Drain:** Security experts spend time on trivial triage instead of architecture

### Business Value (Strategic Investment)

**Primary Value Streams:**

1. **AI-Powered Triage** - Classify findings as TP/FP/NI with >85% accuracy, reducing human triage time by 70%
2. **Automated Remediation** - Generate fix patches for common vulnerabilities, reducing remediation time from hours to minutes
3. **Security Observability** - Real-time security posture dashboard with DORA metrics integration
4. **Compliance Automation** - Automated audit reports with provenance for regulatory requirements

**Success Metrics:**

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| Triage time per finding | 20 min | <5 min | 3 months |
| False positive rate | 70% | <20% | 6 months |
| Mean time to remediation (MTTR) | 5 days | <1 day | 6 months |
| Security scan coverage | 40% | >90% | 3 months |

### Investment Justification (Selling the Option)

**Option Value:**
- **Composability Premium:** MCP integration enables security-as-a-service for other agents
- **Platform Play:** Security scanning becomes core platform capability, not afterthought
- **Competitive Moat:** First SDD toolkit with AI-powered security triage and automated remediation

**Cost:**
- **Development:** 8-10 weeks (scanner orchestration + AI triage + remediation engine + MCP server)
- **Maintenance:** Medium (AI model updates, scanner version tracking)

**Decision:** Build security domain as first-class SDD workflow phase

---

## Decision

### Chosen Architecture: Layered Security Platform

Implement **Security Scanner Platform** with three core layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                   SECURITY PLATFORM ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              PRESENTATION LAYER                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  /jpspec:    │  │   MCP        │  │   Reports    │    │ │
│  │  │  security    │  │  Server      │  │  Generator   │    │ │
│  │  │  CLI         │  │  (Tools)     │  │  (Audit)     │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │ │
│  └─────────┼──────────────────┼──────────────────┼───────────┘ │
│            │                  │                  │              │
│  ┌─────────▼──────────────────▼──────────────────▼───────────┐ │
│  │              APPLICATION LAYER                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  Scanner     │  │   AI Triage  │  │   Fix        │    │ │
│  │  │ Orchestrator │  │   Engine     │  │  Generator   │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │ │
│  └─────────┼──────────────────┼──────────────────┼───────────┘ │
│            │                  │                  │              │
│  ┌─────────▼──────────────────▼──────────────────▼───────────┐ │
│  │              INTEGRATION LAYER                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  Semgrep     │  │   Trivy      │  │   CodeQL     │    │ │
│  │  │  Adapter     │  │   Adapter    │  │   Adapter    │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  Playwright  │  │   Snyk       │  │   AFL++      │    │ │
│  │  │  DAST        │  │   Adapter    │  │   Fuzzer     │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              DATA LAYER                                   │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │  Unified Finding Format (SARIF-inspired JSON)    │    │  │
│  │  │  docs/security/{feature}-scan-results.json       │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

1. **Adapter Pattern** (Integration Layer) - Normalize scanner outputs to unified finding format
2. **Strategy Pattern** (Triage Engine) - Pluggable classification strategies (rule-based, AI, hybrid)
3. **Chain of Responsibility** (Fix Generator) - Try multiple fix strategies until success
4. **Facade Pattern** (Scanner Orchestrator) - Simple interface hiding scanner complexity
5. **Observer Pattern** (Event Emission) - Emit events for hooks integration

---

## Engine Room View: Component Architecture

### 1. Scanner Orchestrator

**Responsibility:** Coordinate execution of multiple security scanners, aggregate results

**Interface:**
```python
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

@dataclass
class ScanConfig:
    target: Path
    scanners: List[str]  # ["semgrep", "trivy", "codeql"]
    fail_on: List[str]   # ["critical", "high"]
    custom_rules: List[Path] = None
    exclude_patterns: List[str] = None

@dataclass
class ScanResult:
    findings: List[Finding]
    metadata: Dict[str, Any]
    scan_duration_seconds: float
    scanners_executed: List[str]

class ScannerOrchestrator:
    """Orchestrate multiple security scanners with parallel execution."""

    def __init__(self):
        self.adapters = {
            "semgrep": SemgrepAdapter(),
            "trivy": TrivyAdapter(),
            "codeql": CodeQLAdapter(),
            "playwright": PlaywrightDastAdapter(),
            "snyk": SnykAdapter(),
        }

    def scan(self, config: ScanConfig) -> ScanResult:
        """Execute scanners in parallel, aggregate findings."""
        with ThreadPoolExecutor(max_workers=len(config.scanners)) as executor:
            futures = {
                executor.submit(self.adapters[scanner].scan, config): scanner
                for scanner in config.scanners
                if scanner in self.adapters
            }

            all_findings = []
            for future in as_completed(futures):
                scanner = futures[future]
                try:
                    findings = future.result(timeout=300)  # 5 min timeout
                    all_findings.extend(findings)
                except Exception as e:
                    logger.error(f"Scanner {scanner} failed: {e}")

        return ScanResult(
            findings=self._deduplicate(all_findings),
            metadata=self._generate_metadata(),
            scan_duration_seconds=time.time() - start_time,
            scanners_executed=config.scanners,
        )
```

**Design Decisions:**
- **Parallel Execution:** Scanners run concurrently to minimize total scan time
- **Adapter Registry:** Pluggable scanner adapters enable adding new tools without core changes
- **Deduplication:** Cross-scanner finding deduplication by file/line/CWE
- **Fault Tolerance:** Scanner failures don't abort entire scan

### 2. AI Triage Engine

**Responsibility:** Classify findings as TP/FP/NI, prioritize remediation, generate explanations

**Interface:**
```python
from enum import Enum
from dataclasses import dataclass

class Classification(Enum):
    TRUE_POSITIVE = "true_positive"
    FALSE_POSITIVE = "false_positive"
    NEEDS_INVESTIGATION = "needs_investigation"

@dataclass
class TriageResult:
    finding_id: str
    classification: Classification
    confidence_score: float  # 0.0-1.0
    risk_score: int  # 1-100
    explanation: str
    recommended_action: str

class TriageEngine:
    """AI-powered vulnerability triage with rule-based fallback."""

    def __init__(self, ai_provider: str = "claude"):
        self.ai_client = self._init_ai_client(ai_provider)
        self.rule_engine = RuleBasedTriageEngine()

    def triage(self, findings: List[Finding]) -> List[TriageResult]:
        """Classify findings with AI, fallback to rules if AI unavailable."""
        results = []

        for finding in findings:
            try:
                # AI classification
                result = self._ai_classify(finding)
            except Exception as e:
                logger.warning(f"AI triage failed for {finding.id}: {e}")
                # Fallback to rule-based
                result = self.rule_engine.classify(finding)

            results.append(result)

        return results

    def _ai_classify(self, finding: Finding) -> TriageResult:
        """Use AI to classify finding with structured prompt."""
        prompt = self._build_triage_prompt(finding)

        response = self.ai_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse structured response
        classification_data = self._parse_ai_response(response.content)

        return TriageResult(
            finding_id=finding.id,
            classification=Classification(classification_data["classification"]),
            confidence_score=classification_data["confidence"],
            risk_score=self._calculate_risk_score(finding, classification_data),
            explanation=classification_data["explanation"],
            recommended_action=classification_data["recommended_action"],
        )

    def _calculate_risk_score(self, finding: Finding, ai_data: Dict) -> int:
        """Risk score: (impact × exploitability) / detection_time"""
        impact = ai_data.get("impact", 5)  # 1-10
        exploitability = ai_data.get("exploitability", 5)  # 1-10
        detection_time_days = (datetime.now() - finding.created_at).days

        # Exponential decay for old findings
        decay_factor = 1 / (1 + 0.1 * detection_time_days)

        risk = int((impact * exploitability * decay_factor))
        return min(risk, 100)
```

**Design Decisions:**
- **Hybrid Strategy:** AI primary, rule-based fallback for reliability
- **Structured Prompts:** Few-shot learning with examples of TP/FP/NI classifications
- **Risk Scoring Formula:** Combines impact, exploitability, and time decay
- **Confidence Scores:** Enables human review of low-confidence classifications

### 3. Fix Generator

**Responsibility:** Generate code patches for vulnerabilities, apply fixes with user confirmation

**Interface:**
```python
@dataclass
class Fix:
    finding_id: str
    patch_file: Path
    explanation: str
    confidence: float
    test_recommendation: str

class FixGenerator:
    """Generate automated fixes for security vulnerabilities."""

    def __init__(self):
        self.fix_strategies = [
            InputValidationStrategy(),
            OutputEncodingStrategy(),
            AuthenticationFixStrategy(),
            CryptographyUpgradeStrategy(),
        ]

    def generate_fix(self, finding: Finding) -> Optional[Fix]:
        """Try fix strategies in order until one succeeds."""
        for strategy in self.fix_strategies:
            if strategy.can_fix(finding):
                try:
                    fix = strategy.generate_fix(finding)
                    if self._validate_fix(fix, finding):
                        return fix
                except Exception as e:
                    logger.warning(f"Strategy {strategy} failed: {e}")

        return None

    def apply_fix(self, fix: Fix, dry_run: bool = False) -> bool:
        """Apply patch file to codebase."""
        if dry_run:
            logger.info(f"[DRY RUN] Would apply patch: {fix.patch_file}")
            return True

        # Use git apply for atomic patching
        result = subprocess.run(
            ["git", "apply", str(fix.patch_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info(f"Applied fix for {fix.finding_id}")
            return True
        else:
            logger.error(f"Failed to apply patch: {result.stderr}")
            return False
```

**Design Decisions:**
- **Chain of Responsibility:** Try multiple fix strategies until success
- **Validation:** Ensure patch compiles and doesn't break tests
- **Atomic Patching:** Use git apply for safe, reversible changes
- **Dry-run Mode:** Preview fixes before applying

### 4. Unified Finding Format

**Responsibility:** Normalize scanner outputs to common schema for downstream processing

**Schema (SARIF-inspired JSON):**
```json
{
  "version": "1.0",
  "findings": [
    {
      "id": "SEMGREP-CWE-89-001",
      "scanner": "semgrep",
      "rule_id": "python.lang.security.sql-injection",
      "cwe": "CWE-89",
      "severity": "critical",
      "title": "SQL Injection in user authentication",
      "description": "User input directly concatenated into SQL query without sanitization",
      "location": {
        "file": "src/auth/login.py",
        "start_line": 45,
        "end_line": 47,
        "snippet": "query = f\"SELECT * FROM users WHERE email = '{email}'\""
      },
      "metadata": {
        "confidence": "high",
        "owasp_category": "A03:2021-Injection",
        "references": [
          "https://owasp.org/www-community/attacks/SQL_Injection"
        ]
      }
    }
  ],
  "metadata": {
    "scan_timestamp": "2025-12-04T10:30:00Z",
    "scanners_used": ["semgrep", "trivy"],
    "project_root": "/home/user/project",
    "scan_duration_seconds": 42.5
  }
}
```

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 9/10

**Strengths:**
- Clear separation of concerns (orchestration, triage, remediation)
- Well-defined interfaces between components
- Unified finding format provides common vocabulary

**Improvement:**
- Document scanner adapter contract (ADR-012)

### 2. Consistency - 10/10

**Strengths:**
- All scanners use adapter pattern
- Unified finding format across all scanners
- Consistent CLI interface (`/jpspec:security scan|triage|fix`)

### 3. Composability - 10/10

**Strengths:**
- MCP server enables external tool integration
- Event emission enables hook automation
- Modular scanner adapters (add new scanners without core changes)

### 4. Consumption (Developer Experience) - 9/10

**Strengths:**
- Single command for full security workflow: `/jpspec:security`
- AI-generated explanations in plain English
- Interactive triage mode for learning

**Needs Work:**
- Performance optimization for large codebases (>100k LOC)

### 5. Correctness (Validation) - 8/10

**Strengths:**
- JSON Schema validation for finding format
- Triage accuracy benchmark (>85% target)
- Fix validation (compile check + test run)

**Needs Work:**
- Formal security review of fix generator logic

### 6. Completeness - 8/10

**Covers:**
- SAST (Semgrep, CodeQL, Snyk)
- DAST (Playwright web security tests)
- Container security (Trivy)
- Fuzzing (AFL++ optional)

**Missing (Future):**
- Infrastructure-as-Code scanning (Checkov, Terrascan)
- Secrets detection (Trufflehog)
- License compliance (FOSSA)

### 7. Changeability - 10/10

**Strengths:**
- Adapter pattern enables adding scanners
- Strategy pattern enables new triage algorithms
- Plugin architecture for custom security rules

---

## Alternatives Considered and Rejected

### Option A: Single Monolithic Scanner

**Approach:** Build custom scanner with all security checks in one tool.

**Rejected Because:**
- **Reinventing Wheel:** Semgrep, CodeQL, Trivy are mature, well-maintained
- **Coverage Gap:** No single tool covers SAST + DAST + container + fuzzing
- **Maintenance Burden:** Security rules require constant updates for new CVEs

### Option B: No AI Triage (Rule-Based Only)

**Approach:** Use simple rule-based heuristics for triage.

**Rejected Because:**
- **False Positive Problem:** Rules can't understand context (e.g., "this input is already validated")
- **Static Thresholds:** Can't adapt to project-specific patterns
- **No Explanations:** Rules provide no learning opportunity for developers

### Option C: Full Event Sourcing for Security Data

**Approach:** Store all findings in event log with full history.

**Rejected Because:**
- **Complexity:** Event sourcing adds significant architectural complexity
- **Storage:** Security scan history grows unbounded
- **Query Complexity:** Rebuilding current state from events is expensive

**Note:** Current file-based approach sufficient for v1; can migrate to event sourcing in v2 if needed.

---

## Implementation Guidance

### Task Dependency Graph

```
Scanner Orchestrator (task-248, task-249)
    ↓
Unified Finding Format (task-220, ADR-007)
    ↓
AI Triage Engine (task-212, task-280)
    ↓
Fix Generator (task-213)
    ↓
Security CLI Integration (task-216, task-217)
    ↓
MCP Server (task-224, ADR-008)
    ↓
Documentation & Testing (task-218, task-219)
```

### Week-by-Week Implementation Plan

**Week 1-2: Foundation**
- [ ] Implement scanner orchestrator with Semgrep adapter
- [ ] Define unified finding format (JSON Schema)
- [ ] Implement finding deduplication logic
- [ ] Basic CLI: `/jpspec:security scan`

**Week 3-4: AI Triage**
- [ ] Implement AI triage engine with Claude integration
- [ ] Build rule-based fallback
- [ ] Create benchmark dataset (100 labeled findings)
- [ ] Validate triage accuracy >85%

**Week 5-6: Automated Remediation**
- [ ] Implement fix generator with input validation strategy
- [ ] Add output encoding strategy
- [ ] Implement dry-run and interactive modes
- [ ] Test fix generation on 20 common vulnerabilities

**Week 7-8: Integrations**
- [ ] Add Trivy adapter (container scanning)
- [ ] Add CodeQL adapter (dataflow analysis)
- [ ] Implement MCP server (tools + resources)
- [ ] Integrate with backlog.md events

**Week 9-10: Polish & Documentation**
- [ ] Write comprehensive security commands docs
- [ ] Create security expert personas
- [ ] Build security commands test suite
- [ ] Performance optimization for large codebases

---

## Risks and Mitigations

### Risk 1: AI Triage Accuracy Below Target (85%)

**Likelihood:** Medium
**Impact:** High (defeats primary value proposition)

**Mitigation:**
- Start with high-confidence rules as baseline (>70% accuracy)
- Use few-shot learning with hand-labeled examples
- Implement active learning loop (human feedback improves model)
- Provide confidence scores for human review of low-confidence cases

### Risk 2: Scanner Version Skew

**Likelihood:** High
**Impact:** Medium (findings format changes break adapters)

**Mitigation:**
- Pin scanner versions in tool dependency manager (task-249)
- Implement adapter version compatibility matrix
- Add automated tests for adapter parsing on scanner updates

### Risk 3: Performance on Large Codebases

**Likelihood:** Medium
**Impact:** Medium (scan time >10 minutes unacceptable)

**Mitigation:**
- Parallel scanner execution (already designed)
- Incremental scanning (only changed files)
- Caching results for unchanged files
- Scope limiting (scan only high-risk directories)

---

## Success Criteria

**Objective Measures:**

1. **Triage Accuracy** - >85% on benchmark dataset (100 labeled findings)
2. **Scan Performance** - <5 minutes for 50k LOC project (p95)
3. **Fix Success Rate** - >70% of generated patches apply cleanly
4. **False Positive Reduction** - <20% FP rate after triage

**Subjective Measures:**

1. **Developer Satisfaction** - "Security scanning is helpful, not annoying" (NPS >40)
2. **Adoption** - >80% of projects using `/jpspec:security` within 6 months

---

## Decision

**APPROVED for implementation as Layered Security Platform**

**Timing:** Phased rollout over 10 weeks

**Next Steps:**

1. Create detailed implementation tasks for each component
2. Set up security benchmark dataset repository
3. Configure scanner infrastructure (API keys, local installs)

**Review Date:** 2026-Q1 (after v1.0 release)

---

## References

### Related ADRs

- **ADR-005:** Scanner Orchestration Pattern
- **ADR-006:** AI Triage Engine Design
- **ADR-007:** Unified Security Finding Format
- **ADR-008:** Security MCP Server Architecture
- **ADR-009:** CodeQL MCP Integration

### External References

- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [CWE Top 25](https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
