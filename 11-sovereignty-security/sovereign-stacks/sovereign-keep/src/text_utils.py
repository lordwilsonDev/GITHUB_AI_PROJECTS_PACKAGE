"""
Sovereign Keep Protocol - Pure Text Utilities
Pure functions for text processing (no model loading).
"""

import math
import re
import unicodedata
from typing import List
from datetime import datetime, timezone


def normalize_text(text: str) -> str:
    """
    Canonical text normalization for comparison.
    
    FIX #2: Use split() + join() for guaranteed idempotence and whitespace collapse.
    Python's split() handles ALL whitespace (space, tab, newline, etc.) automatically.
    
    Fixes:
    - Idempotence (normalize(normalize(x)) == normalize(x))
    - Whitespace collapsing (no consecutive spaces)
    - Unicode normalization (NFKC)
    
    Args:
        text: Input string
        
    Returns:
        Normalized string
    """
    if text is None or not text:
        return ""
    
    # Unicode normalization (NFKC: compatibility decomposition + canonical composition)
    text = unicodedata.normalize("NFKC", text)
    
    # Case folding (more aggressive than lower())
    text = text.casefold()
    
    # Split by ANY whitespace and rejoin with single space
    # This guarantees no consecutive spaces and is idempotent
    text = " ".join(text.split())
    
    return text


def shannon_entropy(text: str) -> float:
    """
    Calculate Shannon entropy of text (pure function, no model loading).
    Higher entropy = more unique/complex content.
    
    FIX #1: O(N) complexity using Counter instead of O(N^2) text.count()
    
    Args:
        text: Input text string
        
    Returns:
        float: Shannon entropy value (bits per character)
    """
    if not text or len(text) == 0:
        return 0.0
    
    # O(N) optimization using Counter (single pass)
    from collections import Counter
    counts = Counter(text)
    length = len(text)
    
    # Shannon entropy formula: H(X) = -Σ(p(x) * log2(p(x)))
    probs = [count / length for count in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs)
    
    return entropy


def to_utc_aware(dt: datetime) -> datetime:
    """
    Convert datetime to UTC-aware (Fix #4: Timezone handling).
    
    Args:
        dt: Input datetime (naive or aware)
        
    Returns:
        UTC-aware datetime
    """
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        # Assume naive datetimes are UTC
        return dt.replace(tzinfo=timezone.utc)
    # Convert to UTC
    return dt.astimezone(timezone.utc)


def strip_boilerplate(text: str) -> str:
    """
    Remove common boilerplate (email signatures, footers) before analysis.
    
    Args:
        text: Input text
        
    Returns:
        Text with boilerplate removed
    """
    lines = text.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        # Stop at signature markers
        if stripped == "--" or "sent from my" in stripped.lower():
            break
        out.append(line)
    return "\n".join(out)


def has_negation(text: str) -> bool:
    """
    Detect negation words in text (Fix #6: Negation veto).
    
    Args:
        text: Input text
        
    Returns:
        True if negation detected
    """
    NEG_WORDS = {"not", "no", "never", "n't", "without", "cannot", 
                 "can't", "won't", "don't", "didn't", "isn't", "aren't",
                 "wasn't", "weren't", "hasn't", "haven't", "hadn't"}
    tokens = set(normalize_text(text).split())
    return any(word in tokens for word in NEG_WORDS)


def extract_numbers(text: str) -> List[float]:
    """
    Extract numeric values from text (Fix #6: Numeric veto).
    
    Args:
        text: Input text
        
    Returns:
        List of numeric values
    """
    # Match numbers with optional commas and decimals
    matches = re.findall(r"\b\d[\d,]*(?:\.\d+)?\b", text)
    numbers = []
    for match in matches:
        try:
            numbers.append(float(match.replace(",", "")))
        except ValueError:
            continue
    return numbers


def numeric_conflict(text_a: str, text_b: str, threshold=100.0) -> bool:
    """
    Check if texts have conflicting numeric values (>= threshold ratio).
    
    Args:
        text_a: First text
        text_b: Second text
        threshold: Ratio threshold for conflict (default 100x)
        
    Returns:
        True if numeric conflict detected
    """
    nums_a = extract_numbers(text_a)
    nums_b = extract_numbers(text_b)
    
    if not nums_a or not nums_b:
        return False
        
    # Check all pairs for large ratio differences
    for a in nums_a:
        for b in nums_b:
            if a > 0 and b > 0:
                ratio = max(a, b) / min(a, b)
                if ratio >= threshold:
                    return True
    return False


def negation_conflict(text_a: str, text_b: str) -> bool:
    """
    Check if one text has negation and the other doesn't (XOR).
    
    Args:
        text_a: First text
        text_b: Second text
        
    Returns:
        True if negation conflict (one has, one doesn't)
    """
    return has_negation(text_a) ^ has_negation(text_b)  # XOR
