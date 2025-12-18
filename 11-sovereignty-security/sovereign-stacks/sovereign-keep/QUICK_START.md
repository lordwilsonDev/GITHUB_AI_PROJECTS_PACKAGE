# Sovereign Keep Protocol - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Export Your Google Keep Notes

1. Go to [Google Takeout](https://takeout.google.com)
2. Click "Deselect all"
3. Scroll down and check only "Keep"
4. Click "Next step" → "Create export"
5. Wait for the email (usually 5-10 minutes)
6. Download and extract the zip file

### Step 2: Run the Analyzer

```bash
cd ~/sovereign-keep
./analyze.sh ~/Downloads/Takeout/Keep
```

That's it! The script will:
- ✅ Check dependencies (install if needed)
- ✅ Load the AI model (all-MiniLM-L6-v2)
- ✅ Analyze your notes for duplicates
- ✅ Calculate information density scores
- ✅ Generate a comprehensive report
- ✅ Open the report automatically

### Step 3: Review and Act

The report will show:

**📊 Summary Statistics**
- Total notes analyzed
- Redundancy clusters found
- Potential duplicates identified

**🔍 Redundancy Clusters**
- Groups of similar notes
- Recommended "survivor" note (most detailed)
- Preview of each note's content

**⭐ Vitality Analysis**
- Highest vitality notes (valuable, keep these!)
- Lowest vitality notes (consider archiving)

**💡 Recommendations**
- Specific actions to take
- Which notes to merge/archive

---

## 📖 Example Output

```
=============================================================
REDUNDANCY ANALYSIS
=============================================================

Found 1 redundancy cluster(s):

Cluster 1: 2 similar notes

  • Meeting Notes - Q4 Planning
    Preview: Discussed quarterly goals...
    Labels: Work
    Updated: 2023-12-18

  • Q4 Planning Meeting  
    Preview: Team meeting about Q4...
    Labels: Work
    Updated: 2023-12-17

Recommended survivor: 'Meeting Notes - Q4 Planning'
(Most detailed: 90 chars)

=============================================================
VITALITY ANALYSIS
=============================================================

Highest vitality: Book Recommendations (0.19)
Lowest vitality: Random Thought (0.08)
```

---

## 🎯 What to Do Next

### For Redundancy Clusters:
1. Open Google Keep on your phone/computer
2. Find the notes mentioned in the cluster
3. Compare them side-by-side
4. Copy any unique content from duplicates to the "survivor"
5. Archive or delete the redundant notes

### For Low Vitality Notes:
1. Review notes with vitality < 0.10
2. Ask: "Do I still need this?"
3. If yes, add more context to increase value
4. If no, archive it

---

## ⚙️ Advanced Usage

### Adjust Similarity Threshold

Default is 0.85 (85% similar). To be more/less strict:

```bash
# More strict (fewer matches, higher confidence)
python src/standalone_analyzer.py ~/Downloads/Takeout/Keep --threshold 0.90

# Less strict (more matches, may include false positives)
python src/standalone_analyzer.py ~/Downloads/Takeout/Keep --threshold 0.80
```

### Export to JSON

```bash
python src/standalone_analyzer.py ~/Downloads/Takeout/Keep --output report.json
```

### Run Demo (Test with Synthetic Data)

```bash
cd ~/sovereign-keep
source venv/bin/activate
python demo.py
```

---

## 🔒 Privacy & Security

✅ **All processing happens locally** - No data sent to external servers  
✅ **No API keys required** - Uses local AI model  
✅ **No authentication needed** - Works with exported files  
✅ **Your data stays on your machine** - Complete privacy  

---

## 🆘 Troubleshooting

### "Command not found: ./analyze.sh"
```bash
chmod +x analyze.sh
./analyze.sh ~/Downloads/Takeout/Keep
```

### "No such file or directory"
Make sure you extracted the Takeout zip file and are pointing to the correct path:
```bash
ls ~/Downloads/Takeout/Keep  # Should show .html files
```

### "Module not found"
Reinstall dependencies:
```bash
cd ~/sovereign-keep
source venv/bin/activate
pip install -r requirements.txt
```

### "Model download failed"
The first run downloads the AI model (~90MB). Ensure you have:
- Internet connection
- ~500MB free disk space
- Wait 2-3 minutes for download

---

## 📅 Recommended Schedule

**Monthly Maintenance:**
1. Export Keep notes (1st of each month)
2. Run analyzer
3. Spend 15 minutes cleaning up duplicates
4. Archive low-vitality notes

**Result:** A clean, organized, high-signal knowledge base!

---

## 📚 More Information

- **Full Documentation**: See [README.md](README.md)
- **Technical Details**: See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Test Results**: See [TEST_RESULTS.md](TEST_RESULTS.md)
- **Demo Instructions**: See [DEMO.md](DEMO.md)

---

## 💬 Questions?

This is a local tool - no support infrastructure. But the code is well-documented:
- Check the `src/` directory for implementation details
- Read the inline comments in each module
- Review the test suite in `tests/` for examples

---

**Happy note organizing! 🎉**
