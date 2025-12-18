#!/usr/bin/env python3
"""
Golden Tests for Sovereign Keep Protocol
End-to-end regression tests using fixed fixtures and diffable outputs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import json
import tempfile
import shutil
from pathlib import Path
import hashlib

from takeout_parser import TakeoutParser
from standalone_analyzer import StandaloneAnalyzer


# ============================================================================
# FIXTURE SETUP
# ============================================================================

@pytest.fixture
def fixtures_dir():
    """Create test fixtures directory."""
    fixtures = Path(__file__).parent / 'fixtures'
    fixtures.mkdir(exist_ok=True)
    return fixtures


@pytest.fixture
def golden_dir():
    """Create golden outputs directory."""
    golden = Path(__file__).parent / 'golden'
    golden.mkdir(exist_ok=True)
    return golden


@pytest.fixture
def small_takeout_fixture(fixtures_dir):
    """
    Create a small, fixed Takeout fixture for testing.
    """
    takeout_dir = fixtures_dir / 'takeout_small'
    takeout_dir.mkdir(exist_ok=True)
    
    # Create 3 fixed notes
    notes = [
        {
            'filename': 'note1',
            'title': 'Shopping List',
            'content': 'Milk<br>Eggs<br>Bread',
            'metadata': {
                'color': 'DEFAULT',
                'isArchived': False,
                'isTrashed': False,
                'isPinned': False,
                'labels': [],
                'createdTimestampUsec': 1609459200000000,
                'userEditedTimestampUsec': 1609459200000000
            }
        },
        {
            'filename': 'note2',
            'title': 'Grocery Shopping',
            'content': 'Eggs<br>Milk<br>Bread',
            'metadata': {
                'color': 'DEFAULT',
                'isArchived': False,
                'isTrashed': False,
                'isPinned': False,
                'labels': [],
                'createdTimestampUsec': 1609459300000000,
                'userEditedTimestampUsec': 1609459300000000
            }
        },
        {
            'filename': 'note3',
            'title': 'Project Ideas',
            'content': 'Build a semantic note analyzer<br>Use NLP for duplicate detection',
            'metadata': {
                'color': 'BLUE',
                'isArchived': False,
                'isTrashed': False,
                'isPinned': True,
                'labels': [{'name': 'Work'}],
                'createdTimestampUsec': 1609459400000000,
                'userEditedTimestampUsec': 1609459400000000
            }
        }
    ]
    
    for note in notes:
        # Write HTML file
        html_file = takeout_dir / f"{note['filename']}.html"
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{note['title']}</title>
</head>
<body>
    <div class="title">{note['title']}</div>
    <div class="content">{note['content']}</div>
</body>
</html>
"""
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Write JSON metadata
        json_file = takeout_dir / f"{note['filename']}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(note['metadata'], f, indent=2)
    
    return takeout_dir


# ============================================================================
# GOLDEN TESTS
# ============================================================================

def test_parser_golden_output(small_takeout_fixture, golden_dir):
    """
    Golden test: Parser output should match saved golden file.
    """
    parser = TakeoutParser(str(small_takeout_fixture))
    notes = parser.parse_all_notes()
    
    # Convert to serializable format
    output = sorted([note.to_dict() for note in notes], key=lambda x: x['id'])
    
    golden_file = golden_dir / 'parser_output.json'
    
    if not golden_file.exists():
        # First run: create golden file
        with open(golden_file, 'w') as f:
            json.dump(output, f, indent=2, sort_keys=True)
        pytest.skip("Golden file created, run again to test")
    
    # Load golden output
    with open(golden_file, 'r') as f:
        golden_output = json.load(f)
    
    # Compare
    assert output == golden_output, \
        "Parser output differs from golden file. If this is intentional, delete golden file and re-run."


def test_deterministic_parsing(small_takeout_fixture):
    """
    Golden test: Parsing same fixture twice should yield identical results.
    """
    parser = TakeoutParser(str(small_takeout_fixture))
    
    notes1 = parser.parse_all_notes()
    notes2 = parser.parse_all_notes()
    
    output1 = sorted([note.to_dict() for note in notes1], key=lambda x: x['id'])
    output2 = sorted([note.to_dict() for note in notes2], key=lambda x: x['id'])
    
    assert output1 == output2, "Parsing is not deterministic"


