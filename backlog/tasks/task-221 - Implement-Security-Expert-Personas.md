---
id: task-221
title: Implement Security Expert Personas
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 02:15'
updated_date: '2025-12-05 22:06'
labels:
  - security
  - personas
  - v1.5
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create 4 security-focused expert personas borrowed from Raptor patterns: @security-analyst, @patch-engineer, @fuzzing-strategist, @exploit-researcher. Use progressive disclosure to load expertise on-demand.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create @security-analyst persona with OWASP expertise
- [x] #2 Create @patch-engineer persona for fix quality focus
- [x] #3 Create @fuzzing-strategist persona for dynamic testing guidance
- [x] #4 Create @exploit-researcher persona for attack surface analysis
- [x] #5 Implement progressive disclosure pattern for persona loading
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Security Expert Personas

### Architecture Reference
- Inspired by Raptor's security expert personas
- Pattern: Progressive Disclosure + Persona-Based Prompting
- Integration: Claude skills system (.claude/skills/)

### Strategic Context
Expert personas provide specialized security knowledge on-demand, reducing token usage by loading expertise only when needed. Borrowed from Raptor's approach but adapted to JP Spec Kit's architecture.

### Implementation Steps

#### Step 1: Design Persona Architecture (2-3 hours)
**Files:**
- .claude/skills/security-analyst.md (new)
- .claude/skills/patch-engineer.md (new)
- .claude/skills/fuzzing-strategist.md (new)
- .claude/skills/exploit-researcher.md (new)
- src/specify_cli/security/personas/ (new directory structure)

**Tasks:**
1. Define persona structure
   ```markdown
   # @security-analyst Persona
   
   ## Role
   Security analyst with deep OWASP Top 10 expertise
   
   ## Expertise Areas
   - Vulnerability classification
   - Risk assessment
   - CVSS scoring
   - Compliance mapping
   
   ## Communication Style
   - Clear, concise technical explanations
   - Focus on business impact
   - Actionable recommendations
   
   ## Tools & Methods
   - Triage engine integration
   - OWASP mapping
   - Risk scoring formulas
   
   ## Example Interactions
   [Provide 3-4 example Q&A pairs]
   ```

2. Create progressive disclosure mechanism
   - Personas only loaded when invoked
   - Cache loaded personas for session
   - Minimal token overhead when not used

3. Design persona invocation API
   ```python
   from specify_cli.security.personas import invoke_persona
   
   response = invoke_persona(
       persona="security-analyst",
       task="analyze_finding",
       context={"finding": finding, "code": code_snippet}
   )
   ```

**Validation:**
- Test persona loading
- Verify token efficiency
- Measure response quality

#### Step 2: Implement @security-analyst Persona (3-4 hours)
**Files:**
- .claude/skills/security-analyst.md
- src/specify_cli/security/personas/security_analyst.py

**Tasks:**
1. Create persona prompt template
   - OWASP Top 10 expertise
   - CWE database knowledge
   - CVSS v3.1 scoring
   - Risk assessment frameworks
   - Compliance requirements (SOC2, ISO27001, HIPAA)

2. Define use cases
   - Analyze finding severity
   - Assess business impact
   - Map to compliance requirements
   - Explain vulnerability to non-technical stakeholders
   - Provide remediation guidance

3. Implement integration with triage engine
   - Invoke for classification decisions
   - Use for explanation generation
   - Consult for risk scoring

4. Add OWASP-specific knowledge
   ```
   - A01:2021 Broken Access Control → CWE-639, CWE-284, CWE-285
   - A02:2021 Cryptographic Failures → CWE-327, CWE-328, CWE-329
   - A03:2021 Injection → CWE-89, CWE-79, CWE-78, CWE-94
   ...
   ```

**Validation:**
- Test with 10 different findings
- Verify OWASP mapping accuracy
- Check explanation quality

#### Step 3: Implement @patch-engineer Persona (3-4 hours)
**Files:**
- .claude/skills/patch-engineer.md
- src/specify_cli/security/personas/patch_engineer.py

**Tasks:**
1. Create persona prompt template
   - Code quality focus
   - Security fix patterns
   - Language-specific idioms
   - Testing strategies
   - Regression prevention

2. Define use cases
   - Review generated fixes
   - Suggest fix improvements
   - Validate patch correctness
   - Identify potential side effects
   - Recommend testing approach

3. Implement integration with fix generator
   - Review AI-generated patches
   - Score fix quality
   - Suggest improvements
   - Validate semantic correctness

4. Add fix pattern expertise
   - SQL injection fixes (parameterized queries)
   - XSS fixes (output encoding, CSP)
   - Path traversal fixes (path validation)
   - Crypto fixes (modern algorithms)
   - Secrets fixes (secret management)

**Validation:**
- Review 20 generated patches
- Measure improvement in fix quality
- Check for false improvements

#### Step 4: Implement @fuzzing-strategist Persona (2-3 hours)
**Files:**
- .claude/skills/fuzzing-strategist.md
- src/specify_cli/security/personas/fuzzing_strategist.py

**Tasks:**
1. Create persona prompt template
   - Dynamic testing expertise
   - Fuzzing strategy development
   - Input generation techniques
   - Crash analysis
   - Coverage optimization

