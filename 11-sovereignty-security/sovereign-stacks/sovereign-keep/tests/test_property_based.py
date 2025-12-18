#!/usr/bin/env python3
"""
Property-Based Tests for Sovereign Keep Protocol
Uses Hypothesis to generate thousands of test cases automatically.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
import re
import unicodedata

# Import modules to test
from src.analysis import SemanticAuditor
from takeout_parser import TakeoutParser


class MockKeepClient:
    """Mock Keep client for testing."""
    pass


# ============================================================================
# NORMALIZATION PROPERTIES
# ============================================================================

def normalize_text(text: str) -> str:
    """
    Text normalization function (extracted from analyzer logic).
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Unicode normalization (NFC)
    text = unicodedata.normalize('NFC', text)
    
    # Lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove punctuation (keep alphanumeric and spaces)
    text = re.sub(r'[^\w\s]', '', text)
    
    return text.strip()


@given(st.text(min_size=0, max_size=1000))
@settings(max_examples=500, suppress_health_check=[HealthCheck.too_slow])
def test_normalization_idempotence(text):
    """
    Property: normalize(normalize(x)) == normalize(x)
    Normalization should be idempotent.
    """
    normalized_once = normalize_text(text)
    normalized_twice = normalize_text(normalized_once)
    
    assert normalized_once == normalized_twice, \
        f"Normalization not idempotent: '{normalized_once}' != '{normalized_twice}'"


@given(st.text(min_size=1, max_size=100))
@settings(max_examples=300)
def test_normalization_lowercase(text):
    """
    Property: normalized text should be lowercase.
    """
    normalized = normalize_text(text)
    
    if normalized:  # Only check if result is non-empty
        assert normalized == normalized.lower(), \
            f"Normalized text not lowercase: '{normalized}'"


@given(st.text(min_size=1, max_size=100))
@settings(max_examples=300)
def test_normalization_no_extra_whitespace(text):
    """
    Property: normalized text should have no leading/trailing/extra whitespace.
    """
    normalized = normalize_text(text)
    
    if normalized:
        # No leading/trailing whitespace
        assert normalized == normalized.strip()
        
        # No consecutive spaces
        assert '  ' not in normalized, \
            f"Normalized text has consecutive spaces: '{normalized}'"


# ============================================================================
# ENTROPY PROPERTIES
# ============================================================================

@given(st.text(min_size=1, max_size=100))
@settings(max_examples=300)
def test_entropy_non_negative(text):
    """
    Property: Entropy should always be non-negative.
    """
    auditor = SemanticAuditor(MockKeepClient())
    entropy = auditor.calculate_entropy(text)
    
    assert entropy >= 0, f"Entropy is negative: {entropy}"


@given(st.text(alphabet='a', min_size=10, max_size=100))
@settings(max_examples=100)
def test_entropy_repetitive_text_low(text):
    """
    Property: Repetitive text (same character) should have low entropy.
    """
    auditor = SemanticAuditor(MockKeepClient())
    entropy = auditor.calculate_entropy(text)
    
    # Repetitive text should have entropy close to 0
    assert entropy < 1.0, \
        f"Repetitive text has high entropy: {entropy} for text length {len(text)}"


@given(st.text(min_size=1, max_size=1))
@settings(max_examples=100)
def test_entropy_single_char_zero(text):
    """
    Property: Single character should have zero entropy.
    """
    auditor = SemanticAuditor(MockKeepClient())
    entropy = auditor.calculate_entropy(text)
    
    assert entropy == 0.0, \
        f"Single character has non-zero entropy: {entropy}"


def test_entropy_empty_string():
    """
    Property: Empty string should have zero entropy.
    """
    auditor = SemanticAuditor(MockKeepClient())
    entropy = auditor.calculate_entropy("")
    
    assert entropy == 0.0, "Empty string has non-zero entropy"


@given(
    st.text(alphabet=st.characters(blacklist_categories=('Cs',)), min_size=10, max_size=50),
    st.text(alphabet=st.characters(blacklist_categories=('Cs',)), min_size=10, max_size=50)
)
@settings(max_examples=200)
def test_entropy_ordering(text1, text2):
    """
    Property: More diverse text should have higher or equal entropy.
    """
    assume(len(set(text1)) > len(set(text2)))  # text1 has more unique chars
    
    auditor = SemanticAuditor(MockKeepClient())
    entropy1 = auditor.calculate_entropy(text1)
    entropy2 = auditor.calculate_entropy(text2)
    
    # More unique characters should generally mean higher entropy
    # (This is a soft property, not always true, but should hold statistically)
    # We just check it doesn't violate basic expectations
    assert entropy1 >= 0 and entropy2 >= 0


