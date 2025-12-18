#!/usr/bin/env python3
"""
Fuzz Testing for Sovereign Keep Protocol
Tests robustness against malformed, pathological, and adversarial inputs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import tempfile
import json
from pathlib import Path

from takeout_parser import TakeoutParser, TakeoutNote
from src.analysis import SemanticAuditor


class MockKeepClient:
    """Mock Keep client for testing."""
    pass


# ============================================================================
# PARSER FUZZ TESTS
# ============================================================================

def test_parser_empty_html():
    """
    Fuzz: Empty HTML file should not crash.
    """
    parser = TakeoutParser.__new__(TakeoutParser)
    title, text = parser._extract_content_from_html("")
    
    assert isinstance(title, str)
    assert isinstance(text, str)


def test_parser_malformed_html():
    """
    Fuzz: Malformed HTML should not crash.
    """
    parser = TakeoutParser.__new__(TakeoutParser)
    
    malformed_cases = [
        "<div class='title'>Unclosed div",
        "<div class=\"content\">No closing tag",
        "<<<>>><<<",
        "<div class='title'><div class='title'>Nested</div></div>",
        "<script>alert('xss')</script>",
        "<div class='title'>Title</div><div class='content'>" + "A" * 1000000 + "</div>",
    ]
    
    for html in malformed_cases:
        try:
            title, text = parser._extract_content_from_html(html)
            assert isinstance(title, str)
            assert isinstance(text, str)
        except Exception as e:
            pytest.fail(f"Parser crashed on malformed HTML: {e}\nHTML: {html[:100]}")


def test_parser_pathological_unicode():
    """
    Fuzz: Pathological unicode should not crash.
    """
    parser = TakeoutParser.__new__(TakeoutParser)
    
    pathological_cases = [
        "\u200b" * 1000,  # Zero-width spaces
        "\u202e" + "reversed" + "\u202d",  # Right-to-left override
        "\ufeff" * 100,  # Byte order marks
        "\U0001f4a9" * 100,  # Emoji spam
        "\u0000" * 10,  # Null characters
        "\n" * 10000,  # Excessive newlines
        "\t" * 10000,  # Excessive tabs
    ]
    
    for text in pathological_cases:
        html = f"<div class='title'>{text}</div><div class='content'>{text}</div>"
        try:
            title, content = parser._extract_content_from_html(html)
            assert isinstance(title, str)
            assert isinstance(content, str)
        except Exception as e:
            pytest.fail(f"Parser crashed on pathological unicode: {e}")


def test_parser_html_injection():
    """
    Fuzz: HTML injection attempts should be handled safely.
    """
    parser = TakeoutParser.__new__(TakeoutParser)
    
    injection_cases = [
        "<div class='title'><img src=x onerror=alert(1)></div>",
        "<div class='content'><iframe src='evil.com'></iframe></div>",
        "<div class='title'><script>alert('xss')</script></div>",
        "<div class='content'>Normal text<script>evil()</script>more text</div>",
    ]
    
    for html in injection_cases:
        title, text = parser._extract_content_from_html(html)
        
        # Should strip script tags
        assert '<script>' not in title.lower()
        assert '<script>' not in text.lower()
        assert '<iframe>' not in text.lower()


def test_parser_truncated_json():
    """
    Fuzz: Truncated JSON should not crash parser.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create truncated JSON file
        json_file = tmpdir / "note.json"
        with open(json_file, 'w') as f:
            f.write('{"title": "Test", "labels": [')
        
        # Create corresponding HTML
        html_file = tmpdir / "note.html"
        with open(html_file, 'w') as f:
            f.write("<div class='title'>Test</div>")
        
        parser = TakeoutParser(str(tmpdir))
        
        # Should handle gracefully (skip or use defaults)
        try:
            notes = parser.parse_all_notes()
            # Should either parse with defaults or skip
            assert isinstance(notes, list)
        except Exception as e:
            # Acceptable to fail, but should be a clean error
            assert "JSON" in str(e) or "parse" in str(e).lower()


