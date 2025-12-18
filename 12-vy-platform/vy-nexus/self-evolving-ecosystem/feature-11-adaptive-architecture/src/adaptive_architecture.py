"""Adaptive Architecture System for vy-nexus Self-Evolving AI Ecosystem.

This module provides adaptive architecture capabilities that modify system
architecture based on usage patterns, scale resources dynamically, optimize
data flows, enhance security, and improve resilience.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict


class ComponentType(Enum):
    """Types of system components."""
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    WORKER = "worker"
    STORAGE = "storage"
    NETWORK = "network"
    COMPUTE = "compute"


class ScalingAction(Enum):
    """Resource scaling actions."""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    OPTIMIZE = "optimize"


class SecurityLevel(Enum):
    """Security protection levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class ThreatType(Enum):
    """Types of security threats."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    DOS_ATTACK = "dos_attack"
    MALWARE = "malware"
    INJECTION = "injection"
    XSS = "xss"
    CSRF = "csrf"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class ResilienceStrategy(Enum):
    """Resilience improvement strategies."""
    RETRY = "retry"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK = "fallback"
    TIMEOUT = "timeout"
    BULKHEAD = "bulkhead"
    CACHE = "cache"
    REDUNDANCY = "redundancy"
    GRACEFUL_DEGRADATION = "graceful_degradation"


@dataclass
class ArchitectureChange:
    """Represents an architecture modification."""
    component: ComponentType
    change_type: str
    description: str
    reason: str
    impact: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    applied: bool = False
    rollback_available: bool = True


@dataclass
class ResourceMetrics:
    """Resource utilization metrics."""
    component: ComponentType
    cpu_usage: float  # 0.0 to 1.0
    memory_usage: float  # 0.0 to 1.0
    disk_usage: float  # 0.0 to 1.0
    network_usage: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DataFlowMetrics:
    """Data flow performance metrics."""
    pipeline_name: str
    throughput: float  # items per second
    latency: float  # seconds
    error_rate: float  # 0.0 to 1.0
    bottleneck: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityThreat:
    """Detected security threat."""
    threat_type: ThreatType
    severity: float  # 0.0 to 1.0
    source: str
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    mitigated: bool = False


@dataclass
class ResilienceImprovement:
    """Resilience improvement action."""
    strategy: ResilienceStrategy
    component: ComponentType
    description: str
    effectiveness: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    active: bool = True


class ArchitectureModifier:
    """Modifies system architecture based on usage patterns."""
    
    def __init__(self, max_changes: int = 1000):
        self.max_changes = max_changes
        self.changes: List[ArchitectureChange] = []
        self.usage_patterns: Dict[ComponentType, List[float]] = defaultdict(list)
        
    def record_usage(self, component: ComponentType, usage: float) -> None:
        """Record component usage pattern."""
        self.usage_patterns[component].append(usage)
        # Keep last 1000 measurements
        if len(self.usage_patterns[component]) > 1000:
            self.usage_patterns[component] = self.usage_patterns[component][-1000:]
    
    def analyze_patterns(self, component: ComponentType) -> Dict[str, Any]:
        """Analyze usage patterns for a component."""
        if component not in self.usage_patterns or not self.usage_patterns[component]:
            return {"avg_usage": 0.0, "peak_usage": 0.0, "trend": "stable"}
        
        usage = self.usage_patterns[component]
        avg_usage = sum(usage) / len(usage)
        peak_usage = max(usage)
        
        # Determine trend
        if len(usage) >= 10:
            recent = sum(usage[-10:]) / 10
            older = sum(usage[:10]) / 10
            if recent > older * 1.2:
                trend = "increasing"
            elif recent < older * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "avg_usage": avg_usage,
            "peak_usage": peak_usage,
            "trend": trend
        }
    
    def propose_change(self, component: ComponentType, change_type: str,
                      description: str, reason: str, impact: float) -> ArchitectureChange:
        """Propose an architecture change."""
        change = ArchitectureChange(
            component=component,
            change_type=change_type,
            description=description,
            reason=reason,
            impact=impact
        )
        
        self.changes.append(change)
        if len(self.changes) > self.max_changes:
            self.changes = self.changes[-self.max_changes:]
        
        return change
    
    def apply_change(self, change: ArchitectureChange) -> bool:
        """Apply an architecture change."""
        if change in self.changes:
            change.applied = True
            return True
        return False
    
    def get_pending_changes(self) -> List[ArchitectureChange]:
        """Get all pending (unapplied) changes."""
        return [c for c in self.changes if not c.applied]
    
    def get_applied_changes(self, since: Optional[datetime] = None) -> List[ArchitectureChange]:
        """Get applied changes, optionally filtered by time."""
        applied = [c for c in self.changes if c.applied]
        if since:
            applied = [c for c in applied if c.timestamp >= since]
        return applied


class ResourceScaler:
    """Dynamically scales resources based on workload."""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: List[ResourceMetrics] = []
        self.scaling_history: List[Dict[str, Any]] = []
        self.thresholds = {
            "cpu_high": 0.8,
            "cpu_low": 0.3,
            "memory_high": 0.85,
            "memory_low": 0.4,
            "disk_high": 0.9,
            "network_high": 0.75
        }
    
    def record_metrics(self, metrics: ResourceMetrics) -> None:
        """Record resource metrics."""
        self.metrics.append(metrics)
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
    
    def analyze_utilization(self, component: ComponentType) -> Dict[str, float]:
        """Analyze resource utilization for a component."""
        component_metrics = [m for m in self.metrics if m.component == component]
        
        if not component_metrics:
            return {"cpu": 0.0, "memory": 0.0, "disk": 0.0, "network": 0.0}
        
        recent = component_metrics[-100:]  # Last 100 measurements
        
        return {
            "cpu": sum(m.cpu_usage for m in recent) / len(recent),
            "memory": sum(m.memory_usage for m in recent) / len(recent),
            "disk": sum(m.disk_usage for m in recent) / len(recent),
            "network": sum(m.network_usage for m in recent) / len(recent)
        }
    
    def determine_scaling_action(self, component: ComponentType) -> ScalingAction:
        """Determine what scaling action to take."""
        utilization = self.analyze_utilization(component)
        
        # Check if any resource is over threshold
        if (utilization["cpu"] > self.thresholds["cpu_high"] or
            utilization["memory"] > self.thresholds["memory_high"] or
            utilization["disk"] > self.thresholds["disk_high"] or
            utilization["network"] > self.thresholds["network_high"]):
            return ScalingAction.SCALE_UP
        
        # Check if all resources are under low threshold
        if (utilization["cpu"] < self.thresholds["cpu_low"] and
            utilization["memory"] < self.thresholds["memory_low"]):
            return ScalingAction.SCALE_DOWN
        
        # Check if optimization could help
        if utilization["cpu"] > 0.6 or utilization["memory"] > 0.6:
            return ScalingAction.OPTIMIZE
        
        return ScalingAction.MAINTAIN
    
    def execute_scaling(self, component: ComponentType, action: ScalingAction) -> Dict[str, Any]:
        """Execute a scaling action."""
        result = {
            "component": component,
            "action": action,
            "timestamp": datetime.now(),
            "success": True
        }
        
        self.scaling_history.append(result)
        if len(self.scaling_history) > 1000:
            self.scaling_history = self.scaling_history[-1000:]
        
        return result
    
    def get_scaling_recommendations(self) -> List[Dict[str, Any]]:
        """Get scaling recommendations for all components."""
        recommendations = []
        
        for component in ComponentType:
            action = self.determine_scaling_action(component)
            if action != ScalingAction.MAINTAIN:
                utilization = self.analyze_utilization(component)
                recommendations.append({
                    "component": component,
                    "action": action,
                    "utilization": utilization,
                    "priority": max(utilization.values())
                })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations


class DataFlowOptimizer:
    """Optimizes data processing pipelines."""
    
    def __init__(self, max_metrics: int = 5000):
        self.max_metrics = max_metrics
        self.metrics: List[DataFlowMetrics] = []
        self.optimizations: List[Dict[str, Any]] = []
    
    def record_flow_metrics(self, metrics: DataFlowMetrics) -> None:
        """Record data flow metrics."""
        self.metrics.append(metrics)
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
    
    def analyze_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """Analyze a data pipeline's performance."""
        pipeline_metrics = [m for m in self.metrics if m.pipeline_name == pipeline_name]
        
        if not pipeline_metrics:
            return {
                "avg_throughput": 0.0,
                "avg_latency": 0.0,
                "avg_error_rate": 0.0,
                "bottlenecks": []
            }
        
        recent = pipeline_metrics[-100:]
        
        bottlenecks = []
        for m in recent:
            if m.bottleneck and m.bottleneck not in bottlenecks:
                bottlenecks.append(m.bottleneck)
        
        return {
            "avg_throughput": sum(m.throughput for m in recent) / len(recent),
            "avg_latency": sum(m.latency for m in recent) / len(recent),
            "avg_error_rate": sum(m.error_rate for m in recent) / len(recent),
            "bottlenecks": bottlenecks
        }
    
    def identify_optimizations(self, pipeline_name: str) -> List[Dict[str, Any]]:
        """Identify optimization opportunities for a pipeline."""
        analysis = self.analyze_pipeline(pipeline_name)
        optimizations = []
        
        # High latency
        if analysis["avg_latency"] > 1.0:
            optimizations.append({
                "type": "reduce_latency",
                "description": "Add caching or parallel processing",
                "priority": analysis["avg_latency"]
            })
        
        # Low throughput
        if analysis["avg_throughput"] < 10.0:
            optimizations.append({
                "type": "increase_throughput",
                "description": "Optimize batch sizes or add workers",
                "priority": 1.0 / (analysis["avg_throughput"] + 0.1)
            })
        
        # High error rate
        if analysis["avg_error_rate"] > 0.05:
            optimizations.append({
                "type": "reduce_errors",
                "description": "Improve error handling and validation",
                "priority": analysis["avg_error_rate"] * 10
            })
        
        # Bottlenecks
        for bottleneck in analysis["bottlenecks"]:
            optimizations.append({
                "type": "remove_bottleneck",
                "description": f"Optimize {bottleneck}",
                "priority": 0.8
            })
        
        optimizations.sort(key=lambda x: x["priority"], reverse=True)
        return optimizations
    
    def apply_optimization(self, pipeline_name: str, optimization_type: str) -> bool:
        """Apply an optimization to a pipeline."""
        self.optimizations.append({
            "pipeline": pipeline_name,
            "type": optimization_type,
            "timestamp": datetime.now()
        })
        
        if len(self.optimizations) > 1000:
            self.optimizations = self.optimizations[-1000:]
        
        return True
    
    def get_all_pipelines(self) -> List[str]:
        """Get list of all tracked pipelines."""
        return list(set(m.pipeline_name for m in self.metrics))


