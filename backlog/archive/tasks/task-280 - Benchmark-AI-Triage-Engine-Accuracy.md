---
id: task-280
title: Benchmark AI Triage Engine Accuracy
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 23:21'
updated_date: '2025-12-05 16:35'
labels:
  - security
  - testing
  - ai
  - benchmark
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create benchmark dataset and measure AI triage accuracy against expert manual triage. Target >85% agreement rate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Curate dataset of 100+ security findings with ground truth labels (TP/FP)
- [x] #2 Include diverse vulnerability types (SQL injection, XSS, path traversal, secrets, crypto)
- [x] #3 Implement benchmark script to run triage and compare with ground truth
- [x] #4 Calculate accuracy metrics: overall accuracy, per-classifier accuracy, precision, recall
- [x] #5 Generate benchmark report with detailed breakdown and failure analysis
- [x] #6 Achieve >85% overall accuracy or document reasons for lower performance
- [x] #7 Document benchmark methodology and dataset curation process
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Benchmark AI Triage Engine Accuracy

### Architecture Reference
- ADR-006: AI Triage Engine Design
- Related: task-212 (AI Triage Engine implementation)
- Purpose: Validate AI classification accuracy meets >85% target

### Strategic Context
AI triage accuracy is critical to user trust and adoption. This benchmark validates the triage engine against expert manual triage, identifies failure modes, and provides a feedback loop for improvement.

### Implementation Steps

#### Step 1: Curate Benchmark Dataset (6-8 hours)
**Files:**
- tests/fixtures/benchmark_dataset/ (new)
- tests/fixtures/benchmark_dataset/README.md
- tests/fixtures/benchmark_dataset/ground_truth.json

**Tasks:**
1. Collect diverse security findings
   - **SQL Injection (CWE-89)**: 20+ examples
     - True positives: String concatenation in queries
     - False positives: Parameterized queries flagged incorrectly
     - Edge cases: ORM usage, prepared statements
   - **XSS (CWE-79)**: 20+ examples
     - True positives: Unescaped output
     - False positives: Template engine auto-escaping
     - Edge cases: CSP headers, React auto-escaping
   - **Path Traversal (CWE-22)**: 15+ examples
     - True positives: User-controlled file paths
     - False positives: Validated paths
     - Edge cases: Whitelist validation
   - **Hardcoded Secrets (CWE-798)**: 15+ examples
     - True positives: API keys, passwords in code
     - False positives: Example values, test fixtures
     - Edge cases: Encrypted secrets, environment variables
   - **Weak Crypto (CWE-327)**: 15+ examples
     - True positives: MD5, DES, weak key sizes
     - False positives: Hashing for non-security purposes
     - Edge cases: Legacy compatibility requirements

2. Source findings from:
   - Open source projects with known vulnerabilities
   - OWASP WebGoat test applications
   - Security CTF challenges
   - Real-world findings (anonymized)
   - Synthetic examples (created specifically)

3. Create ground truth labels
   ```json
   {
     "findings": [
       {
         "id": "BENCH-001",
         "cwe_id": "CWE-89",
         "title": "SQL Injection in login query",
         "file": "auth.py",
         "line_start": 42,
         "code_snippet": "query = f\"SELECT * FROM users WHERE username = '{username}'\"",
         "ground_truth": {
           "classification": "TP",
           "reasoning": "Direct string interpolation in SQL query",
           "severity": "critical",
           "expert": "security-expert-1"
         }
       }
     ]
   }
   ```

4. Get expert validation
   - Have 2-3 security experts review each finding
   - Resolve disagreements via consensus
   - Document reasoning for labels
   - Include confidence scores

**Validation:**
- Dataset covers all 5 CWE categories
- Mix of TP/FP/NI (40% TP, 40% FP, 20% NI target)
- Expert agreement >90%

#### Step 2: Implement Benchmark Script (4-5 hours)
**Files:**
- scripts/benchmark_triage.py (new)
- tests/benchmark/test_triage_accuracy.py

**Tasks:**
1. Create benchmark script
   ```python
   def benchmark_triage_engine(
       dataset_path: Path,
       llm_client: LLMClient | None = None
   ) -> BenchmarkResult:
       # Load dataset and ground truth
       # Run triage engine on each finding
       # Compare with ground truth
       # Calculate metrics
       # Return results
   ```

