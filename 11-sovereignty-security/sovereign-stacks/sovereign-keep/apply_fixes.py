#!/usr/bin/env python3
"""
Apply all systematic fixes to Sovereign Keep Protocol.
"""

import re
import sys
from pathlib import Path

def fix_analysis_py():
    """Fix analysis.py: add model singleton and import pure functions."""
    path = Path('src/analysis.py')
    content = path.read_text()
    
    # Add imports at the top
    imports_to_add = '''
from datetime import datetime, timezone
from .text_utils import (
    normalize_text, shannon_entropy, to_utc_aware,
    strip_boilerplate, numeric_conflict, negation_conflict
)
'''
    
    # Add model singleton before class
    singleton_code = '''
# ============================================================================
# MODULE-LEVEL MODEL SINGLETON (Fix #1: Prevents repeated model loading)
# ============================================================================
_MODEL_CACHE = {}

def get_embedding_model(model_name='all-MiniLM-L6-v2'):
    """Get or create the embedding model singleton."""
    if model_name not in _MODEL_CACHE:
        print(f"[Analysis] Loading embedding model: {model_name}...")
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
        print(f"[Analysis] ✓ Model loaded successfully.")
    return _MODEL_CACHE[model_name]

'''
    
    # Replace imports
    content = content.replace(
        'import numpy as np',
        f'import numpy as np{imports_to_add}'
    )
    
    # Add singleton before class
    content = content.replace(
        'class SemanticAuditor:',
        f'{singleton_code}\nclass SemanticAuditor:'
    )
    
    # Fix __init__ to use singleton and make keep_client optional
    old_init = '''    def __init__(self, keep_client, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the semantic auditor.
        
        Args:
            keep_client: Authenticated gkeepapi.Keep instance
            model_name: Sentence transformer model to use for embeddings
        """
        self.keep = keep_client
        print(f"[Analysis] Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"[Analysis] ✓ Model loaded successfully.")'''
    
    new_init = '''    def __init__(self, keep_client=None, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the semantic auditor.
        
        Args:
            keep_client: Authenticated gkeepapi.Keep instance (optional for testing)
            model_name: Sentence transformer model to use for embeddings
        """
        self.keep = keep_client
        # Use singleton model (Fix #1)
        self.model = get_embedding_model(model_name)'''
    
    content = content.replace(old_init, new_init)
    
    # Replace calculate_entropy to use pure function
    content = re.sub(
        r'def calculate_entropy\(self, text: str\) -> float:.*?return entropy',
        '''def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy (wrapper for pure function)."""
        return shannon_entropy(text)''',
        content,
        flags=re.DOTALL
    )
    
    # Add normalize wrapper
    if 'def normalize(self' not in content:
        content = content.replace(
            '    def calculate_entropy',
            '''    def normalize(self, text: str) -> str:
        """Normalize text (wrapper for pure function)."""
        return normalize_text(text)
    
    def calculate_entropy'''
        )
    
    path.write_text(content)
    print("✓ Fixed analysis.py")

if __name__ == '__main__':
    try:
        fix_analysis_py()
        print("\n✓ All fixes applied successfully!")
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
