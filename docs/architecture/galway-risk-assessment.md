# Galway Tasks: Risk Assessment and Mitigation Strategy

**Author:** Enterprise Software Architect (Hohpe Principles Expert)
**Date:** 2025-12-04
**Status:** Proposed
**Scope:** Risk analysis for 59 tasks across 9 domains

---

## Executive Summary

This risk assessment analyzes **technical, organizational, and integration risks** for implementing 59 tasks across 9 domains. The analysis identifies **3 critical risks**, **8 high risks**, and **12 medium risks** requiring active mitigation.

**Key Findings:**
- **Highest Risk:** AI triage accuracy falling below 85% threshold
- **Highest Impact:** Scanner version skew breaking adapters
- **Most Mitigatable:** Command migration breakage (symlinks provide safety net)

**Overall Risk Profile:** **Medium** (manageable with proactive mitigation)

---

## Risk Categories

### 1. Technical Risks
Risks related to implementation complexity, dependencies, performance

### 2. Integration Risks
Risks related to cross-system integration, API changes, third-party dependencies

### 3. Organizational Risks
Risks related to adoption, change management, resource availability

### 4. Dependency Risks
Risks related to external tools, libraries, upstream contributions

---

## Critical Risks (Likelihood × Impact ≥ 15)

### Risk 1: AI Triage Accuracy Below Target (85%)

**Category:** Technical
**Likelihood:** 6/10 (Medium-High)
**Impact:** 9/10 (Critical)
**Risk Score:** 54/100 (Critical)

**Description:**
AI-powered triage engine fails to achieve >85% accuracy on benchmark dataset, undermining core value proposition of security domain.

**Impact Analysis:**
- **Business:** Security domain loses differentiation vs. rule-based tools
- **Technical:** Must fall back to manual triage (defeats automation goal)
- **Timeline:** 2-3 week delay while improving AI prompts
- **Cost:** Potential pivot to rule-based approach

**Mitigation Strategy:**

1. **Early Validation (Week 3)**
   - Build benchmark dataset of 100 hand-labeled findings (TP/FP/NI)
   - Test AI triage on dataset before building rest of system
   - **Go/No-Go Decision:** If accuracy <75%, pivot to enhanced rule-based approach

2. **Few-Shot Learning**
   - Include 10 examples of TP/FP/NI in AI prompts
   - Use project-specific examples from codebase context

3. **Hybrid Approach**
   - AI for ambiguous cases, rules for obvious patterns
   - Fallback to rule-based triage if AI unavailable/slow

4. **Active Learning Loop**
   - Collect human feedback on low-confidence classifications
   - Retrain/improve prompts based on corrections

5. **Confidence Thresholds**
   - Require human review for confidence <70%
   - Auto-classify only high-confidence findings

**Success Criteria:**
- Accuracy >85% on benchmark by Week 6
- Confidence scores correlate with accuracy (>0.8 Pearson correlation)

**Contingency Plan:**
- If accuracy remains <80% after 2 iterations, pivot to rule-based triage with manual review queue

---

### Risk 2: Scanner Version Skew Breaking Adapters

**Category:** Dependency
**Likelihood:** 7/10 (High)
**Impact:** 7/10 (High)
**Risk Score:** 49/100 (Critical)

**Description:**
Security scanners (Semgrep, Trivy, CodeQL) update output formats, breaking adapter parsing logic.

**Impact Analysis:**
- **Business:** Security scanning fails silently, missing vulnerabilities
- **Technical:** Adapter tests fail, zero findings returned
- **Timeline:** 1-2 days to update adapters per scanner
- **Cost:** Ongoing maintenance burden

**Mitigation Strategy:**

1. **Version Pinning (Day 1)**
   - Pin scanner versions in `tool-dependency-manager` (task-249)
   - Document tested versions in `docs/reference/scanner-versions.md`
   ```yaml
   # .specify/tool-dependencies.yml
   scanners:
     semgrep:
       version: "1.45.0"
       tested_output_format: "json-v1"
     trivy:
       version: "0.48.0"
       tested_output_format: "json"
   ```

2. **Adapter Compatibility Matrix**
   ```
   | Scanner | Version Range | Adapter Version | Status |
   |---------|---------------|-----------------|--------|
   | Semgrep | 1.40-1.50     | v1.0           | ✅      |
   | Trivy   | 0.45-0.50     | v1.0           | ✅      |
   | CodeQL  | 2.15-2.18     | v1.0           | ⚠️      |
   ```

