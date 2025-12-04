# Galway Observability Stack Design

**Status**: Platform Design
**Owner**: Platform Engineer
**Last Updated**: 2025-12-04

## Executive Summary

This document defines the observability architecture for all galway host tasks, implementing Production-First Observability principles with structured logging, metrics, distributed tracing, and event-driven monitoring.

## Observability Pillars

### The Three Pillars

```
┌─────────────────────────────────────────────────────────────────┐
│                      Observability Stack                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Metrics    │  │   Logging    │  │   Tracing    │          │
│  │              │  │              │  │              │          │
│  │ Prometheus   │  │ Structured   │  │ OpenTelemetry│          │
│  │ /            │  │ JSON logs    │  │ W3C Trace    │          │
│  │ OpenMetrics  │  │ +            │  │ Context      │          │
│  │              │  │ Log levels   │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                           │                                     │
│                           ▼                                     │
│              ┌─────────────────────────┐                        │
│              │  Correlation Engine     │                        │
│              │                         │                        │
│              │  • Trace ID linking     │                        │
│              │  • Metric-log join      │                        │
│              │  • Event correlation    │                        │
│              └─────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## Metrics Architecture (task-250, task-253)

### Prometheus Metric Types

**Counter**: Monotonically increasing values
```python
from prometheus_client import Counter

backlog_task_operations = Counter(
    'backlog_task_operations_total',
    'Total task operations by type',
    ['operation', 'status']
)

# Usage
backlog_task_operations.labels(operation='create', status='success').inc()
```

**Gauge**: Current value (can increase or decrease)
```python
from prometheus_client import Gauge

active_tasks_count = Gauge(
    'backlog_active_tasks',
    'Number of tasks in each state',
    ['state', 'priority', 'assignee']
)

# Usage
active_tasks_count.labels(state='In Progress', priority='high', assignee='galway').set(5)
```

**Histogram**: Distribution of values
```python
from prometheus_client import Histogram

task_duration = Histogram(
    'backlog_task_duration_seconds',
    'Time to complete tasks',
    ['state_transition'],
    buckets=[60, 300, 900, 3600, 86400]  # 1m, 5m, 15m, 1h, 1d
)

# Usage
with task_duration.labels(state_transition='To Do -> In Progress').time():
    # Task work happens here
    pass
```

**Summary**: Similar to histogram but calculates quantiles
```python
from prometheus_client import Summary

security_scan_duration = Summary(
    'security_scan_duration_seconds',
    'Duration of security scans',
    ['scan_type', 'tool']
)

# Usage
with security_scan_duration.labels(scan_type='incremental', tool='semgrep').time():
    run_security_scan()
```

### Key Metrics to Collect

**Backlog Metrics** (task-204, task-204.01, task-204.02):
```prometheus
# Task lifecycle
backlog_task_state_transitions_total{from_state, to_state, task_id}
backlog_task_created_total{priority, labels, assignee}
backlog_task_completed_total{priority, labels, assignee, duration_bucket}

# Task health
backlog_task_age_seconds{state, priority}
backlog_stale_tasks{state, days_old_bucket}
backlog_blocked_tasks{reason}

# Acceptance criteria tracking
backlog_acceptance_criteria_total{task_id}
backlog_acceptance_criteria_checked{task_id}
backlog_acceptance_criteria_completion_rate{task_id}
```

**Security Scanning Metrics** (task-248, task-250):
```prometheus
# Scan execution
security_scan_total{scan_type, tool, status}
security_scan_duration_seconds{scan_type, tool}

# Findings
security_findings_total{severity, category, tool}
security_findings_resolved_total{severity, resolution_type}
security_false_positives_total{severity, rule_id}

# Coverage
security_scan_coverage_percent{tool}
security_scan_files_analyzed{tool}
```

**CI/CD Metrics** (task-248, task-253):
```prometheus
# Pipeline execution
ci_pipeline_duration_seconds{job, status}
ci_pipeline_queue_time_seconds{job}
ci_pipeline_runs_total{job, status}

# Test metrics
ci_test_duration_seconds{suite, status}
ci_test_count{suite, result}
ci_test_flakiness_rate{suite}

