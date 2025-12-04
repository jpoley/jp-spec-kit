# Galway DORA Metrics Tracking Design

**Status**: Platform Design
**Owner**: Platform Engineer
**Last Updated**: 2025-12-04
**Related Task**: task-253

## Executive Summary

This document defines DORA (DevOps Research and Assessment) metrics tracking for galway host tasks, implementing automated collection, visualization, and continuous improvement feedback loops to achieve Elite performance.

## The Four Key Metrics

### Metric 1: Deployment Frequency

**Definition**: How often code is deployed to production

**Elite Performance**: On-demand (multiple per day)

**Measurement**:
```prometheus
# Count successful deployments per day
sum(increase(deployment_total{environment="production", status="success"}[1d]))

# Or calculate rate
rate(deployment_total{environment="production", status="success"}[7d]) * 86400
```

**Data Collection**:
```yaml
# Record deployment event
- name: Record deployment
  run: |
    curl -X POST https://metrics.poley.dev/dora/deployment \
      -H "Content-Type: application/json" \
      -d '{
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "environment": "production",
        "commit_sha": "'${{ github.sha }}'",
        "version": "'${{ steps.version.outputs.version }}'"
      }'
```

**Target Progression**:
- **Current**: Per PR merge (~1-2 per day)
- **6 months**: Multiple per day (3-5)
- **12 months**: On-demand (10+)

### Metric 2: Lead Time for Changes

**Definition**: Time from code committed to code successfully running in production

**Elite Performance**: Less than 1 hour

**Measurement**:
```prometheus
# Calculate lead time (commit to deployment)
histogram_quantile(0.50, rate(lead_time_seconds_bucket[7d])) / 60  # P50 in minutes
histogram_quantile(0.95, rate(lead_time_seconds_bucket[7d])) / 60  # P95 in minutes
```

**Data Collection**:
```yaml
# Calculate lead time on deployment
- name: Calculate lead time
  run: |
    # Get first commit time in PR
    FIRST_COMMIT_TIME=$(gh pr view ${{ github.event.pull_request.number }} \
      --json commits --jq '.commits[0].committedDate')

    # Get deployment time
    DEPLOY_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    # Calculate duration in seconds
    LEAD_TIME=$(( $(date -d "$DEPLOY_TIME" +%s) - $(date -d "$FIRST_COMMIT_TIME" +%s) ))

    # Send metric
    curl -X POST https://metrics.poley.dev/dora/lead-time \
      -d "{\"lead_time_seconds\": $LEAD_TIME, \"pr_number\": ${{ github.event.pull_request.number }}}"
```

**Target Progression**:
- **Current**: ~30 minutes (PR open to merge)
- **6 months**: < 15 minutes
- **12 months**: < 5 minutes (Elite)

### Metric 3: Change Failure Rate

**Definition**: Percentage of deployments causing a failure in production

**Elite Performance**: 0-15%

**Measurement**:
```prometheus
# Calculate failure rate
sum(deployment_total{status="failure"}) / sum(deployment_total) * 100
```

**Data Collection**:
```yaml
# Record deployment outcome
- name: Record deployment result
  if: always()
  run: |
    STATUS=${{ job.status }}
    curl -X POST https://metrics.poley.dev/dora/deployment \
      -d '{
        "status": "'$STATUS'",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "commit_sha": "'${{ github.sha }}'"
      }'
```

**Failure Definition**:
- Deployment fails during rollout
- Service health checks fail after deployment
- Rollback required within 1 hour
- Critical bug reported within 24 hours

**Target Progression**:
- **Current**: ~10% (estimated)
- **6 months**: < 5%
- **12 months**: < 5% (Elite sustained)

### Metric 4: Time to Restore Service

**Definition**: Time to restore service after incident

**Elite Performance**: Less than 1 hour

**Measurement**:
```prometheus
# Calculate MTTR (Mean Time To Restore)
avg_over_time(incident_resolution_seconds[30d]) / 60  # Average in minutes
histogram_quantile(0.95, rate(incident_resolution_seconds_bucket[30d])) / 60  # P95
```

**Data Collection**:
```yaml
# Record incident lifecycle
- name: Record incident
  run: |
    # Incident detected
    curl -X POST https://metrics.poley.dev/dora/incident \
      -d '{
        "event": "detected",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "severity": "critical",
        "incident_id": "INC-001"
      }'

    # ... resolution happens ...

    # Incident resolved
    curl -X POST https://metrics.poley.dev/dora/incident \
      -d '{
        "event": "resolved",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "incident_id": "INC-001"
      }'
```

