# Hook Observability Design

## Overview

The JP Spec Kit hook observability system provides comprehensive visibility into hook execution through structured logging, audit trails, and operational metrics. This document defines the observability architecture, log formats, monitoring tools, and implementation requirements.

## Design Principles

1. **Machine-Readable First**: Structured JSON logging enables automated analysis
2. **Privacy-Aware**: Log metadata, not sensitive data (env values, stdout content)
3. **Performance-Conscious**: Logging doesn't block hook execution
4. **Tamper-Evident**: Audit logs are append-only and include integrity markers
5. **Actionable**: Logs provide clear context for debugging and troubleshooting

## Logging Architecture

### Log Types

1. **Audit Log**: Immutable record of all hook executions (compliance, forensics)
2. **Debug Log**: Detailed execution trace (development, troubleshooting)
3. **Error Log**: Hook failures and validation errors (operations, alerting)
4. **Performance Log**: Timing and resource usage (optimization, capacity planning)

### Log Storage

```
.specify/hooks/
├── audit.log           # Append-only audit trail (JSONL)
├── audit.log.1         # Rotated audit logs
├── audit.log.2
├── debug.log           # Debug-level logs (opt-in)
└── metrics.json        # Aggregated metrics (hourly rollup)
```

## Audit Log Format

### Schema Version 1.0

