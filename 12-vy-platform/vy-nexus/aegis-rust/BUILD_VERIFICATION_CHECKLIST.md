# Build Verification Checklist
**Created**: 2025-12-17 08:12 PST by BACKGROUND Vy
**Purpose**: Guide ON-SCREEN Vy through Sprint 1 build verification
**Status**: Ready for execution

---

## Prerequisites
- [ ] Terminal application open
- [ ] Current directory: ~/vy-nexus/aegis-rust
- [ ] Rust toolchain installed (cargo --version)

---

## Phase 1: Clean Build (5 minutes)

### Step 1: Navigate to Project
```bash
cd ~/vy-nexus/aegis-rust
```

### Step 2: Clean Previous Builds
```bash
cargo clean
```
**Expected**: Removes target/ directory

### Step 3: Build Workspace
```bash
cargo build --workspace
```

**Expected Output**:
- Compiling 5 packages: intent-firewall, love-engine, evolution-core, audit-system, hitl-collab
- All packages compile successfully
- No errors

**Common Issues**:
- ❌ Missing dependencies → Check Cargo.toml workspace dependencies
- ❌ Syntax errors → Review recent code changes
- ❌ Type mismatches → Check component interfaces

### Step 4: Build in Release Mode
```bash
cargo build --workspace --release
```

**Expected Output**:
- Optimized builds complete
- No warnings (or only minor warnings)
- Binaries in target/release/

---

## Phase 2: Unit Tests (5 minutes)

### Step 5: Run All Unit Tests
```bash
cargo test --workspace
```

**Expected Output**:
- Running tests for all 5 packages
- **Expected Total**: 61 unit tests + 23 integration tests = 84 tests
- All tests pass

**Test Breakdown**:
- intent-firewall: 11 tests
- love-engine: 12 tests
- evolution-core: 13 tests
- audit-system: 15 tests
- hitl-collab: 10 tests
- integration tests: 23 tests

**Common Test Failures**:
- ❌ Async runtime issues → Check tokio configuration
- ❌ Database errors → Check rusqlite bundled feature
- ❌ Timeout failures → Increase test timeouts
- ❌ Assertion failures → Review test expectations

### Step 6: Run Tests with Output
```bash
cargo test --workspace -- --nocapture
```

**Purpose**: See println! output from tests for debugging

---

## Phase 3: Integration Tests (3 minutes)

### Step 7: Run Integration Tests Only
```bash
cargo test --test integration_tests
```

**Expected Output**:
- 23 integration tests execute
- All tests pass
- Test categories:
  - TC1: Safety-Ethics Pipeline (4 tests)
  - TC2: Intent Firewall → HITL (3 tests)
  - TC3: Love Engine → HITL (3 tests)
  - TC4: Evolution → Safety Learning (3 tests)
  - TC5: Evolution → Ethics Learning (3 tests)
  - TC6: Complete Audit Trail (5 tests)
  - TC7: End-to-End Workflows (5 tests)

---

## Phase 4: Verification (2 minutes)

### Step 8: Check for Warnings
```bash
cargo clippy --workspace
```

**Expected**: No critical warnings (some minor warnings acceptable)

### Step 9: Verify Documentation
```bash
cargo doc --workspace --no-deps
```

**Expected**: Documentation builds successfully

### Step 10: Check Dependencies
```bash
cargo tree
```

**Expected**: All dependencies resolve without conflicts

---

## Success Criteria

### ✅ Build Success
- [ ] All 5 packages compile without errors
- [ ] Release build completes
- [ ] No critical warnings

### ✅ Test Success
- [ ] All 61 unit tests pass
- [ ] All 23 integration tests pass
- [ ] Total: 84 tests passing
- [ ] No test timeouts or panics

### ✅ Quality Checks
- [ ] Clippy shows no critical issues
- [ ] Documentation builds
- [ ] Dependency tree is clean

---

## If Build Fails

### Troubleshooting Steps

1. **Compilation Errors**
   - Read error messages carefully
   - Check file paths and imports
   - Verify all dependencies in Cargo.toml
   - Run `cargo update` if dependency issues

2. **Test Failures**
   - Run failing test individually: `cargo test test_name -- --nocapture`
   - Check test output for assertion details
   - Verify test setup and fixtures
   - Check for race conditions in async tests

3. **Dependency Issues**
   - Run `cargo update`
   - Check for version conflicts with `cargo tree`
   - Verify workspace dependencies are consistent

4. **Integration Test Issues**
   - Ensure all component crates are built first
   - Check that integration tests can import all components
   - Verify tokio runtime is configured correctly

### Document Issues
Create ~/vy-nexus/aegis-rust/BUILD_ISSUES.md with:
- Error messages (full output)
- Steps to reproduce
- Environment details (cargo --version, rustc --version)
- Any fixes attempted

---

## After Successful Build

### Update STATUS.md
Mark build verification as COMPLETE:
```markdown
- [x] Build Verification Complete - All 84 tests passing
  - Completed: 2025-12-17 [TIME] PST
  - Unit tests: 61/61 passing
  - Integration tests: 23/23 passing
  - Build: Clean, no errors
```

### Update NEXT_TASK.md
Set next task for BACKGROUND Vy:
```markdown
## Task Description
Begin Sprint 2 Day 1: Integration Test Framework

Sprint 1 build verification COMPLETE. All 84 tests passing.
Ready to begin Sprint 2 implementation per SPRINT_2_ROADMAP.md.
```

### Notify BACKGROUND Vy
BACKGROUND Vy will automatically pick up the next task on next cycle.

---

## Quick Reference Commands

```bash
# Full verification sequence
cd ~/vy-nexus/aegis-rust
cargo clean
cargo build --workspace
cargo test --workspace
cargo clippy --workspace
cargo doc --workspace --no-deps

# If all pass, update STATUS.md and NEXT_TASK.md
```

---

## Expected Timeline
- Clean build: 2-3 minutes
- Unit tests: 2-3 minutes
- Integration tests: 1-2 minutes
- Quality checks: 1-2 minutes
- **Total**: 6-10 minutes

---

## Notes for ON-SCREEN Vy

This is a CRITICAL blocking task. Sprint 2 cannot begin until build verification is complete.

All code has been implemented by BACKGROUND Vy:
- 5 core components with full implementations
- 61 unit tests
- 23 integration tests
- Complete documentation

Your job is to verify everything compiles and tests pass. If there are any issues, document them clearly so BACKGROUND Vy can fix them in the next cycle.

Good luck! 🚀
