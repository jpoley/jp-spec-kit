# React Frontend - Go Backend Stack

## Overview

A high-performance stack combining React (TypeScript) for the frontend with Go for the backend, ideal for applications requiring scalability, performance, and concurrent request handling.

## Use Cases

- **Ideal For:**
  - High-traffic web applications (>10k concurrent users)
  - Real-time applications and WebSocket servers
  - API-heavy applications with complex business logic
  - Microservices architecture
  - Cloud-native applications and Kubernetes deployments
  - Systems requiring high performance and low latency
  - Applications with concurrent data processing
  - CLI tools with web interfaces

- **Not Ideal For:**
  - Simple CRUD applications with low traffic
  - Projects requiring rapid prototyping with small teams
  - Teams without Go expertise
  - Applications requiring extensive JavaScript code sharing

## Tech Stack Components

### Frontend
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite or Next.js (static export)
- **State Management:** Zustand, Jotai, or React Query
- **Styling:** Tailwind CSS or CSS Modules
- **Routing:** React Router
- **Form Handling:** React Hook Form + Zod
- **HTTP Client:** Axios or Fetch API
- **Testing:** Vitest, React Testing Library, Playwright

### Backend
- **Language:** Go 1.21+
- **Web Framework:**
  - Gin (fastest, most popular)
  - Echo (feature-rich, middleware-friendly)
  - Fiber (Express-like API)
  - Chi (lightweight, idiomatic)
  - Standard library net/http (for simple APIs)
- **Database:**
  - **SQL:** PostgreSQL with pgx or GORM
  - **NoSQL:** MongoDB with mongo-go-driver
  - **Cache:** Redis with go-redis
- **Validation:** validator/v10 or ozzo-validation
- **Authentication:** golang-jwt/jwt
- **Configuration:** viper or envconfig
- **Logging:** zap or zerolog
- **Testing:** Standard testing package, testify
- **API Documentation:** Swagger/OpenAPI with swaggo

### Infrastructure
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes
- **API Gateway:** Traefik, NGINX, or Envoy
- **Message Queue:** NATS, RabbitMQ, or Kafka (go-kafka)
- **Monitoring:** Prometheus + Grafana
- **Tracing:** OpenTelemetry or Jaeger

## Architecture Patterns

### Project Structure

```
project/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   └── api-client.ts   # Generated from OpenAPI
│   │   ├── types/              # Frontend types
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                    # Go application
│   ├── cmd/
│   │   └── api/
│   │       └── main.go         # Application entry point
│   │
│   ├── internal/               # Private application code
│   │   ├── api/                # HTTP handlers and routes
│   │   │   ├── handlers/       # Request handlers
│   │   │   ├── middleware/     # HTTP middleware
│   │   │   └── routes.go       # Route definitions
│   │   │
│   │   ├── domain/             # Business logic and entities
│   │   │   ├── user/
│   │   │   │   ├── model.go    # Domain models
│   │   │   │   ├── service.go  # Business logic
│   │   │   │   └── repository.go # Data access interface
│   │   │   └── errors.go       # Domain errors
│   │   │
│   │   ├── repository/         # Data access implementations
│   │   │   ├── postgres/
│   │   │   │   └── user.go
│   │   │   └── redis/
│   │   │       └── cache.go
│   │   │
│   │   └── config/             # Configuration
│   │       └── config.go
│   │
│   ├── pkg/                    # Public libraries (reusable)
│   │   ├── logger/
│   │   ├── validator/
│   │   └── response/           # Standard API responses
│   │
│   ├── migrations/             # Database migrations
│   │   ├── 001_initial.up.sql
│   │   └── 001_initial.down.sql
│   │
│   ├── api/                    # API definitions
│   │   ├── openapi.yaml        # OpenAPI specification
│   │   └── docs/               # Generated Swagger docs
│   │
│   ├── scripts/                # Build and deployment scripts
│   ├── tests/                  # Integration tests
│   ├── go.mod
│   ├── go.sum
│   ├── Makefile
│   └── Dockerfile
│
├── docker-compose.yml          # Local development setup
├── .github/
│   └── workflows/              # CI/CD pipelines
└── README.md
```

### Key Architectural Decisions

1. **API-First Design**
   - OpenAPI specification as source of truth
   - Generate TypeScript client from OpenAPI spec
   - Versioned API endpoints (/api/v1)
   - Consistent error responses

2. **Hexagonal Architecture (Ports & Adapters)**
   - Domain logic independent of infrastructure
   - Repository pattern for data access
   - Service layer for business logic
   - Clear separation of concerns

3. **Concurrent Request Handling**
   - Goroutines for async operations
   - Context for request lifecycle management
   - Graceful shutdown handling
   - Connection pooling for database

4. **Type Safety Bridge**
   - OpenAPI as contract between frontend and backend
   - JSON schema validation
   - Code generation for API client

## Coding Standards

### Go Backend Standards
**Reference:** `.languages/go/principles/`

Key principles:
- Idiomatic Go code following Go proverbs
- Error handling with explicit checks
- Interfaces for abstraction
- Context propagation for cancellation
- Table-driven tests