```json
{
  "version": "1.0",
  "timestamp": "2025-12-02T15:30:45.123456Z",
  "event_id": "evt_01HQZX123ABC",
  "event_type": "implement.completed",
  "hook_execution": {
    "hook_name": "run-tests",
    "hook_id": "hook_abc123",
    "script_path": ".specify/hooks/run-tests.sh",
    "status": "success",
    "exit_code": 0,
    "duration_ms": 30333,
    "started_at": "2025-12-02T15:30:45.123Z",
    "completed_at": "2025-12-02T15:31:15.456Z"
  },
  "execution_context": {
    "working_directory": "/home/user/project",
    "environment_keys": ["PYTEST_ARGS", "FEATURE_NAME"],
    "pid": 12345,
    "user": "jpoley",
    "hostname": "muckross"
  },
  "output": {
    "stdout_lines": 42,
    "stderr_lines": 0,
    "stdout_truncated": false,
    "stderr_truncated": false
  },
  "security": {
    "validation_passed": true,
    "warnings": [],
    "timeout_enforced": false
  },
  "metadata": {
    "cli_version": "0.0.179",
    "python_version": "3.11.9",
    "platform": "linux"
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Audit log schema version (semantic versioning) |
| `timestamp` | ISO8601 | When audit entry was created (UTC, microsecond precision) |
| `event_id` | string | Unique identifier for event that triggered hook |
| `event_type` | string | Type of event (e.g., `implement.completed`) |
| `hook_execution.hook_name` | string | Name of hook from hooks.yaml |
| `hook_execution.hook_id` | string | Unique identifier for this execution |
| `hook_execution.script_path` | string | Path to executed script (relative to project root) |
| `hook_execution.status` | enum | `success`, `failed`, `timeout`, `error` |
| `hook_execution.exit_code` | integer | Script exit code (0-255) |
| `hook_execution.duration_ms` | integer | Execution time in milliseconds |
| `execution_context.working_directory` | string | CWD where script executed |
| `execution_context.environment_keys` | array | Environment variable names (not values) |
| `execution_context.pid` | integer | Process ID of hook execution |
| `execution_context.user` | string | Username that executed hook |
| `execution_context.hostname` | string | Hostname where hook ran |
| `output.stdout_lines` | integer | Number of lines in stdout |
| `output.stderr_lines` | integer | Number of lines in stderr |
| `output.stdout_truncated` | boolean | Whether stdout was truncated in debug log |
| `output.stderr_truncated` | boolean | Whether stderr was truncated in debug log |
| `security.validation_passed` | boolean | Whether security validation passed |
| `security.warnings` | array | List of security warnings |
| `security.timeout_enforced` | boolean | Whether timeout was hit |

### Status Values

| Status | Exit Code | Description |
|--------|-----------|-------------|
| `success` | 0 | Hook executed successfully |
| `failed` | 1-127 | Hook returned non-zero exit code |
| `timeout` | 124 | Hook exceeded timeout and was killed |
| `error` | 128+ | Hook terminated by signal (SIGTERM=143, SIGKILL=137) |

### Example Audit Entries

**Successful Execution**:
```json
{
  "version": "1.0",
  "timestamp": "2025-12-02T15:30:45.123456Z",
  "event_id": "evt_abc123",
  "event_type": "implement.completed",
  "hook_execution": {
    "hook_name": "run-tests",
    "hook_id": "hook_xyz789",
    "script_path": ".specify/hooks/run-tests.sh",
    "status": "success",
    "exit_code": 0,
    "duration_ms": 30333,
    "started_at": "2025-12-02T15:30:45.123Z",
    "completed_at": "2025-12-02T15:31:15.456Z"
  },
  "execution_context": {
    "working_directory": "/home/jpoley/ps/jp-spec-kit",
    "environment_keys": ["PYTEST_ARGS"],
    "pid": 12345,
    "user": "jpoley",
    "hostname": "muckross"
  },
  "output": {
    "stdout_lines": 42,
    "stderr_lines": 0,
    "stdout_truncated": false,
    "stderr_truncated": false
  },
  "security": {
    "validation_passed": true,
    "warnings": [],
    "timeout_enforced": false
  },
  "metadata": {
    "cli_version": "0.0.179",
    "python_version": "3.11.9",
    "platform": "linux"
  }
}
```

**Timeout Failure**:
```json
{
  "version": "1.0",
  "timestamp": "2025-12-02T16:00:00.000Z",
  "event_id": "evt_def456",
  "event_type": "validate.completed",
  "hook_execution": {
    "hook_name": "long-validation",
    "hook_id": "hook_abc123",
    "script_path": ".specify/hooks/long-validation.sh",
    "status": "timeout",
    "exit_code": 124,
    "duration_ms": 30005,
    "started_at": "2025-12-02T15:59:30.000Z",
    "completed_at": "2025-12-02T16:00:00.005Z"
  },
  "execution_context": {
    "working_directory": "/home/jpoley/ps/jp-spec-kit",
    "environment_keys": [],
    "pid": 12346,
    "user": "jpoley",
    "hostname": "muckross"
  },
  "output": {
    "stdout_lines": 5,
    "stderr_lines": 1,
    "stdout_truncated": false,
    "stderr_truncated": false
  },
  "security": {
    "validation_passed": true,
    "warnings": [],
    "timeout_enforced": true
  },
  "metadata": {
    "cli_version": "0.0.179",
    "python_version": "3.11.9",
    "platform": "linux"
  }
}
```

**Security Violation**:
```json
{
  "version": "1.0",
  "timestamp": "2025-12-02T17:00:00.000Z",
  "event_id": "evt_security_001",
  "event_type": "security.violation",
  "hook_execution": {
    "hook_name": "malicious-hook",
    "hook_id": "hook_rejected",
    "script_path": "../../etc/passwd",
    "status": "error",
    "exit_code": 1,
    "duration_ms": 0,
    "started_at": null,
    "completed_at": null
  },
  "execution_context": {
    "working_directory": null,
    "environment_keys": [],
    "pid": null,
    "user": "jpoley",
    "hostname": "muckross"
  },
  "output": {
    "stdout_lines": 0,
    "stderr_lines": 0,
    "stdout_truncated": false,
    "stderr_truncated": false
  },
  "security": {
    "validation_passed": false,
    "warnings": ["Path traversal detected in script path"],
    "timeout_enforced": false
  },
  "metadata": {
    "cli_version": "0.0.179",
    "python_version": "3.11.9",
    "platform": "linux"
  }
}
```

## Debug Log Format

### Purpose

Debug logs provide detailed execution trace for development and troubleshooting. Unlike audit logs, debug logs include:
- Full stdout/stderr output
- Environment variable values
- Detailed timing breakdowns
- Subprocess metadata

### Enabling Debug Logging

```bash
# Enable via environment variable
export SPECIFY_HOOKS_DEBUG=1
specify hooks run --event-type implement.completed

# Enable via CLI flag
specify hooks run --event-type implement.completed --debug

# Enable via configuration
# .specify/hooks/hooks.yaml
defaults:
  debug_logging: true
