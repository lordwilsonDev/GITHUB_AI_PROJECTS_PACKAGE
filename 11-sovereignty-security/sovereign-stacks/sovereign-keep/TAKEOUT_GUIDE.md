# Google Takeout Analysis Guide

## Overview

This guide shows you how to analyze your Google Keep notes using the **Sovereign Keep Protocol** without needing API access. This is the **recommended production approach** because it's reliable and doesn't depend on unofficial APIs.

## How It Works

1. **Export** your Keep notes via Google Takeout (one-time, ~5 minutes)
2. **Analyze** the exported data with our semantic engine (automatic)
3. **Review** the generated report showing duplicates and low-value notes
4. **Clean up** manually in Google Keep based on recommendations
5. **Repeat** periodically (monthly/quarterly) to maintain hygiene

---

## Step 1: Export Your Keep Notes

### 1.1 Go to Google Takeout

Visit: **https://takeout.google.com**

### 1.2 Select Only Keep

1. Click **"Deselect all"** at the top
2. Scroll down and check **only "Keep"**
3. Click **"Next step"** at the bottom

### 1.3 Configure Export

- **Delivery method**: "Send download link via email" (recommended)
- **Frequency**: "Export once"
- **File type**: ".zip"
- **File size**: "2 GB" (Keep exports are usually small)

### 1.4 Create Export

1. Click **"Create export"**
2. Wait for email (usually arrives in 5-30 minutes)
3. Download the zip file from the email link
4. Extract the zip file

### 1.5 Locate the Keep Folder

After extraction, you'll have a structure like:

```
Takeout/
  └── Keep/
      ├── Note 1.html
      ├── Note 1.json
      ├── Note 2.html
      ├── Note 2.json
      └── ...
```

**Remember the path to the `Keep` folder** - you'll need it for the next step.

Example paths:
- macOS: `/Users/yourname/Downloads/Takeout/Keep`
- Windows: `C:\Users\yourname\Downloads\Takeout\Keep`
- Linux: `/home/yourname/Downloads/Takeout/Keep`

---

## Step 2: Run the Analysis

### 2.1 Navigate to Project Directory

```bash
cd ~/sovereign-keep
source venv/bin/activate
cd src
```

### 2.2 Run the Standalone Analyzer

**Basic usage:**

```bash
python standalone_analyzer.py ~/Downloads/Takeout/Keep
```

**With custom threshold (more strict = fewer duplicates):**

```bash
python standalone_analyzer.py ~/Downloads/Takeout/Keep --threshold 0.90
```

**With custom output directory:**

```bash
python standalone_analyzer.py ~/Downloads/Takeout/Keep --output-dir ~/Desktop/keep-analysis
```

### 2.3 What Happens During Analysis

You'll see output like:

```
=== Loading Notes from Takeout ===
Found 247 note files in Takeout export
Successfully parsed 247 notes
Filtered to 198 active notes (from 247 total)
Loaded 198 active notes for analysis

=== Running Semantic Analysis ===
This may take a few moments...

1. Calculating information entropy...
2. Detecting semantic duplicates...
3. Found 12 redundancy clusters

✓ Report saved to: ../data/analysis_report.txt
✓ JSON results saved to: ../data/analysis_results.json
```

---

## Step 3: Review the Report

The analysis generates two files:

### 3.1 Human-Readable Report (`analysis_report.txt`)

Open this file to see:

1. **Redundancy Clusters**: Groups of duplicate/similar notes
   - Shows which note to KEEP (most detailed)
   - Shows which notes to ARCHIVE (duplicates)
   - Includes note IDs and previews

2. **Low Vitality Notes**: Notes with low information density
   - Old, simple, or repetitive notes
   - Candidates for archival

3. **High Vitality Notes**: Your most valuable notes
   - Complex, unique, information-dense
   - These are your "gems" - keep these!

4. **Summary**: Overall statistics and next steps

### 3.2 Machine-Readable Results (`analysis_results.json`)

JSON file with complete data for programmatic access.

---

## Step 4: Clean Up Your Keep Notes

### 4.1 Review Redundancy Clusters

For each cluster in the report:

1. Open Google Keep in your browser
2. Search for the note titles mentioned
3. Compare the notes side-by-side
4. If they're truly duplicates:
   - Keep the "survivor" note (most detailed)
   - Archive the duplicate notes

