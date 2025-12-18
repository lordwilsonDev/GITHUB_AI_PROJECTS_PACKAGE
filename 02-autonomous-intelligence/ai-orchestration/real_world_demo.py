#!/usr/bin/env python3
"""
Real-World Automation Demo - Content Creation Workflow

Demonstrates the full 620-agent system with a practical use case:
Generate 100 social media posts in parallel

Workflow:
1. Research trending topics (10 research agents)
2. Generate post content (50 writing agents)
3. Edit and refine (20 editing agents)
4. Fact-check claims (10 fact-checking agents)
5. Format for platforms (10 formatting agents)
"""

import asyncio
import logging
import json
from typing import Dict, List
from datetime import datetime
from pathlib import Path

# Import our orchestration components
from agent_framework import WorkerAgent, CoordinatorAgent, AgentCapability
from message_bus import create_message_bus, Message, MessageType
from task_queue import TaskQueue, TaskScheduler, Task, TaskPriority
from persistence import PersistenceManager, CrashRecoveryManager
from dashboard import MonitoringSystem
from deploy_agents import AgentDeploymentManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RealWorldDemo')


class ContentCreationWorkflow:
    """
    Real-world content creation workflow.
    
    Generates social media content using multiple specialized agents.
    """
    
    def __init__(self, task_queue: TaskQueue, message_bus=None):
        self.task_queue = task_queue
        self.message_bus = message_bus
        self.workflow_results = []
        
        logger.info("ContentCreationWorkflow initialized")
    
    async def generate_social_posts(self, num_posts: int = 100, topic: str = "AI trends") -> List[str]:
        """
        Generate social media posts using the agent system.
        
        Args:
            num_posts: Number of posts to generate
            topic: Topic for the posts
        
        Returns:
            List of task IDs
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"CONTENT CREATION WORKFLOW: {num_posts} posts on '{topic}'")
        logger.info(f"{'='*60}\n")
        
        all_task_ids = []
        
        # Phase 1: Research (10 agents, 10 research tasks)
        logger.info("[Phase 1/5] Research - Gathering trending topics...")
        research_tasks = []
        for i in range(10):
            task = Task(
                task_id=f"research_{i}",
                task_type="research",
                payload={
                    'topic': topic,
                    'subtopic': f'{topic} aspect {i}',
                    'sources': 50
                },
                priority=TaskPriority.HIGH,
                required_capability='research'
            )
            research_tasks.append(task)
        
        research_ids = await self.task_queue.submit_batch(research_tasks)
        all_task_ids.extend(research_ids)
        logger.info(f"  Submitted {len(research_ids)} research tasks")
        
        # Phase 2: Writing (50 agents, 100 writing tasks)
        logger.info("\n[Phase 2/5] Writing - Generating post content...")
        writing_tasks = []
        for i in range(num_posts):
            task = Task(
                task_id=f"writing_{i}",
                task_type="writing",
                payload={
                    'post_number': i,
                    'topic': topic,
                    'style': 'engaging',
                    'length': 'short',
                    'platform': ['twitter', 'linkedin', 'facebook'][i % 3]
                },
                priority=TaskPriority.NORMAL,
                required_capability='writing',
                depends_on=[research_ids[i % len(research_ids)]]  # Depend on research
            )
            writing_tasks.append(task)
        
        writing_ids = await self.task_queue.submit_batch(writing_tasks)
        all_task_ids.extend(writing_ids)
        logger.info(f"  Submitted {len(writing_ids)} writing tasks")
        
        # Phase 3: Editing (20 agents, 100 editing tasks)
        logger.info("\n[Phase 3/5] Editing - Refining content...")
        editing_tasks = []
        for i in range(num_posts):
            task = Task(
                task_id=f"editing_{i}",
                task_type="editing",
                payload={
                    'post_number': i,
                    'check_grammar': True,
                    'check_tone': True,
                    'optimize_engagement': True
                },
                priority=TaskPriority.NORMAL,
                required_capability='writing',
                depends_on=[writing_ids[i]]  # Depend on writing
            )
            editing_tasks.append(task)
        
        editing_ids = await self.task_queue.submit_batch(editing_tasks)
        all_task_ids.extend(editing_ids)
        logger.info(f"  Submitted {len(editing_ids)} editing tasks")
        
        # Phase 4: Fact-checking (10 agents, 100 fact-check tasks)
        logger.info("\n[Phase 4/5] Fact-checking - Verifying claims...")
        factcheck_tasks = []
        for i in range(num_posts):
            task = Task(
                task_id=f"factcheck_{i}",
                task_type="fact_checking",
                payload={
                    'post_number': i,
                    'verify_claims': True,
                    'check_sources': True
                },
                priority=TaskPriority.HIGH,
                required_capability='analysis',
                depends_on=[editing_ids[i]]  # Depend on editing
            )
            factcheck_tasks.append(task)
        
        factcheck_ids = await self.task_queue.submit_batch(factcheck_tasks)
        all_task_ids.extend(factcheck_ids)
        logger.info(f"  Submitted {len(factcheck_ids)} fact-checking tasks")
        
        # Phase 5: Formatting (10 agents, 100 formatting tasks)
        logger.info("\n[Phase 5/5] Formatting - Optimizing for platforms...")
        formatting_tasks = []
        for i in range(num_posts):
            task = Task(
                task_id=f"formatting_{i}",
                task_type="formatting",
                payload={
                    'post_number': i,
                    'platform': ['twitter', 'linkedin', 'facebook'][i % 3],
                    'add_hashtags': True,
                    'optimize_length': True
                },
                priority=TaskPriority.LOW,
                required_capability='writing',
                depends_on=[factcheck_ids[i]]  # Depend on fact-checking
            )
            formatting_tasks.append(task)
        
        formatting_ids = await self.task_queue.submit_batch(formatting_tasks)
        all_task_ids.extend(formatting_ids)
        logger.info(f"  Submitted {len(formatting_ids)} formatting tasks")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"WORKFLOW SUBMITTED: {len(all_task_ids)} total tasks")
        logger.info(f"{'='*60}\n")
        
        return all_task_ids
    
    async def monitor_workflow_progress(self, task_ids: List[str]):
        """Monitor workflow progress and report status."""
        logger.info("Monitoring workflow progress...\n")
        
        start_time = datetime.now()
        last_completed = 0
        
        while True:
            stats = self.task_queue.get_queue_stats()
            
            completed = stats['total_completed']
            pending = stats['pending']
            running = stats['running']
            failed = stats['total_failed']
            
            # Calculate progress
            total_tasks = len(task_ids)
            progress = (completed / total_tasks) * 100 if total_tasks > 0 else 0
            
            # Show progress update if changed
            if completed != last_completed:
                elapsed = (datetime.now() - start_time).total_seconds()
                throughput = completed / elapsed if elapsed > 0 else 0
                
                logger.info(
                    f"Progress: {progress:.1f}% | "
                    f"Completed: {completed}/{total_tasks} | "
                    f"Running: {running} | "
                    f"Pending: {pending} | "
                    f"Failed: {failed} | "
                    f"Throughput: {throughput:.2f} tasks/sec"
                )
                
                last_completed = completed
            
            # Check if workflow is complete
            if completed + failed >= total_tasks:
                logger.info(f"\n{'='*60}")
                logger.info("WORKFLOW COMPLETE")
                logger.info(f"{'='*60}")
                logger.info(f"Total time: {elapsed:.2f} seconds")
                logger.info(f"Tasks completed: {completed}")
                logger.info(f"Tasks failed: {failed}")
                logger.info(f"Success rate: {(completed/total_tasks)*100:.1f}%")
                logger.info(f"Average throughput: {throughput:.2f} tasks/sec")
                logger.info(f"{'='*60}\n")
                break
            
            await asyncio.sleep(2)


async def main():
    """Main demo execution."""
    print("\n" + "="*60)
    print("🚀 AI AGENT ORCHESTRATION - REAL-WORLD DEMO")
    print("="*60)
    print("\nTask: Generate 100 social media posts using 100 agents")
    print("Workflow: Research → Writing → Editing → Fact-check → Format")
    print("="*60 + "\n")
    
    # Initialize components
    print("[1/7] Initializing task queue...")
    task_queue = TaskQueue(max_concurrent_tasks=500)
    
    print("[2/7] Initializing message bus...")
    message_bus = await create_message_bus()
    
    print("[3/7] Initializing persistence...")
    persistence = PersistenceManager()
    recovery = CrashRecoveryManager(persistence)
    
    # Check for previous crash
    crashed = await recovery.detect_crash()
    if crashed:
        print("  ⚠️  Previous crash detected - recovering...")
        await recovery.recover_from_crash(task_queue, [])
    
    await recovery.mark_running()
    
    print("[4/7] Deploying agents...")
    deployment = AgentDeploymentManager(task_queue, message_bus)
    
    # Deploy 100 agents with content creation focus
    await deployment.deploy_agent_pool({
        'pool_name': 'research',
        'num_agents': 10,
        'capabilities': ['research', 'analysis'],
        'max_concurrent': 5
    })
    
    await deployment.deploy_agent_pool({
        'pool_name': 'writing',
        'num_agents': 50,
        'capabilities': ['writing'],
        'max_concurrent': 3
    })
    
    await deployment.deploy_agent_pool({
        'pool_name': 'editing',
        'num_agents': 20,
        'capabilities': ['writing', 'analysis'],
        'max_concurrent': 4
    })
    
    await deployment.deploy_agent_pool({
        'pool_name': 'factcheck',
        'num_agents': 10,
        'capabilities': ['research', 'analysis'],
        'max_concurrent': 5
    })
    
    await deployment.deploy_agent_pool({
        'pool_name': 'formatting',
        'num_agents': 10,
        'capabilities': ['writing'],
        'max_concurrent': 3
    })
    
    stats = deployment.get_deployment_stats()
    print(f"  ✅ Deployed {stats['active_agents']} agents")
    print(f"  Distribution: {json.dumps(stats['pool_distribution'], indent=4)}")
    
    print("\n[5/7] Starting task scheduler...")
    await deployment.start_scheduler()
    
    print("[6/7] Starting monitoring system...")
    monitoring = MonitoringSystem(task_queue, deployment.all_agents, port=8080)
    await monitoring.start()
    print("  ✅ Dashboard: http://localhost:8080")
    
    print("\n[7/7] Starting auto-checkpoint...")
    await persistence.start_auto_checkpoint(
        lambda: monitoring.get_current_status()
    )
    
    # Create and execute workflow
    print("\n" + "="*60)
    print("EXECUTING CONTENT CREATION WORKFLOW")
    print("="*60 + "\n")
    
    workflow = ContentCreationWorkflow(task_queue, message_bus)
    task_ids = await workflow.generate_social_posts(
        num_posts=100,
        topic="AI and Machine Learning Trends 2025"
    )
    
    # Simulate task processing (in real system, agents would actually process)
    print("\nSimulating agent processing...\n")
    
    async def simulate_processing():
        """Simulate agents processing tasks."""
        processed = 0
        while processed < len(task_ids):
            # Get next batch of tasks
            for agent in deployment.all_agents[:20]:  # Use first 20 agents
                task = task_queue.get_next_task(
                    agent.agent_id,
                    [c.value for c in agent.capabilities]
                )
                
                if task:
                    await task_queue.mark_task_running(task.task_id)
                    
                    # Simulate processing time
                    await asyncio.sleep(0.05)
                    
                    # Complete task
                    await task_queue.complete_task(task.task_id, {
                        'result': f'Completed {task.task_type} for post',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    processed += 1
            
            await asyncio.sleep(0.1)
    
    # Run processing and monitoring in parallel
    await asyncio.gather(
        simulate_processing(),
        workflow.monitor_workflow_progress(task_ids)
    )
    
    # Save workflow results
    print("\nSaving workflow results...")
    final_stats = task_queue.get_queue_stats()
    await persistence.save_workflow_history('content_creation_100_posts', {
        'num_posts': 100,
        'total_tasks': len(task_ids),
        'completed': final_stats['total_completed'],
        'failed': final_stats['total_failed'],
        'success_rate': final_stats['success_rate'],
        'agents_used': stats['active_agents']
    })
    
    # Show final system status
    print("\n" + "="*60)
    print("FINAL SYSTEM STATUS")
    print("="*60)
    final_status = monitoring.get_current_status()
    print(json.dumps(final_status['summary'], indent=2))
    
    print("\n" + "="*60)
    print("Demo complete! System is still running.")
    print("="*60)
    print("\nOptions:")
    print("  - View dashboard: http://localhost:8080")
    print("  - Press Ctrl+C to shutdown")
    print("="*60 + "\n")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        # Cleanup
        await persistence.stop_auto_checkpoint()
        await monitoring.stop()
        await deployment.stop_scheduler()
        await deployment.shutdown_all_agents()
        if message_bus:
            await message_bus.disconnect()
        await recovery.mark_clean_shutdown()
        
        print("\n✅ Shutdown complete")
        print("\nWorkflow results saved to:")
        print(f"  {persistence.workflows_dir}")
        print("\nCheckpoints saved to:")
        print(f"  {persistence.checkpoints_dir}")
        print("\n" + "="*60)
        print("🎉 Thank you for using AI Agent Orchestration!")
        print("="*60 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