```

### Debug Log Entry

```json
{
  "timestamp": "2025-12-02T15:30:45.123456Z",
  "level": "DEBUG",
  "hook_name": "run-tests",
  "event_type": "implement.completed",
  "message": "Executing hook",
  "details": {
    "script_path": ".specify/hooks/run-tests.sh",
    "script_args": [],
    "working_directory": "/home/jpoley/ps/jp-spec-kit",
    "environment": {
      "PYTEST_ARGS": "-v --cov=src",
      "FEATURE_NAME": "authentication"
    },
    "timeout": 300,
    "pid": 12345
  },
  "timing": {
    "validation_ms": 2,
    "spawn_ms": 5,
    "execution_ms": 30333,
    "logging_ms": 3
  },
  "output": {
    "stdout": "============================= test session starts ==============================\n...",
    "stderr": ""
  }
}
```

**WARNING**: Debug logs may contain sensitive data (environment values, stdout). Never commit debug logs or share publicly.

## Metrics and Analytics

### Aggregated Metrics

Metrics are aggregated hourly and stored in `.specify/hooks/metrics.json`:

```json
{
  "period": {
    "start": "2025-12-02T15:00:00Z",
    "end": "2025-12-02T16:00:00Z"
  },
  "summary": {
    "total_executions": 47,
    "successful_executions": 45,
    "failed_executions": 2,
    "timeout_executions": 0,
    "success_rate": 0.957
  },
  "by_hook": {
    "run-tests": {
      "executions": 23,
      "successes": 23,
      "failures": 0,
      "avg_duration_ms": 28500,
      "p50_duration_ms": 27000,
      "p95_duration_ms": 35000,
      "p99_duration_ms": 42000
    },
    "update-docs": {
      "executions": 12,
      "successes": 12,
      "failures": 0,
      "avg_duration_ms": 1200,
      "p50_duration_ms": 1100,
      "p95_duration_ms": 1500,
      "p99_duration_ms": 1800
    },
    "notify-slack": {
      "executions": 12,
      "successes": 10,
      "failures": 2,
      "avg_duration_ms": 450,
      "p50_duration_ms": 420,
      "p95_duration_ms": 600,
      "p99_duration_ms": 800
    }
  },
  "by_event_type": {
    "implement.completed": 23,
    "spec.created": 12,
    "task.completed": 12
  },
  "security": {
    "validation_failures": 0,
    "timeouts": 0,
    "dangerous_command_warnings": 1
  }
}
```

### Metric Definitions

| Metric | Description | Unit |
|--------|-------------|------|
| `total_executions` | Total hook executions in period | count |
| `successful_executions` | Hooks that exited with code 0 | count |
| `failed_executions` | Hooks that exited with non-zero code | count |
| `timeout_executions` | Hooks killed due to timeout | count |
| `success_rate` | Percentage of successful executions | 0.0-1.0 |
| `avg_duration_ms` | Mean execution time | milliseconds |
| `p50_duration_ms` | Median execution time | milliseconds |
| `p95_duration_ms` | 95th percentile execution time | milliseconds |
| `p99_duration_ms` | 99th percentile execution time | milliseconds |

## CLI Tools for Observability

### 1. View Audit Log

```bash
# View last 20 audit entries
specify hooks audit

# Live tail (follow mode)
specify hooks audit --tail

# Filter by hook name
specify hooks audit --hook run-tests

# Filter by status
specify hooks audit --status failed

# Filter by date range
specify hooks audit --start-date 2025-12-01 --end-date 2025-12-02

# Export to CSV for analysis
specify hooks audit --format csv --output audit-report.csv
```

**Example Output**:
```
Audit Log: /home/jpoley/ps/jp-spec-kit/.specify/hooks/audit.log
==================================================================

2025-12-02 15:31:15  implement.completed  run-tests       ✓ success  (30.3s)
2025-12-02 15:32:00  spec.created         update-docs     ✓ success  (1.2s)
2025-12-02 15:33:45  task.completed       notify-slack    ✗ failed   (0.5s) exit=1
2025-12-02 15:35:00  validate.completed   long-check      ⏱ timeout  (30.0s)

Summary:
  Total Executions: 4
  Success: 2 (50%)
  Failed: 1 (25%)
  Timeout: 1 (25%)
```

### 2. View Metrics

```bash
# View current metrics
specify hooks metrics

# View metrics for specific hook
specify hooks metrics --hook run-tests

# View metrics for date range
specify hooks metrics --start-date 2025-12-01 --end-date 2025-12-02

# Export to JSON
specify hooks metrics --format json --output metrics.json
```

**Example Output**:
```
Hook Metrics Summary
====================

Period: 2025-12-02 00:00:00 - 2025-12-02 23:59:59

Overall Performance:
  Total Executions: 234
  Success Rate: 95.7% (224/234)
  Avg Duration: 15.3s
  P95 Duration: 45.2s

