# Sovereign Keep Protocol - Implementation Guide

## Executive Summary

This guide provides a step-by-step roadmap for implementing the Sovereign Keep Protocol, an intelligent Google Keep automation system that prevents "digital mode collapse" through semantic analysis, entropy-based pruning, and resilient authentication.

## What Has Been Completed

### ✅ Phase 1: Project Foundation (COMPLETE)

1. **Directory Structure**
   - `/sovereign-keep/` - Root project directory
   - `/sovereign-keep/src/` - Source code modules
   - `/sovereign-keep/tests/` - Unit and integration tests
   - `/sovereign-keep/data/` - Session cache and logs
   - `/sovereign-keep/exports/` - Backup exports

2. **Configuration Files**
   - `requirements.txt` - Locked dependency versions
   - `.gitignore` - Excludes sensitive data and cache files
   - `README.md` - Project documentation
   - `TODO.md` - Detailed implementation checklist

3. **Development Environment**
   - Python 3.9.6 virtual environment created
   - Virtual environment located at `~/sovereign-keep/venv/`
   - Git repository initialized

4. **Dependencies** (In Progress)
   - Installation command running: `pip install -r requirements.txt`
   - Expected duration: 10-15 minutes
   - Key packages: gkeepapi, sentence-transformers, networkx, keyring

## Implementation Phases

### Phase 2: Authentication Layer

**File:** `src/auth.py`

**Objective:** Create a resilient authentication system that maintains persistent sessions with Google Keep while avoiding security blocks.

**Key Components:**

1. **SovereignAuth Class**
   ```python
   class SovereignAuth:
       - __init__(username)
       - login() -> Keep instance
       - save_session()
   ```

2. **Three-Tier Authentication Strategy**
   - **Tier 1:** Resume from cached session (fastest)
   - **Tier 2:** Resume with master token from OS keyring
   - **Tier 3:** Fresh login with app password

3. **Session Persistence**
   - Serialize Keep state to `data/session.pickle`
   - Store master token in OS keyring
   - Reduce authentication footprint to avoid security flags

**Implementation Steps:**
1. Create `src/auth.py`
2. Import required modules: `gkeepapi`, `keyring`, `pickle`, `os`
3. Implement SovereignAuth class with three-tier logic
4. Add error handling for `NeedsBrowser` and `BadAuthentication`
5. Test with real Google Keep account
6. Verify session persistence across runs

**Validation:**
- Script should authenticate once and reuse session for subsequent runs
- No "suspicious activity" warnings from Google
- Master token stored securely in OS keyring

### Phase 3: Semantic Analysis Engine

**File:** `src/analysis.py`

**Objective:** Implement semantic understanding of notes using NLP and graph theory to identify redundancy and calculate information value.

**Key Components:**

1. **SemanticAuditor Class**
   ```python
   class SemanticAuditor:
       - __init__(keep_client)
       - calculate_entropy(text) -> float
       - find_redundancy_clusters(threshold) -> List[List[note_ids]]
   ```

2. **Shannon Entropy Calculation**
   - Measures information density of each note
   - Formula: H(X) = -Σ p(x) log₂ p(x)
   - Identifies high-value vs low-value content

3. **Vector Embeddings**
   - Model: `all-MiniLM-L6-v2` (384 dimensions)
   - Local processing (no API calls)
   - Batch encoding for efficiency

4. **Similarity Matrix**
   - Cosine similarity between all note pairs
   - Threshold-based edge creation (default: 0.85)
   - Identifies semantic duplicates

5. **Graph-Based Clustering**
   - NetworkX graph construction
   - Connected components detection
   - Identifies "thought loops" (repeated concepts)

**Implementation Steps:**
1. Create `src/analysis.py`
2. Import: `sentence_transformers`, `networkx`, `math`
3. Load sentence-transformer model (one-time initialization)
4. Implement entropy calculation
5. Implement vector embedding generation
6. Build similarity matrix computation
7. Create graph clustering logic
8. Test with sample notes