# DORA metrics (task-253)
deployment_frequency_per_day
lead_time_for_changes_seconds
change_failure_rate_percent
time_to_restore_seconds
```

**Developer Workflow Metrics** (task-197, task-196):
```prometheus
# Command usage
specify_command_executions_total{command, status}
specify_command_duration_seconds{command}
specify_workflow_phase_duration_seconds{phase}

# Developer productivity
developer_commits_per_day{assignee}
developer_pr_cycle_time_seconds{assignee}
developer_code_review_turnaround_seconds{reviewer}
```

### Metrics Exposition

**HTTP Endpoint**:
```python
from prometheus_client import start_http_server, REGISTRY

# Start metrics server on port 9090
start_http_server(9090)
```

**Metrics Endpoint**: `http://localhost:9090/metrics`

**Prometheus Scrape Config**:
```yaml
scrape_configs:
  - job_name: 'jp-spec-kit'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: /metrics
```

## Structured Logging Architecture

### Log Format Standard

**JSON Structure**:
```json
{
  "timestamp": "2025-12-04T10:15:30.123456Z",
  "level": "INFO",
  "logger": "specify_cli.backlog",
  "message": "Task created successfully",
  "context": {
    "task_id": "task-302",
    "operation": "create",
    "user": "jpoley",
    "host": "galway"
  },
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "duration_ms": 45,
  "status": "success"
}
```

### Log Levels

| Level | Purpose | Example Use Case |
|-------|---------|------------------|
| **DEBUG** | Detailed diagnostic info | Function entry/exit, variable values |
| **INFO** | General informational messages | Task created, workflow started |
| **WARNING** | Potentially problematic situations | Deprecated feature used, retry attempt |
| **ERROR** | Error events that allow continued execution | Task update failed, file not found |
| **CRITICAL** | Severe errors causing abort | Database connection lost, config corrupted |

### Python Structured Logging

**Configuration** (`src/specify_cli/logging_config.py`):
```python
import logging
import json
import sys
from datetime import datetime
from typing import Any

class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add trace context if available
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id
        if hasattr(record, 'span_id'):
            log_data['span_id'] = record.span_id

        # Add custom context
        if hasattr(record, 'context'):
            log_data['context'] = record.context

        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def configure_logging(level: str = "INFO"):
    """Configure structured logging for entire application."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))
```

**Usage in Application Code**:
```python
import logging
from specify_cli.logging_config import configure_logging

configure_logging(level="INFO")
logger = logging.getLogger(__name__)

# Basic logging
logger.info("Task created successfully")

# With context
logger.info(
    "Task state transition",
    extra={
        "context": {
            "task_id": "task-302",
            "from_state": "To Do",
            "to_state": "In Progress",
            "assignee": "galway"
        }
    }
)

# Error logging with exception
try:
    task = load_task("task-999")
except TaskNotFoundError as e:
    logger.error(
        "Failed to load task",
        exc_info=True,
        extra={"context": {"task_id": "task-999"}}
    )
```

### Bash Script Logging

**Structured Logging Functions** (`scripts/bash/logging.sh`):
```bash
#!/bin/bash

# Structured logging functions
log_json() {
    local level=$1
    local message=$2
    local context=${3:-"{}"}

    cat <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")",
  "level": "$level",
  "logger": "bash.${BASH_SOURCE[1]##*/}",
  "message": "$message",
  "context": $context,
  "pid": $$,
  "host": "$(hostname)"
}
EOF
}

log_info() {
    log_json "INFO" "$1" "${2:-{}}"
}

log_error() {
    log_json "ERROR" "$1" "${2:-{}}" >&2
}

log_warning() {
    log_json "WARNING" "$1" "${2:-{}}"
}

log_debug() {
    if [ "${DEBUG:-false}" = "true" ]; then
        log_json "DEBUG" "$1" "${2:-{}}"
    fi
}

# Usage example
log_info "Starting archive process" '{"dry_run": false, "filter": "Done"}'
log_error "Archive failed" '{"reason": "permission denied", "file": "/tmp/archive.tar.gz"}'
```