3. **Automated Adapter Tests**
   - Integration tests for each adapter with real scanner output
   - CI fails if scanner output doesn't parse correctly
   ```python
   def test_semgrep_adapter_parses_real_output():
       # Run semgrep on known vulnerable code
       output = subprocess.run(["semgrep", "--json", "test-files/"])
       findings = SemgrepAdapter().parse(output)
       assert len(findings) > 0
   ```

4. **Output Format Versioning**
   - Adapters check scanner output format version
   - Emit warning if unknown format detected
   ```python
   def parse(self, scanner_output: dict) -> List[Finding]:
       format_version = scanner_output.get("version", "unknown")
       if format_version not in SUPPORTED_VERSIONS:
           logger.warning(f"Unsupported Semgrep version: {format_version}")
   ```

5. **Scanner Update Workflow**
   - Monthly CI job tests latest scanner versions
   - Create GitHub issue if adapter breaks
   - Update adapter + compatibility matrix before scanner upgrade

**Success Criteria:**
- Zero silent failures (adapter errors always logged)
- Adapter updates complete within 48 hours of scanner release

**Contingency Plan:**
- Rollback to last known-good scanner version if adapter cannot be fixed quickly

---

## High Risks (Likelihood × Impact ≥ 9)

### Risk 3: Event Duplication from Multiple Layers

**Category:** Integration
**Likelihood:** 8/10 (High)
**Impact:** 4/10 (Medium)
**Risk Score:** 32/100 (High)

**Description:**
Git hook (Layer 1) and CLI wrapper (Layer 2) both emit events for same backlog operation, causing duplicate hook executions.

**Impact:**
- Slack notifications sent twice
- CI jobs triggered redundantly
- Event log contains duplicates

**Mitigation:**
1. **Event Deduplication by ID**
   ```python
   seen_events = set()
   if event.event_id in seen_events:
       return  # Skip duplicate
   seen_events.add(event.event_id)
   ```

2. **Layer Precedence**
   - If CLI wrapper available, disable git hook event emission
   - Environment variable: `JPSPEC_EVENT_LAYER=cli-wrapper`

3. **Idempotent Hooks**
   - Design all hooks to be safely re-executable
   - Use lock files to prevent concurrent execution

**Success Criteria:**
- No duplicate notifications in production testing

---

### Risk 4: Git Hook Installation Failures

**Category:** Organizational
**Likelihood:** 7/10 (High)
**Impact:** 6/10 (Medium)
**Risk Score:** 42/100 (High)

**Description:**
Users clone repository but git hook doesn't install automatically, breaking event emission.

