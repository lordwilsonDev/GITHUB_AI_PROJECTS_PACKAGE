"""
Tests for Deployment Pipeline Module
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.deployment_pipeline import (
    DeploymentPipeline,
    DeploymentStage,
    DeploymentStatus,
    HealthStatus
)


class TestDeploymentPipeline(unittest.TestCase):
    """Test cases for DeploymentPipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_deployment.db')
        self.pipeline = DeploymentPipeline(db_path=self.db_path)
        
        # Create test artifact
        self.test_artifact = os.path.join(self.test_dir, 'test_artifact.txt')
        with open(self.test_artifact, 'w') as f:
            f.write('Test deployment artifact')
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_create_package(self):
        """Test creating a deployment package"""
        package = self.pipeline.create_package(
            name='test-package',
            version='1.0.0',
            artifact_path=self.test_artifact,
            description='Test package'
        )
        
        self.assertIsNotNone(package.package_id)
        self.assertEqual(package.name, 'test-package')
        self.assertEqual(package.version, '1.0.0')
        self.assertIsNotNone(package.checksum)
    
    def test_deploy_to_development(self):
        """Test deployment to development stage"""
        package = self.pipeline.create_package(
            name='dev-package',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.pipeline.deploy(
            package.package_id,
            DeploymentStage.DEVELOPMENT
        )
        
        self.assertIsNotNone(deployment.deployment_id)
        self.assertEqual(deployment.package_id, package.package_id)
        self.assertEqual(deployment.stage, DeploymentStage.DEVELOPMENT.value)
        self.assertEqual(deployment.status, DeploymentStatus.DEPLOYED.value)
    
    def test_deploy_to_staging(self):
        """Test deployment to staging stage"""
        package = self.pipeline.create_package(
            name='staging-package',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.pipeline.deploy(
            package.package_id,
            DeploymentStage.STAGING
        )
        
        self.assertEqual(deployment.stage, DeploymentStage.STAGING.value)
        self.assertEqual(deployment.status, DeploymentStatus.DEPLOYED.value)
        self.assertTrue(deployment.rollback_available)
    
    def test_deploy_to_production(self):
        """Test deployment to production stage"""
        package = self.pipeline.create_package(
            name='prod-package',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.pipeline.deploy(
            package.package_id,
            DeploymentStage.PRODUCTION
        )
        
        self.assertEqual(deployment.stage, DeploymentStage.PRODUCTION.value)
        self.assertEqual(deployment.status, DeploymentStatus.DEPLOYED.value)
        # Production deployments should have extra validation
        self.assertIn('production_ready', deployment.validation_results)
    
    def test_validation_results(self):
        """Test pre-deployment validation"""
        package = self.pipeline.create_package(
            name='validation-test',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.pipeline.deploy(
            package.package_id,
            DeploymentStage.STAGING
        )
        
        # Check validation results
        self.assertIn('checksum', deployment.validation_results)
        self.assertIn('dependencies', deployment.validation_results)
        self.assertIn('safety', deployment.validation_results)
        
        # All validations should pass
        for check, result in deployment.validation_results.items():
            self.assertTrue(result['passed'], f"{check} validation failed")
    
    def test_rollback(self):
        """Test deployment rollback"""
        package = self.pipeline.create_package(
            name='rollback-test',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.pipeline.deploy(
            package.package_id,
            DeploymentStage.STAGING
        )
        
        # Rollback should be available
        self.assertTrue(deployment.rollback_available)
        
        # Execute rollback
        success = self.pipeline.rollback(
            deployment.deployment_id,
            reason='Testing rollback'
        )
        
        self.assertTrue(success)
        
        # Check updated status
        updated = self.pipeline.get_deployment_status(deployment.deployment_id)
        self.assertEqual(updated.status, DeploymentStatus.ROLLED_BACK.value)
        self.assertFalse(updated.rollback_available)
    
    def test_get_deployment_status(self):
        """Test retrieving deployment status"""
        package = self.pipeline.create_package(
            name='status-test',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.pipeline.deploy(
            package.package_id,
            DeploymentStage.DEVELOPMENT
        )
        
        # Retrieve status
        status = self.pipeline.get_deployment_status(deployment.deployment_id)
        
        self.assertIsNotNone(status)
        self.assertEqual(status.deployment_id, deployment.deployment_id)
        self.assertEqual(status.status, deployment.status)
    
    def test_deployment_history(self):
        """Test retrieving deployment history"""
        # Create multiple deployments
        for i in range(3):
            package = self.pipeline.create_package(
                name=f'history-test-{i}',
                version='1.0.0',
                artifact_path=self.test_artifact
            )
            self.pipeline.deploy(package.package_id, DeploymentStage.DEVELOPMENT)
        
        # Get history
        history = self.pipeline.get_deployment_history(limit=10)
        
        self.assertGreaterEqual(len(history), 3)
        # Should be ordered by most recent first
        for i in range(len(history) - 1):
            self.assertGreaterEqual(history[i].started_at, history[i+1].started_at)
    
    def test_deployment_history_filter_by_package(self):
        """Test filtering deployment history by package"""
        package1 = self.pipeline.create_package(
            name='filter-test-1',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        package2 = self.pipeline.create_package(
            name='filter-test-2',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        self.pipeline.deploy(package1.package_id, DeploymentStage.DEVELOPMENT)
        self.pipeline.deploy(package2.package_id, DeploymentStage.DEVELOPMENT)
        self.pipeline.deploy(package1.package_id, DeploymentStage.STAGING)
        
        # Filter by package1
        history = self.pipeline.get_deployment_history(package_id=package1.package_id)
        
        self.assertEqual(len(history), 2)
        for record in history:
            self.assertEqual(record.package_id, package1.package_id)
    
    def test_deployment_history_filter_by_stage(self):
        """Test filtering deployment history by stage"""
        package = self.pipeline.create_package(
            name='stage-filter-test',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        self.pipeline.deploy(package.package_id, DeploymentStage.DEVELOPMENT)
        self.pipeline.deploy(package.package_id, DeploymentStage.STAGING)
        self.pipeline.deploy(package.package_id, DeploymentStage.PRODUCTION)
        
        # Filter by staging
        history = self.pipeline.get_deployment_history(stage=DeploymentStage.STAGING)
        
        self.assertGreaterEqual(len(history), 1)
        for record in history:
            self.assertEqual(record.stage, DeploymentStage.STAGING.value)
    
    def test_health_status(self):
        """Test health status tracking"""
        package = self.pipeline.create_package(
            name='health-test',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.pipeline.deploy(
            package.package_id,
            DeploymentStage.STAGING
        )
        
        # Health status should be set after deployment
        self.assertEqual(deployment.health_status, HealthStatus.HEALTHY.value)
    
    def test_package_metadata(self):
        """Test package metadata storage"""
        metadata = {
            'author': 'vy-system',
            'tags': ['optimization', 'automation'],
            'priority': 'high'
        }
        
        package = self.pipeline.create_package(
            name='metadata-test',
            version='1.0.0',
            artifact_path=self.test_artifact,
            metadata=metadata
        )
        
        self.assertEqual(package.metadata, metadata)
    
    def test_checksum_calculation(self):
        """Test artifact checksum calculation"""
        package1 = self.pipeline.create_package(
            name='checksum-test-1',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        # Create identical artifact
        test_artifact2 = os.path.join(self.test_dir, 'test_artifact2.txt')
        with open(test_artifact2, 'w') as f:
            f.write('Test deployment artifact')
        
        package2 = self.pipeline.create_package(
            name='checksum-test-2',
            version='1.0.0',
            artifact_path=test_artifact2
        )
        
        # Checksums should match for identical content
        self.assertEqual(package1.checksum, package2.checksum)
    
    def test_multiple_deployments_same_package(self):
        """Test deploying same package to multiple stages"""
        package = self.pipeline.create_package(
            name='multi-stage-test',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        # Deploy to all stages
        dev_deployment = self.pipeline.deploy(package.package_id, DeploymentStage.DEVELOPMENT)
        staging_deployment = self.pipeline.deploy(package.package_id, DeploymentStage.STAGING)
        prod_deployment = self.pipeline.deploy(package.package_id, DeploymentStage.PRODUCTION)
        
        # All should succeed
        self.assertEqual(dev_deployment.status, DeploymentStatus.DEPLOYED.value)
        self.assertEqual(staging_deployment.status, DeploymentStatus.DEPLOYED.value)
        self.assertEqual(prod_deployment.status, DeploymentStatus.DEPLOYED.value)
        
        # Each should have unique deployment ID
        self.assertNotEqual(dev_deployment.deployment_id, staging_deployment.deployment_id)
        self.assertNotEqual(staging_deployment.deployment_id, prod_deployment.deployment_id)


if __name__ == '__main__':
    unittest.main()
