---
description: Incident response guidance for production issues and outages.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command provides structured incident response guidance for handling production incidents, outages, and critical issues.

### Incident Response Framework

**Incident Severity Levels**:

| Severity | Impact | Response Time | Example |
|----------|--------|---------------|---------|
| **SEV-1** | Complete outage, data loss | Immediate | Total service down, data breach |
| **SEV-2** | Major degradation | < 15 minutes | Critical feature broken, high error rate |
| **SEV-3** | Partial degradation | < 1 hour | Non-critical feature impaired |
| **SEV-4** | Minor issue | < 4 hours | UI bug, performance degradation |

### Incident Response Steps

1. **Detect**
2. **Acknowledge**
3. **Assess**
4. **Mitigate**
5. **Resolve**
6. **Post-Mortem**

### Step 1: Detect

**Detection Sources**:
- Monitoring alerts (Prometheus, Datadog)
- Customer reports
- Health check failures
- Error rate spikes
- Manual discovery

**Initial Actions**:
```bash
# Check system status
kubectl get pods -n production
systemctl status app-service

# Check recent logs
tail -100 /var/log/app/error.log
kubectl logs -n production deploy/app --tail=100

# Check metrics dashboard
# Open Grafana/monitoring dashboard
```

### Step 2: Acknowledge

**Incident Declaration**:
```text
INCIDENT DECLARED
Severity: SEV-2
Time: 2025-12-09 14:23 UTC
Summary: High error rate on /api/orders endpoint
Impact: ~30% of order requests failing
Incident Commander: @alice
```

**Communication Channels**:
- Create incident Slack channel: `#incident-YYYY-MM-DD-orders`
- Page on-call engineer
- Notify stakeholders (for SEV-1/SEV-2)
- Update status page

### Step 3: Assess

**Gather Information**:
```bash
# Check error logs
grep -i error /var/log/app/app.log | tail -50

# Check recent deployments
kubectl rollout history deployment/app -n production
git log --oneline --since="2 hours ago"

# Check resource usage
kubectl top pods -n production
free -h
df -h

# Check dependencies
curl https://external-api.example.com/health
redis-cli ping

# Check database
psql -c "SELECT pg_size_pretty(pg_database_size('dbname'));"
psql -c "SELECT * FROM pg_stat_activity;"
```

**Key Questions**:
- When did it start?
- What changed recently?
- What's the blast radius?
- Are dependencies healthy?
- Are resources saturated?

### Step 4: Mitigate

**Mitigation Strategies**:

**1. Rollback**:
```bash
# Kubernetes rollback
kubectl rollout undo deployment/app -n production

# Verify rollback
kubectl rollout status deployment/app -n production
```

**2. Scale Up**:
```bash
# Increase replicas
kubectl scale deployment/app --replicas=10 -n production

# Verify scaling
kubectl get pods -n production
```

**3. Circuit Breaker**:
```bash
# Disable failing feature
kubectl set env deployment/app FEATURE_FLAG_ORDERS=false -n production

# Or via ConfigMap
kubectl edit configmap app-config -n production
```

**4. Traffic Shifting**:
```bash
# Route traffic to backup region
kubectl patch service app -p '{"spec":{"selector":{"region":"us-west"}}}'

# Or use ingress
kubectl edit ingress app-ingress -n production
```

**5. Database Query Kill**:
```sql
-- Find long-running queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Kill problematic query
SELECT pg_terminate_backend(12345);
```

### Step 5: Resolve

**Verification**:
```bash
# Check error rate
# (Should be back to baseline)
curl "http://prometheus:9090/api/v1/query?query=rate(http_errors_total[5m])"

# Check latency
# (Should be within SLO)

# Spot check functionality
curl https://api.example.com/health
curl https://api.example.com/api/orders/123
```

**Declare Resolution**:
```text
INCIDENT RESOLVED
Time: 2025-12-09 15:45 UTC
Duration: 1h 22m
Root Cause: Database connection pool exhaustion
Mitigation: Increased pool size from 20 to 50
Next Steps: Post-mortem scheduled for Dec 10 @ 10am
```