**Validation:**
- Known duplicate notes should cluster together
- Entropy scores should correlate with content complexity
- Similarity threshold tuning via dry-run analysis

### Phase 4: Action Layer

**File:** `src/action.py`

**Objective:** Execute intelligent pruning decisions while maintaining data safety and traceability.

**Key Components:**

1. **SovereignReaper Class**
   ```python
   class SovereignReaper:
       - __init__(keep_client)
       - process_cluster(note_ids)
   ```

2. **Survivor Selection Logic**
   - Rank by text length (detail proxy)
   - Tie-break by last updated timestamp
   - Select most comprehensive note

3. **Archival Process**
   - Never delete, only archive
   - Add tombstone link to survivor
   - Apply "AutoPruned" label for tracking

4. **Label Divergence Check**
   - Prevent merging notes with different labels
   - Respect user-defined contexts (Work vs Personal)
   - Penalize edge weights for label mismatches

**Implementation Steps:**
1. Create `src/action.py`
2. Implement SovereignReaper class
3. Build cluster processing logic
4. Add survivor selection algorithm
5. Implement tombstone linking
6. Add label divergence checking
7. Create dry-run mode (no actual changes)

**Validation:**
- Dry-run should output proposed actions without executing
- Archived notes should retain tombstone links
- AutoPruned label should allow easy undo

### Phase 5: Main Orchestration

**File:** `src/main.py`

**Objective:** Coordinate all components into a cohesive workflow with proper error handling and user controls.

**Key Components:**

1. **CLI Argument Parser**
   - `--dry-run`: Preview actions without executing
   - `--threshold`: Similarity threshold (default: 0.85)
   - `--backup`: Export before processing
   - `--verbose`: Detailed logging

2. **Execution Flow**
   ```
   1. Parse arguments
   2. Initialize authentication
   3. Sync with Google Keep
   4. Optional: Create backup
   5. Run semantic analysis
   6. Process clusters
   7. Final sync
   8. Generate report
   ```

3. **Error Handling**
   - Exponential backoff for rate limiting
   - Session corruption recovery
   - Graceful degradation on partial failures

4. **Progress Indicators**
   - Use `tqdm` for long operations
   - Status updates for each phase
   - Summary statistics at completion

**Implementation Steps:**
1. Create `src/main.py`
2. Implement argparse CLI
3. Build main execution flow
4. Add error handling wrappers
5. Implement exponential backoff decorator
6. Add progress indicators
7. Create summary report generation

**Validation:**
- All CLI flags should work as expected
- Errors should be caught and logged gracefully
- Progress should be visible for long operations

### Phase 6: Backup & Export System

**File:** `src/backup.py`

**Objective:** Ensure data safety through comprehensive backup mechanisms.

**Key Components:**

1. **Export Formats**
   - JSON: Complete metadata preservation
   - Markdown: Human-readable format

2. **Backup Strategy**
   - Pre-execution full backup
   - Incremental backups (optional)
   - Timestamped backup files

3. **Restore Functionality**
   - Import from JSON backup
   - Verify data integrity
   - Conflict resolution

**Implementation Steps:**
1. Create `src/backup.py`
2. Implement JSON export
3. Implement Markdown export
4. Add restore functionality
5. Test backup/restore cycle

### Phase 7: Logging & Monitoring

**File:** `src/logger.py`

**Objective:** Provide visibility into system operations and enable post-analysis.

**Key Components:**

1. **Structured Logging**
   - All archival actions with similarity scores
   - Authentication events
   - Sync errors
   - Performance metrics

2. **CSV Export**
   - Archival decisions log
   - Similarity scores for threshold tuning
   - Timestamp tracking

3. **Summary Reports**
   - Notes analyzed
   - Clusters found
   - Actions taken
   - Processing time