### Log Aggregation Strategy

**Local Development**: Stdout/stderr with pretty-printing
```bash
uv run specify task list | jq -r '.message'
```

**CI/CD Pipeline**: GitHub Actions log aggregation (automatic)

**Production (Future)**: Centralized logging with Loki
```yaml
# Promtail scrape config
scrape_configs:
  - job_name: jp-spec-kit
    static_configs:
      - targets:
          - localhost
        labels:
          job: jp-spec-kit
          __path__: /var/log/specify/*.log
    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
      - labels:
          level:
          logger:
```

## Distributed Tracing Architecture (task-136)

### OpenTelemetry Integration

**Trace Context Propagation (W3C Trace Context)**:
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
            │  └─────────── trace_id ───────────┘  └── span_id ──┘  │
            │                                                        │
         version                                                 flags
```

**Python OpenTelemetry Setup** (`src/specify_cli/tracing.py`):
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
import os

def configure_tracing(service_name: str = "specify-cli"):
    """Configure OpenTelemetry tracing."""
    # Create tracer provider
    provider = TracerProvider(
        resource=Resource.create({
            "service.name": service_name,
            "service.version": "0.0.250",
            "deployment.environment": os.getenv("ENV", "development"),
            "host.name": os.getenv("HOSTNAME", "unknown")
        })
    )

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        headers={"Authorization": f"Bearer {os.getenv('OTEL_API_KEY')}"}
    )

    # Add batch span processor
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Instrument logging to include trace context
    LoggingInstrumentor().instrument()

    return trace.get_tracer(__name__)

# Usage in application code
tracer = configure_tracing()

@tracer.start_as_current_span("task_create")
def create_task(title: str, description: str):
    span = trace.get_current_span()
    span.set_attribute("task.title", title)
    span.set_attribute("task.priority", "high")

    with tracer.start_as_current_span("validate_input"):
        validate_task_input(title, description)

    with tracer.start_as_current_span("write_to_disk"):
        write_task_file(task_data)

    span.add_event("task_created", {"task_id": "task-302"})
    return task_id
```

**Bash Tracing with curl**:
```bash
#!/bin/bash

# Generate trace and span IDs
TRACE_ID=$(openssl rand -hex 16)
SPAN_ID=$(openssl rand -hex 8)

# Send span to OTLP endpoint
send_span() {
    local span_name=$1
    local start_time=$2
    local end_time=$3

    curl -X POST http://localhost:4318/v1/traces \
      -H "Content-Type: application/json" \
      -d @- <<EOF
{
  "resourceSpans": [{
    "resource": {
      "attributes": [{
        "key": "service.name",
        "value": {"stringValue": "bash-script"}
      }]
    },
    "scopeSpans": [{
      "spans": [{
        "traceId": "$TRACE_ID",
        "spanId": "$SPAN_ID",
        "name": "$span_name",
        "kind": 1,
        "startTimeUnixNano": $start_time,
        "endTimeUnixNano": $end_time
      }]
    }]
  }]
}
EOF
}

# Usage
START=$(date +%s%N)
archive_tasks
END=$(date +%s%N)
send_span "archive_tasks" $START $END
```

### Trace-Log-Metric Correlation

**Correlation Strategy**:
1. **Trace ID injection**: Add trace_id to all log entries during active span
2. **Span ID in metrics**: Use span_id as exemplar in Prometheus metrics
3. **Unified querying**: Query logs by trace_id, then jump to metrics

**Example Correlation Query** (Grafana):
```promql
# Find slow task operations
rate(backlog_task_duration_seconds_sum[5m])
  / rate(backlog_task_duration_seconds_count[5m])
  > 60  # Operations taking > 60 seconds

# Jump to logs for specific trace
{logger="specify_cli.backlog"} | json | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"
```

## Event-Driven Monitoring (task-204, task-204.01, task-204.02)

### Event Model Schema (task-198)

