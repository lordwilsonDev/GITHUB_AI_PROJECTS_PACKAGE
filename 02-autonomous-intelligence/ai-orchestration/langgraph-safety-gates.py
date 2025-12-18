"""LangGraph AI Agent with Safety Gates and Human-in-the-Loop

Demonstrates:
- Multi-layer guardrails for autonomous agents
- Human approval gates for risky operations
- Sandbox-based modification testing
- State persistence and rollback capabilities
"""

from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
import operator


class AgentState(TypedDict):
    """State maintained across agent execution"""
    messages: Annotated[list, operator.add]
    task_queue: list
    completed_tasks: list
    pending_approval: dict | None
    modifications_log: list
    risk_level: str


def input_validation_node(state: AgentState) -> AgentState:
    """Layer 1: Input validation and sanitization"""
    print("[SAFETY] Validating inputs...")
    
    # Validate task queue
    validated_tasks = []
    for task in state.get("task_queue", []):
        # Check for malicious patterns
        if "delete_database" in str(task).lower():
            print(f"[SAFETY] Blocked dangerous task: {task}")
            continue
        validated_tasks.append(task)
    
    state["task_queue"] = validated_tasks
    return state


def task_execution_node(state: AgentState) -> AgentState:
    """Layer 2: Execute tasks with in-process monitoring"""
    print("[EXECUTION] Processing tasks...")
    
    completed = []
    for task in state.get("task_queue", []):
        print(f"  Executing: {task}")
        
        # Simulate task execution
        result = {"task": task, "status": "completed", "output": f"Result of {task}"}
        completed.append(result)
    
    state["completed_tasks"] = state.get("completed_tasks", []) + completed
    state["task_queue"] = []
    return state


def self_modification_proposal_node(state: AgentState) -> AgentState:
    """Agent proposes self-modification"""
    print("[AGENT] Proposing self-modification...")
    
    # Agent analyzes performance and proposes improvement
    modification = {
        "type": "algorithm_update",
        "description": "Optimize task scheduling algorithm",
        "code_changes": "def new_scheduler(): ...",
        "risk_level": "medium",
        "expected_improvement": "20% faster task processing"
    }
    
    state["pending_approval"] = modification
    state["risk_level"] = modification["risk_level"]
    return state


def sandbox_validation_node(state: AgentState) -> AgentState:
    """Layer 3: Validate modification in sandbox"""
    print("[SAFETY] Testing modification in sandbox...")
    
    modification = state.get("pending_approval")
    if not modification:
        return state
    
    # Simulate sandbox testing
    # In production: Docker container, E2B sandbox, or gVisor
    sandbox_results = {
        "tests_passed": True,
        "benchmark_score": 0.95,
        "security_scan": "clean",
        "resource_usage": "within limits"
    }
    
    modification["sandbox_results"] = sandbox_results
    state["pending_approval"] = modification
    
    print(f"  Sandbox results: {sandbox_results}")
    return state


def approval_gate_node(state: AgentState) -> AgentState:
    """Layer 4: Human approval gate for risky operations"""
    print("[SAFETY GATE] Waiting for human approval...")
    
    modification = state.get("pending_approval")
    risk_level = state.get("risk_level", "low")
    
    # Auto-approve low-risk modifications
    if risk_level == "low":
        print("  Auto-approved (low risk)")
        state["modifications_log"] = state.get("modifications_log", []) + [modification]
        state["pending_approval"] = None
        return state
    
    # For medium/high risk, workflow pauses here
    # In production with Temporal: workflow.wait_condition()
    # In LangGraph: use interrupt() to pause execution
    print(f"  PAUSED - Requires human approval for {risk_level} risk modification")
    print(f"  Modification: {modification['description']}")
    
    # This would pause execution until human provides approval signal
    # For this example, we'll simulate approval
    approved = True  # In production: wait for signal
    
    if approved:
        print("  ✓ APPROVED by human operator")
        state["modifications_log"] = state.get("modifications_log", []) + [modification]
    else:
        print("  ✗ REJECTED by human operator")
    
    state["pending_approval"] = None
    return state


def output_verification_node(state: AgentState) -> AgentState:
    """Layer 5: Verify outputs before deployment"""
    print("[SAFETY] Verifying outputs...")
    
    # Check for hallucinations, harmful content, etc.
    for task in state.get("completed_tasks", []):
        output = task.get("output", "")
        
        # Simulate verification checks
        if "harmful" in output.lower():
            print(f"  ⚠ Blocked harmful output: {task}")
            task["status"] = "blocked"
    
    return state


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """Routing logic"""
    if state.get("task_queue"):
        return "continue"
    return "end"


def create_agent_graph():
    """Build LangGraph with safety gates"""
    
    # Create graph with checkpointing for state persistence
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("input_validation", input_validation_node)
    workflow.add_node("task_execution", task_execution_node)
    workflow.add_node("self_modification", self_modification_proposal_node)
    workflow.add_node("sandbox_validation", sandbox_validation_node)
    workflow.add_node("approval_gate", approval_gate_node)
    workflow.add_node("output_verification", output_verification_node)
    
    # Define flow
    workflow.set_entry_point("input_validation")
    workflow.add_edge("input_validation", "task_execution")
    workflow.add_edge("task_execution", "output_verification")
    workflow.add_edge("output_verification", "self_modification")
    workflow.add_edge("self_modification", "sandbox_validation")
    workflow.add_edge("sandbox_validation", "approval_gate")
    workflow.add_edge("approval_gate", END)
    
    # Add memory for state persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)


def main():
    """Example usage with safety gates"""
    print("=" * 60)
    print("AI Agent with Multi-Layer Safety Gates")
    print("=" * 60)
    
    # Create agent graph
    agent = create_agent_graph()
    
    # Initial state
    initial_state = {
        "messages": [],
        "task_queue": [
            "analyze_data",
            "generate_report",
            "send_email",  # Safe operation
            # "delete_database",  # Would be blocked by input validation
        ],
        "completed_tasks": [],
        "pending_approval": None,
        "modifications_log": [],
        "risk_level": "low"
    }
    
    # Run agent with state persistence
    config = {"configurable": {"thread_id": "agent-001"}}
    
    print("\n[START] Running agent workflow...\n")
    
    # Execute workflow
    final_state = agent.invoke(initial_state, config)
    
    print("\n" + "=" * 60)
    print("[COMPLETE] Workflow finished")
    print("=" * 60)
    print(f"\nCompleted tasks: {len(final_state['completed_tasks'])}")
    print(f"Modifications approved: {len(final_state['modifications_log'])}")
    
    # Show state can be retrieved later
    print("\n[CHECKPOINT] State persisted for recovery")
    print(f"Thread ID: {config['configurable']['thread_id']}")
    
    # Demonstrate rollback capability
    print("\n[ROLLBACK] Can restore to any previous state")
    print(f"Modifications log: {final_state['modifications_log']}")


if __name__ == "__main__":
    main()
