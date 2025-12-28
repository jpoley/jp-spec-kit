---
id: task-253
title: Track DORA Metrics for Security Scanning
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
Implement DORA metrics collection and reporting for security scanning workflow. Ensure security scans don't degrade DORA Elite performance (deployment frequency, lead time, change failure rate, MTTR).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Track deployment frequency (ensure security scans don't block multiple daily deploys)
- [ ] #2 Track lead time for security fixes (<2 days from scan to remediation)
- [ ] #3 Track change failure rate (security-related production incidents)
- [ ] #4 Track MTTR for critical vulnerabilities (<1 hour target)
- [ ] #5 Create monthly DORA report showing security workflow impact
- [ ] #6 Set up alerts for DORA metric degradation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Track DORA Metrics for Security Scanning

### Overview
Implement DORA metrics collection and reporting to ensure security scanning maintains DORA Elite performance targets without degrading deployment velocity.

### Step-by-Step Implementation

#### Step 1: Define DORA Metric Data Models
**File**: `src/specify_cli/security/dora_metrics.py`
**Duration**: 2 hours

1. Create data models for DORA metrics:
   ```python
   from dataclasses import dataclass
   from datetime import datetime
   from typing import Optional
   
   @dataclass
   class DeploymentEvent:
       timestamp: datetime
       commit_sha: str
       scan_duration_seconds: float
       security_gate_blocked: bool
       severity_counts: dict
   
   @dataclass
   class SecurityIncident:
       timestamp: datetime
       severity: str
       cwe_id: str
       discovered_in: str  # "dev", "staging", "production"
       time_to_fix_hours: float
   
   @dataclass
   class DORAMetrics:
       # Deployment Frequency: deployments per day
       deployment_frequency: float
       avg_deployments_per_day: float
       
       # Lead Time for Changes: commit to deploy
       lead_time_hours: float
       lead_time_p50: float
       lead_time_p95: float
       security_scan_overhead_pct: float  # % of lead time spent on security
       
       # Change Failure Rate: % of deployments causing security incidents
       change_failure_rate: float
       security_related_failures: int
       total_deployments: int
       
       # Mean Time to Recovery: time to fix critical vulnerabilities
       mttr_hours: float
       mttr_critical_vulnerabilities: float
       mttr_high_vulnerabilities: float
   ```

2. Add metric calculation functions
3. Store metrics in `docs/security/dora-metrics.json`

#### Step 2: Implement Deployment Frequency Tracking
**Duration**: 2 hours

1. Track deployments with security scanning:
   ```python
   def record_deployment_event(commit_sha: str, scan_results: ScanResults):
       """Record deployment event with security scan data."""
       event = DeploymentEvent(
           timestamp=datetime.utcnow(),
           commit_sha=commit_sha,
           scan_duration_seconds=scan_results.duration,
           security_gate_blocked=scan_results.gate_blocked,
           severity_counts=scan_results.severity_counts
       )
       append_to_metrics_log(event)
   ```

2. Calculate deployment frequency:
   ```python
   def calculate_deployment_frequency(days: int = 7) -> float:
       """Calculate deployments per day over period."""
       events = load_deployment_events(days=days)
       blocked = [e for e in events if e.security_gate_blocked]
       successful = [e for e in events if not e.security_gate_blocked]
       
       return {
           "total_deployments": len(events),
           "successful_deployments": len(successful),
           "blocked_deployments": len(blocked),
           "deployments_per_day": len(successful) / days,
           "block_rate": len(blocked) / len(events) if events else 0
       }
   ```

3. Set alert threshold:
   - Target: Multiple deploys per day (>1)
   - Alert if: <1 deploy/day over 7 days

#### Step 3: Implement Lead Time Tracking
**Duration**: 2 hours

1. Track commit-to-deploy time:
   ```python
   def record_lead_time(commit_sha: str, commit_time: datetime, deploy_time: datetime, scan_time: float):
       """Record lead time with security scan overhead."""
       lead_time_hours = (deploy_time - commit_time).total_seconds() / 3600
       scan_overhead_pct = (scan_time / 3600) / lead_time_hours * 100
       
       metric = {
           "commit_sha": commit_sha,
           "lead_time_hours": lead_time_hours,
           "scan_time_seconds": scan_time,
           "scan_overhead_pct": scan_overhead_pct,
           "timestamp": deploy_time.isoformat()
       }
       append_to_lead_time_log(metric)
   ```