**Event Base Schema**:
```json
{
  "event_id": "evt_01HQZXY9ABCDEFGHIJK",
  "event_type": "backlog.task.state_changed",
  "event_version": "1.0",
  "timestamp": "2025-12-04T10:15:30.123456Z",
  "source": "specify-cli",
  "source_version": "0.0.250",
  "correlation_id": "corr_01HQZXY9XYZ",
  "trace_context": {
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "span_id": "00f067aa0ba902b7"
  },
  "actor": {
    "type": "user",
    "id": "jpoley",
    "host": "galway"
  },
  "data": {
    "task_id": "task-302",
    "from_state": "To Do",
    "to_state": "In Progress",
    "assignee": "galway",
    "labels": ["backend", "high-priority"]
  },
  "metadata": {
    "git_branch": "feature/task-302",
    "git_commit": "abc123def456",
    "working_directory": "/home/jpoley/ps/jp-spec-kit"
  }
}
```

**Event Types**:
```
backlog.task.created
backlog.task.updated
backlog.task.state_changed
backlog.task.assigned
backlog.task.completed
backlog.task.archived
backlog.task.ac_checked
backlog.document.created
backlog.document.updated
security.scan.started
security.scan.completed
security.finding.detected
ci.pipeline.started
ci.pipeline.completed
ci.test.failed
```

### Event Emission Architecture

**Python Event Emitter** (`src/specify_cli/events.py`):
```python
import json
import logging
from datetime import datetime
from typing import Any, Dict
from ulid import ULID
from opentelemetry import trace

logger = logging.getLogger(__name__)

class EventEmitter:
    def __init__(self, source: str = "specify-cli"):
        self.source = source
        self.tracer = trace.get_tracer(__name__)

    def emit(self, event_type: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Emit structured event with trace context."""
        span = trace.get_current_span()
        span_context = span.get_span_context()

        event = {
            "event_id": f"evt_{ULID()}",
            "event_type": event_type,
            "event_version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": self.source,
            "source_version": "0.0.250",
            "trace_context": {
                "trace_id": format(span_context.trace_id, '032x'),
                "span_id": format(span_context.span_id, '016x')
            },
            "actor": {
                "type": "user",
                "id": os.getenv("USER"),
                "host": os.getenv("HOSTNAME")
            },
            "data": data,
            "metadata": metadata or {}
        }

        # Log event as structured log entry
        logger.info(
            f"Event emitted: {event_type}",
            extra={
                "context": {"event": event}
            }
        )

        # Send to event bus (if configured)
        self._send_to_event_bus(event)

        return event["event_id"]

    def _send_to_event_bus(self, event: Dict[str, Any]):
        """Send event to configured event bus (future enhancement)."""
        # TODO: Implement event bus integration (Kafka, NATS, etc.)
        pass

# Usage
emitter = EventEmitter()

emitter.emit(
    "backlog.task.state_changed",
    data={
        "task_id": "task-302",
        "from_state": "To Do",
        "to_state": "In Progress"
    },
    metadata={
        "git_branch": get_current_branch(),
        "git_commit": get_current_commit()
    }
)
```

### Git Hook Event Emission (task-204.01)

**Post-commit Hook** (`.git/hooks/post-commit`):
```bash
#!/bin/bash

# Emit event after successful commit
COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# Check if backlog files changed
if echo "$CHANGED_FILES" | grep -q "^backlog/tasks/"; then
    EVENT_DATA=$(cat <<EOF
{
  "event_type": "backlog.task.updated_via_commit",
  "data": {
    "commit_sha": "$COMMIT_SHA",
    "commit_message": "$COMMIT_MSG",
    "changed_files": $(echo "$CHANGED_FILES" | jq -R -s -c 'split("\n")')
  }
}
EOF
)

    # Send event (example: append to event log)
    echo "$EVENT_DATA" >> ~/.specify/events.log

    # Or send to remote endpoint
    curl -X POST http://localhost:8080/events \
      -H "Content-Type: application/json" \
      -d "$EVENT_DATA"
fi
```

### Backlog CLI Event Wrapper (task-204.02)