**Target Progression**:
- **Current**: N/A (no production yet)
- **6 months**: < 1 hour
- **12 months**: < 30 minutes (Elite)

## Automated Data Collection

### GitHub Actions Integration

**Workflow** (`.github/workflows/dora-metrics.yml`):
```yaml
name: DORA Metrics Collection

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, closed]
  release:
    types: [published]

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for lead time calculation

      - name: Calculate deployment frequency
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          # Count deployments in last 24 hours
          DEPLOYS=$(gh run list \
            --workflow=release.yml \
            --created "$(date -d '24 hours ago' -Iseconds)" \
            --json conclusion \
            | jq '[.[] | select(.conclusion=="success")] | length')

          echo "deployments_per_day=$DEPLOYS"

          # Send metric
          curl -X POST ${{ secrets.METRICS_ENDPOINT }}/deployment-frequency \
            -H "Authorization: Bearer ${{ secrets.METRICS_API_KEY }}" \
            -d "{\"count\": $DEPLOYS, \"window\": \"24h\"}"

      - name: Calculate lead time
        if: github.event_name == 'pull_request' && github.event.action == 'closed' && github.event.pull_request.merged
        run: |
          PR_NUM=${{ github.event.pull_request.number }}

          # Get first commit time
          FIRST_COMMIT=$(gh pr view $PR_NUM --json commits \
            | jq -r '.commits[0].committedDate')

          # Get merge time
          MERGED_AT=${{ github.event.pull_request.merged_at }}

          # Calculate lead time in seconds
          FIRST_COMMIT_EPOCH=$(date -d "$FIRST_COMMIT" +%s)
          MERGED_EPOCH=$(date -d "$MERGED_AT" +%s)
          LEAD_TIME=$((MERGED_EPOCH - FIRST_COMMIT_EPOCH))

          echo "lead_time_seconds=$LEAD_TIME"
          echo "lead_time_minutes=$((LEAD_TIME / 60))"

          # Send metric
          curl -X POST ${{ secrets.METRICS_ENDPOINT }}/lead-time \
            -H "Authorization: Bearer ${{ secrets.METRICS_API_KEY }}" \
            -d "{
              \"lead_time_seconds\": $LEAD_TIME,
              \"pr_number\": $PR_NUM,
              \"commit_count\": $(gh pr view $PR_NUM --json commits | jq '.commits | length')
            }"

      - name: Calculate change failure rate
        if: github.event_name == 'release'
        run: |
          # Get releases in last 30 days
          RELEASES=$(gh release list --limit 100 --json tagName,createdAt \
            | jq '[.[] | select(.createdAt > (now - 30*86400 | todate))] | length')

          # Count releases with hotfixes within 24h (proxy for failures)
          HOTFIXES=$(gh pr list --search "label:hotfix merged:>=$(date -d '30 days ago' +%Y-%m-%d)" \
            --json number --jq 'length')

          FAILURE_RATE=$(awk "BEGIN {print ($HOTFIXES / $RELEASES) * 100}")

          echo "change_failure_rate=$FAILURE_RATE%"

          # Send metric
          curl -X POST ${{ secrets.METRICS_ENDPOINT }}/change-failure-rate \
            -d "{\"rate\": $FAILURE_RATE, \"window\": \"30d\"}"

      - name: Store metrics locally
        if: always()
        run: |
          mkdir -p .dora-metrics
          cat > .dora-metrics/latest.json <<EOF
          {
            "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "event": "${{ github.event_name }}",
            "deployment_frequency": "${DEPLOYS:-N/A}",
            "lead_time_seconds": "${LEAD_TIME:-N/A}",
            "change_failure_rate": "${FAILURE_RATE:-N/A}"
          }
          EOF

      - name: Upload metrics artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: dora-metrics-${{ github.run_id }}
          path: .dora-metrics/
          retention-days: 90
```

### Python Collection Script