2. Implement metric calculation
   - **Overall Accuracy**: % correct classifications
   - **Per-Classifier Accuracy**: Accuracy for each CWE type
   - **Precision**: TP / (TP + FP)
   - **Recall**: TP / (TP + FN)
   - **F1 Score**: Harmonic mean of precision and recall
   - **Confusion Matrix**: TP/FP/NI breakdown
   - **Confidence Calibration**: Are high-confidence predictions more accurate?

3. Add error analysis
   - Categorize failure modes
     - False positives (AI said TP, was FP)
     - False negatives (AI said FP, was TP)
     - Needs investigation misclassified
   - Identify patterns in failures
   - Track which CWEs are hardest
   - Note confidence scores on failures

4. Generate benchmark report
   ```markdown
   # Triage Engine Benchmark Results
   
   ## Overall Metrics
   - Accuracy: 87.3% (target: >85%) ✓
   - Precision: 0.91
   - Recall: 0.84
   - F1 Score: 0.87
   
   ## Per-Classifier Results
   | CWE Type | Accuracy | Precision | Recall | F1 |
   |----------|----------|-----------|--------|-----|
   | SQL Injection (CWE-89) | 92% | 0.94 | 0.90 | 0.92 |
   | XSS (CWE-79) | 88% | 0.89 | 0.87 | 0.88 |
   | ... | ... | ... | ... | ... |
   
   ## Failure Analysis
   ### False Positives (8 cases)
   1. BENCH-042: ORM query flagged as SQL injection
      - Issue: AI didn't recognize SQLAlchemy parameterization
      - Confidence: 0.72 (medium)
   
   ### False Negatives (5 cases)
   ...
   
   ## Recommendations
   1. Improve ORM detection in SQL injection classifier
   2. Add more context lines for XSS classifier
   3. ...
   ```

**Validation:**
- Script runs on full dataset
- Metrics calculated correctly
- Report is actionable

#### Step 3: Implement Confidence Calibration Analysis (2-3 hours)
**Files:**
- scripts/benchmark_triage.py
- tests/benchmark/confidence_calibration.py

**Tasks:**
1. Analyze confidence vs. accuracy
   - Group predictions by confidence bucket (0-0.5, 0.5-0.7, 0.7-0.9, 0.9-1.0)
   - Calculate accuracy within each bucket
   - Verify high confidence = high accuracy

2. Create calibration plot
   ```
   Confidence vs Accuracy
   
   100% |                    *
        |               *
    90% |          *
        |     *
    80% | *
        +----+----+----+----+----
         0.5  0.6  0.7  0.8  0.9
              Confidence Score
   
   Expected: Points should be near diagonal
   ```

3. Identify miscalibration issues
   - Overconfident: High confidence, low accuracy
   - Underconfident: Low confidence, high accuracy
   - Recommend confidence threshold adjustments

4. Add calibration metrics
   - Expected Calibration Error (ECE)
   - Maximum Calibration Error (MCE)
   - Brier score

**Validation:**
- Calibration analysis identifies issues
- Recommendations are actionable
- Metrics are standard (ECE, MCE)

#### Step 4: Implement Comparative Analysis (2-3 hours)
**Files:**
- scripts/benchmark_triage.py
- tests/benchmark/comparative_analysis.py

**Tasks:**
1. Benchmark with vs. without LLM
   - Run with AI triage
   - Run with heuristic-only triage
   - Compare accuracy
   - Measure improvement

2. Benchmark per-classifier vs. default
   - Test specialized classifiers (SQL, XSS, etc.)
   - Test default classifier only
   - Measure accuracy gain from specialization

3. Benchmark with vs. without personas (future)
   - If personas implemented (task-221)
   - Compare response quality
   - Measure accuracy improvement

4. Generate comparative report
   ```markdown
   ## Comparative Analysis
   
   | Configuration | Accuracy | Improvement |
   |--------------|----------|-------------|
   | Heuristic-only | 68% | baseline |
   | AI + Default classifier | 82% | +14% |
   | AI + Specialized classifiers | 87% | +19% |
   | AI + Specialized + Personas | 89% | +21% |
   ```

**Validation:**
- Comparisons show expected improvements
- Findings guide optimization efforts

#### Step 5: Implement Continuous Benchmarking (3-4 hours)
**Files:**
- .github/workflows/benchmark.yml (new, if using GH Actions)
- scripts/benchmark_triage.py
- docs/guides/benchmarking.md

