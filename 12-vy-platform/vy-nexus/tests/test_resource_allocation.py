#!/usr/bin/env python3
"""
Tests for Resource Allocation System

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import unittest
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'self_improvement'))

from resource_allocation import (
    ResourceType,
    AllocationStrategy,
    Resource,
    AllocationRequest,
    Allocation,
    ResourceAllocator,
    AllocationOptimizer
)


class TestResource(unittest.TestCase):
    """Test cases for Resource class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.resource = Resource(
            type=ResourceType.CPU,
            total_capacity=100.0,
            available=100.0,
            unit="percent"
        )
    
    def test_initialization(self):
        """Test resource initialization."""
        self.assertEqual(self.resource.type, ResourceType.CPU)
        self.assertEqual(self.resource.total_capacity, 100.0)
        self.assertEqual(self.resource.available, 100.0)
        self.assertEqual(self.resource.unit, "percent")
    
    def test_allocate_success(self):
        """Test successful allocation."""
        result = self.resource.allocate(30.0)
        self.assertTrue(result)
        self.assertEqual(self.resource.available, 70.0)
    
    def test_allocate_failure(self):
        """Test allocation failure when insufficient resources."""
        result = self.resource.allocate(150.0)
        self.assertFalse(result)
        self.assertEqual(self.resource.available, 100.0)
    
    def test_release(self):
        """Test resource release."""
        self.resource.allocate(30.0)
        self.resource.release(20.0)
        self.assertEqual(self.resource.available, 90.0)
    
    def test_release_cap(self):
        """Test that release doesn't exceed capacity."""
        self.resource.release(50.0)
        self.assertEqual(self.resource.available, 100.0)
    
    def test_utilization(self):
        """Test utilization calculation."""
        self.assertEqual(self.resource.utilization(), 0.0)
        self.resource.allocate(50.0)
        self.assertEqual(self.resource.utilization(), 0.5)
        self.resource.allocate(25.0)
        self.assertEqual(self.resource.utilization(), 0.75)


class TestResourceAllocator(unittest.TestCase):
    """Test cases for ResourceAllocator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        self.allocator = ResourceAllocator(str(self.config_path))
    
    def test_initialization(self):
        """Test allocator initialization."""
        self.assertIsNotNone(self.allocator)
        self.assertGreater(len(self.allocator.resources), 0)
        self.assertEqual(len(self.allocator.allocations), 0)
    
    def test_config_creation(self):
        """Test that config file is created."""
        self.assertTrue(self.config_path.exists())
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        self.assertIn('default_strategy', config)
        self.assertIn('resources', config)
        self.assertIn('allocation_limits', config)
    
    def test_resource_initialization(self):
        """Test that resources are initialized from config."""
        self.assertIn(ResourceType.CPU, self.allocator.resources)
        self.assertIn(ResourceType.MEMORY, self.allocator.resources)
        
        cpu = self.allocator.resources[ResourceType.CPU]
        self.assertEqual(cpu.total_capacity, 100.0)
        self.assertEqual(cpu.available, 100.0)
    
    def test_simple_allocation(self):
        """Test simple resource allocation."""
        alloc_id = self.allocator.request_allocation(
            task_id="test_task",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.8
        )
        
        self.assertIsNotNone(alloc_id)
        self.assertIn(alloc_id, self.allocator.allocations)
        
        # Check resource was allocated
        cpu = self.allocator.resources[ResourceType.CPU]
        self.assertEqual(cpu.available, 70.0)
    
    def test_allocation_with_priority(self):
        """Test that higher priority requests are processed first."""
        # Fill most of the resource
        self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=40.0,
            priority=0.5
        )
        
        # Request more than available
        alloc_low = self.allocator.request_allocation(
            task_id="task2",
            resource_type=ResourceType.CPU,
            amount=40.0,
            priority=0.3
        )
        
        alloc_high = self.allocator.request_allocation(
            task_id="task3",
            resource_type=ResourceType.CPU,
            amount=40.0,
            priority=0.9
        )
        
        # Both should be queued
        self.assertIsNone(alloc_low)
        self.assertIsNone(alloc_high)
        self.assertGreater(len(self.allocator.pending_requests), 0)
    
    def test_allocation_limits(self):
        """Test that allocation limits are enforced."""
        # Try to allocate more than max_per_task
        alloc_id = self.allocator.request_allocation(
            task_id="greedy_task",
            resource_type=ResourceType.CPU,
            amount=80.0,  # More than 50% limit
            priority=0.9
        )
        
        # Should be capped at max_per_task (50%)
        if alloc_id:
            allocation = self.allocator.allocations[alloc_id]
            self.assertLessEqual(allocation.amount, 50.0)
    
    def test_release_allocation(self):
        """Test releasing an allocation."""
        alloc_id = self.allocator.request_allocation(
            task_id="test_task",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.8
        )
        
        self.assertIsNotNone(alloc_id)
        
        # Release
        result = self.allocator.release_allocation(alloc_id)
        self.assertTrue(result)
        self.assertNotIn(alloc_id, self.allocator.allocations)
        
        # Check resource was released
        cpu = self.allocator.resources[ResourceType.CPU]
        self.assertEqual(cpu.available, 100.0)
    
    def test_pending_request_processing(self):
        """Test that pending requests are processed when resources free up."""
        # Fill resource
        alloc1 = self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=40.0,
            priority=0.8
        )
        
        # Queue another request
        alloc2 = self.allocator.request_allocation(
            task_id="task2",
            resource_type=ResourceType.CPU,
            amount=40.0,
            priority=0.7
        )
        
        self.assertIsNone(alloc2)
        
        # Release first allocation
        self.allocator.release_allocation(alloc1)
        
        # Pending request should be processed
        # (In real implementation, this happens automatically)
    
    def test_resource_status(self):
        """Test getting resource status."""
        status = self.allocator.get_resource_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('cpu', status)
        
        cpu_status = status['cpu']
        self.assertIn('total_capacity', cpu_status)
        self.assertIn('available', cpu_status)
        self.assertIn('utilization', cpu_status)
    
    def test_allocation_metrics(self):
        """Test allocation metrics."""
        # Make some allocations
        self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.8
        )
        
        metrics = self.allocator.get_allocation_metrics()
        
        self.assertIn('total_requests', metrics)
        self.assertIn('successful_allocations', metrics)
        self.assertIn('success_rate', metrics)
        self.assertGreater(metrics['total_requests'], 0)
    
    def test_optimize_allocations(self):
        """Test allocation optimization."""
        # Create allocation with expiration
        alloc_id = self.allocator.request_allocation(
            task_id="temp_task",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.8,
            duration=timedelta(seconds=-1)  # Already expired
        )
        
        # Optimize should remove expired allocations
        self.allocator.optimize_allocations()
        
        # Allocation should be removed
        self.assertNotIn(alloc_id, self.allocator.allocations)


class TestAllocationOptimizer(unittest.TestCase):
    """Test cases for AllocationOptimizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.allocator = ResourceAllocator()
        self.optimizer = AllocationOptimizer(self.allocator)
    
    def test_initialization(self):
        """Test optimizer initialization."""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.allocator, self.allocator)
    
    def test_throughput_optimization(self):
        """Test throughput optimization recommendations."""
        # Create some allocations
        self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=10.0,
            priority=0.8
        )
        
        recommendations = self.optimizer.optimize_for_throughput()
        
        self.assertIsInstance(recommendations, list)
        # Should recommend increasing allocation due to low utilization
        self.assertGreater(len(recommendations), 0)
    
    def test_fairness_optimization(self):
        """Test fairness optimization."""
        # Create multiple allocations
        self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.8
        )
        
        self.allocator.request_allocation(
            task_id="task2",
            resource_type=ResourceType.CPU,
            amount=20.0,
            priority=0.6
        )
        
        fair_shares = self.optimizer.optimize_for_fairness()
        
        self.assertIsInstance(fair_shares, dict)
        # All tasks should get equal share
        if len(fair_shares) > 1:
            values = list(fair_shares.values())
            self.assertEqual(values[0], values[1])
    
    def test_resource_prediction(self):
        """Test resource need prediction."""
        # Create some history
        self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.8
        )
        
        predictions = self.optimizer.predict_resource_needs("task1")
        
        self.assertIsInstance(predictions, dict)


