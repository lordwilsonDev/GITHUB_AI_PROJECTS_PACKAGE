# architecture/brain_core.py
import autogen
from tools.physical_hand import safe_click

# Configuration for Gemma 2 9B via Ollama
config_list = [
    {
        "model": "gemma2:9b",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama", 
        "price": [0, 0], # It's free!
    }
]

# 1. The Solver: Physical Agent
solver = autogen.AssistantAgent(
    name="Physical_Solver",
    system_message="""You are a macOS automation expert. 
    You have a tool 'safe_click'. 
    Plan your actions. 
    If a click fails, reflect on why (wrong coordinates?) and retry.
    Output 'TERMINATE' when the task is visually complete.""",
    llm_config={
        "config_list": config_list,
        "timeout": 120,
        "functions": [
            {
                "name": "safe_click",
                "description": "Click a pixel on screen",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"}
                    },
                    "required": ["x", "y"]
                }
            }
        ]
    }
)

# 2. The User Proxy: The Executor
user_proxy = autogen.UserProxyAgent(
    name="Executor",
    human_input_mode="ALWAYS", # Safety First for Level 33
    max_consecutive_auto_reply=5,
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": False  # Disable Docker requirement
    },
    function_map={"safe_click": safe_click} 
)

if __name__ == "__main__":
    # Example usage
    print("Level 33 Sovereign Architecture - Brain Core")
    print("Physical Agent initialized with Gemma 2 9B")
    
    # Start a conversation
    # user_proxy.initiate_chat(
    #     solver,
    #     message="Click at coordinates 100, 100"
    # )
