# Sovereign Keep Protocol

## Overview
An automated Google Keep management system that uses semantic analysis, NLP, and graph theory to prevent "digital mode collapse" by detecting duplicates, calculating information entropy, and intelligently pruning redundant notes.

## Project Status

### ✅ Completed
- Project directory structure created
- Requirements.txt with locked dependencies
- Python 3.9.6 virtual environment set up
- All dependencies installed (gkeepapi, sentence-transformers, networkx, etc.)
- .gitignore configured
- Git repository initialized
- **Authentication layer implemented** (SovereignAuth class with 3-tier auth)
- **Semantic analysis engine implemented** (SemanticAuditor class)
- **Action layer created** (SovereignReaper class structure)
- **Main orchestration script created** (main.py)
- **Backup system created** (backup.py)
- **Comprehensive test suite created** (test_semantic_analysis.py)
- **All tests passing** ✓ Semantic engine validated with synthetic data

### ⚠️ Blocked
- Live Google Keep authentication (gkeepapi library limitations)
- Real-world testing with production Keep data

### 📋 Next Steps
- ✅ **Google Takeout parser implemented** (production-ready!)
- ✅ **Standalone analyzer created** (works without API)
- Complete SovereignReaper implementation details
- Add comprehensive logging system
- Create GUI/web interface (optional)

## Quick Start

### 🚀 Recommended: Google Takeout Analysis

**This is the production-ready approach that works right now!**

```bash
# 1. Export your Keep notes from https://takeout.google.com
# 2. Extract the zip file
# 3. Run the analyzer:

cd ~/sovereign-keep
source venv/bin/activate
cd src
python standalone_analyzer.py ~/Downloads/Takeout/Keep

# 4. View the report:
open ../data/analysis_report.txt
```

**📖 See [TAKEOUT_GUIDE.md](TAKEOUT_GUIDE.md) for complete step-by-step instructions.**

### 🔧 Alternative: Development Setup

```bash
cd ~/sovereign-keep
source venv/bin/activate
pip install -r requirements.txt  # Takes 10-15 minutes
python tests/test_semantic_analysis.py  # Verify installation
```

## Architecture

### Core Components

1. **SovereignAuth** (`src/auth.py`)
   - Three-tier authentication strategy
   - Session persistence via pickle
   - OS keyring integration for security
   - Handles NeedsBrowser exceptions

2. **SemanticAuditor** (`src/analysis.py`)
   - Shannon entropy calculation
   - Vector embeddings using all-MiniLM-L6-v2
   - Cosine similarity matrix generation
   - NetworkX graph-based clustering

3. **SovereignReaper** (`src/action.py`)
   - Cluster processing logic
   - Note ranking and survivor selection
   - Tombstone linking for traceability
   - Label divergence checking

4. **Main Orchestrator** (`src/main.py`)
   - CLI argument parsing
   - Execution flow coordination
   - Rate limiting and error handling

## Key Features

### Semantic Deduplication
- Uses vector embeddings to find conceptually similar notes
- Threshold-based similarity detection (default: 0.85)
- Graph-based clustering to find related note groups

### Information Entropy Analysis
- Calculates Shannon entropy for each note
- Identifies high-value "archival gems" vs low-value "digital dust"
- Age-weighted vitality scoring

### Resilient Authentication
- Session caching to avoid repeated logins
- Master token storage in OS keyring
- Graceful fallback through authentication tiers

### Data Safety
- Never deletes notes, only archives
- Automatic backup before processing
- Tombstone links for merge traceability
- Undo mechanism via AutoPruned label

## Technical Specifications

### Dependencies
- **gkeepapi**: Unofficial Google Keep API client
- **sentence-transformers**: Local NLP model for semantic analysis
- **networkx**: Graph analysis for clustering
- **keyring**: Secure credential storage
- **numpy/scipy**: Numerical computing

### Privacy & Security
- All processing happens locally
- No data sent to external APIs
- Credentials stored in OS keyring
- Session tokens encrypted

## Development Roadmap

See `TODO.md` for detailed implementation checklist.

### Phase 1: Foundation ✅ COMPLETE
- ✅ Project setup
- ✅ Dependency installation

### Phase 2: Core Implementation ✅ COMPLETE
- ✅ Authentication layer (3-tier system)
- ✅ Semantic analysis engine (entropy + vectors + clustering)
- ✅ Action layer structure

### Phase 3: Integration ✅ MOSTLY COMPLETE
- ✅ Main orchestration script
- ✅ Backup system
- ⏭️ Logging framework (pending)

### Phase 4: Validation ⚠️ PARTIALLY COMPLETE
- ✅ Unit tests for semantic analysis
- ✅ Synthetic data validation
- ⚠️ Authentication testing (blocked by API)
- ⏭️ Real-world testing with dry-run mode

### Phase 5: Polish ⏭️ PENDING
- ✅ Core documentation (README, guides, test results)
- ⏭️ Error handling refinement
- ⏭️ Optional UI (Streamlit)

## Usage Examples

### Dry Run (Safe Testing)
```bash
python src/main.py --dry-run --verbose
```

### Production Run with Backup
```bash
python src/main.py --backup --threshold 0.85
```

### Custom Similarity Threshold
```bash
python src/main.py --threshold 0.90
```

## Troubleshooting

### Authentication Issues
- Ensure 2FA app password is used (not regular password)
- Check OS keyring permissions
- Delete `data/session.pickle` to force fresh login

### Installation Issues
- Ensure Python 3.9+ is installed
- Virtual environment must be activated
- May need Xcode Command Line Tools on macOS

### Performance Issues
- First run downloads sentence-transformer model (~80MB)
- Large note collections (1000+) may take several minutes
- Consider adjusting similarity threshold

## Contributing

This is a personal knowledge management tool. Contributions welcome for:
- Bug fixes
- Performance optimizations
- Additional semantic analysis features
- UI improvements

## License

To be determined.

## References

- [gkeepapi Documentation](https://gkeepapi.readthedocs.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [NetworkX Documentation](https://networkx.org/)
- [Building a Second Brain](https://www.buildingasecondbrain.com/)
