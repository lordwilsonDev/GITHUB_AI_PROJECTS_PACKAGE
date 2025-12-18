#!/usr/bin/env python3
"""
Programming Language Learner - Vy-Nexus Technical Learning System

Learns programming languages, syntax patterns, best practices, and idioms.
Enables adaptive code generation and language understanding.

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, Counter
import hashlib


class LanguageCategory(Enum):
    """Categories of programming languages."""
    COMPILED = "compiled"
    INTERPRETED = "interpreted"
    SCRIPTING = "scripting"
    FUNCTIONAL = "functional"
    OBJECT_ORIENTED = "object_oriented"
    PROCEDURAL = "procedural"
    DECLARATIVE = "declarative"


class PatternType(Enum):
    """Types of code patterns."""
    SYNTAX = "syntax"
    IDIOM = "idiom"
    DESIGN_PATTERN = "design_pattern"
    ANTI_PATTERN = "anti_pattern"
    BEST_PRACTICE = "best_practice"
    API_USAGE = "api_usage"


@dataclass
class LanguageFeature:
    """Represents a feature of a programming language."""
    feature_id: str
    language: str
    feature_name: str
    feature_type: str
    description: str
    syntax_examples: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    learned_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CodePattern:
    """Represents a learned code pattern."""
    pattern_id: str
    language: str
    pattern_type: str
    name: str
    description: str
    code_template: str
    frequency: int = 0
    quality_score: float = 0.0
    contexts: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)


@dataclass
class LanguageKnowledge:
    """Complete knowledge about a programming language."""
    language: str
    category: str
    version: str
    features: Dict[str, LanguageFeature] = field(default_factory=dict)
    patterns: Dict[str, CodePattern] = field(default_factory=dict)
    best_practices: List[str] = field(default_factory=list)
    common_errors: List[Dict[str, str]] = field(default_factory=list)
    libraries: Dict[str, Dict] = field(default_factory=dict)
    proficiency_level: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class ProgrammingLanguageLearner:
    """Learns programming languages and their patterns."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/language_learning"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.knowledge_file = os.path.join(self.data_dir, "language_knowledge.json")
        self.patterns_file = os.path.join(self.data_dir, "code_patterns.json")
        self.learning_log_file = os.path.join(self.data_dir, "learning_log.json")
        
        self.knowledge = self._load_knowledge()
        self.patterns = self._load_patterns()
        self.learning_log = self._load_learning_log()
        
        # Initialize with basic language knowledge
        self._initialize_base_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Dict]:
        """Load language knowledge."""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_knowledge(self):
        """Save language knowledge."""
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, List[Dict]]:
        """Load code patterns."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_patterns(self):
        """Save code patterns."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_learning_log(self) -> List[Dict]:
        """Load learning log."""
        if os.path.exists(self.learning_log_file):
            with open(self.learning_log_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_learning_log(self):
        """Save learning log."""
        with open(self.learning_log_file, 'w') as f:
            json.dump(self.learning_log, f, indent=2)
    
    def _initialize_base_knowledge(self):
        """Initialize base knowledge for common languages."""
        base_languages = {
            'python': {
                'category': LanguageCategory.INTERPRETED.value,
                'version': '3.x',
                'key_features': ['dynamic_typing', 'indentation', 'list_comprehensions'],
                'common_patterns': ['context_managers', 'decorators', 'generators']
            },
            'javascript': {
                'category': LanguageCategory.INTERPRETED.value,
                'version': 'ES6+',
                'key_features': ['async_await', 'promises', 'arrow_functions'],
                'common_patterns': ['callbacks', 'closures', 'prototypes']
            },
            'java': {
                'category': LanguageCategory.COMPILED.value,
                'version': '17',
                'key_features': ['static_typing', 'oop', 'interfaces'],
                'common_patterns': ['singleton', 'factory', 'builder']
            }
        }
        
        for lang, info in base_languages.items():
            if lang not in self.knowledge:
                self.knowledge[lang] = {
                    'language': lang,
                    'category': info['category'],
                    'version': info['version'],
                    'features': {},
                    'patterns': {},
                    'best_practices': [],
                    'common_errors': [],
                    'libraries': {},
                    'proficiency_level': 0.3,  # Basic knowledge
                    'last_updated': datetime.now().isoformat()
                }
        
        self._save_knowledge()
    
    def learn_language_feature(self, language: str, feature_name: str,
                              feature_type: str, description: str,
                              syntax_examples: Optional[List[str]] = None) -> LanguageFeature:
        """Learn a new language feature."""
        
        if language not in self.knowledge:
            self.knowledge[language] = {
                'language': language,
                'category': LanguageCategory.INTERPRETED.value,
                'version': 'unknown',
                'features': {},
                'patterns': {},
                'best_practices': [],
                'common_errors': [],
                'libraries': {},
                'proficiency_level': 0.1,
                'last_updated': datetime.now().isoformat()
            }
        
        feature_id = f"{language}_{feature_name}_{hashlib.md5(feature_name.encode()).hexdigest()[:8]}"
        
        feature = LanguageFeature(
            feature_id=feature_id,
            language=language,
            feature_name=feature_name,
            feature_type=feature_type,
            description=description,
            syntax_examples=syntax_examples or []
        )
        
        self.knowledge[language]['features'][feature_id] = asdict(feature)
        self.knowledge[language]['last_updated'] = datetime.now().isoformat()
        
        # Update proficiency
        self._update_proficiency(language)
        
        # Log learning
        self._log_learning(
            language=language,
            item_type='feature',
            item_name=feature_name,
            details={'feature_type': feature_type}
        )
        
        self._save_knowledge()
        
        return feature
    
    def learn_code_pattern(self, language: str, pattern_name: str,
                          pattern_type: str, code_template: str,
                          description: str,
                          contexts: Optional[List[str]] = None) -> CodePattern:
        """Learn a code pattern."""
        
        pattern_id = f"{language}_{pattern_name}_{hashlib.md5(code_template.encode()).hexdigest()[:8]}"
        
        pattern = CodePattern(
            pattern_id=pattern_id,
            language=language,
            pattern_type=pattern_type,
            name=pattern_name,
            description=description,
            code_template=code_template,
            frequency=1,
            quality_score=0.5,
            contexts=contexts or []
        )
        
        # Add to patterns
        if language not in self.patterns:
            self.patterns[language] = []
        
        # Check if pattern already exists
        existing = None
        for i, p in enumerate(self.patterns[language]):
            if p['name'] == pattern_name:
                existing = i
                break
        
        if existing is not None:
            # Update frequency
            self.patterns[language][existing]['frequency'] += 1
        else:
            self.patterns[language].append(asdict(pattern))
        
        # Also add to language knowledge
        if language in self.knowledge:
            self.knowledge[language]['patterns'][pattern_id] = asdict(pattern)
        
        # Update proficiency
        self._update_proficiency(language)
        
        # Log learning
        self._log_learning(
            language=language,
            item_type='pattern',
            item_name=pattern_name,
            details={'pattern_type': pattern_type}
        )
        
        self._save_patterns()
        self._save_knowledge()
        
        return pattern
    
    def learn_best_practice(self, language: str, practice: str,
                           rationale: str):
        """Learn a best practice for a language."""
        
        if language not in self.knowledge:
            self.learn_language_feature(language, 'basic', 'core', 'Basic language knowledge')
        
        best_practice = {
            'practice': practice,
            'rationale': rationale,
            'learned_at': datetime.now().isoformat()
        }
        
        self.knowledge[language]['best_practices'].append(best_practice)
        
        # Log learning
        self._log_learning(
            language=language,
            item_type='best_practice',
            item_name=practice,
            details={'rationale': rationale}
        )
        
        self._save_knowledge()
    
    def learn_common_error(self, language: str, error_type: str,
                          description: str, solution: str):
        """Learn a common error and its solution."""
        
        if language not in self.knowledge:
            self.learn_language_feature(language, 'basic', 'core', 'Basic language knowledge')
        
        error = {
            'error_type': error_type,
            'description': description,
            'solution': solution,
            'learned_at': datetime.now().isoformat()
        }
        
        self.knowledge[language]['common_errors'].append(error)
        
        # Log learning
        self._log_learning(
            language=language,
            item_type='error',
            item_name=error_type,
            details={'solution': solution}
        )
        
        self._save_knowledge()
    
    def learn_library(self, language: str, library_name: str,
                     purpose: str, common_functions: Optional[List[str]] = None):
        """Learn about a library/framework."""
        
        if language not in self.knowledge:
            self.learn_language_feature(language, 'basic', 'core', 'Basic language knowledge')
        
        library_info = {
            'name': library_name,
            'purpose': purpose,
            'common_functions': common_functions or [],
            'learned_at': datetime.now().isoformat()
        }
        
        self.knowledge[language]['libraries'][library_name] = library_info
        
        # Log learning
        self._log_learning(
            language=language,
            item_type='library',
            item_name=library_name,
            details={'purpose': purpose}
        )
        
        self._save_knowledge()
    
    def analyze_code_sample(self, language: str, code: str) -> Dict[str, Any]:
        """Analyze a code sample to extract patterns and learn."""
        
        analysis = {
            'language': language,
            'lines_of_code': len(code.split('\n')),
            'patterns_found': [],
            'features_used': [],
            'potential_improvements': [],
            'quality_score': 0.0
        }
        
        # Extract patterns based on language
        if language == 'python':
            analysis.update(self._analyze_python_code(code))
        elif language == 'javascript':
            analysis.update(self._analyze_javascript_code(code))
        elif language == 'java':
            analysis.update(self._analyze_java_code(code))
        
        # Learn from the code
        for pattern in analysis['patterns_found']:
            if pattern not in [p['name'] for p in self.patterns.get(language, [])]:
                self.learn_code_pattern(
                    language=language,
                    pattern_name=pattern,
                    pattern_type=PatternType.IDIOM.value,
                    code_template=code[:200],  # Sample
                    description=f"Pattern found in code analysis"
                )
        
        return analysis
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code."""
        patterns = []
        features = []
        
        # Check for common patterns
        if 'with ' in code:
            patterns.append('context_manager')
            features.append('context_managers')
        
        if '@' in code and 'def ' in code:
            patterns.append('decorator')
            features.append('decorators')
        
        if 'yield' in code:
            patterns.append('generator')
            features.append('generators')
        
        if '[' in code and 'for ' in code and ']' in code:
            patterns.append('list_comprehension')
            features.append('comprehensions')
        
        if 'async def' in code or 'await ' in code:
            patterns.append('async_await')
            features.append('async_programming')
        
        # Quality checks
        quality_score = 0.5
        improvements = []
        
        if 'import *' in code:
            improvements.append('Avoid wildcard imports')
            quality_score -= 0.1
        
        if code.count('\n') > 0:
            avg_line_length = len(code) / code.count('\n')
            if avg_line_length > 100:
                improvements.append('Consider breaking long lines')
                quality_score -= 0.05
        
        return {
            'patterns_found': patterns,
            'features_used': features,
            'potential_improvements': improvements,
            'quality_score': max(0, min(1, quality_score))
        }
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript code."""
        patterns = []
        features = []
        
        if '=>' in code:
            patterns.append('arrow_function')
            features.append('arrow_functions')
        
        if 'async' in code or 'await' in code:
            patterns.append('async_await')
            features.append('async_programming')
        
        if '.then(' in code:
            patterns.append('promise')
            features.append('promises')
        
        if 'const ' in code or 'let ' in code:
            patterns.append('modern_variable_declaration')
            features.append('es6_syntax')
        
        quality_score = 0.5
        improvements = []
        
        if 'var ' in code:
            improvements.append('Use const/let instead of var')
            quality_score -= 0.1
        
        if '==' in code and '===' not in code:
            improvements.append('Use === for strict equality')
            quality_score -= 0.05
        
        return {
            'patterns_found': patterns,
            'features_used': features,
            'potential_improvements': improvements,
            'quality_score': max(0, min(1, quality_score))
        }
    
    def _analyze_java_code(self, code: str) -> Dict[str, Any]:
        """Analyze Java code."""
        patterns = []
        features = []
        
        if 'interface ' in code:
            patterns.append('interface')
            features.append('interfaces')
        
        if 'extends ' in code:
            patterns.append('inheritance')
            features.append('inheritance')
        
        if 'implements ' in code:
            patterns.append('interface_implementation')
            features.append('polymorphism')
        
        if '@Override' in code:
            patterns.append('method_override')
            features.append('annotations')
        
        quality_score = 0.5
        improvements = []
        
        return {
            'patterns_found': patterns,
            'features_used': features,
            'potential_improvements': improvements,
            'quality_score': quality_score
        }
    
    def _update_proficiency(self, language: str):
        """Update proficiency level for a language."""
        if language not in self.knowledge:
            return
        
        lang_data = self.knowledge[language]
        
        # Calculate proficiency based on knowledge
        features_count = len(lang_data['features'])
        patterns_count = len(lang_data['patterns'])
        practices_count = len(lang_data['best_practices'])
        libraries_count = len(lang_data['libraries'])
        
        # Weighted proficiency
        proficiency = min(1.0, (
            features_count * 0.02 +
            patterns_count * 0.03 +
            practices_count * 0.05 +
            libraries_count * 0.04
        ))
        
        lang_data['proficiency_level'] = proficiency
    
    def _log_learning(self, language: str, item_type: str,
                     item_name: str, details: Dict[str, Any]):
        """Log a learning event."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'language': language,
            'item_type': item_type,
            'item_name': item_name,
            'details': details
        }
        
        self.learning_log.append(log_entry)
        self._save_learning_log()
    
    def get_language_knowledge(self, language: str) -> Optional[Dict]:
        """Get knowledge about a language."""
        return self.knowledge.get(language)
    
    def get_patterns_for_language(self, language: str,
                                 pattern_type: Optional[str] = None) -> List[Dict]:
        """Get code patterns for a language."""
        patterns = self.patterns.get(language, [])
        
        if pattern_type:
            patterns = [p for p in patterns if p['pattern_type'] == pattern_type]
        
        # Sort by frequency
        patterns.sort(key=lambda x: x['frequency'], reverse=True)
        
        return patterns
    
    def compare_languages(self, lang1: str, lang2: str) -> Dict[str, Any]:
        """Compare two programming languages."""
        if lang1 not in self.knowledge or lang2 not in self.knowledge:
            return {'error': 'One or both languages not found'}
        
        data1 = self.knowledge[lang1]
        data2 = self.knowledge[lang2]
        
        comparison = {
            'languages': [lang1, lang2],
            'categories': [data1['category'], data2['category']],
            'proficiency': {
                lang1: data1['proficiency_level'],
                lang2: data2['proficiency_level']
            },
            'features_count': {
                lang1: len(data1['features']),
                lang2: len(data2['features'])
            },
            'patterns_count': {
                lang1: len(data1['patterns']),
                lang2: len(data2['patterns'])
            },
            'common_patterns': self._find_common_patterns(lang1, lang2)
        }
        
        return comparison
    
    def _find_common_patterns(self, lang1: str, lang2: str) -> List[str]:
        """Find common patterns between two languages."""
        patterns1 = set(p['name'] for p in self.patterns.get(lang1, []))
        patterns2 = set(p['name'] for p in self.patterns.get(lang2, []))
        
        return list(patterns1.intersection(patterns2))
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress."""
        summary = {
            'languages_learned': len(self.knowledge),
            'total_features': sum(len(lang['features']) for lang in self.knowledge.values()),
            'total_patterns': sum(len(lang['patterns']) for lang in self.knowledge.values()),
            'total_best_practices': sum(len(lang['best_practices']) for lang in self.knowledge.values()),
            'languages_by_proficiency': [],
            'recent_learning': self.learning_log[-10:] if len(self.learning_log) > 10 else self.learning_log
        }
        
        # Sort languages by proficiency
        for lang, data in self.knowledge.items():
            summary['languages_by_proficiency'].append({
                'language': lang,
                'proficiency': data['proficiency_level']
            })
        
        summary['languages_by_proficiency'].sort(
            key=lambda x: x['proficiency'],
            reverse=True
        )
        
        return summary


if __name__ == "__main__":
    # Example usage
    learner = ProgrammingLanguageLearner()
    
    # Learn Python features
    learner.learn_language_feature(
        'python',
        'list_comprehension',
        'syntax',
        'Concise way to create lists',
        syntax_examples=['[x**2 for x in range(10)]']
    )
    
    # Learn a pattern
    learner.learn_code_pattern(
        'python',
        'context_manager',
        PatternType.BEST_PRACTICE.value,
        'with open(file) as f:\n    data = f.read()',
        'Automatic resource management',
        contexts=['file_handling', 'resource_management']
    )
    
    # Learn best practice
    learner.learn_best_practice(
        'python',
        'Use list comprehensions instead of map/filter when simple',
        'More readable and Pythonic'
    )
    
    # Analyze code
    sample_code = """
with open('file.txt') as f:
    data = [line.strip() for line in f if line]
    """
    
    analysis = learner.analyze_code_sample('python', sample_code)
    
    print("\nCode Analysis:")
    print(f"Patterns found: {analysis['patterns_found']}")
    print(f"Features used: {analysis['features_used']}")
    print(f"Quality score: {analysis['quality_score']:.2f}")
    
    # Get learning summary
    summary = learner.get_learning_summary()
    print(f"\nLearning Summary:")
    print(f"Languages learned: {summary['languages_learned']}")
    print(f"Total patterns: {summary['total_patterns']}")
    print(f"Total features: {summary['total_features']}")