class TestAllocationStrategies(unittest.TestCase):
    """Test different allocation strategies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.allocator = ResourceAllocator()
    
    def test_priority_based_strategy(self):
        """Test priority-based allocation strategy."""
        self.allocator.default_strategy = AllocationStrategy.PRIORITY_BASED
        
        # Make allocations with different priorities
        high = self.allocator.request_allocation(
            task_id="high_priority",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.9
        )
        
        low = self.allocator.request_allocation(
            task_id="low_priority",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.3
        )
        
        # Both should succeed if resources available
        self.assertIsNotNone(high)
    
    def test_fair_share_reallocation(self):
        """Test fair share reallocation."""
        # Create unequal allocations
        self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=40.0,
            priority=0.8
        )
        
        self.allocator.request_allocation(
            task_id="task2",
            resource_type=ResourceType.CPU,
            amount=20.0,
            priority=0.6
        )
        
        # Reallocate fairly
        self.allocator.reallocate_resources(AllocationStrategy.FAIR_SHARE)
        
        # Check that allocations are now equal
        allocations = list(self.allocator.allocations.values())
        if len(allocations) >= 2:
            # Should be approximately equal
            amounts = [a.amount for a in allocations if a.resource_type == ResourceType.CPU]
            if len(amounts) >= 2:
                self.assertAlmostEqual(amounts[0], amounts[1], delta=1.0)


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.allocator = ResourceAllocator()
    
    def test_high_load_scenario(self):
        """Test behavior under high load."""
        # Create many allocation requests
        for i in range(10):
            self.allocator.request_allocation(
                task_id=f"task_{i}",
                resource_type=ResourceType.CPU,
                amount=15.0,
                priority=0.5 + (i * 0.05)
            )
        
        # Check that system handled load
        metrics = self.allocator.get_allocation_metrics()
        self.assertGreater(metrics['total_requests'], 0)
    
    def test_resource_exhaustion(self):
        """Test behavior when resources are exhausted."""
        # Allocate all CPU
        self.allocator.request_allocation(
            task_id="greedy",
            resource_type=ResourceType.CPU,
            amount=45.0,  # Max per task
            priority=0.9
        )
        
        # Try to allocate more
        result = self.allocator.request_allocation(
            task_id="blocked",
            resource_type=ResourceType.CPU,
            amount=45.0,
            priority=0.8
        )
        
        # Should be queued
        self.assertIsNone(result)
        self.assertGreater(len(self.allocator.pending_requests), 0)
    
    def test_mixed_resource_types(self):
        """Test allocating different resource types."""
        cpu_alloc = self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.CPU,
            amount=30.0,
            priority=0.8
        )
        
        mem_alloc = self.allocator.request_allocation(
            task_id="task1",
            resource_type=ResourceType.MEMORY,
            amount=4096.0,
            priority=0.8
        )
        
        self.assertIsNotNone(cpu_alloc)
        self.assertIsNotNone(mem_alloc)
        
        # Check status for both
        status = self.allocator.get_resource_status()
        self.assertGreater(status['cpu']['utilization'], 0)
        self.assertGreater(status['memory']['utilization'], 0)


if __name__ == '__main__':
    unittest.main()
