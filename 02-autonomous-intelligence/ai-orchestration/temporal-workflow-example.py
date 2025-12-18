"""Temporal Workflow Example with Safety Gates for AI Agents

Demonstrates:
- Durable execution with state persistence
- Human-in-the-loop approval gates
- Signal handlers for runtime control
- Continue-As-New for long-running workflows
"""

import asyncio
from datetime import timedelta
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


@activity.defn
async def execute_agent_task(task_data: dict) -> dict:
    """Execute a single AI agent task"""
    print(f"Executing task: {task_data}")
    # Simulate agent work
    await asyncio.sleep(2)
    return {"status": "completed", "result": f"Processed {task_data['task_id']}"}


@activity.defn
async def validate_agent_modification(modification: dict) -> bool:
    """Validate proposed self-modification in sandbox"""
    print(f"Validating modification: {modification}")
    # Run in sandbox, check against benchmarks
    await asyncio.sleep(1)
    return True  # Simplified for example


@workflow.defn
class AIAgentCoordinationWorkflow:
    """Coordinates multiple AI agents with safety gates"""

    def __init__(self):
        self.approved_modifications = []
        self.pending_approval = None
        self.task_count = 0

    @workflow.run
    async def run(self, agent_config: dict) -> dict:
        """Main workflow execution"""
        
        # Execute initial tasks
        for i in range(5):
            task_data = {"task_id": i, "agent_id": agent_config["agent_id"]}
            result = await workflow.execute_activity(
                execute_agent_task,
                task_data,
                start_to_close_timeout=timedelta(seconds=30),
            )
            self.task_count += 1

        # Agent proposes self-modification
        modification = {
            "type": "code_update",
            "description": "Optimize task processing",
            "risk_level": "medium"
        }

        # Validate in sandbox
        is_valid = await workflow.execute_activity(
            validate_agent_modification,
            modification,
            start_to_close_timeout=timedelta(seconds=60),
        )

        if is_valid and modification["risk_level"] in ["medium", "high"]:
            # SAFETY GATE: Wait for human approval
            self.pending_approval = modification
            
            # Wait indefinitely for approval signal (consumes zero compute)
            await workflow.wait_condition(
                lambda: self.pending_approval is None
            )

        return {
            "tasks_completed": self.task_count,
            "modifications_approved": len(self.approved_modifications),
            "status": "success"
        }

    @workflow.signal
    async def approve_modification(self, approved: bool):
        """Signal handler for human approval"""
        if approved and self.pending_approval:
            self.approved_modifications.append(self.pending_approval)
        self.pending_approval = None

    @workflow.signal
    async def emergency_stop(self):
        """Emergency stop signal"""
        raise workflow.ApplicationError("Emergency stop triggered")

    @workflow.query
    def get_status(self) -> dict:
        """Query current workflow state"""
        return {
            "task_count": self.task_count,
            "pending_approval": self.pending_approval is not None,
            "approved_modifications": len(self.approved_modifications)
        }


async def main():
    """Example usage"""
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")

    # Start workflow
    handle = await client.start_workflow(
        AIAgentCoordinationWorkflow.run,
        {"agent_id": "agent-001"},
        id="ai-agent-workflow-001",
        task_queue="ai-agent-tasks",
    )

    print(f"Started workflow: {handle.id}")

    # Simulate human approval after 5 seconds
    await asyncio.sleep(5)
    await handle.signal(AIAgentCoordinationWorkflow.approve_modification, True)

    # Wait for completion
    result = await handle.result()
    print(f"Workflow result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