2. Calculate lead time statistics:
   ```python
   def calculate_lead_time_metrics(days: int = 30) -> dict:
       """Calculate lead time percentiles and scan impact."""
       lead_times = load_lead_time_data(days=days)
       
       return {
           "p50_hours": np.percentile([lt["lead_time_hours"] for lt in lead_times], 50),
           "p95_hours": np.percentile([lt["lead_time_hours"] for lt in lead_times], 95),
           "avg_scan_overhead_pct": np.mean([lt["scan_overhead_pct"] for lt in lead_times]),
           "target": 1.0,  # <1 hour for DORA Elite
           "status": "elite" if p50 < 1.0 else "high" if p50 < 24 else "medium"
       }
   ```

3. Set alert thresholds:
   - Target: P50 <1 hour, P95 <2 hours
   - Alert if: P50 >1 hour or scan overhead >20%

#### Step 4: Implement Change Failure Rate Tracking
**Duration**: 2 hours

1. Track security-related failures:
   ```python
   def record_security_incident(severity: str, cwe_id: str, discovered_in: str, commit_sha: str):
       """Record security incident causing deployment failure."""
       incident = SecurityIncident(
           timestamp=datetime.utcnow(),
           severity=severity,
           cwe_id=cwe_id,
           discovered_in=discovered_in,
           related_commit=commit_sha,
           time_to_fix_hours=None  # Set later when fixed
       )
       append_to_incident_log(incident)
   ```

2. Calculate change failure rate:
   ```python
   def calculate_change_failure_rate(days: int = 30) -> dict:
       """Calculate % of deployments causing security incidents."""
       deployments = load_deployment_events(days=days)
       incidents = load_security_incidents(days=days)
       
       # Match incidents to deployments
       failed_deployments = set()
       for incident in incidents:
           if incident.discovered_in == "production":
               failed_deployments.add(incident.related_commit)
       
       return {
           "total_deployments": len(deployments),
           "failed_deployments": len(failed_deployments),
           "change_failure_rate": len(failed_deployments) / len(deployments) if deployments else 0,
           "security_related_failures": len([i for i in incidents if i.discovered_in == "production"]),
           "target": 0.05,  # <5% for DORA Elite
           "status": "elite" if cfr < 0.05 else "high" if cfr < 0.15 else "medium"
       }
   ```

3. Set alert threshold:
   - Target: <5% failure rate
   - Alert if: >15% or trending upward

#### Step 5: Implement MTTR Tracking
**Duration**: 2 hours

1. Track time to fix vulnerabilities:
   ```python
   def record_vulnerability_fix(finding_id: str, discovered: datetime, fixed: datetime, severity: str):
       """Record MTTR for vulnerability remediation."""
       mttr_hours = (fixed - discovered).total_seconds() / 3600
       
       metric = {
           "finding_id": finding_id,
           "severity": severity,
           "discovered": discovered.isoformat(),
           "fixed": fixed.isoformat(),
           "mttr_hours": mttr_hours
       }
       append_to_mttr_log(metric)
   ```

2. Calculate MTTR by severity:
   ```python
   def calculate_mttr_metrics(days: int = 30) -> dict:
       """Calculate mean time to recovery for vulnerabilities."""
       fixes = load_mttr_data(days=days)
       
       critical = [f for f in fixes if f["severity"] == "critical"]
       high = [f for f in fixes if f["severity"] == "high"]
       
       return {
           "mttr_critical_hours": np.mean([f["mttr_hours"] for f in critical]) if critical else None,
           "mttr_high_hours": np.mean([f["mttr_hours"] for f in high]) if high else None,
           "mttr_all_hours": np.mean([f["mttr_hours"] for f in fixes]) if fixes else None,
           "target_critical": 1.0,  # <1 hour for critical
           "target_high": 24.0,  # <24 hours for high
           "status": "elite" if mttr_crit < 1.0 else "high" if mttr_crit < 24 else "medium"
       }
   ```