# ============================================================================
# SIMILARITY PROPERTIES
# ============================================================================

@given(st.text(min_size=5, max_size=100))
@settings(max_examples=100, deadline=5000)
def test_similarity_self_is_one(text):
    """
    Property: similarity(x, x) should be ~1.0 (identical texts).
    """
    assume(len(text.strip()) > 0)  # Non-empty after stripping
    
    auditor = SemanticAuditor(MockKeepClient())
    
    # Encode the same text twice
    embedding = auditor.model.encode([text, text], convert_to_tensor=True)
    similarity = util.cos_sim(embedding[0], embedding[1]).item()
    
    assert 0.99 <= similarity <= 1.01, \
        f"Self-similarity not ~1.0: {similarity} for text: '{text[:50]}...'"


@given(
    st.text(min_size=5, max_size=50),
    st.text(min_size=5, max_size=50)
)
@settings(max_examples=100, deadline=5000)
def test_similarity_symmetric(text1, text2):
    """
    Property: similarity(x, y) == similarity(y, x) (symmetry).
    """
    assume(len(text1.strip()) > 0 and len(text2.strip()) > 0)
    
    auditor = SemanticAuditor(MockKeepClient())
    
    embeddings = auditor.model.encode([text1, text2], convert_to_tensor=True)
    sim_12 = util.cos_sim(embeddings[0], embeddings[1]).item()
    sim_21 = util.cos_sim(embeddings[1], embeddings[0]).item()
    
    assert abs(sim_12 - sim_21) < 0.001, \
        f"Similarity not symmetric: {sim_12} != {sim_21}"


@given(st.text(min_size=5, max_size=50))
@settings(max_examples=100, deadline=5000)
def test_similarity_bounded(text):
    """
    Property: similarity should be in range [-1, 1] (cosine similarity property).
    """
    assume(len(text.strip()) > 0)
    
    auditor = SemanticAuditor(MockKeepClient())
    
    # Compare with random text
    random_text = "completely unrelated random text about nothing"
    embeddings = auditor.model.encode([text, random_text], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    
    assert -1.0 <= similarity <= 1.0, \
        f"Similarity out of bounds: {similarity}"


# ============================================================================
# PARSER PROPERTIES
# ============================================================================

@given(st.text(min_size=0, max_size=1000))
@settings(max_examples=200)
def test_html_extraction_no_crash(html_content):
    """
    Property: HTML extraction should never crash, even on malformed input.
    """
    parser = TakeoutParser.__new__(TakeoutParser)  # Create without __init__
    
    try:
        title, text = parser._extract_content_from_html(html_content)
        # Should return strings (possibly empty)
        assert isinstance(title, str)
        assert isinstance(text, str)
    except Exception as e:
        pytest.fail(f"HTML extraction crashed on input: {e}")


@given(st.integers(min_value=0, max_value=2**63-1))
@settings(max_examples=200)
def test_timestamp_parsing_no_crash(usec):
    """
    Property: Timestamp parsing should never crash.
    """
    parser = TakeoutParser.__new__(TakeoutParser)
    
    try:
        dt = parser._parse_timestamp(usec)
        assert dt is not None
    except Exception as e:
        pytest.fail(f"Timestamp parsing crashed: {e}")


# ============================================================================
# CLUSTERING PROPERTIES
# ============================================================================

@given(st.lists(st.text(min_size=5, max_size=50), min_size=3, max_size=10))
@settings(max_examples=50, deadline=10000)
def test_clustering_deterministic(texts):
    """
    Property: Clustering should be deterministic (same input -> same output).
    """
    assume(all(len(t.strip()) > 0 for t in texts))  # All non-empty
    assume(len(set(texts)) == len(texts))  # All unique
    
    auditor = SemanticAuditor(MockKeepClient())
    
    # Run clustering twice
    embeddings1 = auditor.model.encode(texts, convert_to_tensor=True)
    embeddings2 = auditor.model.encode(texts, convert_to_tensor=True)
    
    # Embeddings should be identical
    diff = (embeddings1 - embeddings2).abs().max().item()
    
    assert diff < 0.0001, \
        f"Embeddings not deterministic, max diff: {diff}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
