# CI/CD Pipeline Architecture

This document provides an in-depth analysis of the Elite Continuous Delivery Pipeline.

## Pipeline Overview

The pipeline implements a three-job workflow that executes on every push, pull request, and manual trigger.

## Trigger Configuration

```yaml
on:
  push:
    branches: ["**"]        # All branches
    tags-ignore: ["v*"]     # Avoid double-trigger
  pull_request:
    branches: ["master", "main"]
  workflow_dispatch:        # Manual trigger
```

### Concurrency Control

Prevents resource waste by canceling outdated runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Job 1: Quality Assurance

### Purpose
Fast feedback loop for code quality issues.

### Steps

1. **Free Disk Space**: Removes unnecessary files (~14GB)
2. **Checkout**: Clones the repository
3. **Install Task**: Sets up the task runner
4. **Lint & Test**: Runs quality checks

### Performance
Typically completes in 2-3 minutes.

## Job 2: Build & Release

### Purpose
Builds, signs, and publishes container images with semantic versioning.

### Steps

#### 1. Semantic Release

Runs only on main/master branches:

- Analyzes commit history
- Determines next version
- Generates changelog
- Creates GitHub release
- Tags the repository

#### 2. Multi-Platform Setup

**QEMU**: Enables ARM64 emulation on AMD64 runners

**BuildKit**: Latest version with docker-container driver

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
  with:
    driver-opts: image=moby/buildkit:latest
```

#### 3. Registry Authentication

Logs into GitHub Container Registry (GHCR):

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

#### 4. Metadata Extraction

Generates tags based on context:

- **Release**: `v1.2.3`, `latest`
- **Branch**: `branch-name`
- **PR**: `pr-123`
- **Commit**: `sha-abc123`

#### 5. Build and Push

The core build step with advanced features:

```yaml
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    cache-from: type=gha
    cache-to: type=gha,mode=max,compression=zstd
    provenance: mode=max
    sbom: true
```

**Key Features:**

- **Multi-platform**: Builds for AMD64 and ARM64
- **Advanced Caching**: GHA backend with mode=max
- **Compression**: Zstandard for faster I/O
- **Provenance**: SLSA attestations
- **SBOM**: Software Bill of Materials

#### 6. Image Signing

Keyless signing with Sigstore Cosign:

```bash
cosign sign --yes ${images}
```

**Benefits:**
- No key management
- OIDC-based identity
- Transparency log (Rekor)
- Cryptographic verification

### Performance

- **First run**: 10-15 minutes (no cache)
- **Subsequent runs**: 3-5 minutes (with cache)
- **Cache hit rate**: 80-90% for dependencies

## Job 3: Publish Documentation

### Purpose
Deploys versioned documentation to GitHub Pages.

### Conditional Execution

Runs only when a new release is published:

```yaml
if: needs.pipeline.outputs.release_published == 'true'
```

### Steps

1. **Checkout**: Full history for versioning
2. **Setup Python**: Installs Python 3.x
3. **Install Tools**: MkDocs Material and mike
4. **Configure Git**: Sets up committer identity
5. **Deploy**: Publishes versioned docs

### Versioning with mike

```bash
mike deploy --push --update-aliases $VERSION latest
```

Creates a version dropdown in the documentation UI.

## Caching Strategy

### GHA Backend

Uses GitHub Actions cache API:

**Advantages:**
- Fast restore (internal network)
- Automatic eviction (10GB limit)
- Scoped to repository

### mode=max

Caches all intermediate layers:

**Impact:**
- Caches expensive dependency installation
- Reduces build time by 70-80%
- Increases cache size

### Zstandard Compression

Faster decompression than gzip:

**Impact:**
- Reduces I/O bottleneck
- Faster cache loading
- Similar compression ratio

## Supply Chain Security

### SLSA Provenance

Generates build attestations:

- Build parameters
- Git SHA
- Builder identity
- Timestamp

### SBOM

Software Bill of Materials:

- All dependencies
- Version information
- Vulnerability scanning

### Cosign Signing

Keyless signing workflow:

1. Workflow requests OIDC token
2. Fulcio issues certificate
3. Image is signed
4. Signature logged in Rekor

### Verification

Consumers can verify images:

```bash
cosign verify \
  --certificate-identity-regexp=https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE \
  ghcr.io/lordwilsondev/github_ai_projects_package:latest
```

## Branch Protection

Enforces quality gates:

- **Require PR reviews**: Prevents direct pushes
- **Require status checks**: Blocks broken code
- **Linear history**: Enables semantic versioning

## Tagging Strategy

### Feature Branches

Every push creates a tagged image:

- `branch-name`
- `sha-abc123`

### Main/Master Branch

Semantic versioning:

- `v1.2.3` (semantic version)
- `latest` (latest release)

### Pull Requests

PR-specific tags:

- `pr-123`

## Monitoring and Observability

### Workflow Annotations

Errors and warnings appear in the GitHub UI.

### Build Logs

Detailed logs for debugging:

- Disk space usage
- Cache hit/miss
- Build duration
- Layer sizes

### Release Notes

Automatically generated from commits.

## Best Practices

1. **Use Conventional Commits**: Enables automated versioning
2. **Keep builds fast**: Optimize Dockerfile layers
3. **Monitor cache hit rate**: Adjust caching strategy
4. **Review security attestations**: Verify provenance
5. **Update dependencies**: Use Renovate or Dependabot

## Troubleshooting

### Disk Space Issues

The pipeline includes aggressive cleanup:

```bash
sudo rm -rf /usr/share/dotnet
sudo rm -rf /usr/local/lib/android
sudo docker image prune --all --force
```

### Cache Misses

Check if dependencies changed:

- requirements.txt modifications
- Base image updates
- Dockerfile changes

### Build Failures

Review logs for:

- Syntax errors
- Missing dependencies
- Network issues
- Platform-specific problems

## Future Enhancements

- **Renovate integration**: Automated dependency updates
- **Performance metrics**: Build time tracking
- **Cost optimization**: Reduce runner minutes
- **Advanced testing**: Integration and E2E tests

## Next Steps

- Review the [Architecture Overview](overview.md)
- Explore the [Quick Start](../getting-started/quickstart.md) guide
