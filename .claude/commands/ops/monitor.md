---
description: Set up monitoring, alerting, and observability for deployed systems.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command provides guidance for setting up comprehensive monitoring, alerting, and observability for production systems.

### Monitoring Overview

**Three Pillars of Observability**:
1. **Metrics**: Numerical measurements over time
2. **Logs**: Discrete event records
3. **Traces**: Request flow through distributed systems

### Metrics Monitoring

**Key Metrics (The Four Golden Signals)**:

1. **Latency**: How long requests take
2. **Traffic**: How many requests
3. **Errors**: How many requests fail
4. **Saturation**: How full your resources are

**Implementation**:
```python
# Prometheus metrics example
from prometheus_client import Counter, Histogram, Gauge

# Counter: Monotonically increasing value
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Histogram: Distribution of values
request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Gauge: Value that can go up or down
active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# Usage in code
@app.route('/api/users')
def get_users():
    http_requests_total.labels('GET', '/api/users', '200').inc()
    with request_duration_seconds.labels('GET', '/api/users').time():
        # Your handler code
        return users
```

### Logging Strategy

**Log Levels**:
- **ERROR**: Something failed, requires attention
- **WARN**: Something unexpected, may need attention
- **INFO**: Normal operational events
- **DEBUG**: Detailed diagnostic information

**Structured Logging**:
```python
import structlog

log = structlog.get_logger()

# Structured log entry
log.info(
    "user_created",
    user_id=user.id,
    email=user.email,
    registration_source="web",
    duration_ms=response_time
)

# Avoid unstructured logs
# log.info(f"User {user.id} created with email {user.email}")  # BAD
```

**What to Log**:
- Request/response metadata (method, path, status, duration)
- Authentication events (login, logout, failed attempts)
- Business events (order placed, payment processed)
- Errors with context (error type, stack trace, request context)
- Performance metrics (query time, external API calls)

**What NOT to Log**:
- Passwords or credentials
- Credit card numbers or PII
- Session tokens or API keys
- Full request/response bodies with sensitive data

### Distributed Tracing

**OpenTelemetry Example**:
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Instrument code
@app.route('/api/orders/<order_id>')
def get_order(order_id):
    with tracer.start_as_current_span("get_order") as span:
        span.set_attribute("order_id", order_id)

        with tracer.start_as_current_span("fetch_from_db"):
            order = db.get_order(order_id)

        with tracer.start_as_current_span("enrich_order"):
            order = enrich_order_data(order)

        return order
```

### Alerting Rules

**SLO-Based Alerting**:
```yaml
# Prometheus alert rules
groups:
  - name: slo_alerts
    interval: 30s
    rules:
      # Error rate SLO
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (SLO: 99%)"

      # Latency SLO
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(request_duration_seconds_bucket[5m])
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency"
          description: "P95 latency is {{ $value }}s (SLO: 500ms)"

      # Saturation
      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
          > 0.90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"
```

### Dashboard Creation

**Grafana Dashboard JSON**:
```json
{
  "dashboard": {
    "title": "Service Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (endpoint)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "P95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m]))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Connections",
        "targets": [
          {
            "expr": "active_connections"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

### Health Checks

**Liveness and Readiness**:
```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/health/live")
async def liveness():
    """Liveness check - is the app running?"""
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness():
    """Readiness check - can the app serve traffic?"""
    # Check dependencies
    try:
        db.ping()
        cache.ping()
        return {"status": "ok", "checks": {
            "database": "ok",
            "cache": "ok"
        }}
    except Exception as e:
        return Response(
            content={"status": "error", "error": str(e)},
            status_code=503
        )
```

### Monitoring Stack Setup

**Docker Compose**:
```yaml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki
    command: -config.file=/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "16686:16686"  # UI
      - "6831:6831/udp"  # Agent

volumes:
  prometheus-data:
  grafana-data:
  loki-data:
```

### Monitoring Checklist

Before production deployment:
- [ ] Metrics exported (RED/USE metrics minimum)
- [ ] Logs structured and centralized
- [ ] Distributed tracing enabled
- [ ] Health check endpoints implemented
- [ ] Alerts configured for SLO violations
- [ ] Dashboards created for key metrics
- [ ] On-call rotation defined
- [ ] Runbooks created for common issues
- [ ] Monitoring stack deployed and tested
- [ ] Alert notification channels configured (Slack, PagerDuty, etc.)

## Related Commands

- `/ops:deploy` - Deploy applications
- `/ops:respond` - Incident response
- `/ops:scale` - Scaling operations
- `/sec:scan` - Security monitoring