**Script** (`scripts/python/collect-dora-metrics.py`):
```python
#!/usr/bin/env python3
"""
Collect DORA metrics from GitHub API and local data.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY", "jpoley/jp-spec-kit")
API_BASE = f"https://api.github.com/repos/{REPO}"

def get_deployment_frequency(days: int = 7) -> float:
    """Calculate deployments per day over last N days."""
    since = (datetime.now() - timedelta(days=days)).isoformat()

    # Get workflow runs (assuming release workflow = deployment)
    response = requests.get(
        f"{API_BASE}/actions/workflows/release.yml/runs",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        params={"created": f">={since}", "status": "success"}
    )

    runs = response.json().get("workflow_runs", [])
    return len(runs) / days

def get_lead_time_for_changes(count: int = 20) -> dict:
    """Calculate lead time for last N merged PRs."""
    response = requests.get(
        f"{API_BASE}/pulls",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        params={"state": "closed", "per_page": count, "sort": "updated", "direction": "desc"}
    )

    prs = [pr for pr in response.json() if pr.get("merged_at")]
    lead_times = []

    for pr in prs:
        # Get first commit
        commits_response = requests.get(
            pr["commits_url"],
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
        )
        commits = commits_response.json()

        if not commits:
            continue

        first_commit_time = datetime.fromisoformat(commits[0]["commit"]["committer"]["date"].replace("Z", "+00:00"))
        merged_time = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))

        lead_time_seconds = (merged_time - first_commit_time).total_seconds()
        lead_times.append(lead_time_seconds)

    if not lead_times:
        return {"p50": 0, "p95": 0, "mean": 0}

    lead_times.sort()
    return {
        "p50": lead_times[len(lead_times) // 2],
        "p95": lead_times[int(len(lead_times) * 0.95)],
        "mean": sum(lead_times) / len(lead_times),
        "count": len(lead_times)
    }

def get_change_failure_rate(days: int = 30) -> float:
    """Calculate percentage of changes requiring hotfix."""
    since = (datetime.now() - timedelta(days=days)).isoformat()

    # Get all merged PRs
    all_prs_response = requests.get(
        f"{API_BASE}/pulls",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        params={"state": "closed", "since": since}
    )
    all_prs = [pr for pr in all_prs_response.json() if pr.get("merged_at")]

    # Get hotfix PRs
    hotfix_prs_response = requests.get(
        f"{API_BASE}/pulls",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        params={"state": "closed", "since": since}
    )
    hotfix_prs = [pr for pr in hotfix_prs_response.json()
                  if pr.get("merged_at") and any(label["name"] == "hotfix" for label in pr.get("labels", []))]

    if not all_prs:
        return 0.0

    return (len(hotfix_prs) / len(all_prs)) * 100

def main():
    print("Collecting DORA metrics...")

    metrics = {
        "timestamp": datetime.now().isoformat(),
        "deployment_frequency": {
            "per_day_7d": get_deployment_frequency(7),
            "per_day_30d": get_deployment_frequency(30),
        },
        "lead_time_for_changes": get_lead_time_for_changes(20),
        "change_failure_rate": {
            "percent_30d": get_change_failure_rate(30)
        }
    }

    # Save to file
    output_file = Path(".dora-metrics/collected.json")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps(metrics, indent=2))

    print(f"✅ Metrics collected and saved to {output_file}")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
```

## Visualization and Dashboards

### Grafana Dashboard Design

**Dashboard 1: DORA Overview**

**Panels**:

1. **Deployment Frequency (Gauge)**
   ```promql
   # Deployments per day (last 7 days)
   rate(deployment_total{environment="production", status="success"}[7d]) * 86400
   ```
   - Elite: ≥ 1 (green)
   - High: 0.14-1 (yellow)
   - Medium/Low: < 0.14 (red)

2. **Lead Time (Histogram)**
   ```promql
   # P50 and P95 lead time in minutes
   histogram_quantile(0.50, rate(lead_time_seconds_bucket[7d])) / 60
   histogram_quantile(0.95, rate(lead_time_seconds_bucket[7d])) / 60
   ```
   - Elite: < 60 min (green)
   - High: 1-7 days (yellow)
   - Medium/Low: > 7 days (red)

3. **Change Failure Rate (Gauge)**
   ```promql
   # Percentage of failed deployments
   sum(deployment_total{status="failure"}) / sum(deployment_total) * 100
   ```
   - Elite: 0-15% (green)
   - High/Medium: 16-45% (yellow)
   - Low: > 45% (red)

4. **Time to Restore (Histogram)**
   ```promql
   # P95 restoration time in minutes
   histogram_quantile(0.95, rate(incident_resolution_seconds_bucket[30d])) / 60
   ```
   - Elite: < 60 min (green)
   - High: 1 day (yellow)
   - Medium/Low: > 1 day (red)