**Tasks:**
1. Add benchmark to CI/CD
   - Run on every major triage engine change
   - Compare to baseline
   - Fail if accuracy drops below threshold (e.g., <83%)

2. Create regression detection
   - Store historical benchmark results
   - Track accuracy over time
   - Alert if regression detected

3. Add benchmark command
   ```bash
   specify security benchmark-triage \
     --dataset tests/fixtures/benchmark_dataset/ \
     --report benchmark-report.md
   ```

4. Document benchmarking process
   - How to run benchmarks
   - How to interpret results
   - How to add new test cases
   - When to re-benchmark

**Validation:**
- CI integration works
- Regression detection catches drops
- Documentation is clear

#### Step 6: Failure Mode Analysis and Remediation (4-5 hours)
**Files:**
- docs/architecture/triage-failure-modes.md (new)
- src/specify_cli/security/triage/engine.py (improvements)

**Tasks:**
1. Analyze failure patterns
   - What types of findings are hardest?
   - Which classifiers need improvement?
   - Are failures due to:
     - Insufficient context?
     - Ambiguous code patterns?
     - LLM limitations?
     - Prompt issues?

2. Categorize failure modes
   - **Context-Limited**: Need more code lines
   - **Pattern-Ambiguous**: Same pattern, different context
   - **Framework-Specific**: Framework knowledge gap
   - **Prompt-Issue**: Prompt unclear or insufficient

3. Implement targeted improvements
   - Add more context for context-limited failures
   - Add framework detection for framework-specific
   - Refine prompts for prompt-issue failures
   - Document limitations for ambiguous cases

4. Re-benchmark after improvements
   - Measure accuracy gain
   - Verify fixes don't regress other cases
   - Iterate until >85% target met

**Validation:**
- Improvements address failure modes
- Re-benchmark shows gains
- Target accuracy achieved

#### Step 7: Documentation and Reporting (2-3 hours)
**Files:**
- docs/architecture/triage-accuracy-report.md (new)
- docs/guides/improving-triage-accuracy.md (new)

**Tasks:**
1. Document benchmark methodology
   - Dataset curation process
   - Ground truth labeling
   - Metric definitions
   - Expert validation process

2. Create accuracy report
   - Overall results
   - Per-classifier breakdown
   - Failure analysis
   - Recommendations

3. Document improvement process
   - How to identify failure modes
   - How to improve classifiers
   - How to update prompts
   - How to re-benchmark

4. Create public benchmark
   - Share dataset (if not proprietary)
   - Share methodology
   - Invite community validation
   - Track improvements over time

**Validation:**
- Documentation is complete
- Report is professional
- Process is reproducible

### Dependencies
- Triage engine (task-212)
- Benchmark dataset (curated)
- Expert validation (manual)
- Statistical libraries (scikit-learn for metrics)

### Success Criteria
- [ ] Dataset includes 100+ labeled findings across 5 CWE categories
- [ ] Overall accuracy >85% (target met)
- [ ] Per-classifier accuracy documented
- [ ] Failure modes identified and documented
- [ ] Benchmark process is automated and repeatable
- [ ] Report demonstrates accuracy and reliability

### Risks & Mitigations
**Risk:** Accuracy below 85% target
**Mitigation:** Iterate on prompts, add context, use specialized classifiers, implement personas

**Risk:** Dataset not representative of real findings
**Mitigation:** Include real-world examples, diverse sources, expert review

**Risk:** Expert disagreement on ground truth
**Mitigation:** Use consensus voting (2-3 experts), document ambiguous cases

**Risk:** Overfitting to benchmark dataset
**Mitigation:** Hold out test set, validate on new findings, continuous benchmarking

### Design Decisions

**Why 100+ Findings?**
- Statistical significance (95% confidence)
- Diverse coverage across CWEs
- Sufficient for per-classifier analysis

**Why Expert Validation?**
- Ground truth must be reliable
- AI benchmarking AI is circular
- Security expertise required

**Why Continuous Benchmarking?**
- Catch regressions early
- Track improvements over time
- Maintain quality standards

### Estimated Effort
**Total: 23-31 hours (3-4 days)**

**Note:** This task depends on task-212 (Triage Engine) being complete. Should be executed after triage engine is functional.
<!-- SECTION:PLAN:END -->
