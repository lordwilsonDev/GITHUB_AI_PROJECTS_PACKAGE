# Sovereign Keep Protocol - Next Steps

## Current Status
✅ **Foundation Complete** - All core modules implemented and dependencies installed

## What Has Been Built

### 1. Project Structure
```
sovereign-keep/
├── src/
│   ├── auth.py          # Three-tier authentication system
│   ├── analysis.py      # Semantic analysis & clustering
│   ├── action.py        # Safe archival with tombstone links
│   ├── main.py          # CLI orchestration
│   └── backup.py        # Export to JSON/Markdown
├── data/                # Session cache & logs (gitignored)
├── exports/             # Backup exports
├── tests/               # Unit tests (to be written)
├── requirements.txt     # All dependencies installed ✓
└── venv/                # Python 3.9.6 virtual environment
```

### 2. Core Modules Implemented

#### **auth.py - SovereignAuth Class**
- **Tier 1**: Session restoration from pickle (fastest)
- **Tier 2**: Resume with master token from OS keyring
- **Tier 3**: Fresh login with app password (2FA compatible)
- Handles `NeedsBrowser` and `BadAuthentication` exceptions
- Serializes session state to avoid triggering Google security blocks

#### **analysis.py - SemanticAuditor Class**
- Shannon entropy calculation for note vitality scoring
- Vector embeddings using `all-MiniLM-L6-v2` (local, private)
- Cosine similarity matrix for semantic comparison
- NetworkX graph-based clustering to find "thought loops"
- Identifies redundant notes even with different wording

#### **action.py - SovereignReaper Class**
- Ranks notes by detail (length) and recency (timestamp)
- Archives redundant notes (never deletes)
- Adds tombstone links to track merge lineage
- Applies "AutoPruned" label for easy undo
- Respects label divergence (Work vs Personal)

#### **main.py - CLI Interface**
- Dry-run mode by default (safe testing)
- Configurable similarity threshold
- Optional pre-execution backup
- Verbose logging support

#### **backup.py - Export System**
- JSON export with full metadata
- Markdown export for human readability
- Timestamped backup files

## Ready for Testing Phase

### Prerequisites for Testing
1. **Google Account Setup**
   - If you have 2FA enabled, generate an App Password:
     - Go to: https://myaccount.google.com/apppasswords
     - Select "Mail" and "Other (Custom name)"
     - Name it "Sovereign Keep"
     - Copy the 16-character password

2. **First Run Command**
   ```bash
   cd ~/sovereign-keep
   source venv/bin/activate
   python src/main.py your.email@gmail.com
   ```
   - On first run, it will prompt for your app password
   - The password is stored securely in macOS Keychain
   - Subsequent runs will use cached session (no password needed)

3. **Dry-Run Testing** (Default - Safe)
   ```bash
   python src/main.py your.email@gmail.com --threshold 0.85
   ```
   - This will analyze your notes and show what WOULD be archived
   - No actual changes are made
   - Review the output to tune the threshold

4. **Execute Mode** (After validation)
   ```bash
   python src/main.py your.email@gmail.com --execute --backup
   ```
   - Creates backup before making changes
   - Archives redundant notes with tombstone links
   - All changes are reversible via "AutoPruned" label

## Next Development Tasks

### Immediate (Phase 7-8)
- [ ] Add structured logging to CSV for analysis
- [ ] Implement exponential backoff for rate limiting
- [ ] Add optimistic concurrency control (timestamp checking)
- [ ] Create session.bak recovery mechanism

### Testing (Phase 9)
- [ ] Write unit tests for entropy calculation
- [ ] Test with synthetic duplicate notes
- [ ] Validate authentication fallback chain
- [ ] Run dry-run on production Google Keep account
- [ ] Manually review suggested merges
- [ ] Tune similarity threshold (0.80-0.90 range)

### Documentation (Phase 10)
- [ ] Expand README with screenshots
- [ ] Create troubleshooting guide
- [ ] Document architecture decisions
- [ ] Add inline docstrings to all functions

## Key Safety Features

✅ **Never Deletes** - Only archives with tombstone links  
✅ **Dry-Run Default** - Must explicitly use `--execute`  
✅ **Automatic Backup** - Optional pre-execution export  
✅ **Reversible** - "AutoPruned" label enables bulk undo  
✅ **Local Processing** - No data sent to external APIs  
✅ **Session Caching** - Reduces authentication footprint  

## Troubleshooting

### "NeedsBrowser" Error
- Google detected unusual activity
- Delete `data/session.pickle` and re-authenticate
- Wait 15 minutes before retrying
- Consider using a dedicated app password

### "BadAuthentication" Error
- App password may be incorrect or revoked
- Regenerate app password from Google Account settings
- Clear keyring: `python -c "import keyring; keyring.delete_password('gkeep-sovereign-token', 'your.email@gmail.com')"`

### Model Loading Slow
- First run downloads ~90MB model from HuggingFace
- Cached in `~/.cache/torch/sentence_transformers/`
- Subsequent runs are instant

### High Memory Usage
- Sentence-transformers loads ~500MB into RAM
- Normal for NLP workloads
- Consider processing in batches for 1000+ notes

## Performance Expectations

- **100 notes**: ~10 seconds (including model load)
- **500 notes**: ~30 seconds
- **1000 notes**: ~60 seconds
- **5000 notes**: ~5 minutes

Bottleneck is vector embedding generation (CPU-bound).

## Philosophy

This system treats your note repository as a **living knowledge graph**, not a static archive. By identifying semantic redundancy and calculating information entropy, it helps prevent "digital mode collapse" - the state where your external memory becomes so cluttered it hinders rather than helps cognition.

The goal is not to delete information, but to **consolidate and crystallize** it, transforming scattered thoughts into coherent knowledge structures.

---

**Ready to test?** Start with dry-run mode and review the suggestions before executing.
