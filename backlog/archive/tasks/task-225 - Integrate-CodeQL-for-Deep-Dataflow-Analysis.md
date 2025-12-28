---
id: task-225
title: Integrate CodeQL for Deep Dataflow Analysis
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 02:16'
updated_date: '2025-12-28 20:18'
labels:
  - security
  - codeql
  - on-hold
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add CodeQL integration for semantic code analysis with dataflow validation. Requires licensing review before implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Complete CodeQL licensing review for commercial use
- [ ] #2 Implement CodeQL CLI download and setup
- [ ] #3 Create CodeQL query configuration
- [ ] #4 Integrate CodeQL results with unified finding format
- [ ] #5 Add --codeql flag to specify security scan
- [ ] #6 Document CodeQL setup requirements
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: CodeQL Integration for Deep Dataflow Analysis

### Architecture Reference
- ADR-005: Scanner Orchestration Pattern
- Existing: src/specify_cli/security/adapters/ (adapter pattern established)
- Pattern: Adapter Pattern (GoF) + Service Activator (EIP)

### Strategic Context
CodeQL provides semantic code analysis with dataflow tracking, catching vulnerabilities that pattern-based tools (Semgrep) miss. However, commercial licensing requires careful review before implementation.

### Implementation Steps

#### Step 1: CodeQL Licensing Review (4-6 hours)
**Files:**
- docs/legal/codeql-licensing-review.md (new)
- docs/architecture/flowspec-security-architecture.md (update)

**Tasks:**
1. Review GitHub CodeQL licensing terms
   - Open source projects: Free
   - Private repositories: Requires GitHub Advanced Security license
   - Commercial use: Restricted without proper license
   - Documentation: https://github.com/github/codeql-cli-binaries

2. Document licensing requirements
   - When CodeQL can be used freely
   - When license is required
   - Cost structure (if applicable)
   - Alternatives if licensing is prohibitive

3. Design graceful degradation strategy
   - Detect if CodeQL is licensed/available
   - Fall back to Semgrep-only if not
   - Clear messaging to users about limitations
   - Documentation on how to obtain license

4. Create decision matrix
   ```
   Scenario              | CodeQL Available? | Action
   ---------------------|-------------------|---------------------------
   Open source repo     | Yes               | Enable CodeQL by default
   Private repo + GH    | Check license     | Use if licensed, skip if not
   Private repo + no GH | No                | Skip, document alternative
   Commercial use       | Requires license  | Skip unless licensed
   ```

**Validation:**
- Legal review (if needed)
- Document clear guidelines
- Test detection logic

**Decision Point:** STOP HERE if licensing terms are prohibitive. Document why CodeQL is not supported and mark task as "Blocked - Licensing". Otherwise, continue.

#### Step 2: CodeQL Adapter Implementation (6-8 hours)
**Files:**
- src/specify_cli/security/adapters/codeql.py (new)
- src/specify_cli/security/adapters/__init__.py (register adapter)

**Tasks:**
1. Implement CodeQLAdapter class
   ```python
   class CodeQLAdapter(ScannerAdapter):
       """Adapter for GitHub CodeQL semantic analysis."""
       
       TOOL_NAME = "codeql"
       SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "go", "java", "cpp"]
       
       def is_available(self) -> bool:
           """Check if CodeQL CLI is installed and licensed."""
           
       def install(self) -> None:
           """Download and install CodeQL CLI."""
           
       def scan(self, config: ScanConfig) -> ScanResult:
           """Execute CodeQL analysis and normalize results."""
   ```

2. Implement tool discovery
   - Check system PATH for `codeql` binary
   - Check ~/.codeql/ directory
   - Check environment variable CODEQL_HOME
   - Offer download if not found (with license warning)

3. Implement CodeQL database creation
   ```bash
   # Create database (required before analysis)
   codeql database create \
     --language=python \
     --source-root=. \
     <database-path>
   ```
   - Auto-detect language from repository
   - Create database in temp directory
   - Handle multi-language projects