2. Define use cases
   - Suggest fuzzing targets (v2.0 feature)
   - Design test harnesses
   - Analyze crash reports
   - Recommend fuzzing tools (AFL++, libFuzzer)
   - Guide input corpus generation

3. Design integration points (future)
   - Link to /jpspec:security fuzz command (v2.0)
   - Provide fuzzing configuration templates
   - Analyze fuzzing results

4. Add fuzzing-specific knowledge
   - AFL++ usage and configuration
   - Fuzzing vs. SAST trade-offs
   - When to use fuzzing (parsers, protocols, file formats)
   - Coverage-guided vs. mutation-based

**Validation:**
- Generate fuzzing strategy for 5 targets
- Verify recommendations are sound
- Check alignment with industry best practices

#### Step 5: Implement @exploit-researcher Persona (2-3 hours)
**Files:**
- .claude/skills/exploit-researcher.md
- src/specify_cli/security/personas/exploit_researcher.py

**Tasks:**
1. Create persona prompt template
   - Attack surface analysis
   - Exploit scenario generation
   - Vulnerability chaining
   - Defense evasion techniques
   - Real-world exploit examples

2. Define use cases
   - Generate attack scenarios
   - Assess exploitability
   - Explain attack vectors
   - Identify privilege escalation paths
   - Demonstrate business impact

3. Implement integration with triage
   - Provide exploitability scores
   - Generate "how to exploit" explanations
   - Suggest proof-of-concept approaches
   - Identify attack chains

4. Add attack scenario templates
   - SQL injection → data exfiltration
   - XSS → session hijacking
   - Path traversal → credential theft
   - Crypto weakness → data decryption
   - Secrets exposure → lateral movement

**Validation:**
- Generate attack scenarios for 10 findings
- Verify scenarios are realistic
- Check explanations are clear and educational

#### Step 6: Implement Progressive Disclosure System (3-4 hours)
**Files:**
- src/specify_cli/security/personas/__init__.py
- src/specify_cli/security/personas/loader.py
- src/specify_cli/security/personas/cache.py

**Tasks:**
1. Create persona loader
   - Load persona from .claude/skills/ on demand
   - Parse markdown format
   - Extract role, expertise, examples
   - Cache for session duration

2. Implement token optimization
   - Only load personas when invoked
   - Cache loaded personas in memory
   - Lazy initialization
   - Monitor token usage

3. Add persona routing
   - Analyze task type
   - Select appropriate persona(s)
   - Route to specialist(s)
   - Aggregate responses if multiple

4. Create invocation API
   ```python
   # Single persona
   result = invoke_persona("security-analyst", task, context)
   
   # Multiple personas (consensus)
   results = invoke_personas(
       ["security-analyst", "patch-engineer"],
       task="evaluate_fix",
       context={"finding": finding, "patch": patch}
   )
   ```

**Validation:**
- Test persona loading performance
- Measure token usage (should be minimal when not invoked)
- Test cache hit rate

#### Step 7: Integration and Testing (2-3 hours)
**Files:**
- tests/security/test_personas.py
- tests/security/test_persona_integration.py

**Tasks:**
1. Unit tests for each persona
   - Test loading
   - Test invocation
   - Test response quality
2. Integration tests
   - Triage engine + security-analyst
   - Fix generator + patch-engineer
   - Test progressive disclosure
3. Performance tests
   - Measure token overhead
   - Test cache efficiency
   - Benchmark response time
4. Quality tests
   - Manual review of persona responses
   - Compare with/without personas
   - Measure improvement in accuracy

**Validation:**
- All tests pass
- Token usage is efficient
- Response quality improves with personas

### Dependencies
- Claude API (already used by triage/fix engines)
- Markdown parser (for persona skill files)
- LRU cache (for persona caching)

### Success Criteria
- [ ] 4 personas implemented and accessible
- [ ] Progressive disclosure reduces token usage (only load when needed)
- [ ] Persona responses are high-quality and specialized
- [ ] Integration with triage and fix engines works seamlessly
- [ ] Token overhead is minimal (<10% when not invoked)

### Risks & Mitigations
**Risk:** Personas don't improve response quality
**Mitigation:** Compare with/without in benchmark tests, iterate on prompts

**Risk:** Token costs increase significantly
**Mitigation:** Aggressive caching, lazy loading, use personas sparingly

**Risk:** Personas provide inconsistent responses
**Mitigation:** Standardize persona templates, add quality validation

### Design Decisions

**Why Progressive Disclosure?**
- Raptor loads all personas upfront (5000+ tokens)
- We only load when needed (200-500 tokens per persona)
- 80-90% token savings when personas not used

**Why 4 Personas vs. Raptor's 5?**
- Focus on immediate value: analyst, patch engineer
- Add future value: fuzzing, exploit research
- Skip: Raptor's "compiler-warrior" (out of scope for SDD workflow)

**Why Skills vs. Python Classes?**
- Skills integrate with Claude's natural workflow
- Easier to iterate on prompts (Markdown vs. code)
- No code changes needed to update personas

### Estimated Effort
**Total: 15-21 hours (2-3 days)**
<!-- SECTION:PLAN:END -->