Top Hooks by Execution:
  1. run-tests        123 execs  avg=28.5s  success=100%
  2. update-docs       56 execs  avg=1.2s   success=100%
  3. notify-slack      34 execs  avg=0.5s   success=94.1%
  4. check-coverage    21 execs  avg=8.3s   success=100%

Slowest Hooks (P95):
  1. run-tests        45.2s
  2. long-validation  35.0s
  3. check-coverage   12.5s

Failures by Hook:
  1. notify-slack     2 failures (network timeout)

Recommendations:
  - Consider increasing timeout for 'run-tests' (approaching 5min limit)
  - Investigate 'notify-slack' failures (network issues?)
```

### 3. Analyze Trends

```bash
# Show execution trends over time
specify hooks trends --days 30

# Compare week-over-week
specify hooks trends --compare

# Generate report
specify hooks trends --format html --output trends-report.html
```

**Example Output**:
```
Hook Execution Trends (Last 30 Days)
=====================================

Daily Executions:
  Week 1 (2025-11-02 - 2025-11-08):  avg=45/day
  Week 2 (2025-11-09 - 2025-11-15):  avg=52/day  (+15.6%)
  Week 3 (2025-11-16 - 2025-11-22):  avg=61/day  (+17.3%)
  Week 4 (2025-11-23 - 2025-11-29):  avg=68/day  (+11.5%)

Success Rate Trends:
  Week 1: 94.2%
  Week 2: 95.8%  (+1.6pp)
  Week 3: 96.1%  (+0.3pp)
  Week 4: 95.7%  (-0.4pp)

Duration Trends (P95):
  Week 1: 42.3s
  Week 2: 43.1s  (+1.9%)
  Week 3: 44.8s  (+3.9%)
  Week 4: 45.2s  (+0.9%)

Insights:
  ✓ Hook adoption increasing (52% growth in 30 days)
  ✓ Success rate consistently above 95%
  ⚠ P95 duration increasing (potential performance degradation)
```

## Log Rotation and Retention

### Rotation Strategy

**Audit Log**:
- Rotate when file size exceeds 10MB
- Keep last 5 rotated files (total 50MB)
- Rotation preserves chronological order
- Rotated files: `audit.log.1`, `audit.log.2`, ..., `audit.log.5`

**Debug Log**:
- Rotate daily or at 50MB (whichever comes first)
- Keep last 3 rotated files (total 150MB)
- Debug logging disabled by default

**Metrics**:
- Roll up hourly to daily after 7 days
- Roll up daily to weekly after 30 days
- Retain weekly metrics for 1 year

### Retention Configuration

```yaml
# .specify/hooks/hooks.yaml
retention:
  audit_log_days: 30        # Delete entries older than 30 days
  debug_log_days: 7         # Delete debug logs older than 7 days
  metrics_rollup_days: 365  # Keep weekly metrics for 1 year
```

### Manual Cleanup

```bash
# Clean up old logs based on retention policy
specify hooks cleanup

# Force clean all logs (requires confirmation)
specify hooks cleanup --force

# Clean specific log type
specify hooks cleanup --audit-only
```

## Performance Considerations

### Logging Performance Budget

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Audit log write (single entry) | <10ms | p99 latency |
| Audit log rotation | <100ms | worst-case |
| Metrics aggregation (hourly) | <500ms | wall time |
| Audit query (last 100 entries) | <200ms | wall time |

### Optimization Strategies

1. **Buffered Writes**: Batch audit log writes to reduce I/O
2. **Async Logging**: Non-blocking writes (Python `asyncio` or threading)
3. **Index Files**: Create index for fast querying (event_type, timestamp)
4. **Compression**: Gzip rotated logs to save disk space

### Implementation Example

```python
import asyncio
import json
from pathlib import Path
from typing import Dict, Any
from queue import Queue
import threading

class AsyncAuditLogger:
    """Non-blocking audit logger using background thread"""

    def __init__(self, audit_log_path: Path, buffer_size: int = 100):
        self.audit_log_path = audit_log_path
        self.queue: Queue = Queue(maxsize=buffer_size)
        self.running = True
        self.thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.thread.start()

    def log(self, entry: Dict[str, Any]) -> None:
        """
        Non-blocking log write (queues entry for background writing)

        Args:
            entry: Audit log entry dictionary
        """
        try:
            self.queue.put_nowait(json.dumps(entry) + '\n')
        except queue.Full:
            # If queue is full, write synchronously (backpressure)
            self._write_sync(entry)

    def _writer_loop(self) -> None:
        """Background thread that writes queued entries to log file"""
        while self.running:
            entries = []

            # Collect batch of entries (up to 100 or 1 second timeout)
            try:
                entries.append(self.queue.get(timeout=1.0))
                while len(entries) < 100:
                    entries.append(self.queue.get_nowait())
            except queue.Empty:
                pass

            # Write batch to disk
            if entries:
                with open(self.audit_log_path, 'a') as f:
                    f.writelines(entries)

    def _write_sync(self, entry: Dict[str, Any]) -> None:
        """Synchronous fallback write"""
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def close(self) -> None:
        """Flush remaining entries and stop background thread"""
        self.running = False
        self.thread.join(timeout=5.0)
