"""Neural Component - Pattern detection and storm identification.

The neural component uses pattern matching and heuristics to identify
suspicious regions ("storms") that need symbolic verification.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import re
from datetime import datetime


class PatternType(str, Enum):
    """Types of patterns the neural component can detect."""
    COMPLEXITY = "complexity"  # High cyclomatic complexity
    SECURITY = "security"  # Security-sensitive operations
    MEMORY = "memory"  # Memory management issues
    CONCURRENCY = "concurrency"  # Race conditions, deadlocks
    PERFORMANCE = "performance"  # Performance bottlenecks


class Pattern(BaseModel):
    """A detected pattern in code or system."""
    type: PatternType
    location: str  # File, function, or component
    description: str
    confidence: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    evidence: List[str] = []
    metadata: Dict[str, Any] = {}


class StormType(str, Enum):
    """Types of storms (suspicious regions) that need verification."""
    COMPLEXITY_STORM = "complexity_storm"  # High complexity, low coverage
    SECURITY_STORM = "security_storm"  # Security vulnerabilities
    MEMORY_STORM = "memory_storm"  # Memory leaks, corruption
    CONCURRENCY_STORM = "concurrency_storm"  # Race conditions
    PERFORMANCE_STORM = "performance_storm"  # Bottlenecks
    LOGIC_STORM = "logic_storm"  # Logical errors


class Storm(BaseModel):
    """A suspicious region that needs symbolic verification."""
    type: StormType
    location: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    patterns: List[Pattern] = []
    risk_score: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    description: str
    recommendations: List[str] = []
    detected_at: datetime = Field(default_factory=datetime.now)


class NeuralComponent:
    """Neural component for pattern detection and storm identification.
    
    This component uses heuristics and pattern matching to identify
    suspicious regions in code or systems. It doesn't prove correctness,
    but it finds areas that need symbolic verification.
    """

    def __init__(self):
        self.patterns_detected: List[Pattern] = []
        self.storms_identified: List[Storm] = []

    def detect_patterns(self, code: str, context: Dict[str, Any] = None) -> List[Pattern]:
        """Detect patterns in code or system description.
        
        Args:
            code: Code or system description to analyze
            context: Additional context (file path, metrics, etc.)
            
        Returns:
            List of detected patterns
        """
        patterns = []
        context = context or {}

        # Detect complexity patterns
        complexity_patterns = self._detect_complexity(code, context)
        patterns.extend(complexity_patterns)

        # Detect security patterns
        security_patterns = self._detect_security(code, context)
        patterns.extend(security_patterns)

        # Detect memory patterns
        memory_patterns = self._detect_memory(code, context)
        patterns.extend(memory_patterns)

        # Detect concurrency patterns
        concurrency_patterns = self._detect_concurrency(code, context)
        patterns.extend(concurrency_patterns)

        # Detect performance patterns
        performance_patterns = self._detect_performance(code, context)
        patterns.extend(performance_patterns)

        self.patterns_detected.extend(patterns)
        return patterns

    def identify_storms(self, patterns: List[Pattern], context: Dict[str, Any] = None) -> List[Storm]:
        """Identify storms (suspicious regions) from detected patterns.
        
        Args:
            patterns: List of detected patterns
            context: Additional context
            
        Returns:
            List of identified storms
        """
        storms = []
        context = context or {}

        # Group patterns by location
        location_patterns: Dict[str, List[Pattern]] = {}
        for pattern in patterns:
            if pattern.location not in location_patterns:
                location_patterns[pattern.location] = []
            location_patterns[pattern.location].append(pattern)

        # Identify storms in each location
        for location, loc_patterns in location_patterns.items():
            storm = self._analyze_location_for_storms(location, loc_patterns, context)
            if storm:
                storms.append(storm)

        self.storms_identified.extend(storms)
        return storms

    def _detect_complexity(self, code: str, context: Dict[str, Any]) -> List[Pattern]:
        """Detect complexity patterns."""
        patterns = []

        # Check for deeply nested code
        nesting_level = self._calculate_nesting_level(code)
        if nesting_level > 4:
            patterns.append(Pattern(
                type=PatternType.COMPLEXITY,
                location=context.get('location', 'unknown'),
                description=f"Deep nesting detected (level {nesting_level})",
                confidence=min(0.5 + (nesting_level - 4) * 0.1, 1.0),
                evidence=[f"Nesting level: {nesting_level}"],
                metadata={'nesting_level': nesting_level}
            ))

        # Check for long functions
        line_count = len(code.split('\n'))
        if line_count > 100:
            patterns.append(Pattern(
                type=PatternType.COMPLEXITY,
                location=context.get('location', 'unknown'),
                description=f"Long function detected ({line_count} lines)",
                confidence=min(0.5 + (line_count - 100) / 200, 1.0),
                evidence=[f"Line count: {line_count}"],
                metadata={'line_count': line_count}
            ))

        # Check for high cyclomatic complexity indicators
        if_count = len(re.findall(r'\bif\b', code))
        for_count = len(re.findall(r'\bfor\b', code))
        while_count = len(re.findall(r'\bwhile\b', code))
        branch_count = if_count + for_count + while_count

        if branch_count > 10:
            patterns.append(Pattern(
                type=PatternType.COMPLEXITY,
                location=context.get('location', 'unknown'),
                description=f"High branching complexity ({branch_count} branches)",
                confidence=min(0.6 + (branch_count - 10) * 0.04, 1.0),
                evidence=[f"Branches: {branch_count} (if: {if_count}, for: {for_count}, while: {while_count})"],
                metadata={'branch_count': branch_count}
            ))

        return patterns

    def _detect_security(self, code: str, context: Dict[str, Any]) -> List[Pattern]:
        """Detect security patterns."""
        patterns = []

        # Check for dangerous functions
        dangerous_patterns = [
            (r'eval\(', 'eval() usage detected'),
            (r'exec\(', 'exec() usage detected'),
            (r'__import__', 'dynamic import detected'),
            (r'pickle\.loads', 'pickle.loads() detected (deserialization risk)'),
            (r'subprocess\.', 'subprocess usage detected'),
            (r'os\.system', 'os.system() detected'),
        ]

        for pattern_regex, description in dangerous_patterns:
            if re.search(pattern_regex, code):
                patterns.append(Pattern(
                    type=PatternType.SECURITY,
                    location=context.get('location', 'unknown'),
                    description=description,
                    confidence=0.8,
                    evidence=[f"Pattern: {pattern_regex}"],
                    metadata={'pattern': pattern_regex}
                ))

        # Check for SQL injection risks
        if re.search(r'execute\([^?]*%s', code) or re.search(r'execute\([^?]*\+', code):
            patterns.append(Pattern(
                type=PatternType.SECURITY,
                location=context.get('location', 'unknown'),
                description="Potential SQL injection vulnerability",
                confidence=0.7,
                evidence=["String concatenation in SQL query"],
                metadata={'vulnerability': 'sql_injection'}
            ))

        return patterns

    def _detect_memory(self, code: str, context: Dict[str, Any]) -> List[Pattern]:
        """Detect memory management patterns."""
        patterns = []

        # Check for potential memory leaks
        if 'malloc' in code and 'free' not in code:
            patterns.append(Pattern(
                type=PatternType.MEMORY,
                location=context.get('location', 'unknown'),
                description="Potential memory leak (malloc without free)",
                confidence=0.6,
                evidence=["malloc found, no corresponding free"],
                metadata={'issue': 'potential_leak'}
            ))

        # Check for large allocations
        large_alloc_pattern = r'\balloc.*\b(\d+)\s*\*\s*(\d+)'
        matches = re.findall(large_alloc_pattern, code)
        for match in matches:
            size = int(match[0]) * int(match[1])
            if size > 1000000:  # > 1MB
                patterns.append(Pattern(
                    type=PatternType.MEMORY,
                    location=context.get('location', 'unknown'),
                    description=f"Large memory allocation detected ({size} bytes)",
                    confidence=0.7,
                    evidence=[f"Allocation size: {size} bytes"],
                    metadata={'size': size}
                ))

        return patterns

    def _detect_concurrency(self, code: str, context: Dict[str, Any]) -> List[Pattern]:
        """Detect concurrency patterns."""
        patterns = []

        # Check for potential race conditions
        has_threads = 'Thread' in code or 'threading' in code
        has_shared_state = 'global' in code or 'self.' in code
        has_locks = 'Lock' in code or 'mutex' in code or 'synchronized' in code

        if has_threads and has_shared_state and not has_locks:
            patterns.append(Pattern(
                type=PatternType.CONCURRENCY,
                location=context.get('location', 'unknown'),
                description="Potential race condition (threads + shared state, no locks)",
                confidence=0.7,
                evidence=["Threading detected", "Shared state detected", "No locking mechanism found"],
                metadata={'issue': 'race_condition'}
            ))

        # Check for potential deadlocks
        lock_count = len(re.findall(r'\.(acquire|lock)\(', code))
        if lock_count > 2:
            patterns.append(Pattern(
                type=PatternType.CONCURRENCY,
                location=context.get('location', 'unknown'),
                description=f"Multiple locks detected ({lock_count}), potential deadlock risk",
                confidence=0.5,
                evidence=[f"Lock acquisitions: {lock_count}"],
                metadata={'lock_count': lock_count}
            ))

        return patterns

    def _detect_performance(self, code: str, context: Dict[str, Any]) -> List[Pattern]:
        """Detect performance patterns."""
        patterns = []

        # Check for nested loops
        nested_loop_pattern = r'for\s+.*:\s*(?:[^\n]*\n\s*)*for\s+'
        nested_loops = len(re.findall(nested_loop_pattern, code))
        if nested_loops > 0:
            patterns.append(Pattern(
                type=PatternType.PERFORMANCE,
                location=context.get('location', 'unknown'),
                description=f"Nested loops detected ({nested_loops}), O(n²) or worse complexity",
                confidence=0.8,
                evidence=[f"Nested loops: {nested_loops}"],
                metadata={'nested_loops': nested_loops}
            ))

        # Check for repeated operations in loops
        if re.search(r'for\s+.*:.*\n.*\.(append|insert|extend)\(', code):
            patterns.append(Pattern(
                type=PatternType.PERFORMANCE,
                location=context.get('location', 'unknown'),
                description="List modification in loop (consider list comprehension)",
                confidence=0.6,
                evidence=["List modification inside loop"],
                metadata={'optimization': 'list_comprehension'}
            ))

        return patterns

    def _analyze_location_for_storms(self, location: str, patterns: List[Pattern], context: Dict[str, Any]) -> Optional[Storm]:
        """Analyze a location for storms based on patterns."""
        if not patterns:
            return None

        # Calculate risk score
        risk_score = sum(p.confidence for p in patterns) / len(patterns)
        risk_score = min(risk_score, 1.0)

        # Determine severity
        if risk_score >= 0.8:
            severity = "CRITICAL"
        elif risk_score >= 0.6:
            severity = "HIGH"
        elif risk_score >= 0.4:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Determine storm type (use most common pattern type)
        pattern_types = [p.type for p in patterns]
        most_common_type = max(set(pattern_types), key=pattern_types.count)

        storm_type_map = {
            PatternType.COMPLEXITY: StormType.COMPLEXITY_STORM,
            PatternType.SECURITY: StormType.SECURITY_STORM,
            PatternType.MEMORY: StormType.MEMORY_STORM,
            PatternType.CONCURRENCY: StormType.CONCURRENCY_STORM,
            PatternType.PERFORMANCE: StormType.PERFORMANCE_STORM,
        }
        storm_type = storm_type_map.get(most_common_type, StormType.LOGIC_STORM)

        # Generate recommendations
        recommendations = self._generate_recommendations(patterns)

        # Create description
        pattern_descriptions = [p.description for p in patterns]
        description = f"Storm detected at {location}: {', '.join(pattern_descriptions[:3])}"
        if len(pattern_descriptions) > 3:
            description += f" and {len(pattern_descriptions) - 3} more issues"

        return Storm(
            type=storm_type,
            location=location,
            severity=severity,
            patterns=patterns,
            risk_score=risk_score,
            description=description,
            recommendations=recommendations
        )

    def _generate_recommendations(self, patterns: List[Pattern]) -> List[str]:
        """Generate recommendations based on patterns."""
        recommendations = []

        for pattern in patterns:
            if pattern.type == PatternType.COMPLEXITY:
                recommendations.append("Refactor to reduce complexity (extract methods, simplify logic)")
            elif pattern.type == PatternType.SECURITY:
                recommendations.append("Review security implications and use safer alternatives")
            elif pattern.type == PatternType.MEMORY:
                recommendations.append("Audit memory management (ensure proper allocation/deallocation)")
            elif pattern.type == PatternType.CONCURRENCY:
                recommendations.append("Add proper synchronization (locks, mutexes, or use thread-safe structures)")
            elif pattern.type == PatternType.PERFORMANCE:
                recommendations.append("Optimize algorithm complexity or use more efficient data structures")

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        return unique_recommendations[:5]  # Top 5 recommendations

    def _calculate_nesting_level(self, code: str) -> int:
        """Calculate maximum nesting level in code."""
        max_level = 0
        current_level = 0

        for line in code.split('\n'):
            # Count leading whitespace
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                level = indent // 4  # Assuming 4-space indentation
                current_level = level
                max_level = max(max_level, current_level)

        return max_level

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected patterns and storms."""
        return {
            'total_patterns': len(self.patterns_detected),
            'total_storms': len(self.storms_identified),
            'patterns_by_type': {
                ptype.value: sum(1 for p in self.patterns_detected if p.type == ptype)
                for ptype in PatternType
            },
            'storms_by_type': {
                stype.value: sum(1 for s in self.storms_identified if s.type == stype)
                for stype in StormType
            },
            'storms_by_severity': {
                severity: sum(1 for s in self.storms_identified if s.severity == severity)
                for severity in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            },
        }
