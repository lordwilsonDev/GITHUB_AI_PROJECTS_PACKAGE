# Sovereign Keep Protocol - Testing Guide

## Overview

This guide walks you through testing the Sovereign Keep Protocol safely before using it on your production Google Keep data.

## Prerequisites

### 1. Google Account Setup

**If you have 2-Factor Authentication (2FA) enabled:**

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Other (Custom name)"
3. Name it "Sovereign Keep Protocol"
4. Click "Generate"
5. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)
6. **Important**: Remove spaces when entering: `xxxxxxxxxxxxxxxx`

**If you don't have 2FA:**
- You can use your regular Google password
- However, Google may block "less secure apps"
- Recommendation: Enable 2FA and use app password for better security

### 2. Activate Virtual Environment

```bash
cd ~/sovereign-keep
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Testing Phases

### Phase 1: Authentication Test

This test verifies that the three-tier authentication system works correctly.

```bash
python test_auth.py your.email@gmail.com
```

**What happens:**
1. First run: Prompts for app password (or regular password)
2. Stores master token in macOS Keychain
3. Saves session to `data/session.pickle`
4. Displays your Google Keep statistics
5. Shows sample notes (first 5)

**Expected output:**
```
============================================================
Sovereign Keep Protocol - Authentication Test
============================================================

Testing authentication for: your.email@gmail.com

This will test the three-tier authentication system:
  1. Session restoration from cache
  2. Resume with master token from keyring
  3. Fresh login with app password

------------------------------------------------------------

Enter App Password: [you type here]

✅ Authentication successful!

Syncing with Google Keep...
✅ Sync complete!

============================================================
Account Statistics
============================================================
Total notes: 150
  Active: 120
  Archived: 25
  Trashed: 5

Labels: 8
  - Work
  - Personal
  - Ideas
  ...

Sample Active Notes (first 5):
  1. Grocery List
     Milk, Eggs, Bread...
  2. Project Ideas
     Build automation for...
  ...

============================================================
✅ Authentication test completed successfully!
============================================================

Session has been cached for future runs.
Next time you run the script, it will use the cached session.

You can now proceed with semantic analysis.
```

**Second run (testing session cache):**
```bash
python test_auth.py your.email@gmail.com
```

Should output:
```
Session restored from cache.
✅ Authentication successful!
```

No password prompt! This confirms session caching works.

### Phase 2: Semantic Analysis Test

This test analyzes your notes for semantic redundancy **without modifying anything**.

```bash
python test_semantic.py your.email@gmail.com
```

**Optional: Adjust similarity threshold**
```bash
python test_semantic.py your.email@gmail.com 0.80  # More sensitive (finds more clusters)
python test_semantic.py your.email@gmail.com 0.90  # Less sensitive (only very similar notes)
```

**What happens:**
1. Authenticates (uses cached session)
2. Downloads semantic model (first run only, ~90MB, 30-60 seconds)
3. Calculates information entropy for all notes
4. Shows highest/lowest entropy notes
5. Finds semantic clusters (potential duplicates)
6. Recommends which note to keep in each cluster

**Expected output:**
```
============================================================
Sovereign Keep Protocol - Semantic Analysis Test
============================================================

Email: your.email@gmail.com
Similarity Threshold: 0.85

------------------------------------------------------------

Authenticating...
✅ Authenticated

Syncing with Google Keep...
✅ Synced

Loading semantic analysis model...
(First run may take 30-60 seconds to download model)
✅ Model loaded

Analyzing 120 active notes...

Calculating information entropy...

Top 5 Highest Entropy Notes (Most Unique):
  1. Research Paper Draft
     Entropy: 4.82 | Age: 15 days | Length: 2500 chars
  2. Meeting Notes - Q4 Strategy
     Entropy: 4.65 | Age: 3 days | Length: 1800 chars
  ...

Top 5 Lowest Entropy Notes (Most Repetitive):
  1. TODO
     Entropy: 2.10 | Age: 120 days | Length: 50 chars
  2. Groceries
     Entropy: 2.35 | Age: 7 days | Length: 80 chars
  ...

------------------------------------------------------------
Finding semantic clusters (threshold: 0.85)...
This may take 1-2 minutes for large note collections...

Found 3 redundant clusters:

Cluster 1 (3 notes):
  1. Grocery List
     Preview: Milk, Eggs, Bread, Butter, Cheese
     Age: 7 days | Length: 45 chars
  2. Shopping
     Preview: Eggs, Milk, Bread
     Age: 14 days | Length: 30 chars
  3. Food to buy
     Preview: Need to get milk and eggs from store
     Age: 21 days | Length: 38 chars
  ➡️  Recommended survivor: Grocery List

Cluster 2 (2 notes):
  1. Project Ideas
     Preview: Build automation for Google Keep, Create semantic analysis...
     Age: 30 days | Length: 250 chars
     Labels: Work, Ideas
  2. Automation Ideas
     Preview: Google Keep automation using NLP and semantic clustering
     Age: 45 days | Length: 180 chars
     Labels: Work
  ➡️  Recommended survivor: Project Ideas

...

============================================================
✅ Semantic analysis completed!
============================================================

This was a DRY RUN - no notes were modified.