4. Implement query execution
   ```bash
   # Run security queries
   codeql database analyze \
     <database-path> \
     --format=sarif-latest \
     --output=results.sarif \
     <query-suite>
   ```
   - Use security query suite (codeql/python-security-queries)
   - Support custom queries
   - Handle timeouts (CodeQL can be slow)

5. Implement SARIF parsing
   - Parse SARIF 2.1.0 output
   - Extract findings with locations
   - Map to Unified Finding Format
   - Preserve CodeQL-specific metadata (dataflow paths)

**Validation:**
- Test on sample Python/JS/Go projects
- Verify findings match CodeQL expectations
- Test error handling

#### Step 3: Dataflow Path Visualization (4-5 hours)
**Files:**
- src/specify_cli/security/models.py (enhance Finding)
- src/specify_cli/security/adapters/codeql.py
- src/specify_cli/security/exporters/markdown.py (enhance)

**Tasks:**
1. Enhance Finding model to support dataflow
   ```python
   @dataclass
   class DataflowPath:
       """Dataflow path from source to sink."""
       source: Location          # Where data originates (user input)
       steps: list[Location]     # Intermediate steps
       sink: Location           # Where vulnerability occurs
       description: str         # Path description
   
   @dataclass 
   class Finding:
       # ... existing fields ...
       dataflow_path: DataflowPath | None = None
   ```

2. Extract dataflow from CodeQL SARIF
   - Parse codeFlows from SARIF
   - Extract threadFlows and locations
   - Build DataflowPath object
   - Include message annotations

3. Visualize dataflow in reports
   ```markdown
   ## Dataflow Analysis
   
   **Source:** user_input (line 42)
   ↓
   **Step 1:** validate_input() (line 45) [sanitization bypassed]
   ↓
   **Step 2:** process_query() (line 67)
   ↓  
   **Sink:** execute_sql() (line 89) [SQL injection]
   ```

4. Add dataflow to triage context
   - Include dataflow in AI prompts
   - Help AI assess if input is properly sanitized
   - Improve classification accuracy

**Validation:**
- Test on vulnerabilities with known dataflow
- Verify paths are accurate
- Check visualization clarity

#### Step 4: Query Suite Configuration (3-4 hours)
**Files:**
- src/specify_cli/security/config/codeql_queries.py (new)
- templates/codeql-security-suite.yml (new)

**Tasks:**
1. Define security query suites
   ```yaml
   # codeql-security-suite.yml
   - qlpack: codeql/python-queries
     queries:
       - security/CWE-089: sql-injection.ql
       - security/CWE-079: xss.ql
       - security/CWE-022: path-traversal.ql
   ```

2. Support query filtering
   - --codeql-queries flag to select specific CWEs
   - Predefined suites: minimal, standard, extended
   - Custom query paths

3. Add query performance optimization
   - Disable expensive queries by default
   - Timeout per query (5 minutes)
   - Parallel query execution (if safe)

4. Document query customization
   - How to add custom queries
   - How to tune query performance
   - Example custom queries

**Validation:**
- Test different query suites
- Measure scan time for each suite
- Verify findings are relevant

#### Step 5: Integration with Scanner Orchestrator (2-3 hours)
**Files:**
- src/specify_cli/security/orchestrator.py
- src/specify_cli/security/adapters/__init__.py

**Tasks:**
1. Register CodeQL adapter
   ```python
   SCANNER_REGISTRY = {
       "semgrep": SemgrepAdapter,
       "codeql": CodeQLAdapter,
       "trivy": TrivyAdapter,
   }
   ```

2. Add --codeql flag to scan command
   ```bash
   specify security scan --tool codeql
   specify security scan --tool semgrep,codeql  # Both
   specify security scan --tool all              # All available
   ```

3. Implement intelligent scheduling
   - CodeQL is slow (minutes to hours)
   - Run in separate batch from fast scanners
   - Show progress for database creation
   - Display ETA for analysis

