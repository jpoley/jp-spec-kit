---
id: task-250
title: Implement Security Scanning Observability
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 02:26'
updated_date: '2025-12-28 20:18'
labels:
  - security
  - scanning
  - on-hold
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add Prometheus metrics, structured logging, and dashboards for /flow:security commands. Track scan performance, findings trends, AI triage accuracy, and pipeline impact.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement Prometheus metrics (scan_duration, findings_total, triage_accuracy, gate_blocks)
- [ ] #2 Add structured logging with scan_id, tool, duration, findings, outcome
- [ ] #3 Create Grafana dashboard template for security posture tracking
- [ ] #4 Implement alert rules (critical_vulnerability_found, scan_performance_degraded, ai_triage_accuracy_low)
- [ ] #5 Add compliance audit logging (90-day retention in docs/security/audit-log.jsonl)
- [ ] #6 Test metrics collection and dashboard rendering
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Security Scanning Observability

### Overview
Add comprehensive observability for /flow:security commands including Prometheus metrics, structured logging, Grafana dashboards, and compliance audit logging.

### Step-by-Step Implementation

#### Step 1: Implement Prometheus Metrics
**File**: `src/specify_cli/security/metrics.py`
**Duration**: 3 hours

1. Add prometheus_client dependency to pyproject.toml
2. Define metrics:
   ```python
   SCAN_DURATION = Histogram(
       'flowspec_security_scan_duration_seconds',
       'Security scan execution time',
       ['tool', 'scan_type', 'outcome'],
       buckets=[1, 5, 10, 30, 60, 120, 300]
   )
   
   FINDINGS_TOTAL = Counter(
       'flowspec_security_findings_total',
       'Total security findings',
       ['severity', 'cwe_id', 'tool']
   )
   
   TRIAGE_ACCURACY = Gauge(
       'flowspec_security_triage_accuracy',
       'AI triage accuracy vs expert review',
       ['model']
   )
   
   GATE_BLOCKS = Counter(
       'flowspec_security_gate_blocks_total',
       'Pipeline blocks by severity',
       ['severity', 'gate_type']
   )
   ```
3. Add context managers for timing:
   ```python
   with SCAN_DURATION.labels(tool='semgrep', scan_type='incremental', outcome='success').time():
       results = run_scan()
   ```
4. Add metrics export endpoint (optional):
   - HTTP server on port 9090
   - Pushgateway integration

#### Step 2: Implement Structured Logging
**File**: `src/specify_cli/security/logging.py`
**Duration**: 2 hours

1. Add structlog dependency
2. Configure structured logger:
   ```python
   import structlog
   
   logger = structlog.get_logger()
   ```
3. Add log events:
   - `security_scan_started`
   - `security_scan_completed`
   - `security_triage_started`
   - `security_triage_completed`
   - `security_fix_applied`
   - `security_gate_blocked`
4. Include context in all logs:
   - scan_id (UUID)
   - feature name
   - tool name
   - duration_seconds
   - findings counts by severity
   - baseline_commit (for incremental)
5. Configure output formats:
   - Console: colorized for local dev
   - JSON: for CI/CD and production

#### Step 3: Create Grafana Dashboard Template
**File**: `templates/observability/grafana-security-dashboard.json`
**Duration**: 3 hours

1. **Panel 1: Security Posture Over Time**
   - Line chart of findings by severity
   - 7-day moving average
   - PromQL: `avg_over_time(flowspec_security_findings_total[7d])`

2. **Panel 2: Scan Performance**
   - Histogram of scan duration P50/P95/P99
   - By tool and scan type
   - PromQL: `histogram_quantile(0.95, sum(rate(flowspec_security_scan_duration_seconds_bucket[5m])) by (le, tool))`

3. **Panel 3: AI Triage Effectiveness**
   - Gauge of triage accuracy
   - Target line at 80%
   - PromQL: `flowspec_security_triage_accuracy`

4. **Panel 4: Fix Application Rate**
   - Bar chart of findings fixed within 48 hours
   - By severity
   - PromQL: `(flowspec_security_fix_application_rate / flowspec_security_findings_total) * 100`

5. **Panel 5: Pipeline Impact**
   - Counter of gate blocks
   - By severity and gate type (pre-commit, PR, main)

6. Add dashboard variables:
   - Time range selector
   - Repository filter
   - Severity filter

#### Step 4: Implement Alert Rules
**File**: `templates/observability/prometheus-alerts.yml`
**Duration**: 2 hours

1. **CriticalVulnerabilityFound**
   - Trigger: critical findings > 0
   - For: 5 minutes
   - Severity: critical

2. **SecurityScanPerformanceDegraded**
   - Trigger: P95 scan duration > 300 seconds
   - For: 15 minutes
   - Severity: warning

3. **AITriageAccuracyLow**
   - Trigger: triage accuracy < 0.8
   - For: 1 hour
   - Severity: warning

4. **HighVulnerabilityBacklog**
   - Trigger: high severity findings > 10
   - For: 24 hours
   - Severity: warning

5. Add notification templates:
   - Slack webhook format
   - Email format
   - PagerDuty format

#### Step 5: Implement Compliance Audit Logging
**File**: `src/specify_cli/security/audit.py`
**Duration**: 2 hours

1. Create audit log writer:
   ```python
   def write_audit_log(event_type, details):
       entry = {
           "event_type": event_type,
           "timestamp": datetime.utcnow().isoformat(),
           "actor": get_actor(),
           "resource": get_resource_context(),
           "scan_details": details,
           "compliance": {
               "owasp_top_10_coverage": True,
               "cwe_top_25_coverage": True
           }
       }
       # Append to JSONL file
       with open("docs/security/audit-log.jsonl", "a") as f:
           f.write(json.dumps(entry) + "\n")
   ```

2. Add audit events:
   - security_scan_completed
   - security_triage_performed
   - security_fix_applied
   - security_gate_bypassed
   - security_policy_updated

3. Implement log rotation:
   - Keep 90 days in local file
   - Archive to S3/GCS after 90 days (optional)

4. Add audit log viewer:
   ```bash
   specify security audit-log --since 2025-12-01 --format table
   ```

#### Step 6: Testing and Validation
**Duration**: 2 hours

1. **Metrics Test**:
   - Run scan and verify metrics increment
   - Check Prometheus scrape endpoint
   - Verify label values are correct

2. **Logging Test**:
   - Run full workflow (scan → triage → fix)
   - Verify all events logged
   - Check JSON format validity

3. **Dashboard Test**:
   - Import dashboard to test Grafana instance
   - Verify all panels render
   - Test dashboard variables

4. **Alert Test**:
   - Trigger each alert condition
   - Verify alert fires
   - Check notification delivery

5. **Audit Log Test**:
   - Generate audit events
   - Verify JSONL format
   - Test audit log viewer

### Dependencies
- task-248: CI/CD pipeline (for testing in CI)
- Prometheus metrics implementation in core CLI (if not already present)

### Testing Checklist
- [ ] All metrics increment correctly
- [ ] Structured logs output valid JSON
- [ ] Grafana dashboard imports without errors
- [ ] All panels display data
- [ ] Alert rules trigger correctly
- [ ] Audit log is valid JSONL
- [ ] Audit log viewer works

### Estimated Effort
**Total**: 14 hours (1.75 days)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**ON HOLD (Dec 2025)**: Security scanning features may move to dedicated security repo.
<!-- SECTION:NOTES:END -->
