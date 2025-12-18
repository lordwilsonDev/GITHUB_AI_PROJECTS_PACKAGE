"""Tests for Adaptive Architecture System."""

import pytest
from datetime import datetime, timedelta
from adaptive_architecture import (
    ArchitectureModifier, ResourceScaler, DataFlowOptimizer,
    SecurityEnhancer, ResilienceImprover, AdaptiveArchitectureEngine,
    ComponentType, ScalingAction, SecurityLevel, ThreatType,
    ResilienceStrategy, ArchitectureChange, ResourceMetrics,
    DataFlowMetrics, SecurityThreat, ResilienceImprovement
)


class TestArchitectureModifier:
    """Test ArchitectureModifier component."""
    
    def test_record_usage(self):
        """Test recording component usage."""
        modifier = ArchitectureModifier()
        
        modifier.record_usage(ComponentType.API, 0.7)
        modifier.record_usage(ComponentType.API, 0.8)
        
        assert len(modifier.usage_patterns[ComponentType.API]) == 2
        assert modifier.usage_patterns[ComponentType.API][0] == 0.7
    
    def test_analyze_patterns(self):
        """Test pattern analysis."""
        modifier = ArchitectureModifier()
        
        # Record increasing usage
        for i in range(20):
            modifier.record_usage(ComponentType.DATABASE, 0.5 + (i * 0.02))
        
        analysis = modifier.analyze_patterns(ComponentType.DATABASE)
        
        assert analysis["trend"] == "increasing"
        assert analysis["avg_usage"] > 0.5
        assert analysis["peak_usage"] > 0.8
    
    def test_propose_change(self):
        """Test proposing architecture changes."""
        modifier = ArchitectureModifier()
        
        change = modifier.propose_change(
            ComponentType.CACHE,
            "add_layer",
            "Add Redis caching layer",
            "High database load",
            0.8
        )
        
        assert change.component == ComponentType.CACHE
        assert change.applied == False
        assert len(modifier.changes) == 1
    
    def test_apply_change(self):
        """Test applying changes."""
        modifier = ArchitectureModifier()
        
        change = modifier.propose_change(
            ComponentType.API,
            "scale",
            "Scale API servers",
            "High traffic",
            0.9
        )
        
        result = modifier.apply_change(change)
        
        assert result == True
        assert change.applied == True
    
    def test_get_pending_changes(self):
        """Test getting pending changes."""
        modifier = ArchitectureModifier()
        
        change1 = modifier.propose_change(ComponentType.API, "scale", "Scale", "Load", 0.8)
        change2 = modifier.propose_change(ComponentType.DATABASE, "optimize", "Optimize", "Slow", 0.7)
        
        modifier.apply_change(change1)
        
        pending = modifier.get_pending_changes()
        
        assert len(pending) == 1
        assert pending[0] == change2


class TestResourceScaler:
    """Test ResourceScaler component."""
    
    def test_record_metrics(self):
        """Test recording resource metrics."""
        scaler = ResourceScaler()
        
        metrics = ResourceMetrics(
            component=ComponentType.WORKER,
            cpu_usage=0.75,
            memory_usage=0.65,
            disk_usage=0.50,
            network_usage=0.40
        )
        
        scaler.record_metrics(metrics)
        
        assert len(scaler.metrics) == 1
        assert scaler.metrics[0].cpu_usage == 0.75
    
    def test_analyze_utilization(self):
        """Test utilization analysis."""
        scaler = ResourceScaler()
        
        # Record high CPU usage
        for _ in range(10):
            metrics = ResourceMetrics(
                component=ComponentType.COMPUTE,
                cpu_usage=0.85,
                memory_usage=0.60,
                disk_usage=0.40,
                network_usage=0.30
            )
            scaler.record_metrics(metrics)
        
        utilization = scaler.analyze_utilization(ComponentType.COMPUTE)
        
        assert utilization["cpu"] == 0.85
        assert utilization["memory"] == 0.60
    
    def test_determine_scaling_action(self):
        """Test scaling action determination."""
        scaler = ResourceScaler()
        
        # High CPU - should scale up
        for _ in range(10):
            metrics = ResourceMetrics(
                component=ComponentType.API,
                cpu_usage=0.90,
                memory_usage=0.70,
                disk_usage=0.50,
                network_usage=0.40
            )
            scaler.record_metrics(metrics)
        
        action = scaler.determine_scaling_action(ComponentType.API)
        
        assert action == ScalingAction.SCALE_UP
    
    def test_scaling_recommendations(self):
        """Test getting scaling recommendations."""
        scaler = ResourceScaler()
        
        # High usage for API
        for _ in range(10):
            scaler.record_metrics(ResourceMetrics(
                component=ComponentType.API,
                cpu_usage=0.85,
                memory_usage=0.80,
                disk_usage=0.50,
                network_usage=0.40
            ))
        
        # Low usage for WORKER
        for _ in range(10):
            scaler.record_metrics(ResourceMetrics(
                component=ComponentType.WORKER,
                cpu_usage=0.20,
                memory_usage=0.25,
                disk_usage=0.30,
                network_usage=0.15
            ))
        
        recommendations = scaler.get_scaling_recommendations()
        
        assert len(recommendations) >= 1
        assert recommendations[0]["action"] in [ScalingAction.SCALE_UP, ScalingAction.SCALE_DOWN]


