---
description: Scale infrastructure and applications to handle load.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command provides guidance for scaling infrastructure and applications to handle increased load, both vertically and horizontally.

### Scaling Strategies

**Horizontal Scaling (Scale Out)**:
- Add more instances/pods
- Better fault tolerance
- Handles larger loads
- Requires load balancer
- More cost-effective at scale

**Vertical Scaling (Scale Up)**:
- Increase CPU/memory per instance
- Simpler to implement
- Limited by hardware
- Requires restart (downtime)
- Cost increases linearly

### Kubernetes Horizontal Pod Autoscaling

**HPA Configuration**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
        - type: Pods
          value: 4
          periodSeconds: 30
      selectPolicy: Max
```

**Manual Scaling**:
```bash
# Scale deployment to specific replica count
kubectl scale deployment app --replicas=10 -n production

# Verify scaling
kubectl get pods -n production -l app=app

# Check HPA status
kubectl get hpa -n production
kubectl describe hpa app-hpa -n production
```

### Database Scaling

**Read Replicas**:
```yaml
# PostgreSQL read replica setup
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
spec:
  instances: 3  # 1 primary + 2 read replicas
  primaryUpdateStrategy: unsupervised
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "256MB"
  storage:
    size: 100Gi
```

**Connection Pooling**:
```python
# PgBouncer configuration
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@pgbouncer:6432/dbname",
    poolclass=QueuePool,
    pool_size=20,  # Number of persistent connections
    max_overflow=10,  # Additional connections when pool exhausted
    pool_timeout=30,  # Timeout waiting for connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connection health before use
)
```

**Query Optimization**:
```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;

-- Identify slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Caching Strategies

**Redis Cache**:
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def cache_result(ttl=3600):
    """Decorator to cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator

@cache_result(ttl=600)
def get_user_profile(user_id):
    """Fetch user profile with 10-minute cache."""
    return db.query(User).filter(User.id == user_id).first()
```

**CDN for Static Assets**:
```nginx
# Nginx CDN configuration
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header X-Cache-Status $upstream_cache_status;
}
```

### Load Balancing

**Nginx Load Balancer**:
```nginx
upstream app_backend {
    least_conn;  # Route to server with fewest connections

    server app-1:8000 weight=3;
    server app-2:8000 weight=3;
    server app-3:8000 weight=1 backup;  # Backup server

    # Health checks
    check interval=3000 rise=2 fall=3 timeout=1000;
}

server {
    listen 80;

    location / {
        proxy_pass http://app_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Connection settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 30s;

        # Retry failed requests
        proxy_next_upstream error timeout http_500 http_502 http_503;
    }
}
```

### Async Processing

**Celery Task Queue**:
```python
from celery import Celery

app = Celery('tasks', broker='redis://redis:6379/0')

@app.task(bind=True, max_retries=3)
def process_large_file(self, file_id):
    """Process file asynchronously."""
    try:
        file = get_file(file_id)
        result = heavy_processing(file)
        save_result(result)
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

# In API handler
@app.post("/upload")
def upload_file(file: UploadFile):
    file_id = save_file(file)
    # Process asynchronously instead of blocking
    process_large_file.delay(file_id)
    return {"status": "processing", "file_id": file_id}
```

### Auto-Scaling Policies

**AWS Auto Scaling Group**:
```yaml
# CloudFormation template
AutoScalingGroup:
  Type: AWS::AutoScaling::AutoScalingGroup
  Properties:
    MinSize: 3
    MaxSize: 20
    DesiredCapacity: 5
    HealthCheckType: ELB
    HealthCheckGracePeriod: 300
    LaunchTemplate:
      LaunchTemplateId: !Ref AppLaunchTemplate
      Version: !GetAtt AppLaunchTemplate.LatestVersionNumber
    TargetGroupARNs:
      - !Ref AppTargetGroup
    MetricsCollection:
      - Granularity: 1Minute

TargetTrackingScalingPolicy:
  Type: AWS::AutoScaling::ScalingPolicy
  Properties:
    AutoScalingGroupName: !Ref AutoScalingGroup
    PolicyType: TargetTrackingScaling
    TargetTrackingConfiguration:
      PredefinedMetricSpecification:
        PredefinedMetricType: ASGAverageCPUUtilization
      TargetValue: 70.0

RequestCountScalingPolicy:
  Type: AWS::AutoScaling::ScalingPolicy
  Properties:
    AutoScalingGroupName: !Ref AutoScalingGroup
    PolicyType: TargetTrackingScaling
    TargetTrackingConfiguration:
      PredefinedMetricSpecification:
        PredefinedMetricType: ALBRequestCountPerTarget
        ResourceLabel: !GetAtt AppTargetGroup.TargetGroupFullName
      TargetValue: 1000.0
```

### Capacity Planning

**Calculating Required Capacity**:
```python
# Capacity planning calculation
current_rps = 1000  # Current requests per second
growth_rate = 0.20  # 20% monthly growth
months_ahead = 6

# Projected RPS
projected_rps = current_rps * (1 + growth_rate) ** months_ahead
print(f"Projected RPS in {months_ahead} months: {projected_rps:.0f}")

# Current capacity
current_instances = 10
rps_per_instance = 150

# Required instances
required_instances = math.ceil(projected_rps / rps_per_instance)
buffer_instances = math.ceil(required_instances * 0.20)  # 20% buffer
total_instances = required_instances + buffer_instances

print(f"Required instances: {total_instances}")
print(f"Need to add: {total_instances - current_instances} instances")
```

### Scaling Checklist

Before scaling:
- [ ] Identify bottleneck (CPU, memory, disk, network, database)
- [ ] Review metrics and trends
- [ ] Calculate capacity requirements
- [ ] Test scaling in staging
- [ ] Verify monitoring alerts
- [ ] Check cost implications

During scaling:
- [ ] Scale gradually (not all at once)
- [ ] Monitor key metrics
- [ ] Watch for errors or degradation
- [ ] Verify load distribution
- [ ] Check downstream dependencies

After scaling:
- [ ] Verify performance improvement
- [ ] Update capacity plan
- [ ] Document changes
- [ ] Optimize if needed
- [ ] Set up auto-scaling if applicable

## Related Commands

- `/ops:deploy` - Deploy applications
- `/ops:monitor` - Monitoring and observability
- `/ops:respond` - Incident response
- `/arch:design` - Architecture planning
