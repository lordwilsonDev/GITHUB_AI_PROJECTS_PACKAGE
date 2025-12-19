# Architecture Overview

## Elite Continuous Delivery Pipeline

This repository implements a state-of-the-art CI/CD pipeline based on modern DevOps best practices and the principles outlined in the DORA (DevOps Research and Assessment) metrics.

## Pipeline Stages

### 1. Quality Assurance

**Trigger:** Every push, pull request

```yaml
quality:
  - Checkout code
  - Setup Python 3.11
  - Install Task runner
  - Install dependencies
  - Run: task ci
    - Lint Python code (flake8, pylint)
    - Lint Dockerfile (hadolint)
    - Run tests with coverage
```

### 2. Build & Release

**Trigger:** After quality checks pass

```yaml
pipeline:
  - Semantic Release (main branch only)
    - Analyze commits (Conventional Commits)
    - Generate version number
    - Create GitHub release
    - Update CHANGELOG.md
  
  - Setup Build Infrastructure
    - QEMU for multi-platform
    - Docker Buildx with latest BuildKit
    - Login to GHCR
  
  - Build & Push
    - Multi-platform: linux/amd64, linux/arm64
    - Advanced caching: GHA backend, mode=max, zstd
    - Generate SBOM and provenance
    - Push to ghcr.io
  
  - Sign Images
    - Keyless signing with Cosign
    - OIDC identity from GitHub Actions
```

### 3. Documentation

**Trigger:** Only when a new release is published

```yaml
docs:
  - Checkout with full history
  - Install MkDocs Material + mike
  - Deploy versioned docs
  - Update 'latest' alias
```

## Key Technologies

### Taskfile (Task Runner)

Replaces traditional Makefiles with a modern YAML-based approach:

**Advantages:**
- YAML syntax (consistent with GitHub Actions, K8s)
- Native parallelism
- Checksum-based caching
- Cross-platform (Windows, macOS, Linux)
- Import/include support

### Docker BuildKit

**Features Used:**
- Multi-stage builds with parallel execution
- Advanced caching (GHA backend)
- Cache mode=max (caches all intermediate layers)
- Zstandard compression for faster I/O
- Multi-platform builds (amd64/arm64)

### Semantic Release

**Automated Versioning:**
- Analyzes commit messages (Conventional Commits)
- Determines version bump (major/minor/patch)
- Generates CHANGELOG.md
- Creates GitHub releases
- Tags Docker images

**Commit Types:**
- `feat:` → Minor version bump
- `fix:` → Patch version bump
- `BREAKING CHANGE:` → Major version bump

### Supply Chain Security

**Sigstore Cosign:**
- Keyless signing using OIDC
- No long-lived private keys
- Transparency log (Rekor)
- Verifiable by anyone

**SLSA Provenance:**
- Build metadata attestation
- Proves build origin
- Enables policy enforcement

**SBOM (Software Bill of Materials):**
- Complete dependency inventory
- Vulnerability scanning
- License compliance

## Performance Optimizations

### Caching Strategy

1. **GitHub Actions Cache (GHA):**
   - 10GB limit per repository
   - Fastest restore within GitHub infrastructure
   - Automatic eviction (LRU)

2. **Cache Mode: max:**
   - Caches ALL intermediate layers
   - Critical for multi-stage builds
   - Speeds up dependency installation

3. **Zstandard Compression:**
   - Faster decompression than gzip
   - Reduces I/O bottleneck
   - Similar compression ratio

### Multi-Platform Builds

**QEMU Emulation:**
- Supports ARM64 on AMD64 runners
- Transparent to Dockerfile
- Mitigated by aggressive caching

**Build Time Comparison:**
- Without cache: 15-20 minutes
- With cache (warm): 2-3 minutes
- Speedup: ~7x

## Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Benefits:**
- Cancels outdated builds on new push
- Saves CI minutes
- Faster feedback loop

## Tagging Strategy

### Feature Branches / PRs
- `branch-name`
- `pr-123`
- `sha-a1b2c3d`

### Main Branch (Releases)
- `v1.2.3` (semantic version)
- `latest`

**Result:** Every push is saved, but clean namespace for releases.

## Next Steps

- [CI/CD Pipeline Details](cicd.md)
- [Docker Setup](docker.md)
- [Contributing Guide](../development/contributing.md)