**Wrapper Script** (`scripts/bash/backlog-wrapper.sh`):
```bash
#!/bin/bash

# Wrap backlog CLI to emit events
BACKLOG_BIN=$(which backlog)

emit_event() {
    local event_type=$1
    local event_data=$2

    echo "{
      \"event_type\": \"$event_type\",
      \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")\",
      \"data\": $event_data
    }" >> ~/.specify/events.log
}

# Parse backlog command
COMMAND=$1
shift

case $COMMAND in
    task)
        SUBCOMMAND=$1
        shift

        # Execute original command
        OUTPUT=$($BACKLOG_BIN task $SUBCOMMAND "$@" 2>&1)
        EXIT_CODE=$?

        # Emit event based on subcommand
        case $SUBCOMMAND in
            create)
                if [ $EXIT_CODE -eq 0 ]; then
                    TASK_ID=$(echo "$OUTPUT" | grep -oP 'task-\d+')
                    emit_event "backlog.task.created" "{\"task_id\": \"$TASK_ID\"}"
                fi
                ;;
            edit)
                if [ $EXIT_CODE -eq 0 ]; then
                    TASK_ID=$1
                    emit_event "backlog.task.updated" "{\"task_id\": \"$TASK_ID\"}"
                fi
                ;;
        esac

        echo "$OUTPUT"
        exit $EXIT_CODE
        ;;
    *)
        $BACKLOG_BIN "$COMMAND" "$@"
        ;;
esac
```

## Dashboard and Alerting

### Grafana Dashboard Specifications

**Dashboard 1: Developer Productivity**

**Panels**:
1. **Task Throughput**: Rate of tasks completed per day
2. **Lead Time Distribution**: Histogram of time from To Do → Done
3. **Work In Progress**: Current count of tasks In Progress by assignee
4. **Blocked Tasks**: Count and age of blocked tasks
5. **Sprint Burndown**: Remaining work vs. time (if using sprints)

**PromQL Queries**:
```promql
# Task completion rate (per day)
rate(backlog_task_completed_total[1d])

# Average lead time (last 7 days)
avg_over_time(backlog_task_duration_seconds[7d])

# Current WIP
sum(backlog_active_tasks{state="In Progress"}) by (assignee)

# Blocked tasks count
count(backlog_blocked_tasks) by (reason)
```

**Dashboard 2: CI/CD Health**

**Panels**:
1. **Pipeline Success Rate**: Percentage of successful CI runs
2. **Pipeline Duration P95**: 95th percentile duration by job
3. **Test Flakiness**: Tests that intermittently fail
4. **Security Findings Trend**: Security vulnerabilities over time
5. **DORA Metrics**: Four key metrics in single panel

**PromQL Queries**:
```promql
# Success rate (last 24h)
sum(rate(ci_pipeline_runs_total{status="success"}[24h]))
  / sum(rate(ci_pipeline_runs_total[24h]))

# P95 duration
histogram_quantile(0.95, rate(ci_pipeline_duration_seconds_bucket[1h]))

# Flaky tests
rate(ci_test_count{result="flaky"}[1d])

# Security findings by severity
sum(security_findings_total) by (severity)
```

**Dashboard 3: Security Observability** (task-250)

**Panels**:
1. **Scan Coverage**: Percentage of codebase scanned
2. **Finding Resolution Time**: Time to fix vulnerabilities
3. **False Positive Rate**: Dismissed findings / total findings
4. **Tool Effectiveness**: Findings per tool per scan
5. **OWASP Top 10 Distribution**: Vulnerabilities categorized by OWASP

### Alert Definitions

**Critical Alerts** (PagerDuty/Slack):
```yaml
groups:
  - name: critical_alerts
    interval: 1m
    rules:
      - alert: HighSecurityFindings
        expr: sum(security_findings_total{severity="critical"}) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Critical security vulnerability detected"
          description: "{{ $value }} critical findings detected in recent scan"

      - alert: CIPipelineFailureRate
        expr: |
          sum(rate(ci_pipeline_runs_total{status="failure"}[10m]))
            / sum(rate(ci_pipeline_runs_total[10m])) > 0.5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CI pipeline failure rate > 50%"
          description: "More than half of CI runs failing in last 10 minutes"

      - alert: DeploymentBlocked
        expr: sum(backlog_blocked_tasks{labels=~".*deploy.*"}) > 0
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "Deployment blocked for > 1 hour"
          description: "{{ $value }} deployment tasks blocked"
```

