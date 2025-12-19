# Installation

This guide will help you get started with the GitHub AI Projects Package.

## Prerequisites

- Docker (for containerized deployment)
- Python 3.11+ (for local development)
- Git
- Task (optional, but recommended)

## Docker Installation (Recommended)

### Pull from GitHub Container Registry

The easiest way to get started is using our pre-built Docker images:

```bash
# Pull the latest version
docker pull ghcr.io/lordwilsondev/github_ai_projects_package:latest

# Or pull a specific version
docker pull ghcr.io/lordwilsondev/github_ai_projects_package:v1.0.0
```

### Run the Container

```bash
docker run -it ghcr.io/lordwilsondev/github_ai_projects_package:latest
```

### Verify Image Signature (Security Best Practice)

All our images are signed with Cosign for supply chain security:

```bash
# Install Cosign
brew install cosign  # macOS
# or
wget https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64

# Verify the image
cosign verify \
  --certificate-identity-regexp=https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  ghcr.io/lordwilsondev/github_ai_projects_package:latest
```

## Local Development Installation

### Clone the Repository

```bash
git clone https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE.git
cd GITHUB_AI_PROJECTS_PACKAGE
```

### Install Task Runner

Task is our modern task runner (replaces Make):

**macOS:**
```bash
brew install go-task
```

**Linux:**
```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
```

**Windows:**
```powershell
choco install go-task
```

### Install Python Dependencies

```bash
# Using Task (recommended)
task setup

# Or manually
pip install -r requirements.txt
pip install flake8 pylint pytest pytest-cov mkdocs-material
```

### Verify Installation

```bash
# Run quality checks
task ci

# Build Docker image locally
task build

# Serve documentation locally
task docs:serve
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Learn the basics
- [Architecture Overview](../architecture/overview.md) - Understand the system
- [Contributing](../development/contributing.md) - Start contributing