4. Handle CodeQL-specific errors
   - Database creation failures
   - Out of memory errors
   - Query timeouts
   - License errors

**Validation:**
- Test orchestrator with CodeQL + Semgrep
- Verify scheduling works
- Test error handling

#### Step 6: Performance Optimization (2-3 hours)
**Files:**
- src/specify_cli/security/adapters/codeql.py
- src/specify_cli/security/cache/ (new)

**Tasks:**
1. Implement database caching
   - Cache CodeQL database between scans
   - Invalidate when code changes (git hash)
   - Store in .specify/codeql_cache/
   - Max cache size: 2GB

2. Add incremental analysis
   - Only analyze changed files if possible
   - Fallback to full scan if needed
   - Document limitations

3. Optimize query execution
   - Run expensive queries only when requested
   - Use threading for parallel queries
   - Set memory limits

4. Add performance metrics
   - Database creation time
   - Query execution time
   - Cache hit rate
   - Memory usage

**Validation:**
- Measure scan time with/without cache
- Test on large codebases (100K+ LOC)
- Monitor memory usage

#### Step 7: Documentation and Testing (3-4 hours)
**Files:**
- docs/guides/codeql-setup.md (new)
- docs/reference/codeql-queries.md (new)
- tests/security/test_codeql_adapter.py

**Tasks:**
1. Write setup documentation
   - How to install CodeQL CLI
   - Licensing requirements and how to check
   - Configuration options
   - Troubleshooting common issues

2. Create example configurations
   - Minimal config for quick scans
   - Extended config for thorough analysis
   - Custom query examples

3. Write integration tests
   - Test CodeQL detection
   - Test database creation
   - Test query execution
   - Test SARIF parsing
   - Test dataflow extraction
   - Mock CodeQL for CI tests

4. Add benchmark tests
   - Measure scan time on reference projects
   - Compare accuracy vs. Semgrep
   - Document trade-offs

**Validation:**
- Documentation is clear and complete
- Tests pass
- Setup guide works for new users

### Dependencies
- CodeQL CLI (external tool, ~500MB)
- CodeQL query packs (downloaded automatically)
- SARIF parser (already have for other formats)
- Git (for change detection)

### Success Criteria
- [ ] Licensing review completed and documented
- [ ] CodeQL adapter implements ScannerAdapter interface
- [ ] Dataflow paths extracted and visualized
- [ ] Integration with orchestrator works seamlessly
- [ ] Documentation covers setup and usage
- [ ] Performance is acceptable (<10 min for 100K LOC)

### Risks & Mitigations
**Risk:** Licensing prohibits use in commercial contexts
**Mitigation:** Document clearly, provide Semgrep-only option, mark feature as "open source only"

**Risk:** CodeQL scans are too slow for interactive use
**Mitigation:** Database caching, run in background, show progress, offer "quick scan" mode

**Risk:** CodeQL installation is complex
**Mitigation:** Auto-download, provide Docker option, extensive docs

**Risk:** Findings overlap significantly with Semgrep
**Mitigation:** Deduplicate, highlight CodeQL-unique findings (dataflow)

### Design Decisions

**Why CodeQL Despite Licensing?**
- Best-in-class dataflow analysis
- Catches bugs Semgrep misses
- Worth offering for open source projects
- Many Flowspec users on GitHub Enterprise

**Why Not Make It Default?**
- Licensing restrictions
- Slow performance
- Complex setup
- Semgrep is "good enough" for most

**When to Recommend CodeQL?**
- High-security applications (finance, healthcare)
- Complex dataflow vulnerabilities
- Post-MVP security hardening
- Open source projects (always free)

### Estimated Effort
**Total: 24-33 hours (3-4 days)**

**Note:** Initial 4-6 hours for licensing review is a GO/NO-GO decision point. If licensing is prohibitive, document and stop. Total effort assumes licensing allows implementation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**ON HOLD (Dec 2025)**: Security scanning features may move to dedicated security repo.
<!-- SECTION:NOTES:END -->
