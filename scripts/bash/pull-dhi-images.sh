#!/usr/bin/env bash
#
# pull-dhi-images.sh - Pull Docker Hardened Images (DHI) locally
#
# DHI provides 95%+ CVE reduction, SLSA Level 3 provenance, and supply chain security.
# Images are free but require authentication with Docker Hub credentials.
#
# Usage:
#   ./pull-dhi-images.sh              # Pull all core images
#   ./pull-dhi-images.sh --minimal    # Pull minimal set (base + python + node)
#   ./pull-dhi-images.sh --category databases  # Pull specific category
#   ./pull-dhi-images.sh --list       # List available images without pulling
#   ./pull-dhi-images.sh --dev        # Include -dev variants (with build tools)
#
# Prerequisites:
#   docker login dhi.io  (uses Docker Hub credentials)
#
# Reference: https://docs.docker.com/dhi/
#            https://github.com/docker-hardened-images/catalog

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# DHI Registry
REGISTRY="dhi.io"

# Default OS variant (alpine is smaller, debian has more compatibility)
OS_VARIANT="${DHI_OS_VARIANT:-alpine}"
OS_VERSION="${DHI_OS_VERSION:-3.22}"

# Debian variant settings
DEBIAN_VERSION="13"

# =============================================================================
# Image Definitions - Organized by Category
# =============================================================================

# Base images - foundation for custom images
declare -a BASE_IMAGES=(
    "alpine-base:${OS_VERSION}"
    "debian-base:${DEBIAN_VERSION}"
    "busybox:latest"
)

# Language runtimes - for application development
declare -a LANGUAGE_IMAGES=(
    "python:3.13-${OS_VARIANT}${OS_VERSION}"
    "python:3.12-${OS_VARIANT}${OS_VERSION}"
    "python:3.11-${OS_VARIANT}${OS_VERSION}"
    "node:22-${OS_VARIANT}${OS_VERSION}"
    "node:20-${OS_VARIANT}${OS_VERSION}"
    "golang:1.23-${OS_VARIANT}${OS_VERSION}"
    "golang:1.22-${OS_VARIANT}${OS_VERSION}"
    "rust:1.83-${OS_VARIANT}${OS_VERSION}"
)

# Language runtimes - dev variants (include build tools: gcc, make, etc.)
declare -a LANGUAGE_DEV_IMAGES=(
    "python:3.13-${OS_VARIANT}${OS_VERSION}-dev"
    "python:3.12-${OS_VARIANT}${OS_VERSION}-dev"
    "node:22-${OS_VARIANT}${OS_VERSION}-dev"
    "node:20-${OS_VARIANT}${OS_VERSION}-dev"
    "golang:1.23-${OS_VARIANT}${OS_VERSION}-dev"
)

# Databases - data storage
declare -a DATABASE_IMAGES=(
    "postgres:17-debian${DEBIAN_VERSION}"
    "postgres:16-debian${DEBIAN_VERSION}"
    "redis:7-${OS_VARIANT}${OS_VERSION}"
    "valkey:8-${OS_VARIANT}${OS_VERSION}"
    "mongodb:8-debian${DEBIAN_VERSION}"
    "mysql:8-debian${DEBIAN_VERSION}"
)

# Infrastructure - web servers, proxies, load balancers
declare -a INFRA_IMAGES=(
    "nginx:1.27-${OS_VARIANT}${OS_VERSION}"
    "haproxy:3.1-${OS_VARIANT}${OS_VERSION}"
    "traefik:3.3-${OS_VARIANT}${OS_VERSION}"
)

# Observability - monitoring and logging
declare -a OBSERVABILITY_IMAGES=(
    "prometheus:3.1-${OS_VARIANT}${OS_VERSION}"
    "grafana:11-${OS_VARIANT}${OS_VERSION}"
    "fluent-bit:3.2-${OS_VARIANT}${OS_VERSION}"
)

# Kubernetes tools - cluster management
declare -a K8S_IMAGES=(
    "kubectl:1.32-${OS_VARIANT}${OS_VERSION}"
    "helm:3.16-${OS_VARIANT}${OS_VERSION}"
    "kustomize:5.5-${OS_VARIANT}${OS_VERSION}"
)

