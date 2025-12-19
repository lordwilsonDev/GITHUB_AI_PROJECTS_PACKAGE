# Contributing to GitHub AI Projects Package

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/GITHUB_AI_PROJECTS_PACKAGE.git`
3. Install dependencies (see [Installation Guide](../docs/getting-started/installation.md))
4. Create a feature branch: `git checkout -b feat/your-feature`

## Development Workflow

### 1. Make Your Changes

Ensure your changes follow the project's coding standards.

### 2. Run Quality Checks

Before committing, run the quality checks locally:

```bash
task default
```

This runs both linting and tests.

### 3. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning.

**Commit Message Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature (minor version bump)
- `fix`: Bug fix (patch version bump)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**

```bash
git commit -m "feat: add new AI model integration"
git commit -m "fix: resolve Docker build caching issue"
git commit -m "docs: update installation guide"
```

**Breaking Changes:**

For breaking changes, add `BREAKING CHANGE:` in the footer:

```bash
git commit -m "feat: redesign API

BREAKING CHANGE: API endpoints have been restructured"
```

### 4. Push Your Changes

```bash
git push origin feat/your-feature
```

### 5. Create a Pull Request

1. Go to the original repository
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template
5. Submit the PR

## Pull Request Guidelines

- **Title**: Use Conventional Commits format
- **Description**: Provide clear context and motivation
- **Tests**: Include tests for new features
- **Documentation**: Update docs if needed
- **Single Purpose**: One feature/fix per PR

## Branch Protection

The `master` branch is protected:

- ✅ Requires pull request reviews
- ✅ Requires status checks to pass
- ✅ Requires linear history (squash merging)

Direct pushes to `master` are not allowed.

## CI/CD Pipeline

Every PR triggers the Elite Delivery Pipeline:

1. **Quality Assurance**: Linting and testing
2. **Build & Release**: Docker image build (PR-tagged)
3. **Documentation**: Preview (on release only)

All checks must pass before merging.

## Code Review Process

1. Automated checks run first
2. Maintainers review the code
3. Address feedback if requested
4. Once approved, PR is squash-merged

## Local Development

### Available Tasks

View all available tasks:

```bash
task --list
```

### Running Tests

```bash
task test
```

### Running Linters

```bash
task lint
```

### Building Docker Images

```bash
task build
```

### Serving Documentation

```bash
task docs:serve
```

## Reporting Issues

Use the issue templates:

- **Bug Report**: For reporting bugs
- **Feature Request**: For suggesting new features

Provide as much detail as possible.

## Questions?

If you have questions, feel free to:

- Open a discussion
- Comment on an existing issue
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! 🎉