### 4.2 Review Low Vitality Notes

1. Look at the bottom 5-10 notes
2. Ask yourself:
   - Is this still relevant?
   - Does this provide value?
   - Have I already acted on this?
3. Archive notes that are no longer useful

### 4.3 Celebrate High Vitality Notes

These are your best ideas! Consider:
- Expanding them into full documents
- Sharing them with others
- Using them as starting points for projects

---

## Step 5: Maintain Hygiene

### Recommended Schedule

- **Monthly**: Quick analysis (5 minutes)
- **Quarterly**: Deep review and cleanup (30 minutes)
- **Annually**: Full audit and reorganization (1-2 hours)

### Automation (Optional)

You can automate the export and analysis:

1. Set up a monthly reminder to export via Takeout
2. Run the analysis script automatically
3. Review the report when convenient

---

## Understanding the Metrics

### Entropy

- **High entropy** (4.0+): Complex, unique vocabulary
- **Medium entropy** (2.0-4.0): Normal notes
- **Low entropy** (0.0-2.0): Simple, repetitive text

### Vitality Score

Combines entropy and age:

```
Vitality = (0.7 × Entropy) + (0.3 × Recency)
```

- **High vitality**: Valuable, keep these
- **Low vitality**: Consider archiving

### Similarity Threshold

- **0.85** (default): Balanced - finds clear duplicates
- **0.90**: Strict - only very similar notes
- **0.80**: Loose - finds more potential duplicates

---

## Troubleshooting

### "No notes found"

- Check that you're pointing to the `Keep` folder, not `Takeout`
- Verify the folder contains `.html` and `.json` files

### "Failed to parse notes"

- Some notes may have unusual formatting
- Check the console output for specific errors
- The script will skip problematic notes and continue

### "No redundancy clusters found"

- Your notes are well-organized! 🎉
- Try lowering the threshold to 0.80 to find more subtle duplicates
- Or your notes are genuinely unique

### "Analysis is slow"

- First run downloads the AI model (~90MB)
- Subsequent runs are much faster
- Large note collections (500+) may take 1-2 minutes

---

## Advanced Usage

### Custom Analysis Scripts

You can write custom scripts using the parsed data:

```python
from takeout_parser import TakeoutParser

parser = TakeoutParser('~/Downloads/Takeout/Keep')
notes = parser.parse_all_notes()

# Your custom analysis here
for note in notes:
    if 'important' in note.title.lower():
        print(f"Important note: {note.title}")
```

### Exporting to Other Formats

The parsed notes can be exported to:
- Markdown files (for Obsidian, Notion)
- CSV (for spreadsheet analysis)
- Database (for complex queries)

See `src/backup.py` for export utilities.

---

## Privacy & Security

✅ **All processing happens locally** on your machine  
✅ **No data sent to external APIs** (except Google Takeout)  
✅ **No credentials stored** (you download the export manually)  
✅ **Open source** - you can audit the code  

---

## Comparison: Takeout vs. API Approach

| Feature | Google Takeout | gkeepapi API |
|---------|----------------|---------------|
| **Reliability** | ✅ Very high | ⚠️ Breaks often |
| **Setup** | ✅ Simple | ❌ Complex |
| **Real-time** | ⚠️ Manual export | ✅ Live sync |
| **Authentication** | ✅ No issues | ❌ Frequent blocks |
| **Maintenance** | ✅ None needed | ⚠️ Requires updates |
| **Recommended** | ✅ **YES** | ❌ Not currently |

---

## Next Steps

After you're comfortable with the Takeout approach:

1. **Automate exports**: Set up monthly reminders
2. **Customize thresholds**: Tune for your note style
3. **Integrate with PKM**: Export to Obsidian, Notion, etc.
4. **Share insights**: Help others organize their notes

---

## Support

If you encounter issues:

1. Check the `TROUBLESHOOTING.md` file
2. Review the console output for error messages
3. Ensure you're using Python 3.9+
4. Verify all dependencies are installed

---

## Summary

**The Takeout approach is production-ready and recommended.** It's reliable, secure, and doesn't depend on fragile APIs. Run it monthly to keep your digital mind sharp and organized.

**Remember**: The goal isn't to delete everything - it's to surface your best ideas and reduce cognitive clutter. The Sovereign Keep Protocol helps you maintain a high signal-to-noise ratio in your external memory.
