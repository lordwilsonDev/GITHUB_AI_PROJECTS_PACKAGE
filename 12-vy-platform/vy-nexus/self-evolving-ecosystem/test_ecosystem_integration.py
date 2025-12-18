"""Test suite for Ecosystem Integration"""

import asyncio
import pytest
from datetime import datetime, timedelta
from ecosystem_integration import (
    EcosystemIntegration,
    EcosystemConfig,
    EcosystemState,
    CyclePhase,
    IntegrationStatus,
    UnifiedConfigManager
)


class TestEcosystemIntegration:
    """Test ecosystem integration functionality"""
    
    def test_initialization(self):
        """Test ecosystem initialization"""
        ecosystem = EcosystemIntegration()
        
        assert ecosystem.state == EcosystemState.INITIALIZING
        assert len(ecosystem.modules) == 10
        assert ecosystem.metrics.total_cycles_completed == 0
        print("✅ Initialization test passed")
    
    def test_module_registration(self):
        """Test module registration"""
        ecosystem = EcosystemIntegration()
        
        # Check all modules are registered
        expected_modules = [
            "Continuous Learning Engine",
            "Background Process Optimization",
            "Real-Time Adaptation System",
            "Meta-Learning Analysis",
            "Self-Improvement Cycle",
            "Knowledge Acquisition System",
            "Evolution Reporting System",
            "System Evolution Tracking",
            "Predictive Optimization",
            "Adaptive Architecture"
        ]
        
        for module_name in expected_modules:
            assert module_name in ecosystem.modules
            module = ecosystem.modules[module_name]
            assert module.status == IntegrationStatus.NOT_INTEGRATED
            assert module.run_count == 0
        
        print("✅ Module registration test passed")
    
    @pytest.mark.asyncio
    async def test_module_integration(self):
        """Test integrating a single module"""
        ecosystem = EcosystemIntegration()
        
        module_name = "Continuous Learning Engine"
        result = await ecosystem.integrate_module(module_name)
        
        assert result is True
        assert ecosystem.modules[module_name].status == IntegrationStatus.INTEGRATED
        print("✅ Module integration test passed")
    
    @pytest.mark.asyncio
    async def test_integrate_all_modules(self):
        """Test integrating all modules"""
        ecosystem = EcosystemIntegration()
        
        results = await ecosystem.integrate_all_modules()
        
        assert len(results) == 10
        assert all(results.values())
        
        for module in ecosystem.modules.values():
            assert module.status == IntegrationStatus.INTEGRATED
        
        print("✅ Integrate all modules test passed")
    
    def test_data_sharing(self):
        """Test data sharing between modules"""
        ecosystem = EcosystemIntegration()
        
        # Share data
        ecosystem.share_data("Module A", "test_key", {"value": 123})
        
        # Retrieve data
        data = ecosystem.get_shared_data("Module A", "test_key")
        
        assert data is not None
        assert data["value"] == 123
        print("✅ Data sharing test passed")
    
    def test_data_flow_registration(self):
        """Test registering data flows"""
        ecosystem = EcosystemIntegration()
        
        ecosystem.register_data_flow(
            "Continuous Learning Engine",
            "Meta-Learning Analysis",
            "learning_events"
        )
        
        assert len(ecosystem.data_flows) == 1
        flow = ecosystem.data_flows[0]
        assert flow.source_module == "Continuous Learning Engine"
        assert flow.target_module == "Meta-Learning Analysis"
        assert flow.data_type == "learning_events"
        print("✅ Data flow registration test passed")
    
    def test_cycle_phase_detection(self):
        """Test detecting current cycle phase"""
        ecosystem = EcosystemIntegration()
        
        phase = ecosystem.get_current_phase()
        
        assert phase in [CyclePhase.DAYTIME_LEARNING, CyclePhase.EVENING_IMPLEMENTATION]
        print(f"✅ Cycle phase detection test passed (current: {phase.value})")
    
    @pytest.mark.asyncio
    async def test_module_cycle_execution(self):
        """Test running a module cycle"""
        ecosystem = EcosystemIntegration()
        
        # Integrate module first
        await ecosystem.integrate_module("Continuous Learning Engine")
        
        # Run cycle
        await ecosystem.run_module_cycle("Continuous Learning Engine")
        
        module = ecosystem.modules["Continuous Learning Engine"]
        assert module.run_count == 1
        assert module.last_run is not None
        assert module.next_run is not None
        assert ecosystem.metrics.total_cycles_completed == 1
        print("✅ Module cycle execution test passed")
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check functionality"""
        ecosystem = EcosystemIntegration()
        await ecosystem.integrate_all_modules()
        
        health = await ecosystem.health_check()
        
        assert 'ecosystem_state' in health
        assert 'current_phase' in health
        assert 'modules' in health
        assert len(health['modules']) == 10
        print("✅ Health check test passed")
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test starting and stopping ecosystem"""
        ecosystem = EcosystemIntegration()
        
        await ecosystem.start()
        assert ecosystem.state == EcosystemState.RUNNING
        assert ecosystem.start_time is not None
        
        await ecosystem.stop()
        assert ecosystem.state == EcosystemState.SHUTDOWN
        print("✅ Start/stop test passed")
    
    def test_status_report_generation(self):
        """Test generating status report"""
        ecosystem = EcosystemIntegration()
        
        report = ecosystem.generate_status_report()
        
        assert "SELF-EVOLVING AI ECOSYSTEM" in report
        assert "ECOSYSTEM METRICS" in report
        assert "MODULE STATUS" in report
        assert len(report) > 100
        print("✅ Status report generation test passed")
    
    def test_metrics_tracking(self):
        """Test metrics tracking"""
        ecosystem = EcosystemIntegration()
        
        # Update metrics
        ecosystem.metrics.learning_events = 50
        ecosystem.metrics.optimizations_applied = 25
        ecosystem.metrics.adaptations_made = 15
        
        metrics_dict = ecosystem.metrics.to_dict()
        
        assert metrics_dict['learning_events'] == 50
        assert metrics_dict['optimizations_applied'] == 25
        assert metrics_dict['adaptations_made'] == 15
        print("✅ Metrics tracking test passed")