class SecurityEnhancer:
    """Enhances security protections adaptively."""
    
    def __init__(self, max_threats: int = 5000):
        self.max_threats = max_threats
        self.threats: List[SecurityThreat] = []
        self.security_level: SecurityLevel = SecurityLevel.STANDARD
        self.protections: Dict[ThreatType, List[str]] = defaultdict(list)
    
    def detect_threat(self, threat: SecurityThreat) -> None:
        """Detect and record a security threat."""
        self.threats.append(threat)
        if len(self.threats) > self.max_threats:
            self.threats = self.threats[-self.max_threats:]
        
        # Auto-adjust security level based on threat severity
        if threat.severity > 0.8:
            self.adjust_security_level(SecurityLevel.MAXIMUM)
        elif threat.severity > 0.6:
            self.adjust_security_level(SecurityLevel.ENHANCED)
    
    def adjust_security_level(self, level: SecurityLevel) -> None:
        """Adjust overall security level."""
        if level.value > self.security_level.value:
            self.security_level = level
    
    def add_protection(self, threat_type: ThreatType, protection: str) -> None:
        """Add a protection measure for a threat type."""
        if protection not in self.protections[threat_type]:
            self.protections[threat_type].append(protection)
    
    def mitigate_threat(self, threat: SecurityThreat) -> bool:
        """Mitigate a detected threat."""
        if threat in self.threats:
            threat.mitigated = True
            return True
        return False
    
    def get_active_threats(self) -> List[SecurityThreat]:
        """Get all active (unmitigated) threats."""
        return [t for t in self.threats if not t.mitigated]
    
    def get_threat_summary(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get summary of threats."""
        threats = self.threats
        if since:
            threats = [t for t in threats if t.timestamp >= since]
        
        if not threats:
            return {
                "total": 0,
                "active": 0,
                "by_type": {},
                "avg_severity": 0.0
            }
        
        by_type = defaultdict(int)
        for t in threats:
            by_type[t.threat_type.value] += 1
        
        return {
            "total": len(threats),
            "active": len([t for t in threats if not t.mitigated]),
            "by_type": dict(by_type),
            "avg_severity": sum(t.severity for t in threats) / len(threats)
        }
    
    def get_recommendations(self) -> List[str]:
        """Get security enhancement recommendations."""
        recommendations = []
        active_threats = self.get_active_threats()
        
        # Group by threat type
        threat_counts = defaultdict(int)
        for threat in active_threats:
            threat_counts[threat.threat_type] += 1
        
        # Recommend protections for common threats
        for threat_type, count in threat_counts.items():
            if count > 5:
                recommendations.append(
                    f"Implement additional protections for {threat_type.value} (detected {count} times)"
                )
        
        # Recommend security level upgrade
        if len(active_threats) > 10 and self.security_level != SecurityLevel.MAXIMUM:
            recommendations.append("Consider upgrading to maximum security level")
        
        return recommendations


class ResilienceImprover:
    """Improves error handling and system resilience."""
    
    def __init__(self, max_improvements: int = 2000):
        self.max_improvements = max_improvements
        self.improvements: List[ResilienceImprovement] = []
        self.failure_history: List[Dict[str, Any]] = []
    
    def record_failure(self, component: ComponentType, error_type: str,
                      description: str, recovered: bool) -> None:
        """Record a system failure."""
        self.failure_history.append({
            "component": component,
            "error_type": error_type,
            "description": description,
            "recovered": recovered,
            "timestamp": datetime.now()
        })
        
        if len(self.failure_history) > 5000:
            self.failure_history = self.failure_history[-5000:]
    
    def analyze_failures(self, component: ComponentType) -> Dict[str, Any]:
        """Analyze failure patterns for a component."""
        component_failures = [f for f in self.failure_history if f["component"] == component]
        
        if not component_failures:
            return {
                "total_failures": 0,
                "recovery_rate": 1.0,
                "common_errors": []
            }
        
        recovered = len([f for f in component_failures if f["recovered"]])
        recovery_rate = recovered / len(component_failures)
        
        # Find common error types
        error_counts = defaultdict(int)
        for f in component_failures:
            error_counts[f["error_type"]] += 1
        
        common_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_failures": len(component_failures),
            "recovery_rate": recovery_rate,
            "common_errors": [e[0] for e in common_errors]
        }
    
    def recommend_strategy(self, component: ComponentType) -> Optional[ResilienceStrategy]:
        """Recommend a resilience strategy for a component."""
        analysis = self.analyze_failures(component)
        
        if analysis["total_failures"] == 0:
            return None
        
        # Low recovery rate - need better strategies
        if analysis["recovery_rate"] < 0.5:
            return ResilienceStrategy.CIRCUIT_BREAKER
        
        # Moderate failures - add retry logic
        if analysis["total_failures"] > 10:
            return ResilienceStrategy.RETRY
        
        # Occasional failures - add fallback
        if analysis["total_failures"] > 5:
            return ResilienceStrategy.FALLBACK
        
        return ResilienceStrategy.GRACEFUL_DEGRADATION
    
    def apply_improvement(self, improvement: ResilienceImprovement) -> None:
        """Apply a resilience improvement."""
        self.improvements.append(improvement)
        if len(self.improvements) > self.max_improvements:
            self.improvements = self.improvements[-self.max_improvements:]
    
    def get_active_improvements(self, component: Optional[ComponentType] = None) -> List[ResilienceImprovement]:
        """Get active resilience improvements."""
        active = [i for i in self.improvements if i.active]
        if component:
            active = [i for i in active if i.component == component]
        return active
    
    def measure_effectiveness(self, component: ComponentType) -> float:
        """Measure effectiveness of resilience improvements."""
        # Compare failure rates before and after improvements
        improvements = self.get_active_improvements(component)
        if not improvements:
            return 0.0
        
        first_improvement = min(improvements, key=lambda x: x.timestamp)
        
        failures_before = [f for f in self.failure_history 
                          if f["component"] == component and f["timestamp"] < first_improvement.timestamp]
        failures_after = [f for f in self.failure_history 
                         if f["component"] == component and f["timestamp"] >= first_improvement.timestamp]
        
        if not failures_before:
            return 1.0
        
        rate_before = len(failures_before)
        rate_after = len(failures_after) if failures_after else 0
        
        # Calculate improvement (reduction in failure rate)
        if rate_before == 0:
            return 1.0
        
        improvement = max(0.0, 1.0 - (rate_after / rate_before))
        return improvement


class AdaptiveArchitectureEngine:
    """Orchestrates all adaptive architecture components."""
    
    def __init__(self, cycle_interval_minutes: int = 45):
        self.cycle_interval = timedelta(minutes=cycle_interval_minutes)
        self.last_cycle = datetime.now()
        self.running = False
        
        # Initialize all components
        self.architecture_modifier = ArchitectureModifier()
        self.resource_scaler = ResourceScaler()
        self.data_flow_optimizer = DataFlowOptimizer()
        self.security_enhancer = SecurityEnhancer()
        self.resilience_improver = ResilienceImprover()
    
    async def run_cycle(self) -> Dict[str, Any]:
        """Run one adaptation cycle."""
        cycle_start = datetime.now()
        
        # Get recommendations from all components
        scaling_recs = self.resource_scaler.get_scaling_recommendations()
        security_recs = self.security_enhancer.get_recommendations()
        
        # Analyze all pipelines
        pipeline_optimizations = []
        for pipeline in self.data_flow_optimizer.get_all_pipelines():
            opts = self.data_flow_optimizer.identify_optimizations(pipeline)
            if opts:
                pipeline_optimizations.append({"pipeline": pipeline, "optimizations": opts})
        
        # Check resilience for all components
        resilience_recs = []
        for component in ComponentType:
            strategy = self.resilience_improver.recommend_strategy(component)
            if strategy:
                resilience_recs.append({"component": component, "strategy": strategy})
        
        self.last_cycle = cycle_start
        
        return {
            "timestamp": cycle_start,
            "scaling_recommendations": scaling_recs,
            "security_recommendations": security_recs,
            "pipeline_optimizations": pipeline_optimizations,
            "resilience_recommendations": resilience_recs,
            "pending_architecture_changes": len(self.architecture_modifier.get_pending_changes()),
            "active_threats": len(self.security_enhancer.get_active_threats())
        }
    
    async def start(self) -> None:
        """Start the adaptive architecture engine."""
        self.running = True
        
        while self.running:
            if datetime.now() - self.last_cycle >= self.cycle_interval:
                await self.run_cycle()
            
            await asyncio.sleep(60)  # Check every minute
    
    def stop(self) -> None:
        """Stop the adaptive architecture engine."""
        self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of adaptive architecture."""
        return {
            "running": self.running,
            "last_cycle": self.last_cycle,
            "next_cycle": self.last_cycle + self.cycle_interval,
            "security_level": self.security_enhancer.security_level.value,
            "pending_changes": len(self.architecture_modifier.get_pending_changes()),
            "active_threats": len(self.security_enhancer.get_active_threats()),
            "total_improvements": len(self.resilience_improver.improvements)
        }
