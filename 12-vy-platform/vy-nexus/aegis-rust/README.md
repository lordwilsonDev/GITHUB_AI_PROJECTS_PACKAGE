# Aegis-Rust: Self-Evolving AI Agent

## Overview

Aegis-Rust is a self-evolving AI agent system built in Rust with five core components working together to create a safe, ethical, and continuously improving autonomous system.

## Architecture

The system consists of five main crates:

### 1. **intent-firewall**
First line of defense - validates all incoming requests before execution.
- Vector-based intent classification
- Pattern matching for harmful requests
- Rate limiting and abuse prevention

### 2. **love-engine**
Ethical alignment and harm prevention.
- Thermodynamic love computation (entropy reduction)
- Natural Language Inference for ethical checking
- Hallucination detection
- Value alignment verification

### 3. **evolution-core**
Self-improvement and dynamic capability expansion.
- Rhai script execution for rapid prototyping
- WASM compilation for performance
- Tool promotion (script → WASM → native)
- Performance benchmarking

### 4. **audit-system**
Cryptographic accountability for all actions.
- Ed25519 signatures for all operations
- Merkle tree for tamper-proof audit chain
- SQLite for persistent storage
- Query interface for audit review

### 5. **hitl-collab**
Human-in-the-loop workflows for critical decisions.
- CRDT-based state synchronization
- Pause/resume capability
- Approval workflows
- State persistence

## Getting Started

### Prerequisites

- Rust 1.70 or later
- Cargo

### Building

```bash
# Build all crates
cargo build

# Build in release mode
cargo build --release

# Build specific crate
cargo build -p intent-firewall
```

### Testing

```bash
# Run all tests
cargo test

# Run tests for specific crate
cargo test -p love-engine

# Run with output
cargo test -- --nocapture
```

### Development

```bash
# Check code without building
cargo check

# Format code
cargo fmt

# Run linter
cargo clippy
```

## Project Structure

```
aegis-rust/
├── Cargo.toml              # Workspace configuration
├── README.md               # This file
├── intent-firewall/        # Intent validation
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs
├── love-engine/            # Ethical alignment
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs
├── evolution-core/         # Self-improvement
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs
├── audit-system/           # Cryptographic audit
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs
└── hitl-collab/            # Human collaboration
    ├── Cargo.toml
    └── src/
        └── lib.rs
```

## Development Workflow

This project uses a two-mode development approach:

### Background Mode (15-minute cycles)
- Heavy execution work
- Component implementation
- Test writing
- Bug fixing

### On-Screen Mode (1-hour sessions)
- Planning and integration
- Architecture decisions
- Progress review
- Strategic planning

All work is documented in `~/vy-nexus/build-log/`.

## Documentation

See `~/vy-nexus/ARCHITECTURE.md` for detailed architecture documentation.

## License

MIT

## Status

🚧 **Under Active Development** 🚧

Current Sprint: Foundation Setup
Progress: 15%

See `~/vy-nexus/STATUS.md` for current status.