**Warning Alerts** (Slack only):
```yaml
groups:
  - name: warning_alerts
    interval: 5m
    rules:
      - alert: StaleTasksAccumulating
        expr: sum(backlog_stale_tasks{days_old_bucket="7+"}) > 10
        for: 1d
        labels:
          severity: warning
        annotations:
          summary: "More than 10 stale tasks (>7 days old)"
          description: "Run archive-tasks.sh to clean up"

      - alert: LowTestCoverage
        expr: avg(ci_test_coverage_percent) < 80
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Test coverage below 80%"
          description: "Current coverage: {{ $value }}%"

      - alert: SlowCIPipeline
        expr: |
          histogram_quantile(0.95, rate(ci_pipeline_duration_seconds_bucket[1h])) > 600
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "CI pipeline P95 duration > 10 minutes"
          description: "Consider optimizing pipeline or investigating bottlenecks"
```

## Observability as Code

**Configuration Repository Structure**:
```
observability/
├── prometheus/
│   ├── prometheus.yml           # Scrape configs
│   ├── alerts/
│   │   ├── critical.yml
│   │   └── warning.yml
│   └── recording_rules.yml      # Pre-computed queries
├── grafana/
│   ├── dashboards/
│   │   ├── developer-productivity.json
│   │   ├── cicd-health.json
│   │   └── security-observability.json
│   └── datasources.yml
├── loki/
│   └── promtail.yml
└── otel/
    └── otel-collector-config.yml
```

**Deployment**: All configs version-controlled and deployed via GitOps

## Success Metrics

**Observability Coverage**:
- **Metrics Coverage**: 100% of critical paths instrumented
- **Log Coverage**: All services emit structured JSON logs
- **Trace Coverage**: 90% of operations have distributed traces

**Mean Time to Detect (MTTD)**: < 5 minutes for critical issues
**Mean Time to Investigate (MTTI)**: < 15 minutes to identify root cause
**Mean Time to Resolve (MTTR)**: < 30 minutes for critical issues

**Developer Experience**:
- Developers can find relevant logs in < 30 seconds
- Correlation between logs/metrics/traces is automatic
- Dashboards answer "what happened" without manual log grepping

## Future Enhancements

### Phase 2: Advanced Observability

1. **Anomaly Detection**: ML-based detection of unusual patterns
2. **Automatic Root Cause Analysis**: AI-assisted RCA based on traces
3. **Predictive Alerting**: Alert before issues occur (capacity, performance)
4. **Cost Observability**: Track infrastructure costs per feature

### Phase 3: Chaos Engineering Observability

1. **Failure Injection Tracing**: Track chaos experiments with traces
2. **Resilience Metrics**: Time to recover from injected failures
3. **Blast Radius Measurement**: Impact scope of failures

## Related Tasks

| Task ID | Title | Integration Point |
|---------|-------|-------------------|
| task-250 | Security Scanning Observability | Metrics + logging + tracing |
| task-253 | DORA Metrics | Deployment frequency, lead time, CFR, MTTR |
| task-136 | claude-trace Integration | Distributed tracing |
| task-204 | Event Emission Integration | Event-driven monitoring |
| task-204.01 | Git Hook Events | Event emission |
| task-204.02 | CLI Wrapper Events | Event emission |
| task-197 | Custom Statusline | Real-time metrics display |

## Appendix: OpenTelemetry Environment Variables

```bash
# Exporter configuration
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer $OTEL_API_KEY"

# Service configuration
export OTEL_SERVICE_NAME="specify-cli"
export OTEL_SERVICE_VERSION="0.0.250"
export OTEL_DEPLOYMENT_ENVIRONMENT="production"

# Trace sampling
export OTEL_TRACES_SAMPLER="parentbased_traceidratio"
export OTEL_TRACES_SAMPLER_ARG="1.0"  # 100% sampling

# Resource attributes
export OTEL_RESOURCE_ATTRIBUTES="service.name=specify-cli,host.name=galway"
```
