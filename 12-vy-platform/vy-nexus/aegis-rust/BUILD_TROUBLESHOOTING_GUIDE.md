# Build Troubleshooting Guide
**Created**: 2025-12-17 08:13 PST by BACKGROUND Vy
**Purpose**: Common build issues and solutions for Aegis-Rust project

---

## Common Build Errors

### Error 1: Missing Dependencies

**Symptom**:
```
error: package `chrono` cannot be found
```

**Solution**:
```bash
# Add missing dependency to workspace Cargo.toml
# Or add to specific crate's Cargo.toml
cargo update
cargo build --workspace
```

**Prevention**: All workspace dependencies should be defined in root Cargo.toml

---

### Error 2: Type Mismatches

**Symptom**:
```
error[E0308]: mismatched types
  expected `Result<ValidationResult, Error>`
  found `Result<ValidationResult, anyhow::Error>`
```

**Solution**:
- Check that all components use consistent error types
- Verify async-trait is properly imported
- Use `.map_err()` to convert between error types if needed

---

### Error 3: Async Runtime Issues

**Symptom**:
```
error: async fn cannot be used in trait without async-trait
```

**Solution**:
```rust
use async_trait::async_trait;

#[async_trait]
trait MyTrait {
    async fn my_method(&self) -> Result<()>;
}
```

---

### Error 4: Integration Test Import Failures

**Symptom**:
```
error[E0432]: unresolved import `intent_firewall`
```

**Solution**:
1. Ensure all component crates are built first
2. Check that integration tests are in `tests/` directory (not `src/`)
3. Verify workspace members include all crates
4. Integration tests should import crates by name, not path

**Correct Import**:
```rust
use intent_firewall::{IntentFirewall, BasicIntentFirewall};
```

---

### Error 5: SQLite/Rusqlite Issues

**Symptom**:
```
error: failed to run custom build command for `rusqlite`
```

**Solution**:
- Ensure `bundled` feature is enabled in Cargo.toml:
```toml
rusqlite = { version = "0.30", features = ["bundled"] }
```
- This bundles SQLite, avoiding system dependency issues

---

### Error 6: Tokio Test Utilities

**Symptom**:
```
error: cannot find attribute `tokio::test` in this scope
```

**Solution**:
Add tokio with test features to dev-dependencies:
```toml
[dev-dependencies]
tokio = { workspace = true, features = ["test-util", "macros"] }
```

---

## Common Test Failures

### Test Failure 1: Async Test Timeout

**Symptom**:
```
test tc1_1_safe_and_ethical_action ... FAILED
thread 'tc1_1_safe_and_ethical_action' panicked at 'timeout'
```

**Solution**:
- Increase timeout in test
- Check for deadlocks in async code
- Verify tokio runtime is configured correctly

---

### Test Failure 2: Assertion Failures

**Symptom**:
```
assertion failed: safety_score >= 0.7, got 0.65
```

**Solution**:
- Review test expectations
- Check if component logic changed
- Verify test input data is correct
- May need to adjust thresholds or test data

---

### Test Failure 3: Database Lock Issues

**Symptom**:
```
Error: database is locked
```

**Solution**:
- Use in-memory databases for tests: `BasicAuditLogger::new_in_memory()`
- Ensure proper cleanup between tests
- Use separate database files per test

---

### Test Failure 4: Race Conditions

**Symptom**:
- Tests pass individually but fail when run together
- Intermittent failures

**Solution**:
- Use `Arc<Mutex<>>` for shared state
- Ensure proper async synchronization
- Run tests with `--test-threads=1` to isolate:
```bash
cargo test -- --test-threads=1
```

---

## Dependency Conflicts

### Conflict 1: Version Mismatches

**Symptom**:
```
error: failed to select a version for `serde`
```

**Solution**:
```bash
# Update all dependencies to compatible versions
cargo update

# Or specify exact versions in workspace Cargo.toml
[workspace.dependencies]
serde = "=1.0.195"
```

---

### Conflict 2: Feature Conflicts

**Symptom**:
```
error: feature `full` is required but not enabled
```

**Solution**:
Ensure tokio has all required features:
```toml
tokio = { version = "1.35", features = ["full"] }
```

---

## Build Performance Issues

### Issue 1: Slow Compilation

**Solution**:
```bash
# Use parallel compilation (default, but can specify)
cargo build -j 8

# Use incremental compilation (enabled by default in dev)
# Check Cargo.toml:
[profile.dev]
incremental = true
```

---

### Issue 2: Large Binary Size

**Solution**:
Already configured in Cargo.toml:
```toml
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true  # Removes debug symbols
```

---

## Integration Test Specific Issues

### Issue 1: Tests Can't Find Components

**Symptom**:
```
error: can't find crate for `intent_firewall`
```

**Solution**:
1. Integration tests must be in `tests/` directory at workspace root
2. Each component must be a library crate (have `src/lib.rs`)
3. Workspace must list all members:
```toml
[workspace]
members = [
    "intent-firewall",
    "love-engine",
    "evolution-core",
    "audit-system",
    "hitl-collab",
]
```

---

### Issue 2: Mock HITL Not Working

**Symptom**:
Tests hang waiting for HITL decisions

**Solution**:
- Ensure tests use short timeouts
- Implement proper timeout handling
- Use `tokio::time::timeout()` wrapper:
```rust
let result = tokio::time::timeout(
    Duration::from_secs(5),
    hitl.wait_for_decision(&decision_id)
).await;
```

---

## Environment Issues

### Issue 1: Rust Version Too Old

**Symptom**:
```
error: edition 2021 is unstable
```

**Solution**:
```bash
# Update Rust toolchain
rustup update stable
rustc --version  # Should be 1.56+
```

---

### Issue 2: Missing System Dependencies

**Symptom**:
```
error: linker `cc` not found
```

**Solution**:
```bash
# macOS
xcode-select --install

# Verify
cc --version
```

---

## Quick Diagnostic Commands

```bash
# Check Rust version
rustc --version
cargo --version

# Check dependency tree
cargo tree

# Check for outdated dependencies
cargo outdated

# Clean and rebuild
cargo clean
cargo build --workspace

# Run specific test with output
cargo test test_name -- --nocapture

# Check for common issues
cargo clippy --workspace

# Format code
cargo fmt --all

# Update dependencies
cargo update
```

---

## When to Ask for Help

If you encounter:
1. **Persistent compilation errors** after trying solutions above
2. **Segmentation faults** or crashes
3. **Mysterious test failures** that don't match any pattern above
4. **Build succeeds but tests all fail**

Document the issue in BUILD_ISSUES.md with:
- Full error output
- Steps to reproduce
- Environment details
- Solutions attempted

BACKGROUND Vy will review and fix in next cycle.

---

## Success Indicators

✅ **Build is healthy when**:
- `cargo build --workspace` completes in 2-5 minutes
- All 84 tests pass
- `cargo clippy` shows no errors
- `cargo doc` builds successfully
- No warnings about deprecated dependencies

---

## Additional Resources

- Rust Error Index: https://doc.rust-lang.org/error-index.html
- Tokio Documentation: https://tokio.rs/
- Cargo Book: https://doc.rust-lang.org/cargo/
- Async Book: https://rust-lang.github.io/async-book/

---

**Remember**: Most build issues are simple fixes. Read error messages carefully, they usually tell you exactly what's wrong!