class TestDataFlowOptimizer:
    """Test DataFlowOptimizer component."""
    
    def test_record_flow_metrics(self):
        """Test recording data flow metrics."""
        optimizer = DataFlowOptimizer()
        
        metrics = DataFlowMetrics(
            pipeline_name="user_data_pipeline",
            throughput=100.0,
            latency=0.5,
            error_rate=0.02
        )
        
        optimizer.record_flow_metrics(metrics)
        
        assert len(optimizer.metrics) == 1
    
    def test_analyze_pipeline(self):
        """Test pipeline analysis."""
        optimizer = DataFlowOptimizer()
        
        # Record metrics with bottleneck
        for _ in range(10):
            metrics = DataFlowMetrics(
                pipeline_name="data_processing",
                throughput=50.0,
                latency=2.0,
                error_rate=0.05,
                bottleneck="database_write"
            )
            optimizer.record_flow_metrics(metrics)
        
        analysis = optimizer.analyze_pipeline("data_processing")
        
        assert analysis["avg_throughput"] == 50.0
        assert analysis["avg_latency"] == 2.0
        assert "database_write" in analysis["bottlenecks"]
    
    def test_identify_optimizations(self):
        """Test optimization identification."""
        optimizer = DataFlowOptimizer()
        
        # High latency pipeline
        for _ in range(10):
            metrics = DataFlowMetrics(
                pipeline_name="slow_pipeline",
                throughput=5.0,
                latency=3.0,
                error_rate=0.10
            )
            optimizer.record_flow_metrics(metrics)
        
        optimizations = optimizer.identify_optimizations("slow_pipeline")
        
        assert len(optimizations) > 0
        assert any(opt["type"] == "reduce_latency" for opt in optimizations)
        assert any(opt["type"] == "reduce_errors" for opt in optimizations)
    
    def test_apply_optimization(self):
        """Test applying optimizations."""
        optimizer = DataFlowOptimizer()
        
        result = optimizer.apply_optimization("test_pipeline", "reduce_latency")
        
        assert result == True
        assert len(optimizer.optimizations) == 1


class TestSecurityEnhancer:
    """Test SecurityEnhancer component."""
    
    def test_detect_threat(self):
        """Test threat detection."""
        enhancer = SecurityEnhancer()
        
        threat = SecurityThreat(
            threat_type=ThreatType.UNAUTHORIZED_ACCESS,
            severity=0.7,
            source="192.168.1.100",
            description="Multiple failed login attempts"
        )
        
        enhancer.detect_threat(threat)
        
        assert len(enhancer.threats) == 1
        assert enhancer.security_level == SecurityLevel.ENHANCED
    
    def test_adjust_security_level(self):
        """Test security level adjustment."""
        enhancer = SecurityEnhancer()
        
        # High severity threat
        threat = SecurityThreat(
            threat_type=ThreatType.DATA_BREACH,
            severity=0.9,
            source="external",
            description="Attempted data exfiltration"
        )
        
        enhancer.detect_threat(threat)
        
        assert enhancer.security_level == SecurityLevel.MAXIMUM
    
    def test_add_protection(self):
        """Test adding protections."""
        enhancer = SecurityEnhancer()
        
        enhancer.add_protection(ThreatType.INJECTION, "Input sanitization")
        enhancer.add_protection(ThreatType.INJECTION, "Parameterized queries")
        
        assert len(enhancer.protections[ThreatType.INJECTION]) == 2
    
    def test_mitigate_threat(self):
        """Test threat mitigation."""
        enhancer = SecurityEnhancer()
        
        threat = SecurityThreat(
            threat_type=ThreatType.DOS_ATTACK,
            severity=0.6,
            source="external",
            description="High request rate"
        )
        
        enhancer.detect_threat(threat)
        result = enhancer.mitigate_threat(threat)
        
        assert result == True
        assert threat.mitigated == True
    
    def test_get_threat_summary(self):
        """Test threat summary."""
        enhancer = SecurityEnhancer()
        
        # Add multiple threats
        for i in range(5):
            threat = SecurityThreat(
                threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                severity=0.5 + (i * 0.1),
                source=f"source_{i}",
                description="Test threat"
            )
            enhancer.detect_threat(threat)
        
        summary = enhancer.get_threat_summary()
        
        assert summary["total"] == 5
        assert summary["active"] == 5
        assert summary["avg_severity"] > 0.5


