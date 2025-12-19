# CI/CD Pipeline

## Workflow Overview

The Elite Delivery Pipeline is defined in `.github/workflows/ci.yml` and orchestrates three main phases.

## Triggers

```yaml
on:
  push:
    branches: ["**"]        # All branches
    tags-ignore: ["v*"]     # Avoid double-trigger
  pull_request:
    branches: ["main"]
  workflow_dispatch:        # Manual trigger
```

## Phase 1: Quality Assurance

### Purpose
Validate code quality before building artifacts.

### Steps
1. **Checkout** - Clone repository
2. **Setup Python** - Install Python 3.11 with pip caching
3. **Install Task** - Install task runner
4. **Install Dependencies** - Install linters and test tools
5. **Run CI** - Execute `task ci`

### What Gets Checked
- Python code style (flake8)
- Python code quality (pylint)
- Dockerfile best practices (hadolint)
- Unit tests with coverage

## Phase 2: Build & Release

### Semantic Release (Main Branch Only)

**When:** Only on pushes to `main` branch

**What it does:**
1. Analyzes commit history since last release
2. Determines version bump based on commit types
3. Generates release notes
4. Updates CHANGELOG.md
5. Creates GitHub release
6. Outputs: `new_release_published`, `new_release_version`

### Build Infrastructure Setup

**QEMU:**
```yaml
- uses: docker/setup-qemu-action@v3
```
Enables ARM64 emulation on AMD64 runners.

**Buildx:**
```yaml
- uses: docker/setup-buildx-action@v3
  with:
    driver-opts: image=moby/buildkit:latest
```
Sets up BuildKit with latest features.

### Metadata Generation

```yaml
- uses: docker/metadata-action@v5
  with:
    tags: |
      type=raw,value=latest,enable=${{ ... }}
      type=raw,value=${{ version }},enable=${{ ... }}
      type=ref,event=branch
      type=ref,event=pr
      type=sha
```

**Generates tags:**
- Release: `v1.2.3`, `latest`
- Branch: `feature-login`
- PR: `pr-42`
- Commit: `sha-a1b2c3d`

### Build & Push

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
- Multi-platform builds
- Advanced caching (GHA backend, max mode, zstd)
- SLSA provenance generation
- SBOM generation

### Image Signing

```yaml
- uses: sigstore/cosign-installer@v3.5.0
- run: cosign sign --yes ${images}
```

**Keyless Signing:**
1. GitHub Actions provides OIDC token
2. Cosign requests certificate from Fulcio
3. Signs image with ephemeral key
4. Uploads signature to Rekor transparency log

## Phase 3: Documentation

### Conditional Execution

```yaml
if: needs.pipeline.outputs.release_published == 'true'
```

Only runs when a new release is published.

### Versioned Docs with Mike

```bash
mike deploy --push --update-aliases $VERSION latest
```

**Creates:**
- Version-specific docs: `/v1.2.3/`
- Latest alias: `/latest/` → `/v1.2.3/`
- Version selector dropdown

## Permissions

```yaml
permissions:
  contents: write       # Semantic Release, docs
  packages: write       # GHCR push
  id-token: write       # Cosign OIDC
  issues: write         # Release comments
  pull-requests: write  # Release comments
```

**Principle:** Least privilege - only what's needed.

## Concurrency

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Behavior:**
- New push cancels previous build for same branch
- Saves CI minutes
- Faster feedback

## Secrets

**Required:**
- `GITHUB_TOKEN` - Automatically provided by GitHub

**Optional:**
- None! Uses keyless signing (no PAT needed)

## Monitoring

### Success Indicators
- ✅ Quality checks pass
- ✅ Image pushed to GHCR
- ✅ Image signed with Cosign
- ✅ Release created (main branch)
- ✅ Docs deployed (releases only)

### Failure Handling
- Quality failures block build
- Build failures don't block signing (can't sign nothing)
- Docs failures don't block release

## Local Testing

Test the pipeline locally:

```bash
# Run quality checks
task ci

# Build image (without push)
task build

# Build with caching
task build:advanced
```

## Next Steps

- [Docker Setup](docker.md)
- [Contributing Guide](../development/contributing.md)