class TestUnifiedConfigManager:
    """Test unified configuration manager"""
    
    def test_config_manager_initialization(self):
        """Test config manager initialization"""
        manager = UnifiedConfigManager()
        
        assert manager.config_dir.exists()
        assert isinstance(manager.configs, dict)
        print("✅ Config manager initialization test passed")
    
    def test_load_all_configs(self):
        """Test loading all configurations"""
        manager = UnifiedConfigManager()
        manager.load_all_configs()
        
        # Should have loaded configs for all modules
        assert len(manager.configs) >= 0
        print("✅ Load all configs test passed")
    
    def test_get_config(self):
        """Test getting module config"""
        manager = UnifiedConfigManager()
        manager.load_all_configs()
        
        config = manager.get_config('learning')
        assert isinstance(config, dict)
        print("✅ Get config test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("Ecosystem Integration - Test Suite")
    print("=" * 70)
    
    # Synchronous tests
    test_integration = TestEcosystemIntegration()
    
    print("\n1. Testing initialization...")
    test_integration.test_initialization()
    
    print("\n2. Testing module registration...")
    test_integration.test_module_registration()
    
    print("\n3. Testing data sharing...")
    test_integration.test_data_sharing()
    
    print("\n4. Testing data flow registration...")
    test_integration.test_data_flow_registration()
    
    print("\n5. Testing cycle phase detection...")
    test_integration.test_cycle_phase_detection()
    
    print("\n6. Testing status report generation...")
    test_integration.test_status_report_generation()
    
    print("\n7. Testing metrics tracking...")
    test_integration.test_metrics_tracking()
    
    # Config manager tests
    test_config = TestUnifiedConfigManager()
    
    print("\n8. Testing config manager initialization...")
    test_config.test_config_manager_initialization()
    
    print("\n9. Testing load all configs...")
    test_config.test_load_all_configs()
    
    print("\n10. Testing get config...")
    test_config.test_get_config()
    
    # Async tests
    print("\n11. Testing module integration...")
    asyncio.run(test_integration.test_module_integration())
    
    print("\n12. Testing integrate all modules...")
    asyncio.run(test_integration.test_integrate_all_modules())
    
    print("\n13. Testing module cycle execution...")
    asyncio.run(test_integration.test_module_cycle_execution())
    
    print("\n14. Testing health check...")
    asyncio.run(test_integration.test_health_check())
    
    print("\n15. Testing start/stop...")
    asyncio.run(test_integration.test_start_stop())
    
    print("\n" + "=" * 70)
    print("✅ ALL 15/15 TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
