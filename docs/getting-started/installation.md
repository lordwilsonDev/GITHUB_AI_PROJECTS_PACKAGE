# Installation

This guide will help you set up the development environment for the GitHub AI Projects Package.

## Prerequisites

- **Git**: Version control system
- **Docker**: Container runtime (20.10+)
- **Task**: Modern task runner ([installation guide](https://taskfile.dev/installation/))
- **Python**: 3.11 or higher (for local development)

## Installing Task

Task is our unified task runner that provides parity between local and CI environments.

### macOS

```bash
brew install go-task
```

### Linux

```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
```

### Windows

```powershell
choco install go-task
```

## Cloning the Repository

```bash
git clone https://github.com/lordwilsonDev/GITHUB_AI_PROJECTS_PACKAGE.git
cd GITHUB_AI_PROJECTS_PACKAGE
```

## Verifying Installation

Run the following command to verify your setup:

```bash
task --version
```

You should see the Task version number.

## Docker Setup

Ensure Docker is running:

```bash
docker --version
docker ps
```

## Next Steps

Once you have everything installed, proceed to the [Quick Start](quickstart.md) guide to learn how to use the repository.