```go
// Example: User handler
package handlers

import (
    "context"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/user/project/internal/domain/user"
    "go.uber.org/zap"
)

type UserHandler struct {
    userService user.Service
    logger      *zap.Logger
}

func NewUserHandler(service user.Service, logger *zap.Logger) *UserHandler {
    return &UserHandler{
        userService: service,
        logger:      logger,
    }
}

// CreateUser handles POST /api/v1/users
// @Summary Create a new user
// @Description Create a new user with the provided data
// @Tags users
// @Accept json
// @Produce json
// @Param user body CreateUserRequest true "User data"
// @Success 201 {object} UserResponse
// @Failure 400 {object} ErrorResponse
// @Router /api/v1/users [post]
func (h *UserHandler) CreateUser(c *gin.Context) {
    ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Second)
    defer cancel()

    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        h.logger.Error("invalid request", zap.Error(err))
        c.JSON(http.StatusBadRequest, ErrorResponse{
            Error: "Invalid request format",
        })
        return
    }

    // Validate request
    if err := req.Validate(); err != nil {
        c.JSON(http.StatusBadRequest, ErrorResponse{
            Error: err.Error(),
        })
        return
    }

    // Call service
    usr, err := h.userService.Create(ctx, user.CreateParams{
        Email: req.Email,
        Name:  req.Name,
    })
    if err != nil {
        h.handleError(c, err)
        return
    }

    c.JSON(http.StatusCreated, toUserResponse(usr))
}

func (h *UserHandler) handleError(c *gin.Context, err error) {
    switch {
    case user.IsValidationError(err):
        c.JSON(http.StatusBadRequest, ErrorResponse{Error: err.Error()})
    case user.IsNotFoundError(err):
        c.JSON(http.StatusNotFound, ErrorResponse{Error: "User not found"})
    default:
        h.logger.Error("internal error", zap.Error(err))
        c.JSON(http.StatusInternalServerError, ErrorResponse{
            Error: "Internal server error",
        })
    }
}
```

### React Frontend Standards
**Reference:** `.languages/ts-js/principles.md`

```typescript
// Example: API client using generated types
import type { User, CreateUserRequest, ErrorResponse } from '@/types/api';

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async createUser(data: CreateUserRequest): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/v1/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.error);
    }

    return response.json();
  }

  async getUser(id: string): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/v1/users/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient(import.meta.env.VITE_API_URL);
```

## Selection Criteria

### Choose This Stack When:

1. **Performance is Critical**
   - High throughput requirements (>10k requests/sec)
   - Low latency requirements (<50ms p99)
   - Efficient resource utilization needed
   - Concurrent processing required

2. **Scalability Requirements**
   - Need to handle high concurrent connections
   - Microservices architecture
   - Cloud-native deployment
   - Kubernetes orchestration

3. **System Characteristics**
   - Network-intensive operations
   - Real-time data processing
   - WebSocket servers
   - API gateway or proxy services

4. **Team & Organization**
   - Backend team has Go expertise
   - Frontend team comfortable with React/TypeScript
   - Clear API contract between teams
   - Need for separate deployment cycles

### Avoid This Stack When:

1. **Project Constraints**
   - Small team without Go experience
   - Rapid prototyping phase
   - Simple CRUD application
   - Low traffic expectations

2. **Development Speed Priority**
   - Need faster time to market
   - Frequent requirement changes
   - Want code sharing between frontend/backend
   - Prefer rapid iteration over performance

## Best Practices

### 1. API Contract Management

```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /api/v1/users:
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        created_at:
          type: string
          format: date-time
      required:
        - id
        - email
        - name
        - created_at

    CreateUserRequest:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
      required:
        - email
        - name

    ErrorResponse:
      type: object
      properties:
        error:
          type: string
      required:
        - error
```

### 2. Database Access with Repository Pattern

```go
// internal/domain/user/repository.go
package user

import "context"

type Repository interface {
    Create(ctx context.Context, user *User) error
    FindByID(ctx context.Context, id string) (*User, error)
    FindByEmail(ctx context.Context, email string) (*User, error)
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
}

// internal/repository/postgres/user.go
package postgres

import (
    "context"
    "database/sql"
    "fmt"

    "github.com/user/project/internal/domain/user"
)

type userRepository struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) user.Repository {
    return &userRepository{db: db}
}

func (r *userRepository) Create(ctx context.Context, u *user.User) error {
    query := `
        INSERT INTO users (id, email, name, created_at)
        VALUES ($1, $2, $3, $4)
    `
    _, err := r.db.ExecContext(ctx, query, u.ID, u.Email, u.Name, u.CreatedAt)
    if err != nil {
        return fmt.Errorf("failed to create user: %w", err)
    }
    return nil
}

func (r *userRepository) FindByID(ctx context.Context, id string) (*user.User, error) {
    query := `
        SELECT id, email, name, created_at
        FROM users
        WHERE id = $1
    `

    var u user.User
    err := r.db.QueryRowContext(ctx, query, id).Scan(
        &u.ID, &u.Email, &u.Name, &u.CreatedAt,
    )
    if err == sql.ErrNoRows {
        return nil, user.ErrNotFound
    }
    if err != nil {
        return nil, fmt.Errorf("failed to find user: %w", err)
    }

    return &u, nil
}
```