To execute archival, use: python src/main.py --execute
```

### Phase 3: Review Results

**Questions to ask:**

1. **Are the clusters accurate?**
   - Do the grouped notes actually represent the same concept?
   - If not, the threshold might be too low (try 0.90)

2. **Is the survivor selection correct?**
   - Does the recommended survivor have the most detail?
   - Check if labels are being respected (Work vs Personal)

3. **Are there false negatives?**
   - Do you see obvious duplicates that weren't caught?
   - Try lowering threshold to 0.80

4. **Entropy scores make sense?**
   - High entropy = complex, unique content
   - Low entropy = simple, repetitive content

### Phase 4: Dry-Run with Main Script

Once you're confident in the analysis, test the full pipeline:

```bash
python src/main.py your.email@gmail.com --threshold 0.85
```

This runs the complete workflow in **dry-run mode** (no changes):
1. Authentication
2. Sync
3. Semantic analysis
4. Cluster identification
5. **Simulated** archival (shows what would happen)

**Expected output:**
```
[DRY RUN] Would archive: "Shopping" (merged into "Grocery List")
[DRY RUN] Would add label: AutoPruned
[DRY RUN] Would add tombstone: [Auto-Archived: Merged into Grocery List]
...

Summary:
  Total notes analyzed: 120
  Clusters found: 3
  Notes that would be archived: 5
  Notes that would be kept: 3
```

### Phase 5: Execute (With Backup)

**⚠️ IMPORTANT: Only proceed if you're satisfied with the dry-run results!**

```bash
python src/main.py your.email@gmail.com --execute --backup --threshold 0.85
```

**What happens:**
1. Creates backup in `exports/backup_YYYYMMDD_HHMMSS.json`
2. Creates Markdown export in `exports/backup_YYYYMMDD_HHMMSS/`
3. Executes archival process
4. Archives redundant notes
5. Adds "AutoPruned" label
6. Adds tombstone links
7. Syncs changes to Google Keep

**Expected output:**
```
Creating backup...
✅ Backup saved to: exports/backup_20251216_152030.json
✅ Markdown export: exports/backup_20251216_152030/

Executing archival process...

Cluster 1: Keeping "Grocery List", archiving 2 notes
  ✓ Archived: "Shopping"
  ✓ Archived: "Food to buy"

Cluster 2: Keeping "Project Ideas", archiving 1 note
  ✓ Archived: "Automation Ideas"

Syncing changes to Google Keep...
✅ Sync complete!

============================================================
Execution Summary
============================================================
Total notes analyzed: 120
Clusters processed: 3
Notes archived: 5
Notes kept: 3

All archived notes have been labeled "AutoPruned" for easy review.
============================================================
```

### Phase 6: Verify in Google Keep

1. Open [Google Keep](https://keep.google.com)
2. Check that archived notes are in the Archive
3. Open an archived note and verify the tombstone link
4. Check that the "AutoPruned" label exists
5. Verify survivor notes are still active

### Phase 7: Undo (If Needed)

If you want to reverse the changes:

```bash
python src/main.py your.email@gmail.com --undo
```

This will:
1. Find all notes with "AutoPruned" label
2. Unarchive them
3. Remove the label
4. Remove tombstone text

## Troubleshooting

### "NeedsBrowser" Error

**Cause**: Google detected unusual activity and requires browser verification.

**Solution**:
1. Wait 15 minutes
2. Delete `data/session.pickle`
3. Run `python test_auth.py your.email@gmail.com` again
4. If persists, try from a different IP or wait 24 hours

### "BadAuthentication" Error

**Cause**: App password is incorrect or revoked.

**Solution**:
1. Regenerate app password at [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Clear keyring:
   ```bash
   python -c "import keyring; keyring.delete_password('gkeep-sovereign-token', 'your.email@gmail.com')"
   ```
3. Delete `data/session.pickle`
4. Run authentication test again

### Model Download Fails

**Cause**: Network issue or HuggingFace is down.

**Solution**:
1. Check internet connection
2. Try again later
3. Manual download:
   ```bash
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

### High Memory Usage

**Cause**: Sentence-transformers loads ~500MB into RAM.

**Solution**: This is normal for NLP workloads. If you have <4GB RAM, consider:
1. Processing in batches
2. Using a smaller model
3. Running on a more powerful machine

### Slow Performance

**Benchmarks**:
- 100 notes: ~10 seconds
- 500 notes: ~30 seconds
- 1000 notes: ~60 seconds
- 5000 notes: ~5 minutes

**If slower**: Check CPU usage. Vector embedding is CPU-bound.

### False Positives (Wrong Clusters)

**Cause**: Threshold too low or model doesn't understand domain-specific jargon.

**Solution**:
1. Increase threshold to 0.90 or 0.95
2. Review clusters manually before executing
3. Use label divergence to prevent cross-context merges

### False Negatives (Missed Duplicates)

**Cause**: Threshold too high or notes use very different wording.

**Solution**:
1. Lower threshold to 0.80 or 0.75
2. Review results to ensure quality doesn't degrade

## Best Practices

1. **Always start with dry-run**: Never use `--execute` on first run
2. **Always backup**: Use `--backup` flag when executing
3. **Review clusters**: Manually verify suggested merges
4. **Tune threshold**: Start at 0.85, adjust based on results
5. **Test on subset**: If you have 1000+ notes, test on a smaller account first
6. **Monitor for a week**: After first execution, check if results are satisfactory
7. **Run periodically**: Weekly or monthly to prevent accumulation

## Next Steps

Once testing is complete:

1. **Schedule regular runs**: Add to cron or launchd
2. **Customize thresholds**: Fine-tune for your note-taking style
3. **Extend functionality**: Add custom features (see NEXT_STEPS.md)
4. **Share feedback**: Document what works and what doesn't

---

**Ready to test?** Start with Phase 1 (Authentication Test).
