# Architecture Overview

This document provides a comprehensive overview of the GitHub AI Projects Package architecture.

## Repository Structure

The repository follows a professional structure that separates concerns:

### Root Level

- **Taskfile.yml**: Unified task runner configuration
- **Dockerfile**: Multi-stage optimized container build
- **.dockerignore**: Build context optimization
- **mkdocs.yml**: Documentation configuration
- **.releaserc.json**: Semantic Release configuration

### .github Directory

Contains all GitHub-specific configurations:

- **workflows/ci.yml**: Elite CI/CD pipeline
- **ISSUE_TEMPLATE/**: Issue templates for bug reports and feature requests
- **PULL_REQUEST_TEMPLATE/**: PR template for consistent contributions

### docs Directory

Contains all documentation in Markdown format, organized by topic.

## Key Components

### 1. Taskfile (Task Runner)

Replaces traditional Makefiles with a modern YAML-based task runner:

**Advantages:**
- YAML syntax (consistent with GitHub Actions)
- Cross-platform compatibility
- Built-in parallelism
- Checksum-based caching
- Local/CI parity

### 2. Multi-Stage Dockerfile

Optimized for BuildKit with two stages:

**Builder Stage:**
- Installs system dependencies
- Collects and installs Python requirements
- Prepares application dependencies

**Runtime Stage:**
- Minimal Python slim image
- Copies only necessary artifacts
- Optimized for size and security

### 3. GitHub Actions Workflow

Three-phase pipeline:

**Phase 1: Quality Assurance**
- Disk space cleanup
- Linting and testing
- Fast feedback loop

**Phase 2: Build & Release**
- Semantic versioning
- Multi-platform Docker builds
- Supply chain security (Cosign, SBOM, provenance)
- Image signing

**Phase 3: Documentation**
- Conditional on release
- Versioned documentation deployment
- GitHub Pages integration

## Design Principles

### 1. Shift-Left Security

Security is integrated from the start:
- Keyless signing with Sigstore Cosign
- SLSA provenance generation
- SBOM (Software Bill of Materials)
- Cryptographic verification

### 2. Developer Experience (DevEx)

Optimized for developer productivity:
- Single command execution (`task ci`)
- Local/CI parity
- Fast feedback loops
- Clear error messages

### 3. Performance

Optimized for speed:
- Advanced caching (GHA backend, mode=max, zstd)
- Parallel execution
- Incremental builds
- Efficient layer caching

### 4. Maintainability

Designed for long-term maintenance:
- Clear separation of concerns
- Self-documenting configuration
- Automated dependency updates (Renovate-ready)
- Comprehensive documentation

## Technology Stack

- **CI/CD**: GitHub Actions
- **Container Runtime**: Docker with BuildKit
- **Task Runner**: Task (Taskfile)
- **Documentation**: MkDocs Material with mike
- **Versioning**: Semantic Release
- **Security**: Sigstore Cosign
- **Registry**: GitHub Container Registry (GHCR)

## Next Steps

- Explore the [CI/CD Pipeline](cicd.md) in detail
- Review the [Quick Start](../getting-started/quickstart.md) guide
