# Quick Start

Get up and running with the GitHub AI Projects Package in minutes.

## Using Docker

The fastest way to start:

```bash
# Pull and run
docker run -it ghcr.io/lordwilsondev/github_ai_projects_package:latest
```

## Local Development

### 1. Clone and Setup

```bash
git clone https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE.git
cd GITHUB_AI_PROJECTS_PACKAGE
task setup
```

### 2. Run Quality Checks

```bash
task ci
```

This runs:
- Code linting (flake8, pylint)
- Dockerfile linting (hadolint)
- Unit tests with coverage

### 3. Build Docker Image

```bash
task build
```

### 4. View Documentation

```bash
task docs:serve
```

Open http://localhost:8000 in your browser.

## Available Task Commands

View all available commands:

```bash
task --list
```

Common commands:

- `task` or `task default` - Run lint + test
- `task lint` - Run all linters
- `task test` - Run tests with coverage
- `task build` - Build Docker image
- `task build:advanced` - Build with BuildKit caching
- `task docs:serve` - Serve docs locally
- `task docs:build` - Build docs
- `task clean` - Clean build artifacts
- `task ci` - Run full CI pipeline locally

## Project Structure

```
GITHUB_AI_PROJECTS_PACKAGE/
├── .github/
│   ├── workflows/
│   │   └── ci.yml              # Elite CI/CD pipeline
│   ├── actions/              # Composite actions
│   ├── ISSUE_TEMPLATE/       # Issue templates
│   └── PULL_REQUEST_TEMPLATE/ # PR templates
├── docs/                    # Documentation
├── 01-core-operating-systems/
├── 02-autonomous-intelligence/
├── ... (35 categories total)
├── Dockerfile               # Multi-stage optimized
├── .dockerignore
├── Taskfile.yml             # Task runner config
├── .releaserc.json          # Semantic Release config
├── mkdocs.yml               # Documentation config
└── README.md
```

## Next Steps

- Explore the [Architecture](../architecture/overview.md)
- Browse [Project Categories](../projects/categories.md)
- Learn about [Contributing](../development/contributing.md)
