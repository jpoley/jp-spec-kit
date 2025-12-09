---
id: task-353
title: Optimize Docker image size and layer caching
status: To Do
assignee: []
created_date: '2025-12-09 01:03'
labels:
  - infrastructure
  - cicd
  - optimization
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reduce Docker image size and optimize layer caching for faster builds and smaller downloads.

**Current State**: ~1.2 GB (estimated)
**Target**: < 1 GB

**Optimization Strategies**:

1. **Multi-Stage Build Optimization**:
   - Separate build dependencies from runtime dependencies
   - Use `--no-cache-dir` for pip/npm installs
   - Prune pnpm cache after global installs

2. **Layer Ordering**:
   - Order layers from least to most frequently changed
   - Combine RUN commands where appropriate
   - Use `.dockerignore` to exclude unnecessary files

3. **Package Cleanup**:
   - `apt-get clean && rm -rf /var/lib/apt/lists/*`
   - `pnpm store prune`
   - Remove build-only dependencies

4. **Base Image Evaluation**:
   - Current: `mcr.microsoft.com/devcontainers/python:3.11-bullseye`
   - Alternative: `-slim` variant (trade-off: compatibility)

5. **Compression**:
   - Use Docker buildx with compression
   - Evaluate squashing layers (trade-off: cache)

**Measurement**:
```bash
# Before optimization
docker image inspect ai-coding-agents:before --format='{{.Size}}' | awk '{print $1/1024/1024 " MB"}'

# After optimization
docker image inspect ai-coding-agents:after --format='{{.Size}}' | awk '{print $1/1024/1024 " MB"}'

# Calculate savings
echo "Savings: $(($BEFORE_SIZE - $AFTER_SIZE)) MB"
```

**Testing**:
- Verify all functionality still works after optimization
- Test on both amd64 and arm64
- Measure build time impact

**Trade-offs**:
- Smaller image = less flexibility (e.g., missing debug tools)
- Fewer layers = worse caching
- Balance between size and usability
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Image size reduced to < 1 GB (or document reasons if not achievable)
- [ ] #2 All functionality verified working after optimization
- [ ] #3 Build cache hit rate improved or maintained
- [ ] #4 Build time not increased by optimization
- [ ] #5 Documentation updated with size optimization techniques
- [ ] #6 Both amd64 and arm64 images benefit from optimization
<!-- AC:END -->
