# Task 011: Create and Test Go CI/CD Template

**Status**: Not Started
**Priority**: High
**Estimated Time**: 2-3 hours
**Dependencies**: Task 006 (completed)

---

## Objective

Create a **standalone Go CI/CD workflow template** in `templates/github-actions/go-ci-cd.yml` that follows outer-loop principles, similar to the Node.js and Python templates created in Task 006.

**Note**: A Go workflow already exists in `.stacks/react-frontend-go-backend/workflows/ci-cd.yml`, but this task creates a **simplified, standalone template** for pure Go backend projects (without React frontend).

---

## Background

### Current State
- ✅ Go is used in multiple spec-kit stacks:
  - `react-frontend-go-backend` - Has complete CI/CD workflow
  - `mobile-frontend-go-backend`
  - `tray-app-cross-platform` - Go with systray library
- ✅ Go language documentation exists in `.languages/go/`
- ❌ No standalone Go template in `templates/github-actions/`
- ❌ No act testing performed for Go workflows

### Why This Matters
- Go is a **first-class language** in spec-kit (2 stacks + tray apps)
- Backend services often use Go without React frontend
- Microservices and CLI tools need standalone Go workflows
- Task 006 created Node.js/Python templates but **missed Go**

---

## Requirements

### 1. Create Go CI/CD Template

**Location**: `templates/github-actions/go-ci-cd.yml`

**Template Variables** (to be replaced by users):
- `{{GO_VERSION}}` - e.g., "1.21", "1.22"
- `{{PROJECT_NAME}}` - Project name for artifacts
- `{{MODULE_PATH}}` - Go module path (e.g., github.com/user/project)
- `{{BUILD_COMMAND}}` - e.g., "go build -o bin/server ./cmd/server"
- `{{TEST_COMMAND}}` - e.g., "go test ./..."

### 2. Jobs to Include

#### Job 1: `build-and-test`
**Purpose**: Build once, never rebuild

**Steps**:
1. Checkout code (`actions/checkout@v4`)
2. Setup Go (`actions/setup-go@v5`)
   - Use `{{GO_VERSION}}`
   - Enable Go modules caching
3. Install dependencies (`go mod download`)
4. Run gofmt check (`gofmt -l .`)
5. Run go vet (`go vet ./...`)
6. Run golangci-lint (`golangci/golangci-lint-action@v4`)
7. Run tests with coverage (`go test -v -race -coverprofile=coverage.out ./...`)
8. Upload coverage to Codecov (optional)
9. Calculate version (git describe)
10. Build binary with version embedding
11. Calculate binary digest (SHA256)
12. Upload build artifacts (binary)

**Outputs**:
- `artifact-digest`: SHA256 of built binary
- `version`: Git describe version

#### Job 2: `security-scan`
**Purpose**: SAST and SCA for Go

**Steps**:
1. Checkout code
2. Setup Go
3. Install dependencies
4. Run gosec (SAST for Go)
   ```bash
   go install github.com/securego/gosec/v2/cmd/gosec@latest
   gosec -fmt json -out gosec-report.json ./...
   ```
5. Run go mod tidy check
   ```bash
   go mod tidy
   git diff --exit-code go.mod go.sum
   ```
6. Run Nancy (SCA for Go dependencies)
   ```bash
   go list -json -deps ./... | nancy sleuth
   ```
7. Upload security reports

#### Job 3: `sbom`
**Purpose**: Generate Software Bill of Materials

**Steps**:
1. Checkout code
2. Setup Go
3. Install CycloneDX for Go
   ```bash
   go install github.com/CycloneDX/cyclonedx-gomod/cmd/cyclonedx-gomod@latest
   ```
4. Generate SBOM
   ```bash
   cyclonedx-gomod mod -json -output sbom.json
   cyclonedx-gomod mod -xml -output sbom.xml
   ```
5. Upload SBOM artifacts

#### Job 4: `container` (optional, if Dockerfile exists)
**Purpose**: Build container image

**Uses**: Same pattern as Node.js template
- Check for Dockerfile with `hashFiles('Dockerfile') != ''`
- Build multi-stage Docker image
- Push to ghcr.io
- Generate image SBOM
- Sign with Cosign

#### Job 5: `attest` (optional, main branch only)
**Purpose**: SLSA provenance attestation

**Uses**: `actions/attest-build-provenance@v1`
- Attest binary provenance
- Attest SBOM

#### Job 6: `deploy-staging`, `deploy-production` (optional)
**Purpose**: Promote immutable artifacts

**Pattern**: Same as Node.js template
- Download artifacts
- Verify digest
- Deploy to Kubernetes/Cloud Run/etc.

### 3. Outer-Loop Compliance

The template MUST implement:

✅ **Build Once, Promote Everywhere**
- Binary built ONCE in CI
- Same binary used in all environments
- NO rebuilding for different environments

✅ **Immutable Artifacts**
- SHA256 digest calculated for binary
- Content-addressable storage
- Digest verification before deployment