class TestResilienceImprover:
    """Test ResilienceImprover component."""
    
    def test_record_failure(self):
        """Test recording failures."""
        improver = ResilienceImprover()
        
        improver.record_failure(
            ComponentType.DATABASE,
            "connection_timeout",
            "Database connection timed out",
            recovered=True
        )
        
        assert len(improver.failure_history) == 1
    
    def test_analyze_failures(self):
        """Test failure analysis."""
        improver = ResilienceImprover()
        
        # Record multiple failures
        for i in range(10):
            improver.record_failure(
                ComponentType.API,
                "timeout",
                "Request timeout",
                recovered=(i % 2 == 0)
            )
        
        analysis = improver.analyze_failures(ComponentType.API)
        
        assert analysis["total_failures"] == 10
        assert analysis["recovery_rate"] == 0.5
        assert "timeout" in analysis["common_errors"]
    
    def test_recommend_strategy(self):
        """Test strategy recommendation."""
        improver = ResilienceImprover()
        
        # Low recovery rate - should recommend circuit breaker
        for i in range(20):
            improver.record_failure(
                ComponentType.QUEUE,
                "connection_error",
                "Connection failed",
                recovered=(i < 5)  # Only 25% recovery
            )
        
        strategy = improver.recommend_strategy(ComponentType.QUEUE)
        
        assert strategy == ResilienceStrategy.CIRCUIT_BREAKER
    
    def test_apply_improvement(self):
        """Test applying improvements."""
        improver = ResilienceImprover()
        
        improvement = ResilienceImprovement(
            strategy=ResilienceStrategy.RETRY,
            component=ComponentType.API,
            description="Add retry logic with exponential backoff",
            effectiveness=0.8
        )
        
        improver.apply_improvement(improvement)
        
        assert len(improver.improvements) == 1
    
    def test_get_active_improvements(self):
        """Test getting active improvements."""
        improver = ResilienceImprover()
        
        improvement1 = ResilienceImprovement(
            strategy=ResilienceStrategy.RETRY,
            component=ComponentType.API,
            description="Retry logic",
            effectiveness=0.8
        )
        
        improvement2 = ResilienceImprovement(
            strategy=ResilienceStrategy.FALLBACK,
            component=ComponentType.DATABASE,
            description="Fallback to cache",
            effectiveness=0.7
        )
        
        improver.apply_improvement(improvement1)
        improver.apply_improvement(improvement2)
        
        api_improvements = improver.get_active_improvements(ComponentType.API)
        
        assert len(api_improvements) == 1
        assert api_improvements[0].strategy == ResilienceStrategy.RETRY


class TestAdaptiveArchitectureEngine:
    """Test AdaptiveArchitectureEngine orchestrator."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = AdaptiveArchitectureEngine(cycle_interval_minutes=30)
        
        assert engine.architecture_modifier is not None
        assert engine.resource_scaler is not None
        assert engine.data_flow_optimizer is not None
        assert engine.security_enhancer is not None
        assert engine.resilience_improver is not None
    
    @pytest.mark.asyncio
    async def test_run_cycle(self):
        """Test running an adaptation cycle."""
        engine = AdaptiveArchitectureEngine()
        
        # Add some data
        engine.resource_scaler.record_metrics(ResourceMetrics(
            component=ComponentType.API,
            cpu_usage=0.85,
            memory_usage=0.75,
            disk_usage=0.50,
            network_usage=0.40
        ))
        
        result = await engine.run_cycle()
        
        assert "timestamp" in result
        assert "scaling_recommendations" in result
        assert "security_recommendations" in result
    
    def test_get_status(self):
        """Test getting engine status."""
        engine = AdaptiveArchitectureEngine()
        
        status = engine.get_status()
        
        assert "running" in status
        assert "last_cycle" in status
        assert "security_level" in status
        assert status["security_level"] == "standard"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
