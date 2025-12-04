# Go API Project Constitution Example

This example shows a customized constitution for a Go HTTP API project.

## Before: Template

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
<!-- SECTION:TECH_STACK:END -->
```

## After: Customized

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: Go 1.21+
- **Framework**: Chi router
- **Database**: PostgreSQL with pgx driver
- **Migration Tool**: golang-migrate
- **Build Tool**: Make or Mage
- **Container Base**: scratch (static binary)
<!-- SECTION:TECH_STACK:END -->

## Quality Standards
<!-- SECTION:QUALITY:BEGIN -->
- Test coverage minimum: 80%
- All exported functions must have godoc comments
- Error handling: explicit error returns (no panics in production)
- Zero external dependencies in main package
- Structured logging with slog
<!-- SECTION:QUALITY:END -->

## Testing
<!-- SECTION:TESTING:BEGIN -->
- Framework: go test (standard library)
- Table-driven tests for complex logic
- Coverage: go test -coverprofile with 80% threshold
- Integration tests use testcontainers-go
- HTTP tests use httptest.Server
- Race detector enabled: go test -race
<!-- SECTION:TESTING:END -->

## Code Quality
<!-- SECTION:CODE_QUALITY:BEGIN -->
- Linter: golangci-lint (all recommended linters enabled)
- Formatter: gofmt + goimports
- Static analysis: go vet + staticcheck
- Security: gosec for SAST scanning
- Vulnerability check: govulncheck
<!-- SECTION:CODE_QUALITY:END -->

## CI/CD
<!-- SECTION:CICD:BEGIN -->
- Platform: GitHub Actions
- Workflows: test.yml, release.yml
- Deploy: Static binary to Kubernetes
- SLSA Level 3 compliance with GoReleaser
- Container: multi-stage build, distroless base
<!-- SECTION:CICD:END -->

## API Standards
<!-- SECTION:API:BEGIN -->
- RESTful design principles
- JSON API responses (application/json)
- Consistent error format (RFC 7807 Problem Details)
- HTTP status codes follow RFC 7231
- Request ID propagation (X-Request-ID header)
- Structured logging with request context
<!-- SECTION:API:END -->

## Error Handling
<!-- SECTION:ERROR_HANDLING:BEGIN -->
- No panics in production code (use errors.Is/As)
- Wrap errors with context (fmt.Errorf with %w)
- Log errors at error/warn level with context
- Return appropriate HTTP status codes
- Never expose internal error details to clients
<!-- SECTION:ERROR_HANDLING:END -->

## Database
<!-- SECTION:DATABASE:BEGIN -->
- Connection pooling configured
- Prepared statements for all queries
- Transactions for multi-statement operations
- Context-aware queries (context.Context)
- Migration files in db/migrations/
- No ORM (use pgx directly)
<!-- SECTION:DATABASE:END -->

## Security
<!-- SECTION:SECURITY:BEGIN -->
- Never log sensitive data
- Parameterized queries only (prevent SQL injection)
- Input validation on all endpoints
- Rate limiting with middleware
- CORS configured explicitly
- TLS 1.3 minimum
<!-- SECTION:SECURITY:END -->

## Observability
<!-- SECTION:OBSERVABILITY:BEGIN -->
- Structured logging: slog with JSON handler
- Metrics: Prometheus client_golang
- Tracing: OpenTelemetry SDK
- Health endpoints: /healthz, /readyz
- Profiling: pprof endpoint (internal only)
<!-- SECTION:OBSERVABILITY:END -->
```

## repo-facts.md Generated

```yaml
---
detected_at: "2025-12-04T10:30:00"
languages:
  - Go
frameworks:
  - Chi
database: PostgreSQL
database_driver: pgx
ci_cd: GitHub Actions
test_framework: go test
linter: golangci-lint
formatter: gofmt
security_tools:
  - gosec
  - govulncheck
deployment: Kubernetes
build_tool: Make
---
```

## Key Customization Points

1. **Technology Stack**: Go 1.21+, Chi router, pgx driver
2. **Quality Standards**: 80% coverage, godoc required, explicit errors
3. **Testing**: Table-driven tests, testcontainers, race detector
4. **Error Handling**: No panics, wrapped errors, structured logging
5. **Database**: Direct pgx usage (no ORM), context-aware queries
6. **Observability**: slog, Prometheus, OpenTelemetry

## Usage

```bash
# After running /speckit:constitution
specify constitution validate

# Apply customizations from this example
# Edit .specify/memory/constitution.md
# Replace template sections with customized versions
```

## Project Structure Example

```
project/
├── cmd/
│   └── server/
│       └── main.go          # Entry point
├── internal/
│   ├── api/                 # HTTP handlers
│   ├── service/             # Business logic
│   └── repository/          # Data access
├── pkg/                     # Public packages
├── db/
│   └── migrations/          # SQL migrations
├── Makefile                 # Build automation
├── go.mod
└── go.sum
```

## Common Customizations

### gRPC Service

If building a gRPC service instead of REST:

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: Go 1.21+
- **Framework**: gRPC with grpc-go
- **Protocol**: Protocol Buffers v3
- **Gateway**: grpc-gateway for REST API
<!-- SECTION:TECH_STACK:END -->
```

### CLI Application

If building a CLI tool:

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: Go 1.21+
- **CLI Framework**: Cobra + Viper
- **Distribution**: GoReleaser with Homebrew tap
- **Signing**: Cosign for binary attestation
<!-- SECTION:TECH_STACK:END -->
```