✅ **SBOM Generation**
- CycloneDX format (JSON + XML)
- Generated with cyclonedx-gomod

✅ **Security Scanning**
- gosec (SAST - Static Application Security Testing)
- Nancy (SCA - Software Composition Analysis)
- go mod tidy verification

✅ **Version Embedding**
```go
// Embed version at build time
var (
    Version   = "dev"
    Commit    = "none"
    BuildTime = "unknown"
)

// Build command in workflow:
go build -ldflags="-X main.Version={{VERSION}} -X main.Commit={{COMMIT}}" -o bin/server ./cmd/server
```

### 4. Testing with act

**Create Test Project**: `.test-projects/go-test/`

**Minimal Go Project**:
```
.test-projects/go-test/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Full template (with OIDC features)
│       └── ci-act-test.yml        # act-compatible (without OIDC)
├── cmd/
│   └── server/
│       └── main.go                # Simple HTTP server
├── internal/
│   └── handlers/
│       └── hello.go
├── go.mod
├── go.sum
└── .git/                          # Git repo for version calculation
```

**main.go Example**:
```go
package main

import (
    "fmt"
    "net/http"
    "os"
)

var (
    Version   = "dev"
    Commit    = "none"
    BuildTime = "unknown"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Go Server %s (commit: %s)\n", Version, Commit)
    })

    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        fmt.Fprintln(w, "OK")
    })

    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    fmt.Printf("Server starting on port %s\n", port)
    http.ListenAndServe(":"+port, nil)
}
```

**go.mod Example**:
```go
module github.com/example/go-test

go 1.21

require (
    // Minimal dependencies for testing
)
```

**Testing Commands**:
```bash
# Switch to Docker Desktop context
docker context use desktop-linux

# Navigate to test project
cd .test-projects/go-test

# Run all jobs with act
DOCKER_HOST=unix:///Users/jasonpoley/.docker/run/docker.sock \
  act \
  -W .github/workflows/ci-act-test.yml \
  --container-architecture linux/amd64 \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest

# Or test individual jobs
act -j build-and-test -W .github/workflows/ci-act-test.yml
act -j security-scan -W .github/workflows/ci-act-test.yml
act -j sbom -W .github/workflows/ci-act-test.yml
```

**Expected Results**:
- ✅ Build and Test: gofmt, go vet, golangci-lint, tests, build all pass
- ✅ Security Scan: gosec, Nancy scans complete
- ✅ SBOM: CycloneDX JSON and XML generated
- ❌ Artifact upload: Expected to fail (act limitation)
- ❌ Container/Attest: Removed from act-test version

### 5. Documentation

**Update Files**:
1. `templates/github-actions/README.md` - Add Go section
2. `TODO/TASK-006-STACK-TESTING-MATRIX.md` - Mark Go as complete
3. Create `TODO/TASK-011-GO-TEST-RESULTS.md` - Document actual test results

**Go Template Documentation**:
```markdown
## Go Template

**Location**: `templates/github-actions/go-ci-cd.yml`

**Best For**:
- Backend APIs and microservices
- CLI tools and utilities
- gRPC services
- System tools

**Features**:
- Go 1.21+ support
- Go modules with dependency caching
- golangci-lint comprehensive linting
- Race detector in tests
- gosec SAST scanning
- Nancy SCA scanning
- CycloneDX SBOM generation
- Version embedding with ldflags
- Multi-platform builds (optional)

**Customization Variables**:
- `GO_VERSION`: Go version (default: "1.21")
- `PROJECT_NAME`: Project name for artifacts
- `MODULE_PATH`: Go module path
- `BUILD_COMMAND`: Custom build command
- `TEST_COMMAND`: Custom test command

**Usage**:
```yaml
# Copy to .github/workflows/ci.yml
# Replace {{GO_VERSION}} with your Go version
# Replace {{PROJECT_NAME}} with your project name
# Replace {{MODULE_PATH}} with your module path
# Replace {{BUILD_COMMAND}} with your build command
```
```

---

## Implementation Steps

### Phase 1: Template Creation (30-45 min)
1. Read existing Go workflow: `.stacks/react-frontend-go-backend/workflows/ci-cd.yml`
2. Extract Go backend jobs (ignore React frontend)
3. Simplify to standalone Go project pattern
4. Create `templates/github-actions/go-ci-cd.yml`
5. Add template variables (`{{GO_VERSION}}`, etc.)
6. Add comprehensive comments

### Phase 2: Test Project Setup (15-20 min)
1. Create `.test-projects/go-test/` directory structure
2. Create minimal Go HTTP server (cmd/server/main.go)
3. Add go.mod with go 1.21
4. Initialize git repository
5. Tag with v1.0.0
6. Create ci.yml (full template)
7. Create ci-act-test.yml (act-compatible)

