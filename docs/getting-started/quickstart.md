# Quick Start

This guide will help you quickly get started with the GitHub AI Projects Package.

## Available Tasks

The repository uses Taskfile for unified command execution. View all available tasks:

```bash
task --list
```

## Running Tests and Linting

Run the default quality checks (lint + test):

```bash
task default
```

Or run them individually:

```bash
task lint
task test
```

## Building Docker Images

### Local Build

Build the Docker image locally:

```bash
task build
```

### Advanced Build

Build with multi-platform support (requires Docker Buildx):

```bash
task build:advanced
```

## Documentation

### Local Preview

Serve the documentation locally with live reload:

```bash
task docs:serve
```

Then open http://localhost:8000 in your browser.

### Building Documentation

Build the static documentation site:

```bash
task docs:build
```

## CI/CD Workflow

The repository uses an Elite Continuous Delivery Pipeline that automatically:

1. **On every push**: Runs quality checks and builds Docker images
2. **On main/master**: Performs semantic versioning and creates releases
3. **On release**: Publishes versioned documentation

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes and commit using Conventional Commits:
   ```bash
   git commit -m "feat: add new feature"
   ```

3. Push and create a Pull Request:
   ```bash
   git push origin feat/my-feature
   ```

## Conventional Commits

This repository uses Conventional Commits for automated versioning:

- `feat:` - New feature (minor version bump)
- `fix:` - Bug fix (patch version bump)
- `docs:` - Documentation changes (no version bump)
- `chore:` - Maintenance tasks (no version bump)
- `BREAKING CHANGE:` - Breaking change (major version bump)

## Next Steps

- Learn about the [Architecture](../architecture/overview.md)
- Explore the [CI/CD Pipeline](../architecture/cicd.md)
