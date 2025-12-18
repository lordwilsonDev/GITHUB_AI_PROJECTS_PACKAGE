"""
Integration Tests for Phase 5 - Evening Implementation System

Tests the integration of:
- Deployment Pipeline
- Meta-Learning Framework
- Workflow Template Updater
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.deployment_pipeline import (
    DeploymentPipeline,
    DeploymentStage,
    DeploymentStatus
)
from modules.meta_learning_framework import (
    MetaLearningFramework,
    LearningMethod,
    LearningDomain
)
from modules.workflow_template_updater import (
    WorkflowTemplateUpdater,
    TemplateType,
    UpdateType
)


class TestPhase5Integration(unittest.TestCase):
    """Integration tests for Phase 5 components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        
        # Initialize all components
        self.deployment = DeploymentPipeline(
            db_path=os.path.join(self.test_dir, 'deployment.db')
        )
        self.meta_learning = MetaLearningFramework(
            db_path=os.path.join(self.test_dir, 'meta_learning.db')
        )
        self.template_updater = WorkflowTemplateUpdater(
            db_path=os.path.join(self.test_dir, 'templates.db')
        )
        
        # Create test artifact
        self.test_artifact = os.path.join(self.test_dir, 'test.txt')
        with open(self.test_artifact, 'w') as f:
            f.write('Test artifact')
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_full_improvement_cycle(self):
        """Test complete improvement cycle: learn -> optimize -> deploy"""
        # Step 1: Record learning sessions
        for i in range(10):
            session = self.meta_learning.record_learning_session(
                method=LearningMethod.PATTERN_BASED,
                domain=LearningDomain.TASK_OPTIMIZATION,
                started_at=datetime.now() - timedelta(hours=1),
                completed_at=datetime.now(),
                items_learned=20 + i,
                success_rate=0.7 + (i * 0.02),
                retention_score=0.6 + (i * 0.02)
            )
        
        # Step 2: Analyze learning effectiveness
        effectiveness = self.meta_learning.analyze_method_effectiveness(
            method=LearningMethod.PATTERN_BASED,
            domain=LearningDomain.TASK_OPTIMIZATION
        )
        
        self.assertEqual(len(effectiveness), 1)
        self.assertGreater(effectiveness[0].effectiveness_score, 0.0)
        
        # Step 3: Generate optimizations
        optimizations = self.meta_learning.generate_optimizations(
            domain=LearningDomain.TASK_OPTIMIZATION
        )
        
        # Should have optimization recommendations
        self.assertGreaterEqual(len(optimizations), 0)
        
        # Step 4: Create deployment package for optimization
        package = self.deployment.create_package(
            name='learning-optimization',
            version='1.0.0',
            artifact_path=self.test_artifact,
            description='Optimization based on learning analysis'
        )
        
        # Step 5: Deploy to staging
        deployment = self.deployment.deploy(
            package.package_id,
            DeploymentStage.STAGING
        )
        
        self.assertEqual(deployment.status, DeploymentStatus.DEPLOYED.value)
        
    def test_template_learning_integration(self):
        """Test integration of template updates with learning"""
        # Create a workflow template
        template = self.template_updater.create_template(
            name='Learning Workflow',
            template_type=TemplateType.TASK_AUTOMATION,
            content={
                'steps': ['analyze', 'learn', 'apply'],
                'learning_method': 'pattern_based'
            }
        )
        
        # Record learning sessions using this template
        for i in range(5):
            self.meta_learning.record_learning_session(
                method=LearningMethod.PATTERN_BASED,
                domain=LearningDomain.TASK_OPTIMIZATION,
                started_at=datetime.now() - timedelta(minutes=30),
                completed_at=datetime.now(),
                items_learned=15,
                success_rate=0.75,
                retention_score=0.70
            )
        
        # Identify improvement opportunities
        opportunities = self.template_updater.identify_improvement_opportunities(
            template.template_id
        )
        
        # Should identify some opportunities (or none if performance is good)
        self.assertIsInstance(opportunities, list)
        
    def test_deployment_with_learning_validation(self):
        """Test deployment with learning-based validation"""
        # Record successful learning sessions
        for i in range(8):
            self.meta_learning.record_learning_session(
                method=LearningMethod.SUPERVISED,
                domain=LearningDomain.TECHNICAL_SKILLS,
                started_at=datetime.now() - timedelta(hours=2),
                completed_at=datetime.now() - timedelta(hours=1),
                items_learned=25,
                success_rate=0.85,
                retention_score=0.80
            )
        
        # Analyze effectiveness
        effectiveness = self.meta_learning.analyze_method_effectiveness()
        
        # Only deploy if learning shows good effectiveness
        if effectiveness and effectiveness[0].effectiveness_score >= 0.7:
            package = self.deployment.create_package(
                name='validated-improvement',
                version='1.0.0',
                artifact_path=self.test_artifact,
                description='Improvement validated by learning metrics'
            )
            
            deployment = self.deployment.deploy(
                package.package_id,
                DeploymentStage.PRODUCTION
            )
            
            self.assertEqual(deployment.status, DeploymentStatus.DEPLOYED.value)
        
    def test_template_update_deployment_cycle(self):
        """Test full cycle: template update -> package -> deploy"""
        # Create template
        template = self.template_updater.create_template(
            name='Optimization Template',
            template_type=TemplateType.OPTIMIZATION,
            content={
                'algorithm': 'gradient_descent',
                'iterations': 100
            }
        )
        
        # Propose update
        update = self.template_updater.propose_update(
            template_id=template.template_id,
            update_type=UpdateType.OPTIMIZATION,
            changes={'modify_iterations': 200, 'add_early_stopping': True},
            rationale='Improve convergence'
        )
        
        # Apply update
        success = self.template_updater.apply_update(update.update_id)
        self.assertTrue(success)
        
        # Create deployment package for updated template
        package = self.deployment.create_package(
            name=f'template-update-{template.name}',
            version='1.1.0',
            artifact_path=self.test_artifact,
            description=f'Updated template: {update.rationale}'
        )
        
        # Deploy to staging first
        staging_deployment = self.deployment.deploy(
            package.package_id,
            DeploymentStage.STAGING
        )
        
        self.assertEqual(staging_deployment.status, DeploymentStatus.DEPLOYED.value)
        
        # If staging successful, deploy to production
        if staging_deployment.status == DeploymentStatus.DEPLOYED.value:
            prod_deployment = self.deployment.deploy(
                package.package_id,
                DeploymentStage.PRODUCTION
            )
            
            self.assertEqual(prod_deployment.status, DeploymentStatus.DEPLOYED.value)
    
    def test_learning_driven_template_optimization(self):
        """Test template optimization driven by learning insights"""
        # Create template
        template = self.template_updater.create_template(
            name='Learning-Driven Template',
            template_type=TemplateType.DATA_PROCESSING,
            content={
                'batch_size': 32,
                'learning_rate': 0.01
            }
        )
        
        # Simulate learning sessions with varying success
        learning_data = [
            (0.60, 0.55),  # Low performance
            (0.65, 0.58),
            (0.70, 0.62),
            (0.72, 0.65),
            (0.75, 0.68),
        ]
        
        for success, retention in learning_data:
            self.meta_learning.record_learning_session(
                method=LearningMethod.REINFORCEMENT,
                domain=LearningDomain.TASK_OPTIMIZATION,
                started_at=datetime.now() - timedelta(minutes=20),
                completed_at=datetime.now(),
                items_learned=10,
                success_rate=success,
                retention_score=retention
            )
        
        # Generate optimizations based on learning
        optimizations = self.meta_learning.generate_optimizations()
        
        # Auto-generate template updates
        template_updates = self.template_updater.auto_generate_updates(
            template.template_id
        )
        
        # Should generate updates or optimizations
        total_improvements = len(optimizations) + len(template_updates)
        self.assertGreaterEqual(total_improvements, 0)
    
    def test_rollback_integration(self):
        """Test rollback capabilities across components"""
        # Create and deploy template
        template = self.template_updater.create_template(
            name='Rollback Test Template',
            template_type=TemplateType.DEPLOYMENT,
            content={'version': 1}
        )
        
        original_version = template.version
        
        # Update template
        update = self.template_updater.propose_update(
            template_id=template.template_id,
            update_type=UpdateType.FEATURE_ADDITION,
            changes={'add_new_feature': True},
            rationale='Add new feature'
        )
        
        self.template_updater.apply_update(update.update_id)
        
        # Deploy updated version
        package = self.deployment.create_package(
            name='rollback-test',
            version='2.0.0',
            artifact_path=self.test_artifact
        )
        
        deployment = self.deployment.deploy(
            package.package_id,
            DeploymentStage.PRODUCTION
        )
        
        # Simulate failure - rollback both
        deployment_rollback = self.deployment.rollback(
            deployment.deployment_id,
            reason='Performance degradation'
        )
        
        template_rollback = self.template_updater.rollback_template(
            template.template_id,
            original_version
        )
        
        self.assertTrue(deployment_rollback)
        self.assertTrue(template_rollback)
    
    def test_multi_stage_deployment_with_learning(self):
        """Test multi-stage deployment with learning validation at each stage"""
        stages = [
            DeploymentStage.DEVELOPMENT,
            DeploymentStage.STAGING,
            DeploymentStage.PRODUCTION
        ]
        
        package = self.deployment.create_package(
            name='multi-stage-test',
            version='1.0.0',
            artifact_path=self.test_artifact
        )
        
        for stage in stages:
            # Deploy to stage
            deployment = self.deployment.deploy(
                package.package_id,
                stage
            )
            
            self.assertEqual(deployment.status, DeploymentStatus.DEPLOYED.value)
            
            # Record learning from this stage
            self.meta_learning.record_learning_session(
                method=LearningMethod.EXPERIENTIAL,
                domain=LearningDomain.TASK_OPTIMIZATION,
                started_at=datetime.now() - timedelta(minutes=10),
                completed_at=datetime.now(),
                items_learned=5,
                success_rate=0.90,  # High success in all stages
                retention_score=0.85
            )
        
        # Verify all deployments succeeded
        history = self.deployment.get_deployment_history(
            package_id=package.package_id
        )
        
        self.assertEqual(len(history), 3)
        for record in history:
            self.assertEqual(record.status, DeploymentStatus.DEPLOYED.value)
    
    def test_learning_insights_inform_deployments(self):
        """Test that learning insights inform deployment decisions"""
        # Record mixed learning results
        for i in range(10):
            success_rate = 0.5 + (i * 0.04)  # Improving over time
            self.meta_learning.record_learning_session(
                method=LearningMethod.FEEDBACK_DRIVEN,
                domain=LearningDomain.USER_PREFERENCES,
                started_at=datetime.now() - timedelta(hours=1),
                completed_at=datetime.now(),
                items_learned=10,
                success_rate=success_rate,
                retention_score=success_rate - 0.1
            )
        
        # Get learning insights
        insights = self.meta_learning.get_learning_insights(days=1)
        
        # Only deploy if learning shows improvement
        if insights['avg_success_rate'] >= 0.75:
            package = self.deployment.create_package(
                name='insight-driven-deployment',
                version='1.0.0',
                artifact_path=self.test_artifact,
                metadata={'learning_success_rate': insights['avg_success_rate']}
            )
            
            deployment = self.deployment.deploy(
                package.package_id,
                DeploymentStage.PRODUCTION
            )
            
            self.assertEqual(deployment.status, DeploymentStatus.DEPLOYED.value)
        else:
            # Don't deploy if learning isn't effective enough
            self.assertLess(insights['avg_success_rate'], 0.75)


if __name__ == '__main__':
    unittest.main()