3. Set alert thresholds:
   - Target: Critical <1 hour, High <24 hours
   - Alert if: Critical >4 hours or High >48 hours

#### Step 6: Create Monthly DORA Report
**File**: `src/specify_cli/security/dora_report.py`
**Duration**: 3 hours

1. Implement report generator:
   ```bash
   specify security dora-report --month 2025-12 --format markdown,html
   ```

2. Report sections:
   - Executive summary with DORA classification
   - Deployment frequency trend chart
   - Lead time distribution (P50, P95)
   - Security scan overhead analysis
   - Change failure rate by week
   - MTTR by severity level
   - Recommendations for improvement

3. Report template:
   ```markdown
   # DORA Metrics Report: Security Scanning Impact
   
   **Period**: December 2025
   **Generated**: 2025-12-31
   
   ## Executive Summary
   
   - **DORA Classification**: Elite
   - **Deployment Frequency**: 3.2 deploys/day ✅
   - **Lead Time (P50)**: 0.8 hours ✅
   - **Change Failure Rate**: 3.2% ✅
   - **MTTR (Critical)**: 0.7 hours ✅
   
   ## Security Scan Impact
   
   - **Scan Overhead**: 8% of lead time (target: <10%)
   - **Gate Blocks**: 12 blocked, 87 successful (12% block rate)
   - **False Positives**: 5% (down from 15% last month)
   
   ## Trends
   
   [Charts showing metrics over time]
   
   ## Recommendations
   
   1. Continue using incremental scanning (saves 60% time)
   2. Tune rules to reduce false positives further
   3. Investigate spike in lead time on Dec 15
   ```

#### Step 7: Add DORA Metrics Alerts
**File**: `templates/observability/dora-alerts.yml`
**Duration**: 1 hour

1. Create alert rules:
   ```yaml
   alerts:
     - name: DORA_DeploymentFrequencyLow
       condition: deployments_per_day < 1
       for: 7d
       severity: warning
       message: "Deployment frequency below DORA Elite target"
     
     - name: DORA_LeadTimeDegraded
       condition: lead_time_p50_hours > 1
       for: 3d
       severity: warning
       message: "Lead time exceeds 1 hour DORA Elite target"
     
     - name: DORA_SecurityScanOverhead
       condition: scan_overhead_pct > 20
       for: 7d
       severity: warning
       message: "Security scans consuming >20% of lead time"
     
     - name: DORA_ChangeFailureRateHigh
       condition: change_failure_rate > 0.15
       for: 7d
       severity: critical
       message: "Change failure rate above 15%"
     
     - name: DORA_MTTR_Critical_High
       condition: mttr_critical_hours > 4
       for: 24h
       severity: critical
       message: "Critical vulnerability MTTR exceeds 4 hours"
   ```

2. Integrate with existing alerting (Prometheus, Slack)

#### Step 8: Testing
**Duration**: 2 hours

1. **Data collection tests**:
   - Record deployment events
   - Record incidents
   - Record vulnerability fixes
   - Verify data persists correctly

2. **Calculation tests**:
   - Test DORA metric calculations with sample data
   - Verify percentile calculations
   - Test edge cases (no data, single data point)

3. **Report generation tests**:
   - Generate report for test period
   - Verify all sections populate
   - Test multiple output formats

4. **Alert tests**:
   - Trigger each alert condition
   - Verify notifications sent
   - Test alert recovery

### Dependencies
- task-250: Observability (Prometheus metrics)
- Security scan command with timing instrumentation
- Incident tracking system (or manual recording)

### Testing Checklist
- [ ] Deployment events recorded correctly
- [ ] Lead time calculated accurately
- [ ] Change failure rate tracks incidents
- [ ] MTTR calculation works by severity
- [ ] Monthly report generates successfully
- [ ] All DORA alerts trigger appropriately
- [ ] Metrics show security doesn't degrade velocity

### Estimated Effort
**Total**: 14 hours (1.75 days)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**ON HOLD (Dec 2025)**: Security scanning features may move to dedicated security repo.
<!-- SECTION:NOTES:END -->