### Phase 3: act Testing (30-45 min)
1. Install act (if not already installed)
2. Switch Docker context to desktop-linux
3. Run act workflow validation
4. Test build-and-test job
5. Test security-scan job
6. Test sbom job
7. Document any failures or limitations
8. Fix issues and retest

### Phase 4: Documentation (15-20 min)
1. Create TASK-011-GO-TEST-RESULTS.md
2. Update TASK-006-STACK-TESTING-MATRIX.md
3. Update templates/github-actions/README.md
4. Update TASK-006-COMPLETION-REPORT.md

---

## Success Criteria

### Template Quality
- [ ] Go template follows outer-loop principles
- [ ] All jobs documented with comments
- [ ] Template variables clearly marked
- [ ] Security best practices followed (no command injection)
- [ ] Permissions minimal (OIDC where needed)

### Testing Completeness
- [ ] Test project builds successfully
- [ ] golangci-lint passes
- [ ] gosec security scan executes
- [ ] Nancy SCA scan executes
- [ ] CycloneDX SBOM generated (JSON + XML)
- [ ] Binary digest calculated
- [ ] Version embedding works
- [ ] All testable jobs pass with act

### Documentation Quality
- [ ] Test results documented honestly
- [ ] act limitations clearly stated
- [ ] Matrix updated with Go status
- [ ] Usage instructions clear
- [ ] Examples provided

---

## Known Challenges

### Challenge 1: golangci-lint in act
- golangci-lint GitHub Action may not work in act
- **Solution**: Use direct binary installation
  ```bash
  curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin
  golangci-lint run
  ```

### Challenge 2: Nancy Installation
- Nancy is archived, may need alternative
- **Solution**: Use govulncheck instead
  ```bash
  go install golang.org/x/vuln/cmd/govulncheck@latest
  govulncheck ./...
  ```

### Challenge 3: CycloneDX for Go
- cyclonedx-gomod may need specific Go version
- **Solution**: Test with Go 1.21+ and document requirements

### Challenge 4: Cross-Compilation
- Building for multiple OS/arch may complicate workflow
- **Solution**: Start with single platform (linux/amd64)
- **Future**: Add matrix for multi-platform builds

---

## Future Enhancements

### After Basic Template Works
1. **Multi-platform builds**:
   - linux/amd64, linux/arm64
   - darwin/amd64, darwin/arm64
   - windows/amd64
2. **Container optimization**:
   - Multi-stage Dockerfile
   - Distroless base image
   - SBOM in image layers
3. **Performance testing**:
   - Benchmark integration
   - Load testing in CI
4. **Advanced security**:
   - Fuzz testing
   - Code signing with Cosign
5. **Deployment targets**:
   - Kubernetes manifests
   - Cloud Run
   - AWS Lambda (with adapters)

---

## References

### Existing Workflows
- `.stacks/react-frontend-go-backend/workflows/ci-cd.yml` - Complete Go + React workflow
- `templates/github-actions/nodejs-ci-cd.yml` - Node.js template (reference pattern)
- `templates/github-actions/python-ci-cd.yml` - Python template (reference pattern)

### Go Documentation
- `.languages/go/` - Go language docs in spec-kit
- [golangci-lint](https://golangci-lint.run/)
- [gosec](https://github.com/securego/gosec)
- [govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck)
- [CycloneDX for Go](https://github.com/CycloneDX/cyclonedx-gomod)

### Testing Tools
- [act](https://github.com/nektos/act) - GitHub Actions local runner
- Docker Desktop - Required for act

### Related Tasks
- Task 004 - Original outer-loop requirements
- Task 006 - Claude Code conformance, Node.js/Python templates created

---

## Deliverables

1. **Template**: `templates/github-actions/go-ci-cd.yml` (300-400 lines)
2. **Test Project**: `.test-projects/go-test/` (minimal Go HTTP server)
3. **act-Compatible Workflow**: `.test-projects/go-test/.github/workflows/ci-act-test.yml`
4. **Test Results**: `TODO/TASK-011-GO-TEST-RESULTS.md` (detailed test report)
5. **Updated Matrix**: `TODO/TASK-006-STACK-TESTING-MATRIX.md` (Go marked complete)
6. **Updated README**: `templates/github-actions/README.md` (Go section added)

---

## Estimated Time Breakdown

| Phase | Activity | Time |
|-------|----------|------|
| 1 | Template Creation | 30-45 min |
| 2 | Test Project Setup | 15-20 min |
| 3 | act Testing & Fixes | 30-45 min |
| 4 | Documentation | 15-20 min |
| **Total** | | **90-130 min** |

**Contingency**: +30 min for unexpected issues

**Realistic Total**: **2-3 hours**

---

## Notes

- Go is a **first-class citizen** in spec-kit (multiple stacks)
- Existing workflow exists but is complex (React + Go)
- This creates **simplified, standalone template**
- Focus on **backend services and CLI tools**
- **Must test with act** to claim completion

---

**Task Owner**: TBD
**Start Date**: TBD
**End Date**: TBD
**Status**: Waiting to Start