```

## Monitoring and Alerting

### Health Checks

```bash
# Check hook system health
specify hooks health

# Output:
# Hook System Health Check
# ========================
#
# Audit Log:
#   ✓ Writable
#   ✓ Size: 8.3 MB (82% of rotation threshold)
#   ✓ Last entry: 2 minutes ago
#
# Metrics:
#   ✓ Metrics file exists
#   ✓ Last update: 5 minutes ago
#
# Configuration:
#   ✓ hooks.yaml valid
#   ✓ 5 hooks configured
#   ✓ All scripts executable
#
# Performance:
#   ✓ Success rate: 95.7% (last 24h)
#   ⚠ P95 duration: 45.2s (approaching limits for 'run-tests')
#
# Recommendations:
#   - Consider increasing timeout for 'run-tests' hook
#   - Audit log will rotate soon (8.3/10 MB used)
```

### Alert Conditions

| Condition | Severity | Action |
|-----------|----------|--------|
| Success rate < 80% | WARNING | Investigate failing hooks |
| Success rate < 50% | CRITICAL | Disable hooks, page on-call |
| P95 duration > 90% of timeout | WARNING | Increase timeout or optimize |
| Audit log write failed | CRITICAL | Check disk space, permissions |
| Security violation detected | HIGH | Review security logs, notify team |

### Integration with Monitoring Systems

**Prometheus Export**:
```bash
# Export metrics in Prometheus format
specify hooks metrics --format prometheus --output /var/lib/prometheus/node-exporter/hooks.prom
```

**Example Prometheus Metrics**:
```
# HELP hooks_executions_total Total number of hook executions
# TYPE hooks_executions_total counter
hooks_executions_total{hook="run-tests",status="success"} 123
hooks_executions_total{hook="run-tests",status="failed"} 0
hooks_executions_total{hook="notify-slack",status="success"} 32
hooks_executions_total{hook="notify-slack",status="failed"} 2

# HELP hooks_duration_seconds Hook execution duration
# TYPE hooks_duration_seconds histogram
hooks_duration_seconds_bucket{hook="run-tests",le="10"} 0
hooks_duration_seconds_bucket{hook="run-tests",le="30"} 95
hooks_duration_seconds_bucket{hook="run-tests",le="60"} 123
hooks_duration_seconds_bucket{hook="run-tests",le="+Inf"} 123
```

## Implementation Checklist

Observability implementation steps:

### Phase 1: Audit Logging (Week 1)
- [ ] Define audit log schema v1.0
- [ ] Implement `AuditLogger` class with JSONL format
- [ ] Implement log rotation at 10MB threshold
- [ ] Add audit logging to hook runner
- [ ] Write unit tests for audit logger

### Phase 2: CLI Tools (Week 2)
- [ ] Implement `specify hooks audit` command
- [ ] Implement `specify hooks audit --tail` live monitoring
- [ ] Implement filtering by hook name, status, date
- [ ] Implement CSV/JSON export formats
- [ ] Write integration tests for CLI tools

### Phase 3: Metrics (Week 3)
- [ ] Implement metrics aggregation (hourly rollup)
- [ ] Implement `specify hooks metrics` command
- [ ] Implement `specify hooks trends` command
- [ ] Add Prometheus export format
- [ ] Write tests for metrics calculation

### Phase 4: Operations (Week 4)
- [ ] Implement log rotation automation
- [ ] Implement `specify hooks cleanup` command
- [ ] Implement `specify hooks health` command
- [ ] Add performance optimizations (async logging)
- [ ] Write operational documentation

## References

- [JSONL Format Specification](http://jsonlines.org/)
- [Prometheus Metric Types](https://prometheus.io/docs/concepts/metric_types/)
- [OpenTelemetry Logging](https://opentelemetry.io/docs/specs/otel/logs/)
- [Security Logging Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