**Implementation Steps:**
1. Create `src/logger.py`
2. Implement structured logging
3. Add CSV export functionality
4. Create summary report generator

### Phase 8: Testing & Validation

**Directory:** `tests/`

**Objective:** Ensure system reliability and correctness.

**Test Categories:**

1. **Unit Tests**
   - Entropy calculation accuracy
   - Vector similarity correctness
   - Graph clustering logic

2. **Integration Tests**
   - Authentication flow
   - End-to-end workflow
   - Error recovery

3. **Real-World Testing**
   - Dry-run on production data
   - Manual review of suggestions
   - Threshold tuning

**Implementation Steps:**
1. Create test files in `tests/`
2. Write unit tests for each module
3. Create integration test suite
4. Run dry-run on real data
5. Tune parameters based on results

## Critical Design Decisions

### 1. Local vs Cloud Processing

**Decision:** All semantic analysis happens locally

**Rationale:**
- Data sovereignty (no user data leaves machine)
- Cost-effective (no API fees)
- Privacy-preserving
- Immune to API outages

**Trade-off:** Requires local compute resources

### 2. Archive vs Delete

**Decision:** Never delete notes, only archive

**Rationale:**
- Data safety paramount
- Reversible operations
- Tombstone links maintain provenance
- User can manually delete if desired

**Trade-off:** Archived notes still count toward storage

### 3. Similarity Threshold

**Decision:** Default 0.85, user-configurable

**Rationale:**
- Empirically tested on note datasets
- High enough to avoid false positives
- Low enough to catch semantic duplicates
- User can tune based on their data

**Trade-off:** May need adjustment per user

### 4. Authentication Strategy

**Decision:** Three-tier fallback with session caching

**Rationale:**
- Minimizes authentication footprint
- Avoids Google security blocks
- Graceful degradation
- User-friendly (minimal re-auth)

**Trade-off:** Session cache is security-sensitive

## Common Pitfalls & Solutions

### Pitfall 1: Google Security Blocks

**Symptom:** `NeedsBrowser` exception during login

**Solution:**
- Use app password (not regular password)
- Enable session caching
- Reduce login frequency
- Implement exponential backoff

### Pitfall 2: False Positive Merges

**Symptom:** Unrelated notes clustered together

**Solution:**
- Increase similarity threshold
- Implement label divergence checking
- Review dry-run output before execution
- Add manual review step

### Pitfall 3: Slow Processing

**Symptom:** Analysis takes too long on large datasets

**Solution:**
- Batch encode notes (not one-by-one)
- Cache embeddings between runs
- Use sparse matrix for similarity
- Consider incremental processing

### Pitfall 4: Session Corruption

**Symptom:** Sync errors after crash

**Solution:**
- Implement try/finally for session save
- Backup session.pickle to session.bak
- Force fresh sync on corruption detection
- Log sync token state

## Performance Optimization

### 1. Embedding Cache

**Strategy:** Cache note embeddings to avoid recomputation

**Implementation:**
```python
# Store embeddings with note ID and last_modified timestamp
# Recompute only if note changed
```

### 2. Incremental Processing

**Strategy:** Process only new/modified notes

**Implementation:**
```python
# Track last_processed timestamp
# Filter notes by timestamps.updated > last_processed
```

### 3. Sparse Similarity Matrix

**Strategy:** Only compute similarity for promising pairs

**Implementation:**
```python
# Use approximate nearest neighbors (ANN)
# Skip pairs with low TF-IDF overlap
```

## Security Considerations

### 1. Credential Storage

- **Never** store plaintext passwords in code
- Use OS keyring for master token
- Encrypt session.pickle (optional enhancement)
- Add .env to .gitignore

### 2. Session Management

- Limit session.pickle file permissions (600)
- Rotate master tokens periodically
- Implement session expiry checking
- Clear cache on logout

### 3. Data Privacy

- All processing local (no cloud APIs)
- No telemetry or analytics
- User controls all data
- Transparent operations (dry-run mode)