**Impact:**
- No events emitted for backlog operations
- Workflow automation doesn't trigger
- Silent failure (users don't notice)

**Mitigation:**
1. **Auto-Install on `specify init`**
   ```bash
   # src/specify_cli/init.py
   def install_git_hooks():
       hook_source = Path(__file__).parent / "hooks" / "post-commit"
       hook_dest = Path.cwd() / ".git" / "hooks" / "post-commit"
       shutil.copy(hook_source, hook_dest)
       os.chmod(hook_dest, 0o755)
   ```

2. **Health Check Command**
   ```bash
   specify doctor
   # Checks:
   # ✓ Git hooks installed
   # ✓ Hook runner executable
   # ✓ Event emission working
   ```

3. **CI Validation**
   ```yaml
   # .github/workflows/check-hooks.yml
   - name: Verify git hooks installed
     run: |
       if [ ! -f .git/hooks/post-commit ]; then
         echo "ERROR: Git hook missing"
         exit 1
       fi
   ```

4. **Documentation**
   - Clear instructions in `docs/guides/event-setup.md`
   - Troubleshooting guide for common issues

**Success Criteria:**
- >95% of users have hooks installed (telemetry)

---

### Risk 5: Command Migration User Confusion

**Category:** Organizational
**Likelihood:** 6/10 (Medium)
**Impact:** 5/10 (Medium)
**Risk Score:** 30/100 (High)

**Description:**
Users confused by command migration, can't find commands in new locations.

**Impact:**
- Support burden increases
- User satisfaction decreases
- Adoption of new features slows

**Mitigation:**
1. **Backward-Compatible Symlinks (3 months)**
   - Old paths work identically via symlinks
   - Zero breaking changes

2. **Migration Guide**
   - Step-by-step guide in `docs/guides/command-migration.md`
   - Animated GIFs showing new command locations

3. **Deprecation Warnings**
   ```markdown
   <!-- In legacy command files -->
   ⚠️ DEPRECATED: This command has moved to .claude/commands/jpspec/assess.md
   Update your bookmarks by 2026-03-01.
   ```

4. **Migration Script**
   - Automated script updates user's bookmarks/scripts
   - Dry-run mode for safety

5. **Communication Plan**
   - Blog post announcing migration
   - GitHub Discussions thread for questions
   - Changelog entry with prominent notice

**Success Criteria:**
- Support tickets <5 during migration period
- NPS remains stable (±5 points)

---

### Risk 6: Upstream Backlog.md Contribution Rejected

**Category:** Dependency
**Likelihood:** 5/10 (Medium)
**Impact:** 4/10 (Medium)
**Risk Score:** 20/100 (Medium)

**Description:**
Backlog.md maintainers reject event hooks PR, forcing reliance on CLI wrapper.

**Impact:**
- Layer 3 (native events) unavailable
- Slightly higher latency (wrapper overhead)
- Users must use `jpspec-backlog` wrapper instead of `backlog` CLI

**Mitigation:**
1. **Layers 1 & 2 Work Independently**
   - Git hook and CLI wrapper provide full functionality
   - Layer 3 is optimization, not requirement

2. **Propose Optional Feature**
   - Make event hooks opt-in via `--emit-events` flag
   - Offer to maintain event emission code

3. **Community Engagement**
   - Open GitHub issue before PR to gauge interest
   - Provide compelling use cases (CI/CD, notifications)
   - Offer to write documentation

4. **Fallback Strategy**
   - Maintain CLI wrapper as primary solution
   - Document wrapper usage in JP Spec Kit docs

**Success Criteria:**
- Upstream contribution accepted OR
- CLI wrapper provides equivalent functionality with <100ms overhead

---

### Risk 7: Security Scanner Performance on Large Codebases

**Category:** Technical
**Likelihood:** 6/10 (Medium)
**Impact:** 6/10 (Medium)
**Risk Score:** 36/100 (High)

**Description:**
Security scans take >10 minutes on large codebases (>100k LOC), blocking workflow.

**Impact:**
- Developers skip security scans (too slow)
- Workflow velocity decreases
- CI pipelines time out

**Mitigation:**
1. **Parallel Scanner Execution (Already Designed)**
   - Run Semgrep, Trivy, CodeQL concurrently
   - Reduces total time by ~60%

2. **Incremental Scanning**
   ```python
   # Only scan changed files
   changed_files = git diff --name-only HEAD~1
   semgrep --config=auto $changed_files
   ```

3. **Scope Limiting**
   ```yaml
   # .specify/security-config.yml
   scan_scope:
     include:
       - src/
       - lib/
     exclude:
       - vendor/
       - node_modules/
       - test/fixtures/
   ```

4. **Result Caching**
   - Cache scan results for unchanged files
   - Invalidate cache on file modification

5. **Performance Benchmarks**
   - Test on 50k, 100k, 200k LOC projects
   - Establish performance targets (5 min p95)
   - Optimize if targets not met

**Success Criteria:**
- Scan time <5 min (p95) for 50k LOC
- Scan time <10 min (p95) for 100k LOC

---

### Risk 8: Claude API Rate Limiting

**Category:** Dependency
**Likelihood:** 5/10 (Medium)
**Impact:** 7/10 (High)
**Risk Score:** 35/100 (High)

**Description:**
AI triage engine exceeds Claude API rate limits during bulk scans, causing failures.

**Impact:**
- Triage fails mid-scan
- Users must retry (poor UX)
- Cost increases (retries consume additional quota)

**Mitigation:**
1. **Rate Limit Handling**
   ```python
   @retry(
       wait=wait_exponential(min=1, max=60),
       stop=stop_after_attempt(3),
       retry=retry_if_exception_type(RateLimitError)
   )
   def call_claude_api(prompt):
       response = anthropic.messages.create(...)
       return response
   ```

2. **Batch Processing**
   - Process findings in batches of 10
   - Pause 1 second between batches

3. **Local Caching**
   - Cache AI triage results by finding hash
   - Skip re-triaging identical findings

4. **Fallback to Rules**
   - If rate limit hit, switch to rule-based triage
   - Resume AI triage after cooldown period

5. **Usage Monitoring**
   - Track API usage per project
   - Warn users approaching limits

**Success Criteria:**
- <1% of triage operations fail due to rate limits

---

## Medium Risks (12 additional risks)

| Risk | Category | L×I | Mitigation |
|------|----------|-----|------------|
| Race conditions in rapid task edits | Technical | 24 | File locking, state checksum validation |
| Skills not discoverable by Claude Code | Integration | 20 | Clear naming, comprehensive docs |
| Constitution validation too strict | Organizational | 18 | Configurable strictness levels |
| Archive script deletes wrong tasks | Technical | 18 | Dry-run required, confirmation prompts |
| MCP server startup failures | Technical | 16 | Health check endpoint, auto-restart |
| Fix generator introduces new bugs | Technical | 16 | Validate patches compile, run tests |
| Event schema evolution breaks hooks | Dependency | 15 | Versioning, 2-version support |
| macOS CI matrix failures | Technical | 15 | Skip macOS initially, Linux-first |
| Plugin API not extensible enough | Technical | 12 | Design with extension points |
| Diagram generation tool conflicts | Integration | 12 | Support multiple tools (Mermaid, PlantUML) |
| Case study documentation outdated | Organizational | 10 | Quarterly review process |
| Spec quality metrics ambiguous | Technical | 10 | Clear rubric, examples |

---

## Risk Management Framework

### Risk Monitoring Cadence

| Risk Level | Review Frequency | Owner |
|------------|------------------|-------|
| Critical | Weekly | Software Architect |
| High | Bi-weekly | Tech Lead |
| Medium | Monthly | Engineering Manager |

### Escalation Criteria

**Escalate to stakeholders when:**
- Critical risk materializes (inform immediately)
- High risk shows trend toward materialization (2 weeks notice)
- Multiple medium risks compound (monthly status)

### Risk Dashboard (Proposed)

```
┌─────────────────────────────────────────┐
│  RISK DASHBOARD - Galway Tasks          │
├─────────────────────────────────────────┤
│  Critical Risks:   3 ⚠️                  │
│  High Risks:       8 🟨                  │
│  Medium Risks:     12 🟦                 │
│  Low Risks:        15 🟢                 │
│                                          │
│  Top 3 Risks to Watch:                  │
│  1. AI Triage Accuracy (54 score)       │
│  2. Scanner Version Skew (49 score)     │
│  3. Git Hook Installation (42 score)    │
│                                          │
│  Mitigation Status:                     │
│  ✅ 12 mitigations implemented           │
│  🔄 8 mitigations in progress            │
│  📋 18 mitigations planned               │
└─────────────────────────────────────────┘
```

---

## Risk Acceptance Decisions

### Accepted Risks (No Mitigation Planned)

1. **Learning Curve for New Architecture**
   - **Rationale:** Expected for any significant change
   - **Acceptance:** Provide comprehensive documentation

2. **Plugin API Incompatibility (v1 → v2)**
   - **Rationale:** Early plugin ecosystem, breaking changes acceptable
   - **Acceptance:** Semantic versioning communicates breaking changes

3. **Third-Party Scanner Licensing Changes**
   - **Rationale:** Outside our control, scanners are industry standard
   - **Acceptance:** Monitor licenses, have fallback options

---

## Success Criteria for Risk Management

**Objective Measures:**
- Zero critical risks materialized by end of Phase 1
- <3 high risks materialized during entire implementation
- 100% of critical/high risk mitigations implemented before related tasks

**Subjective Measures:**
- Engineering team feels "risks are well-managed" (survey >80% agree)
- Stakeholders have confidence in risk visibility (NPS >40)

---

## Conclusion

The galway task portfolio represents **medium overall risk** with **well-defined mitigations**. The highest risks (AI triage accuracy, scanner version skew) have clear go/no-go decision points and contingency plans.

**Key Recommendations:**

1. **Prioritize Early Validation:**
   - AI triage benchmark by Week 3
   - Scanner orchestrator performance test by Week 5

2. **Invest in Mitigation Infrastructure:**
   - Version pinning from Day 1
   - Adapter compatibility matrix in CI
   - Health check commands for all integrations

3. **Establish Risk Review Cadence:**
   - Weekly critical risk review during Phase 1-2
   - Bi-weekly for all risks during Phase 3-4

4. **Communicate Proactively:**
   - Share risk dashboard with stakeholders monthly
   - Escalate immediately if critical risk trends negative

**Risk Profile:** **Manageable** with active monitoring and proactive mitigation.

---

## References

- **Risk Framework:** [PMBOK Risk Management](https://www.pmi.org/pmbok-guide-standards)
- **Related ADRs:** ADR-011, ADR-012, ADR-013
- **Architecture Overview:** `docs/architecture/galway-planning-overview.md`

---

*This risk assessment follows Hohpe's principle: "Good architects reduce uncertainty by making risks visible and creating options to manage them."*