### 3. Graceful Shutdown

```go
// cmd/api/main.go
package main

import (
    "context"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/gin-gonic/gin"
    "go.uber.org/zap"
)

func main() {
    logger, _ := zap.NewProduction()
    defer logger.Sync()

    router := gin.Default()
    // Setup routes...

    srv := &http.Server{
        Addr:    ":8080",
        Handler: router,
    }

    // Start server in goroutine
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            logger.Fatal("server failed", zap.Error(err))
        }
    }()

    // Wait for interrupt signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    logger.Info("shutting down server...")

    // Graceful shutdown with timeout
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        logger.Fatal("server forced to shutdown", zap.Error(err))
    }

    logger.Info("server exited")
}
```

### 4. Frontend API Client with React Query

```typescript
// hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { CreateUserRequest } from '@/types/api';

export function useUser(id: string) {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => apiClient.getUser(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserRequest) => apiClient.createUser(data),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// Component usage
import { useCreateUser } from '@/hooks/useUsers';

export function CreateUserForm() {
  const createUser = useCreateUser();

  const handleSubmit = async (data: CreateUserRequest) => {
    try {
      await createUser.mutateAsync(data);
      // Success!
    } catch (error) {
      // Handle error
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

## Testing Strategy

### Backend Testing

```go
// internal/domain/user/service_test.go
package user_test

import (
    "context"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/user/project/internal/domain/user"
)

// Mock repository
type MockRepository struct {
    mock.Mock
}

func (m *MockRepository) Create(ctx context.Context, u *user.User) error {
    args := m.Called(ctx, u)
    return args.Error(0)
}

func TestUserService_Create(t *testing.T) {
    tests := []struct {
        name    string
        params  user.CreateParams
        setup   func(*MockRepository)
        wantErr bool
    }{
        {
            name: "success",
            params: user.CreateParams{
                Email: "test@example.com",
                Name:  "Test User",
            },
            setup: func(repo *MockRepository) {
                repo.On("Create", mock.Anything, mock.Anything).Return(nil)
            },
            wantErr: false,
        },
        {
            name: "invalid email",
            params: user.CreateParams{
                Email: "invalid",
                Name:  "Test User",
            },
            setup:   func(repo *MockRepository) {},
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            repo := new(MockRepository)
            tt.setup(repo)

            service := user.NewService(repo)
            _, err := service.Create(context.Background(), tt.params)

            if tt.wantErr {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

### Integration Testing

```go
// tests/integration/user_test.go
package integration

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/stretchr/testify/assert"
)

func TestCreateUser_Integration(t *testing.T) {
    // Setup test database and server
    router := setupTestRouter(t)

    reqBody := map[string]string{
        "email": "test@example.com",
        "name":  "Test User",
    }
    body, _ := json.Marshal(reqBody)

    req := httptest.NewRequest(http.MethodPost, "/api/v1/users", bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")

    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusCreated, w.Code)

    var response map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &response)
    assert.Equal(t, "test@example.com", response["email"])
}
```

## Deployment Considerations

### Docker Configuration

```dockerfile
# Backend Dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /api ./cmd/api

# Runtime stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /api .
COPY migrations ./migrations

EXPOSE 8080

CMD ["./api"]
```

### Docker Compose for Local Development

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8080

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://user:pass@postgres:5432/db
      - REDIS_URL=redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: myapp/api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Performance Optimization

### Backend Optimization
- Use connection pooling for database
- Implement caching with Redis
- Enable gzip compression
- Use goroutine pools for CPU-bound tasks
- Profile with pprof
- Optimize database queries with EXPLAIN
- Use prepared statements

### Frontend Optimization
- Code splitting and lazy loading
- Image optimization
- CDN for static assets
- Service worker for caching
- Debounce API calls
- Virtual scrolling for lists

## Security Considerations

- JWT authentication with refresh tokens
- Rate limiting middleware
- CORS configuration
- Input validation on both frontend and backend
- SQL injection prevention (use parameterized queries)
- XSS protection (React escapes by default)
- CSRF tokens for state-changing operations
- Secure headers (helmet equivalent in Go)
- Environment variable management
- Secret rotation strategy

## Monitoring and Observability

### Prometheus Metrics

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )

    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "HTTP request latencies",
        },
        []string{"method", "endpoint"},
    )
)
```

## Learning Resources

- Go Documentation: https://go.dev/doc/
- Refer to `.languages/go/` for detailed Go principles
- Refer to `.languages/ts-js/` for React/TypeScript principles
- Gin Documentation: https://gin-gonic.com/docs/
- OpenAPI Specification: https://swagger.io/specification/

## Success Metrics

- API response time <100ms (p95)
- Throughput >10k requests/second
- Memory usage <512MB per instance
- Test coverage >80%
- Zero downtime deployments
- Error rate <0.1%
- Container build time <5 minutes