def test_hash_stability(small_takeout_fixture):
    """
    Golden test: Hash of parsed output should be stable.
    """
    parser = TakeoutParser(str(small_takeout_fixture))
    notes = parser.parse_all_notes()
    
    # Create deterministic hash
    output = sorted([note.to_dict() for note in notes], key=lambda x: x['id'])
    output_str = json.dumps(output, sort_keys=True)
    hash1 = hashlib.sha256(output_str.encode()).hexdigest()
    
    # Parse again
    notes2 = parser.parse_all_notes()
    output2 = sorted([note.to_dict() for note in notes2], key=lambda x: x['id'])
    output_str2 = json.dumps(output2, sort_keys=True)
    hash2 = hashlib.sha256(output_str2.encode()).hexdigest()
    
    assert hash1 == hash2, f"Output hash changed: {hash1} != {hash2}"


def test_analyzer_deterministic(small_takeout_fixture, tmp_path):
    """
    Golden test: Running analyzer twice should produce identical reports.
    """
    output1 = tmp_path / 'report1.txt'
    output2 = tmp_path / 'report2.txt'
    
    # Run analyzer twice
    analyzer1 = StandaloneAnalyzer(str(small_takeout_fixture), threshold=0.85)
    analyzer1.load_notes()
    results1 = analyzer1.analyze()
    analyzer1.generate_report(results1, str(output1))
    
    analyzer2 = StandaloneAnalyzer(str(small_takeout_fixture), threshold=0.85)
    analyzer2.load_notes()
    results2 = analyzer2.analyze()
    analyzer2.generate_report(results2, str(output2))
    
    # Compare outputs
    with open(output1) as f1, open(output2) as f2:
        content1 = f1.read()
        content2 = f2.read()
    
    assert content1 == content2, "Analyzer output is not deterministic"


def test_analyzer_deterministic_old(small_takeout_fixture, tmp_path):
    """
    OLD VERSION - SKIP THIS
    """
    pytest.skip("Replaced by test_analyzer_deterministic")
    try:
        from standalone_analyzer import main as analyzer_main
        
        # Mock sys.argv for first run
        import sys
        old_argv = sys.argv
        sys.argv = ['analyzer', str(small_takeout_fixture), '--output', str(output1), '--threshold', '0.85']
        
        try:
            analyzer_main()
        except SystemExit:
            pass
        
        # Second run
        sys.argv = ['analyzer', str(small_takeout_fixture), '--output', str(output2), '--threshold', '0.85']
        
        try:
            analyzer_main()
        except SystemExit:
            pass
        
        sys.argv = old_argv
        
        # Compare outputs (if files were created)
        if output1.exists() and output2.exists():
            with open(output1) as f1, open(output2) as f2:
                content1 = f1.read()
                content2 = f2.read()
            
            # Remove timestamps from comparison
            import re
            content1 = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', content1)
            content2 = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', content2)
            
            assert content1 == content2, "Analyzer output is not deterministic"
    
    except ImportError:
        pytest.skip("Analyzer module not available")


def test_empty_takeout_handling(tmp_path):
    """
    Golden test: Empty Takeout directory should be handled gracefully.
    """
    empty_dir = tmp_path / 'empty_takeout'
    empty_dir.mkdir()
    
    parser = TakeoutParser(str(empty_dir))
    notes = parser.parse_all_notes()
    
    assert notes == [], "Empty directory should return empty list"


def test_partial_files_handling(tmp_path):
    """
    Golden test: HTML without JSON should still parse.
    """
    partial_dir = tmp_path / 'partial_takeout'
    partial_dir.mkdir()
    
    # Create HTML without JSON
    html_file = partial_dir / 'note.html'
    with open(html_file, 'w') as f:
        f.write('<div class="title">Test</div><div class="content">Content</div>')
    
    parser = TakeoutParser(str(partial_dir))
    notes = parser.parse_all_notes()
    
    assert len(notes) == 1
    assert notes[0].title == 'Test'
    assert notes[0].text == 'Content'
    # Should use defaults for missing metadata
    assert notes[0].labels == []
    assert notes[0].archived == False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