## Deployment Options

### Option 1: Manual Execution

**Use Case:** Occasional cleanup

**Method:**
```bash
cd ~/sovereign-keep
source venv/bin/activate
python src/main.py --backup --dry-run
# Review output
python src/main.py --backup
```

### Option 2: Scheduled Execution (cron)

**Use Case:** Weekly automated cleanup

**Method:**
```bash
# Add to crontab
0 2 * * 0 cd ~/sovereign-keep && source venv/bin/activate && python src/main.py --backup
```

### Option 3: Docker Container

**Use Case:** Portable, reproducible environment

**Method:**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "src/main.py"]
```

### Option 4: Streamlit UI

**Use Case:** Non-technical users

**Method:**
```python
# Create src/ui.py with Streamlit interface
# Provides buttons, sliders, and visual feedback
```

## Maintenance & Updates

### Regular Tasks

1. **Weekly:** Review AutoPruned notes
2. **Monthly:** Tune similarity threshold based on logs
3. **Quarterly:** Update dependencies
4. **Annually:** Rotate master tokens

### Dependency Updates

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade gkeepapi

# Update all (test first!)
pip install --upgrade -r requirements.txt
```

### Monitoring Health

```bash
# Check session validity
python -c "from src.auth import SovereignAuth; auth = SovereignAuth('email'); auth.login()"

# Verify model loading
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Test Keep connection
python -c "import gkeepapi; keep = gkeepapi.Keep(); print('OK')"
```

## Troubleshooting Guide

### Issue: Installation Fails

**Symptoms:**
- pip install errors
- Missing dependencies
- Compilation errors

**Solutions:**
1. Ensure Python 3.9+ installed
2. Install Xcode Command Line Tools (macOS)
3. Update pip: `pip install --upgrade pip`
4. Install packages individually to isolate issue

### Issue: Authentication Fails

**Symptoms:**
- BadAuthentication exception
- NeedsBrowser exception
- Token expired errors

**Solutions:**
1. Generate new app password
2. Delete session.pickle and retry
3. Check keyring permissions
4. Verify Google account status

### Issue: No Duplicates Found

**Symptoms:**
- Analysis completes but finds 0 clusters
- Known duplicates not detected

**Solutions:**
1. Lower similarity threshold (try 0.75)
2. Check note content (may be too short)
3. Verify model loaded correctly
4. Review similarity score distribution in logs

### Issue: Too Many False Positives

**Symptoms:**
- Unrelated notes clustered together
- Dry-run shows incorrect merges

**Solutions:**
1. Increase similarity threshold (try 0.90)
2. Enable label divergence checking
3. Review note labels and contexts
4. Consider manual review step

## Next Steps After Installation

Once dependencies are installed:

1. **Test Authentication**
   ```bash
   python -c "from src.auth import SovereignAuth; auth = SovereignAuth('your-email@gmail.com'); keep = auth.login(); print(f'Logged in! Found {len(list(keep.all()))} notes')"
   ```

2. **Create First Module**
   - Start with `src/auth.py`
   - Follow Phase 2 implementation guide
   - Test thoroughly before proceeding

3. **Iterate Through Phases**
   - Complete one phase at a time
   - Test after each phase
   - Update TODO.md as you progress

4. **Run First Dry-Run**
   - Use real Google Keep data
   - Review suggested actions
   - Tune parameters as needed

## Conclusion

The Sovereign Keep Protocol represents a sophisticated approach to personal knowledge management. By following this implementation guide systematically, you'll build a robust system that:

- Prevents digital hoarding through intelligent pruning
- Maintains data sovereignty and privacy
- Operates reliably despite API constraints
- Provides transparency and reversibility

The key to success is methodical implementation, thorough testing, and continuous refinement based on real-world usage.

**Remember:** This is your cognitive infrastructure. Build it carefully, test it thoroughly, and trust it completely.