# Security tools - scanning and secrets management
declare -a SECURITY_IMAGES=(
    "vault:1.18-${OS_VARIANT}${OS_VERSION}"
    "trivy:0.58-${OS_VARIANT}${OS_VERSION}"
    "cosign:2.4-${OS_VARIANT}${OS_VERSION}"
)

# =============================================================================
# Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dhi_auth() {
    log_info "Checking DHI authentication..."

    # Check if dhi.io is in docker config
    if docker login dhi.io --get-login 2>/dev/null; then
        log_success "Already authenticated to dhi.io"
        return 0
    fi

    log_warn "Not authenticated to dhi.io"
    echo ""
    echo "DHI requires authentication with your Docker Hub credentials."
    echo "Run: docker login dhi.io"
    echo ""
    echo "DHI is FREE but requires auth. Use your Docker Hub username and password/PAT."
    echo ""

    read -p "Would you like to login now? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker login dhi.io
    else
        log_error "Cannot proceed without DHI authentication"
        exit 1
    fi
}

pull_image() {
    local image="$1"
    local full_ref="${REGISTRY}/${image}"

    echo -n "  Pulling ${image}... "
    if docker pull "${full_ref}" --quiet >/dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

pull_category() {
    local category_name="$1"
    shift
    local images=("$@")

    echo ""
    log_info "Pulling ${category_name} images (${#images[@]} images)..."

    local success=0
    local failed=0

    for image in "${images[@]}"; do
        if pull_image "${image}"; then
            ((success++))
        else
            ((failed++))
        fi
    done

    log_success "${category_name}: ${success} pulled, ${failed} failed"
}

list_images() {
    echo ""
    echo "=== Docker Hardened Images (DHI) Catalog ==="
    echo ""
    echo "Registry: ${REGISTRY}"
    echo "OS Variant: ${OS_VARIANT} (set DHI_OS_VARIANT to change)"
    echo ""

    echo "BASE IMAGES:"
    for img in "${BASE_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "LANGUAGE RUNTIMES:"
    for img in "${LANGUAGE_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "LANGUAGE RUNTIMES (DEV - with build tools):"
    for img in "${LANGUAGE_DEV_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "DATABASES:"
    for img in "${DATABASE_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "INFRASTRUCTURE:"
    for img in "${INFRA_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "OBSERVABILITY:"
    for img in "${OBSERVABILITY_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "KUBERNETES TOOLS:"
    for img in "${K8S_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "SECURITY TOOLS:"
    for img in "${SECURITY_IMAGES[@]}"; do echo "  - ${REGISTRY}/${img}"; done

    echo ""
    echo "Total: $(( ${#BASE_IMAGES[@]} + ${#LANGUAGE_IMAGES[@]} + ${#LANGUAGE_DEV_IMAGES[@]} + ${#DATABASE_IMAGES[@]} + ${#INFRA_IMAGES[@]} + ${#OBSERVABILITY_IMAGES[@]} + ${#K8S_IMAGES[@]} + ${#SECURITY_IMAGES[@]} )) images"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Pull Docker Hardened Images (DHI) locally for reference/extension."
    echo "DHI provides 95%+ CVE reduction and SLSA Level 3 provenance."
    echo ""
    echo "Options:"
    echo "  --minimal          Pull minimal set (base + python + node)"
    echo "  --dev              Include -dev variants (with build tools)"
    echo "  --category NAME    Pull specific category only"
    echo "                     Categories: base, languages, databases, infra,"
    echo "                                 observability, k8s, security"
    echo "  --list             List available images without pulling"
    echo "  --help             Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  DHI_OS_VARIANT     OS variant: alpine (default) or debian"
    echo "  DHI_OS_VERSION     OS version: 3.22 (Alpine default) or 13 (Debian)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Pull all core images"
    echo "  $0 --minimal                 # Pull base + python + node only"
    echo "  $0 --category databases      # Pull database images only"
    echo "  $0 --dev                     # Include dev variants"
    echo "  DHI_OS_VARIANT=debian $0     # Use Debian-based images"
    echo ""
    echo "Prerequisites:"
    echo "  docker login dhi.io          # Uses Docker Hub credentials (free)"
}

# =============================================================================
# Main
# =============================================================================

main() {
    local minimal=false
    local include_dev=false
    local list_only=false
    local category=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --minimal)
                minimal=true
                shift
                ;;
            --dev)
                include_dev=true
                shift
                ;;
            --list)
                list_only=true
                shift
                ;;
            --category)
                category="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # List mode
    if [[ "${list_only}" == true ]]; then
        list_images
        exit 0
    fi

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          Docker Hardened Images (DHI) Puller                 ║"
    echo "║                                                              ║"
    echo "║  95%+ CVE reduction • SLSA Level 3 • Supply chain security  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Check authentication
    check_dhi_auth

    # Track timing
    start_time=$(date +%s)

    # Pull based on mode
    if [[ -n "${category}" ]]; then
        # Single category mode
        case "${category}" in
            base)
                pull_category "Base" "${BASE_IMAGES[@]}"
                ;;
            languages|lang)
                pull_category "Languages" "${LANGUAGE_IMAGES[@]}"
                if [[ "${include_dev}" == true ]]; then
                    pull_category "Languages (Dev)" "${LANGUAGE_DEV_IMAGES[@]}"
                fi
                ;;
            databases|db)
                pull_category "Databases" "${DATABASE_IMAGES[@]}"
                ;;
            infra|infrastructure)
                pull_category "Infrastructure" "${INFRA_IMAGES[@]}"
                ;;
            observability|obs)
                pull_category "Observability" "${OBSERVABILITY_IMAGES[@]}"
                ;;
            k8s|kubernetes)
                pull_category "Kubernetes" "${K8S_IMAGES[@]}"
                ;;
            security|sec)
                pull_category "Security" "${SECURITY_IMAGES[@]}"
                ;;
            *)
                log_error "Unknown category: ${category}"
                echo "Valid categories: base, languages, databases, infra, observability, k8s, security"
                exit 1
                ;;
        esac
    elif [[ "${minimal}" == true ]]; then
        # Minimal mode - just essentials
        pull_category "Base" "${BASE_IMAGES[@]}"
        pull_category "Languages (Python + Node)" \
            "python:3.13-${OS_VARIANT}${OS_VERSION}" \
            "python:3.12-${OS_VARIANT}${OS_VERSION}" \
            "node:22-${OS_VARIANT}${OS_VERSION}" \
            "node:20-${OS_VARIANT}${OS_VERSION}"
        if [[ "${include_dev}" == true ]]; then
            pull_category "Languages Dev" \
                "python:3.13-${OS_VARIANT}${OS_VERSION}-dev" \
                "node:22-${OS_VARIANT}${OS_VERSION}-dev"
        fi
    else
        # Full mode - all categories
        pull_category "Base" "${BASE_IMAGES[@]}"
        pull_category "Languages" "${LANGUAGE_IMAGES[@]}"
        if [[ "${include_dev}" == true ]]; then
            pull_category "Languages (Dev)" "${LANGUAGE_DEV_IMAGES[@]}"
        fi
        pull_category "Databases" "${DATABASE_IMAGES[@]}"
        pull_category "Infrastructure" "${INFRA_IMAGES[@]}"
        pull_category "Observability" "${OBSERVABILITY_IMAGES[@]}"
        pull_category "Kubernetes" "${K8S_IMAGES[@]}"
        pull_category "Security" "${SECURITY_IMAGES[@]}"
    fi

    # Summary
    end_time=$(date +%s)
    duration=$((end_time - start_time))

    echo ""
    log_success "Completed in ${duration} seconds"
    echo ""
    echo "Images are now available locally. To use in a Dockerfile:"
    echo "  FROM dhi.io/python:3.13-alpine3.22"
    echo ""
    echo "To extend an image:"
    echo "  FROM dhi.io/python:3.13-alpine3.22-dev"
    echo "  RUN apk add --no-cache your-packages"
    echo ""
}

main "$@"
