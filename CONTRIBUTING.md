# Contributing to GitHub AI Projects Package

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker
- Git
- Task (task runner)

### Setup Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/GITHUB_AI_PROJECTS_PACKAGE.git
   cd GITHUB_AI_PROJECTS_PACKAGE
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE.git
   ```

4. **Install Task:**
   ```bash
   # macOS
   brew install go-task
   
   # Linux
   sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
   ```

5. **Install dependencies:**
   ```bash
   task setup
   ```

6. **Verify setup:**
   ```bash
   task ci
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

Edit files, add features, fix bugs, etc.

### 3. Run Quality Checks

```bash
# Run all checks
task ci

# Or run individually
task lint
task test
```

### 4. Test Docker Build

```bash
task build
```

### 5. Commit Your Changes

Follow the [Conventional Commits](#commit-message-guidelines) specification:

```bash
git add .
git commit -m "feat: add new AI project category"
```

### 6. Push to Your Fork

```bash
git push origin feat/your-feature-name
```

### 7. Create Pull Request

Go to GitHub and create a pull request from your fork to the main repository.

## Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat:** A new feature (triggers MINOR version bump)
- **fix:** A bug fix (triggers PATCH version bump)
- **docs:** Documentation only changes
- **style:** Code style changes (formatting, missing semi-colons, etc.)
- **refactor:** Code refactoring (no functional changes)
- **perf:** Performance improvements
- **test:** Adding or updating tests
- **build:** Changes to build system or dependencies
- **ci:** Changes to CI configuration
- **chore:** Other changes that don't modify src or test files

### Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or `!` after the type:

```
feat!: remove deprecated API endpoint

BREAKING CHANGE: The /api/v1/old endpoint has been removed.
Use /api/v2/new instead.
```

This triggers a MAJOR version bump.

### Examples

```bash
# Feature
git commit -m "feat: add support for GPU acceleration"

# Bug fix
git commit -m "fix: resolve memory leak in data processing"

# Documentation
git commit -m "docs: update installation instructions"

# Performance
git commit -m "perf: optimize Docker image size by 40%"

# Breaking change
git commit -m "feat!: migrate to Python 3.12"
```

## Pull Request Process

### Before Submitting

1. Ensure `task ci` passes locally
2. Update documentation if needed
3. Add tests for new features
4. Follow commit message guidelines
5. Rebase on latest main branch

### PR Requirements

- **Title:** Use conventional commit format
- **Description:** Clearly explain what and why
- **Tests:** Include test results
- **Documentation:** Update docs if needed

### Review Process

1. Automated checks must pass (CI pipeline)
2. At least one maintainer approval required
3. All review comments must be addressed
4. PR will be squashed and merged

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Maximum line length: 100 characters

### Docker

- Use multi-stage builds
- Minimize layer count
- Use .dockerignore
- Follow hadolint recommendations

### Documentation

- Use Markdown format
- Include code examples
- Keep it concise and clear
- Update table of contents

## Testing

### Running Tests

```bash
# All tests
task test

# With coverage
python -m pytest tests/ -v --cov=. --cov-report=html
```

### Writing Tests

- Place tests in `tests/` directory
- Use pytest framework
- Aim for >80% code coverage
- Test edge cases

## Documentation

### Building Docs Locally

```bash
task docs:serve
```

Open http://localhost:8000

### Documentation Structure

```
docs/
├── index.md
├── getting-started/
├── architecture/
├── projects/
├── development/
└── reference/
```

## Questions?

If you have questions:

1. Check existing [Issues](https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE/issues)
2. Read the [Documentation](https://lordwilsondev.github.io/GITHUB_AI_PROJECTS_PACKAGE/)
3. Open a new issue with the `question` label

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing!
