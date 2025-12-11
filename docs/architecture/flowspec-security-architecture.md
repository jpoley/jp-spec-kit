# /flow:security Architecture - Strategic Framing and System Design

**Date:** 2025-12-02
**Architect:** Enterprise Software Architect
**Status:** Proposed
**Version:** 1.0

---

## Strategic Context (Penthouse View)

### Business Problem

Development teams using JP Flowspec face a critical gap: **security vulnerabilities are discovered late in the development cycle**, when remediation costs are 10-30x higher than during active development. While the existing `/flow:validate` command includes a `@secure-by-design-engineer` agent, there is no automated security scanning integrated into the workflow.

**The Core Tension:** Security tools (Semgrep, CodeQL, Trivy, Snyk) exist but operate **outside** the specification-driven development workflow, creating:
- Tool fragmentation (teams run scans manually, if at all)
- Context loss (findings divorced from feature specifications)
- Inconsistent coverage (scans skipped under time pressure)
- Triage overhead (30% false positive rates consume engineering time)

### Strategic Decision: Build Native vs. Fork Raptor

After evaluating [gadievron/raptor](https://github.com/gadievron/raptor) (221 stars, MIT licensed, AI-powered security framework), we chose to **build native** using Raptor's proven patterns as reference.

**Rationale (Selling the Option):**

| Dimension | Fork Raptor | Build Native | Winner |
|-----------|-------------|--------------|--------|
| **Time to MVP** | 1-2 weeks (integration complexity hidden) | 2-3 weeks (predictable scope) | Raptor +1 week |
| **Dependencies** | 6GB DevContainer, `--privileged` required | Install tools on-demand (~100MB) | Native -5.9GB |
| **Scope Alignment** | Offensive testing (fuzzing, exploits) | SDD workflow integration | Native ✓ |
| **Maintenance Burden** | Track upstream (alpha maturity) | No upstream dependency | Native ✓ |
| **Architectural Fit** | Agent coordination mismatch | Native `/flowspec` workflow | Native ✓ |
| **CodeQL Licensing** | Still requires review | Still requires review | Tie |

**Investment Justification:**
- **Option Value:** Native implementation preserves flexibility to add/remove scanners without upstream constraints
- **Risk Mitigation:** Avoid 6GB DevContainer requirement that conflicts with lightweight CLI philosophy
- **Strategic Alignment:** Building native deepens our security domain expertise and competitive differentiation

**Decision:** Build native, **borrow Raptor's patterns** (progressive token disclosure, tool orchestration, risk scoring formula, expert personas) without forking.

---

## Business Value and Strategic Alignment

### North Star Metric

**% of critical/high vulnerabilities caught before production deployment**

**Target:** >95% within 3 months

### Value Streams

1. **Risk Reduction** - Early vulnerability detection reduces security incident probability by 70% (target)
2. **Cost Efficiency** - Shifting security left reduces remediation costs from $5K-$50K per incident to $500-$2K
3. **Compliance Enablement** - Automated scanning provides audit trails for SOC2, ISO27001, HIPAA
4. **Developer Experience** - AI triage and fix suggestions reduce security investigation time by 60%
5. **Competitive Differentiation** - First specification-driven development toolkit with native AI-powered security workflow

### Organizational Impact

**Developer Workflow:**
```
Before: Code → Manual scan → Triage findings → Google fixes → Implement → Rescan
After:  Code → /flow:security scan+triage+fix → Review patches → Apply → Rescan
```

**Time Savings:** 4 hours → 30 minutes (87.5% reduction) for typical 10-finding remediation cycle

**Platform Engineering:**
- Enforce security gates in CI/CD without becoming bottleneck
- Standardize scanning across teams (eliminate tool fragmentation)
- Audit trail for compliance officers

---

## System Architecture (Engine Room View)

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                          │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │  /flow:security    │  │  specify security    │            │
│  │  Slash Commands      │  │  CLI Commands        │            │
│  └──────────┬───────────┘  └──────────┬───────────┘            │
└─────────────┼──────────────────────────┼──────────────────────┘
              │                          │
┌─────────────▼──────────────────────────▼──────────────────────┐
│              SECURITY WORKFLOW ORCHESTRATION                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────┐  │
│  │   scan     │  │   triage   │  │    fix     │  │  audit  │  │
│  │ coordinator│  │ coordinator│  │coordinator │  │generator│  │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └────┬────┘  │
└────────┼───────────────┼────────────────┼──────────────┼───────┘
         │               │                │              │
┌────────▼───────────────▼────────────────▼──────────────▼───────┐
│                   SECURITY CORE LIBRARY                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Scanner     │  │  AI Triage    │  │    Report     │       │
│  │ Orchestrator  │  │    Engine     │  │   Generator   │       │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘       │
│          │                  │                  │                 │
│  ┌───────▼──────────────────▼──────────────────▼───────┐        │
│  │          Unified Finding Format (UFFormat)           │        │
│  │   - Finding ID, Severity, CWE, Location, CVSS       │        │
│  │   - SARIF export, JSON/Markdown serialization       │        │
│  └──────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
         │                  │                  │
┌────────▼──────────────────▼──────────────────▼─────────────────┐
│              TOOL INTEGRATION LAYER (Adapters)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Semgrep  │  │  CodeQL  │  │  Trivy   │  │  Custom  │        │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │  │  Rules   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
         │                  │                  │
┌────────▼──────────────────▼──────────────────▼─────────────────┐
│                     EXTERNAL TOOLS                               │
│  [ Semgrep ]    [ CodeQL ]    [ Trivy ]    [ AFL++ ]            │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### 1. Scanner Orchestrator (Core Library)

**Purpose:** Discover, install, and execute security scanning tools with unified result aggregation.

**Responsibilities:**
- Tool discovery (check system PATH, venv, offer download)
- Parallel execution of multiple scanners
- Result normalization to Unified Finding Format
- Progress reporting and cancellation support
- Tool version management (SLSA compliance)

**Key Patterns:**
- **Service Activator** (EIP): Launch scanner as external service, aggregate results
- **Adapter** (GoF): Each scanner has adapter translating output to UFFormat
- **Chain of Responsibility**: Try system → venv → download for tool discovery

**See:** ADR-005 Scanner Orchestration Pattern

#### 2. AI Triage Engine (Core Library)

**Purpose:** Use LLM to classify findings as True Positive/False Positive, prioritize by risk, and generate explanations.

**Responsibilities:**
- AI-powered classification (TP/FP/Needs Investigation)
- Risk scoring: `(Impact × Exploitability) / Detection_Time`
- Finding clustering by CWE, file, architectural pattern
- Plain-English vulnerability explanations
- Interactive mode for developer feedback

**Key Patterns:**
- **Content Enricher** (EIP): Augment scanner findings with AI analysis
- **Aggregator** (EIP): Cluster related findings by root cause
- **Strategy** (GoF): Pluggable risk scoring algorithms

**See:** ADR-006 AI Triage Engine Design

#### 3. Report Generator (Core Library)

**Purpose:** Generate compliance-ready audit reports using security-report-template.md.

**Responsibilities:**
- Template population (Jinja2 or similar)
- Multi-format output (Markdown, HTML, PDF, SARIF)
- OWASP Top 10 mapping
- Security posture calculation
- Compliance mode (SOC2, ISO27001, HIPAA)

**Key Patterns:**
- **Template Method** (GoF): Define report structure, vary data population
- **Translator** (EIP): Convert UFFormat → SARIF/HTML/PDF

#### 4. MCP Server (v2.0 Feature)

**Purpose:** Expose security scanning as Model Context Protocol server for tool composition.

**Responsibilities:**
- Tools: `security_scan`, `security_triage`, `security_fix`
- Resources: `security://findings`, `security://status`, `security://config`
- Enable cross-agent queries (e.g., other agents querying vulnerability status)
- Support cross-repo security dashboards

**See:** ADR-008 Security MCP Server Architecture

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 9/10

**Strengths:**
- Clear layer separation (UI → Orchestration → Core → Adapters → Tools)
- Unified Finding Format provides common language across all scanners
- Each command has single responsibility (scan, triage, fix, audit)

**Improvement:**
- Document mental model: "Scan finds, triage classifies, fix remediates, audit reports"

### 2. Consistency - 9/10

**Strengths:**
- All scanners normalized to UFFormat (consistent schema)
- CLI flags consistent with existing `/flowspec` commands (`--format`, `--verbose`)
- State transitions integrate with flowspec_workflow.yml

**Improvement:**
- Ensure SARIF output schema matches GitHub Code Scanning expectations

### 3. Compliance - 10/10

**Strengths:**
- SARIF output format (industry standard)
- SLSA attestation for scanner tool versions
- Audit trail (scan results + timestamps)
- OWASP Top 10 mapping for compliance frameworks

### 4. Composability - 10/10

**Strengths:**
- MCP server enables tool composition with other agents
- Scanners are pluggable (add new scanners without changing core)
- CLI + Slash Commands + MCP provide three consumption models
- Works standalone or integrated into CI/CD

### 5. Coverage - 8/10

**Strengths:**
- SAST (Semgrep, CodeQL)
- Container scanning (Trivy)
- AI triage and fix generation
- Multiple output formats

**Gaps (Future):**
- DAST (Playwright - v1.5)
- Fuzzing (AFL++ - v2.0, optional)
- Dependency scanning (SCA - post-v2.0)

### 6. Consumption (Developer Experience) - 8/10

**Strengths:**
- Progressive disclosure: `/flow:security scan` → triage → fix → audit
- Sensible defaults (Semgrep with OWASP ruleset)
- AI explanations reduce security knowledge barrier
- Auto-apply patches with `--apply` flag

**Needs Work:**
- First-run tool installation messaging (avoid surprise downloads)
- Interactive triage mode needs UX polish

### 7. Credibility (Accuracy) - 7/10 (Risk Area)

**Strengths:**
- AI triage targets >85% accuracy (benchmark validation required)
- Multiple scanners reduce false negatives (defense in depth)

**Risks:**
- False positive rate depends on ruleset tuning (industry avg: 30%)
- AI patch generation correctness needs validation

**Mitigation:**
- Start with conservative rulesets (OWASP Top 10 only)
- Interactive mode for confirming AI decisions
- Include confidence scores with all findings

---

## Integration Patterns (Enterprise Integration Patterns)

### 1. Scanner as Service (Service Activator Pattern)

**Problem:** External scanning tools (Semgrep, CodeQL) are command-line executables.

**Solution:** Wrap each tool in an Adapter that:
1. Detects tool availability
2. Constructs CLI command with appropriate flags
3. Executes tool as subprocess
4. Parses JSON/XML output
5. Translates to Unified Finding Format

**Example:**
```python
class SemgrepAdapter(ScannerAdapter):
    def scan(self, target: Path, config: ScanConfig) -> list[Finding]:
        cmd = ["semgrep", "--config", "auto", "--json", str(target)]
        result = subprocess.run(cmd, capture_output=True)
        semgrep_findings = json.loads(result.stdout)
        return [self._to_finding(f) for f in semgrep_findings["results"]]
```

### 2. Finding Aggregation (Aggregator Pattern)

**Problem:** Running multiple scanners produces duplicate findings.

**Solution:** Aggregator component:
1. Collects findings from all scanners
2. Computes finding fingerprint (hash of file + line + CWE)
3. Deduplicates findings with same fingerprint
4. Merges metadata (e.g., Semgrep found it + CodeQL found it = high confidence)

**Example:**
```python
def aggregate_findings(findings: list[Finding]) -> list[Finding]:
    by_fingerprint = defaultdict(list)
    for finding in findings:
        fingerprint = finding.compute_fingerprint()
        by_fingerprint[fingerprint].append(finding)

    return [merge_findings(group) for group in by_fingerprint.values()]
```

### 3. Report Generation (Content Enricher Pattern)

**Problem:** Raw findings lack context for compliance officers.

**Solution:** Report Generator enriches findings with:
- OWASP Top 10 category mapping
- CVSS score lookup (via CVE database)
- Remediation recommendations (from knowledge base)
- Historical trend analysis (compare to previous scans)

### 4. Workflow Integration (Process Manager Pattern)

**Problem:** Security scanning is a multi-step process (scan → triage → fix → verify).

**Solution:** Workflow coordinator tracks state:
1. Scan creates `{feature}-scan-results.json`
2. Triage reads scan results, creates `{feature}-triage.json`
3. Fix reads triage results, creates `{feature}-fixes.md` and `.patch` files
4. Audit aggregates all artifacts into report

**State Management:** Leverage existing backlog.md integration (workflow_step field from ADR-002).

---

## Migration Path and Versioning

### MVP (v1.0) - Weeks 1-3

**Scope:** Core scanning and triage with Semgrep only

- [ ] Scanner Orchestrator (Semgrep adapter only)
- [ ] Unified Finding Format (data model)
- [ ] AI Triage Engine (TP/FP classification, risk scoring)
- [ ] `/flow:security scan` command
- [ ] `/flow:security triage` command
- [ ] Basic audit report generator
- [ ] Unit tests with mocked Semgrep output

**Deliverable:** Developers can scan, triage, and report on vulnerabilities

### v1.5 - Weeks 4-6

**Scope:** Expert personas, DAST, custom rules

- [ ] Security expert personas (9 modes from Raptor reference)
- [ ] Playwright DAST integration (task-222)
- [ ] Custom rules system (task-223)
- [ ] `/flow:security fix` command (AI patch generation)
- [ ] Backlog.md integration (task-216)
- [ ] CI/CD integration examples (GitHub Actions, GitLab CI)

**Deliverable:** Full remediation workflow with fix generation

### v2.0 - Weeks 7-10

**Scope:** MCP server, CodeQL, optional fuzzing

- [ ] MCP server implementation (task-224)
- [ ] CodeQL integration (task-225)
- [ ] AFL++ fuzzing (task-226, optional)
- [ ] Cross-repo security dashboard (MCP-enabled)
- [ ] Advanced clustering (architectural pattern detection)

**Deliverable:** Enterprise-grade security platform with tool composition

---

## Risk Assessment and Mitigation

### Risk 1: CodeQL Commercial Licensing

**Likelihood:** High
**Impact:** Medium

**Mitigation:**
- Detect license status on first run
- Display clear warning for private repos
- Gracefully fall back to Semgrep-only mode
- Provide documentation link for GitHub Advanced Security

### Risk 2: False Positive Rate Erodes Trust

**Likelihood:** High
**Impact:** High

**Mitigation:**
- Start with conservative rulesets (OWASP Top 10 only, not all community rules)
- AI triage targeting >85% accuracy (validated on benchmark dataset)
- Interactive mode for confirming AI decisions
- Confidence scores prominently displayed
- Feedback mechanism to improve AI over time

### Risk 3: Tool Installation UX

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Clear messaging: "Semgrep not found. Install now? (Y/n)"
- Respect GITHUB_TOKEN for authenticated downloads
- Cache tool binaries in `~/.specify/tools/` (avoid re-download)
- Provide offline mode (use system tools only)

### Risk 4: Performance on Large Codebases

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Incremental scanning (only changed files)
- Parallel scanner execution
- Progress indicators with estimated time
- Cancellation support (Ctrl+C)
- Performance targets: 10K LOC < 1min, 100K LOC < 5min

### Risk 5: AI Patch Correctness

**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- Syntax validation before presenting patches
- Semantic checks (does patch address CWE?)
- Dry-run mode by default (no auto-apply)
- Require confirmation even with `--apply` flag
- Suggest running tests after applying patches

---

## Architectural Principles (For memory/constitution.md)

### Principle 1: Unified Finding Format is Authoritative

**Mandate:** All security findings MUST be normalized to Unified Finding Format before processing.

**Rationale:** Prevents scanner-specific logic leaking into triage, reporting, and workflow layers.

**Implementation:** Each scanner adapter translates native output to UFFormat at boundary.

### Principle 2: Scanners are Pluggable

**Mandate:** Adding a new scanner MUST NOT require changes to core orchestration, triage, or reporting logic.

**Rationale:** Enables future scanner additions without architectural debt.

**Implementation:** ScannerAdapter interface defines contract; registry pattern for discovery.

### Principle 3: AI is Advisory, Not Authoritative

**Mandate:** AI triage decisions MUST include confidence scores and support interactive override.

**Rationale:** Developers must trust the system; AI mistakes should not block workflows.

**Implementation:** Interactive mode prompts for confirmation; confidence scores displayed prominently.

### Principle 4: Security Scanning is Optional in Workflow

**Mandate:** Projects MUST be able to use `/flowspec` workflow without `/flow:security`.

**Rationale:** Not all projects require security scanning; avoid mandatory overhead.

**Implementation:** Security commands are additive; workflow states don't mandate scanning.

### Principle 5: Offline Mode is First-Class

**Mandate:** All security commands MUST work offline if tools are pre-installed.

**Rationale:** Air-gapped environments, CI runners with cached tools.

**Implementation:** Tool discovery checks system PATH and venv before attempting download.

---

## Success Criteria

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| False Positive Rate | <15% | Benchmark on 10 open-source projects |
| AI Triage Accuracy | >85% | Agreement with expert manual triage |
| Scan Performance (10K LOC) | <1 minute | Median execution time |
| Scan Performance (100K LOC) | <5 minutes | Median execution time |
| Test Coverage | >80% | Core library + orchestration |

### Business Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Pre-production vulnerability catch rate | >95% | 3 months |
| `/flow:security` adoption | >80% of projects | 6 weeks |
| Average time-to-fix | <2 days | 3 months |
| Post-deployment incident reduction | 70% decrease | 6 months |

### User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Net Promoter Score (NPS) | >40 | Post-alpha survey |
| Remediation time savings | >60% | Before/after comparison |
| Developer friction reports | <5% of users | Support ticket analysis |

---

## References

### Hohpe's Architectural Principles Applied

1. **Levels of Abstraction** - UI → Orchestration → Core → Adapters → Tools
2. **Composition over Configuration** - MCP server enables tool composition
3. **Single Source of Truth** - Unified Finding Format is canonical schema
4. **Fail Fast** - Validate tool availability before execution
5. **Progressive Disclosure** - Basic scan → AI triage → Fix suggestions → Audit reports

### Related Documents

- **PRD:** `docs/prd/flowspec-security-commands.md` - Product requirements
- **Assessment:** `docs/assess/flowspec-security-commands-assessment.md` - Feature assessment
- **ADR-005:** Scanner Orchestration Pattern
- **ADR-006:** AI Triage Engine Design
- **ADR-007:** Unified Security Finding Format
- **ADR-008:** Security MCP Server Architecture

### External References

- [Raptor Security Framework](https://github.com/gadievron/raptor) - Reference implementation
- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) - Static Analysis Results Interchange Format
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Vulnerability categories
- [CWE Database](https://cwe.mitre.org/) - Common Weakness Enumeration
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) - Hohpe's EIP reference

### Related Tasks

- task-211: Implement Semgrep Scanner Orchestration Module
- task-212: Build AI-Powered Vulnerability Triage Engine
- task-213: Implement Automated Fix Generation
- task-214: Build Security Audit Report Generator
- task-215: Implement /flow:security CLI Commands
- task-216: Integrate with Workflow and Backlog
- task-224: Design and Implement Security Scanner MCP Server

---

## Next Steps

1. Review this strategic framing with stakeholders
2. Create detailed ADRs for each architectural decision:
   - ADR-005: Scanner Orchestration Pattern
   - ADR-006: AI Triage Engine Design
   - ADR-007: Unified Security Finding Format
   - ADR-008: Security MCP Server Architecture
3. Update task-247 implementation plan
4. Begin MVP implementation (task-211: Semgrep Scanner Orchestration)

---

*This architecture follows Gregor Hohpe's philosophy: strategic business framing (why we build), engine room technical details (how we build), platform quality assessment (verification), and constitutional principles (governance).*