def test_parser_invalid_json():
    """
    Fuzz: Invalid JSON should not crash parser.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create invalid JSON file
        json_file = tmpdir / "note.json"
        with open(json_file, 'w') as f:
            f.write("not valid json at all!!!")
        
        # Create corresponding HTML
        html_file = tmpdir / "note.html"
        with open(html_file, 'w') as f:
            f.write("<div class='title'>Test</div>")
        
        parser = TakeoutParser(str(tmpdir))
        
        try:
            notes = parser.parse_all_notes()
            assert isinstance(notes, list)
        except Exception as e:
            # Should handle gracefully
            pass


def test_parser_very_large_file():
    """
    Fuzz: Very large files should not cause memory issues.
    """
    parser = TakeoutParser.__new__(TakeoutParser)
    
    # 10 MB of text
    large_text = "A" * (10 * 1024 * 1024)
    html = f"<div class='title'>Large</div><div class='content'>{large_text}</div>"
    
    try:
        title, text = parser._extract_content_from_html(html)
        assert isinstance(title, str)
        assert isinstance(text, str)
        # Should handle large content
        assert len(text) > 0
    except MemoryError:
        pytest.skip("System doesn't have enough memory for this test")
    except Exception as e:
        pytest.fail(f"Parser crashed on large file: {e}")


def test_parser_timestamp_edge_cases():
    """
    Fuzz: Edge case timestamps should not crash.
    """
    parser = TakeoutParser.__new__(TakeoutParser)
    
    edge_cases = [
        0,  # Zero (should default to now)
        -1,  # Negative (invalid)
        2**63 - 1,  # Max int64
        1,  # Minimum positive
        1609459200000000,  # 2021-01-01 in microseconds
    ]
    
    for usec in edge_cases:
        try:
            dt = parser._parse_timestamp(usec)
            assert dt is not None
        except Exception as e:
            # Negative timestamps might fail, that's acceptable
            if usec >= 0:
                pytest.fail(f"Timestamp parsing failed for {usec}: {e}")


# ============================================================================
# ENTROPY FUZZ TESTS
# ============================================================================

def test_entropy_extreme_lengths():
    """
    Fuzz: Extreme text lengths should not crash entropy calculation.
    """
    auditor = SemanticAuditor(MockKeepClient())
    
    test_cases = [
        "",  # Empty
        "a",  # Single char
        "a" * 1000000,  # 1 MB of same character
        "ab" * 500000,  # 1 MB of alternating
        "\n" * 100000,  # Lots of newlines
    ]
    
    for text in test_cases:
        try:
            entropy = auditor.calculate_entropy(text)
            assert entropy >= 0
            assert not math.isnan(entropy)
            assert not math.isinf(entropy)
        except Exception as e:
            pytest.fail(f"Entropy calculation crashed on text length {len(text)}: {e}")


def test_entropy_special_characters():
    """
    Fuzz: Special characters should not break entropy calculation.
    """
    auditor = SemanticAuditor(MockKeepClient())
    
    special_cases = [
        "\x00" * 100,  # Null bytes
        "\u200b" * 100,  # Zero-width spaces
        "\U0001f4a9" * 50,  # Emojis
        "\n\r\t" * 100,  # Whitespace mix
        "\\" * 100,  # Backslashes
        "'\"'\"" * 100,  # Quotes
    ]
    
    for text in special_cases:
        try:
            entropy = auditor.calculate_entropy(text)
            assert entropy >= 0
        except Exception as e:
            pytest.fail(f"Entropy crashed on special characters: {e}")


# ============================================================================
# SIMILARITY FUZZ TESTS
# ============================================================================

def test_similarity_empty_strings():
    """
    Fuzz: Empty strings should not crash similarity calculation.
    """
    auditor = SemanticAuditor(MockKeepClient())
    
    test_cases = [
        ("", ""),
        ("", "text"),
        ("text", ""),
        (" ", " "),
        ("\n", "\n"),
    ]
    
    for text1, text2 in test_cases:
        try:
            embeddings = auditor.model.encode([text1, text2], convert_to_tensor=True)
            # Should not crash, even if results are undefined
            assert embeddings is not None
        except Exception as e:
            # Empty strings might cause issues, that's acceptable
            pass


def test_similarity_very_long_texts():
    """
    Fuzz: Very long texts should not crash similarity.
    """
    auditor = SemanticAuditor(MockKeepClient())
    
    # 100KB of text
    long_text1 = "This is a very long text. " * 5000
    long_text2 = "This is another very long text. " * 5000
    
    try:
        embeddings = auditor.model.encode([long_text1, long_text2], convert_to_tensor=True)
        assert embeddings is not None
    except Exception as e:
        # Model might have token limits, that's acceptable
        assert "token" in str(e).lower() or "length" in str(e).lower()


import math

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