**Dashboard 2: DORA Trends**

**Panels**:

1. **Deployment Frequency Over Time (Time Series)**
   ```promql
   rate(deployment_total{environment="production", status="success"}[1d]) * 86400
   ```

2. **Lead Time Trend (Time Series)**
   ```promql
   histogram_quantile(0.95, rate(lead_time_seconds_bucket[7d])) / 3600  # Hours
   ```

3. **Change Failure Rate Trend (Time Series)**
   ```promql
   sum(rate(deployment_total{status="failure"}[7d])) / sum(rate(deployment_total[7d])) * 100
   ```

4. **Performance Classification (Stat Panel)**
   - Shows current DORA level: Elite / High / Medium / Low
   - Based on all four metrics

### Dashboard JSON Export

**Grafana Dashboard Definition** (`observability/grafana/dashboards/dora-metrics.json`):
```json
{
  "dashboard": {
    "title": "DORA Metrics - JP Spec Kit",
    "tags": ["dora", "devops", "metrics"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Deployment Frequency",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(deployment_total{environment=\"production\", status=\"success\"}[7d]) * 86400"
          }
        ],
        "fieldConfig": {
          "thresholds": {
            "steps": [
              {"value": 0, "color": "red"},
              {"value": 0.14, "color": "yellow"},
              {"value": 1, "color": "green"}
            ]
          }
        }
      }
    ]
  }
}
```

## Continuous Improvement Process

### Weekly Review

**Process**:
1. **Monday**: Review DORA metrics dashboard
2. **Tuesday**: Identify bottlenecks in CI/CD pipeline
3. **Wednesday**: Implement improvements
4. **Thursday**: Test and validate changes
5. **Friday**: Deploy optimizations, measure impact

**Key Questions**:
- What's blocking faster deployments?
- Where is lead time increasing?
- What caused recent failures?
- How can we reduce MTTR?

### Monthly Retrospective

**Agenda**:
1. Compare current vs. target metrics
2. Review trend direction (improving/degrading)
3. Celebrate wins
4. Identify improvement initiatives for next month

**Output**: Action items with owners and due dates

### Quarterly Goals

**Q1 2025**:
- Deployment Frequency: 1-2 per day → 3-5 per day
- Lead Time: 30 min → 15 min
- Change Failure Rate: Maintain < 10%

**Q2 2025**:
- Deployment Frequency: 5-10 per day
- Lead Time: 15 min → 5 min
- Change Failure Rate: Maintain < 5%

## Integration with Security Metrics (task-250)

**Security-Specific DORA Metrics**:

```prometheus
# Mean Time to Detect (MTTD) vulnerability
security_vulnerability_detection_time_seconds

# Mean Time to Remediate (MTTR) vulnerability
security_vulnerability_remediation_time_seconds

# Security deployment frequency (patches)
security_patch_deployment_total
```

**Target**:
- MTTD: < 24 hours
- MTTR (Critical): < 24 hours
- MTTR (High): < 7 days

## Success Criteria

**6-Month Goal: High Performance**
- Deployment Frequency: Weekly to monthly
- Lead Time: 1-6 months
- Change Failure Rate: 16-30%
- MTTR: < 1 day

**12-Month Goal: Elite Performance**
- Deployment Frequency: On-demand (multiple per day)
- Lead Time: < 1 hour
- Change Failure Rate: 0-15%
- MTTR: < 1 hour

## Related Tasks

| Task ID | Title | DORA Integration |
|---------|-------|------------------|
| task-253 | DORA Metrics Implementation | Core metrics tracking |
| task-250 | Security Observability | Security MTTR/MTTD |
| task-248 | Security Pipeline | Impact on lead time |
| task-282 | Archive Workflow | Automation improving velocity |

## Appendix: DORA Classification Reference

| Level | Deployment Frequency | Lead Time | Change Failure Rate | MTTR |
|-------|---------------------|-----------|---------------------|------|
| **Elite** | On-demand (multiple/day) | < 1 hour | 0-15% | < 1 hour |
| **High** | Weekly to monthly | 1 day - 1 week | 16-30% | < 1 day |
| **Medium** | Monthly to every 6 months | 1 week - 1 month | 16-30% | 1 day - 1 week |
| **Low** | Fewer than once per 6 months | 1-6 months | 16-30% | 1 week - 1 month |

Source: [2023 State of DevOps Report](https://dora.dev/)