### Step 6: Post-Mortem

**Post-Mortem Template**:
```markdown
# Post-Mortem: High Error Rate on Orders API

**Date**: 2025-12-09
**Duration**: 1h 22m
**Severity**: SEV-2
**Incident Commander**: @alice

## Summary

On December 9, 2025, from 14:23 to 15:45 UTC, approximately 30% of order
requests failed with 500 errors due to database connection pool exhaustion.

## Impact

- **Users Affected**: ~5,000 customers
- **Failed Requests**: 12,450 errors over 82 minutes
- **Revenue Impact**: ~$15,000 in failed orders
- **Customer Support**: 23 support tickets created

## Timeline

**14:23 UTC** - First alert: High error rate on /api/orders
**14:25 UTC** - Incident declared SEV-2, @alice paged
**14:30 UTC** - Root cause identified: DB connection pool exhausted
**14:35 UTC** - Mitigation attempted: Restart app servers (no effect)
**14:45 UTC** - Increased connection pool from 20 to 50
**15:00 UTC** - Error rate declining
**15:45 UTC** - Incident resolved, monitoring continued

## Root Cause

The recent feature launch increased database query complexity, causing longer
query execution times. With fixed pool size of 20, connections were held
longer, leading to pool exhaustion under load.

## What Went Well

- Monitoring alerts fired within 2 minutes
- Incident commander assigned quickly
- Team identified root cause in 12 minutes
- Mitigation was straightforward

## What Went Poorly

- Initial mitigation (restart) was ineffective and wasted 10 minutes
- No alerts for connection pool saturation
- Connection pool size hadn't been tuned in 2 years
- Status page wasn't updated until 20 minutes into incident

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Add connection pool monitoring alert | @bob | Dec 12 | TODO |
| Tune pool size based on load testing | @charlie | Dec 15 | TODO |
| Document connection pool runbook | @alice | Dec 13 | TODO |
| Implement auto-scaling for pool size | @dave | Dec 20 | TODO |
| Update incident response playbook | @alice | Dec 12 | DONE |
| Add status page automation to alerting | @eve | Dec 16 | TODO |

## Lessons Learned

1. **Monitoring Blind Spot**: No alerts for connection pool metrics
2. **Configuration Drift**: Pool size unchanged despite 3x traffic growth
3. **Load Testing Gap**: New feature not tested under production load
4. **Communication Delay**: Status page updated manually, too slow

## Prevention

To prevent similar incidents:
- Monitor all critical resource pools (connections, threads, memory)
- Implement auto-scaling for configurable resources
- Load test new features before production
- Automate status page updates via monitoring
```

### Incident Communication Templates

**Initial Announcement**:
```text
🚨 INCIDENT ALERT - SEV-2 🚨

We're investigating reports of failed order requests. Our team is actively
working on resolving this issue. We'll provide updates every 15 minutes.

Status: https://status.example.com
```

**Update**:
```text
📊 INCIDENT UPDATE

We've identified the root cause as database connection pool exhaustion and
are implementing a fix. Approximately 70% of orders are processing
successfully. Next update in 15 minutes.
```

**Resolution**:
```text
✅ INCIDENT RESOLVED

The issue with order failures has been resolved. All systems are operating
normally. We apologize for the disruption. A detailed post-mortem will be
published within 48 hours.
```

### Incident Response Checklist

During incident:
- [ ] Severity assessed and declared
- [ ] Incident commander assigned
- [ ] Communication channels created
- [ ] On-call engineers paged
- [ ] Status page updated
- [ ] Stakeholders notified
- [ ] Mitigation actions documented
- [ ] Customer impact assessed
- [ ] Resolution verified
- [ ] All-clear communicated

After incident:
- [ ] Post-mortem scheduled (within 72 hours)
- [ ] Action items created and assigned
- [ ] Runbooks updated
- [ ] Monitoring gaps addressed
- [ ] Stakeholder debrief completed

## Related Commands

- `/ops:monitor` - Monitoring and alerting
- `/ops:deploy` - Deployment operations
- `/ops:scale` - Scaling resources
- `/sec:audit` - Security incident response
