#!/usr/bin/env python3
"""
The Infinite Recursion Engine - Level 7 Self-Replication Module

This engine generates new code based on goals, creating systems
that build systems. The Ouroboros eating its own tail.

Philosophy:
- Code is crystallized thought
- A system that can write code can evolve indefinitely
- The ultimate intelligence is generative, not just reactive
"""

import os
import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import textwrap


class CodeTemplate:
    """Represents a code template with placeholders"""
    
    def __init__(self, name: str, template: str, placeholders: List[str], 
                 description: str, category: str):
        self.name = name
        self.template = template
        self.placeholders = placeholders
        self.description = description
        self.category = category
    
    def render(self, **kwargs) -> str:
        """Render template with provided values"""
        code = self.template
        for key, value in kwargs.items():
            code = code.replace(f"{{{{{key}}}}}", str(value))
        return code
    
    def validate_placeholders(self, **kwargs) -> bool:
        """Check if all required placeholders are provided"""
        return all(key in kwargs for key in self.placeholders)


class TemplateLibrary:
    """Library of code templates"""
    
    def __init__(self):
        self.templates: Dict[str, CodeTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default code templates"""
        
        # Template 1: Data Class
        self.add_template(CodeTemplate(
            name="data_class",
            template=textwrap.dedent('''
                from dataclasses import dataclass
                from typing import {{type_hints}}
                
                @dataclass
                class {{class_name}}:
                    """{{description}}"""
                    {{fields}}
                    
                    def validate(self) -> bool:
                        """Validate the data"""
                        # TODO: Add validation logic
                        return True
            ''').strip(),
            placeholders=["class_name", "description", "fields", "type_hints"],
            description="Creates a dataclass with validation",
            category="data_structures"
        ))
        
        # Template 2: API Endpoint
        self.add_template(CodeTemplate(
            name="api_endpoint",
            template=textwrap.dedent('''
                from fastapi import APIRouter, HTTPException
                from pydantic import BaseModel
                
                router = APIRouter()
                
                class {{request_model}}(BaseModel):
                    """Request model for {{endpoint_name}}"""
                    {{request_fields}}
                
                class {{response_model}}(BaseModel):
                    """Response model for {{endpoint_name}}"""
                    {{response_fields}}
                
                @router.{{method}}("{{path}}")
                async def {{endpoint_name}}(request: {{request_model}}) -> {{response_model}}:
                    """{{description}}"""
                    # TODO: Implement endpoint logic
                    return {{response_model}}()
            ''').strip(),
            placeholders=["endpoint_name", "method", "path", "request_model", 
                         "response_model", "request_fields", "response_fields", "description"],
            description="Creates a FastAPI endpoint",
            category="api"
        ))
        
        # Template 3: State Machine
        self.add_template(CodeTemplate(
            name="state_machine",
            template=textwrap.dedent('''
                from enum import Enum
                from typing import Dict, Callable, Optional
                
                class {{state_enum}}(Enum):
                    """States for {{machine_name}}"""
                    {{states}}
                
                class {{machine_name}}:
                    """{{description}}"""
                    
                    def __init__(self):
                        self.state = {{state_enum}}.{{initial_state}}
                        self.transitions: Dict[{{state_enum}}, Dict[str, {{state_enum}}]] = {{transitions}}
                    
                    def transition(self, event: str) -> bool:
                        """Attempt to transition on event"""
                        if event in self.transitions.get(self.state, {}):
                            old_state = self.state
                            self.state = self.transitions[self.state][event]
                            print(f"Transitioned: {old_state} -> {self.state} (event: {event})")
                            return True
                        return False
                    
                    def get_state(self) -> {{state_enum}}:
                        """Get current state"""
                        return self.state
            ''').strip(),
            placeholders=["machine_name", "state_enum", "states", "initial_state", 
                         "transitions", "description"],
            description="Creates a finite state machine",
            category="patterns"
        ))
        
        # Template 4: Observer Pattern
        self.add_template(CodeTemplate(
            name="observer",
            template=textwrap.dedent('''
                from typing import List, Callable
                from abc import ABC, abstractmethod
                
                class {{observer_interface}}(ABC):
                    """Observer interface for {{subject_name}}"""
                    
                    @abstractmethod
                    def update(self, {{update_params}}) -> None:
                        """Called when subject changes"""
                        pass
                
                class {{subject_name}}:
                    """{{description}}"""
                    
                    def __init__(self):
                        self._observers: List[{{observer_interface}}] = []
                        {{state_vars}}
                    
                    def attach(self, observer: {{observer_interface}}) -> None:
                        """Attach an observer"""
                        if observer not in self._observers:
                            self._observers.append(observer)
                    
                    def detach(self, observer: {{observer_interface}}) -> None:
                        """Detach an observer"""
                        if observer in self._observers:
                            self._observers.remove(observer)
                    
                    def notify(self) -> None:
                        """Notify all observers"""
                        for observer in self._observers:
                            observer.update({{notify_args}})
                    
                    {{methods}}
            ''').strip(),
            placeholders=["subject_name", "observer_interface", "update_params", 
                         "state_vars", "notify_args", "methods", "description"],
            description="Creates an observer pattern implementation",
            category="patterns"
        ))
        
        # Template 5: Plugin System
        self.add_template(CodeTemplate(
            name="plugin_system",
            template=textwrap.dedent('''
                from abc import ABC, abstractmethod
                from typing import Dict, List, Any
                import importlib
                import inspect
                
                class {{plugin_interface}}(ABC):
                    """Plugin interface for {{system_name}}"""
                    
                    @property
                    @abstractmethod
                    def name(self) -> str:
                        """Plugin name"""
                        pass
                    
                    @abstractmethod
                    def execute(self, {{execute_params}}) -> {{return_type}}:
                        """Execute plugin logic"""
                        pass
                
                class {{manager_name}}:
                    """{{description}}"""
                    
                    def __init__(self):
                        self.plugins: Dict[str, {{plugin_interface}}] = {}
                    
                    def register(self, plugin: {{plugin_interface}}) -> None:
                        """Register a plugin"""
                        self.plugins[plugin.name] = plugin
                        print(f"✅ Registered plugin: {plugin.name}")
                    
                    def unregister(self, name: str) -> None:
                        """Unregister a plugin"""
                        if name in self.plugins:
                            del self.plugins[name]
                            print(f"❌ Unregistered plugin: {name}")
                    
                    def execute(self, name: str, {{execute_params}}) -> {{return_type}}:
                        """Execute a plugin by name"""
                        if name not in self.plugins:
                            raise ValueError(f"Plugin not found: {name}")
                        return self.plugins[name].execute({{execute_args}})
                    
                    def list_plugins(self) -> List[str]:
                        """List all registered plugins"""
                        return list(self.plugins.keys())
            ''').strip(),
            placeholders=["system_name", "plugin_interface", "manager_name", 
                         "execute_params", "execute_args", "return_type", "description"],
            description="Creates a plugin system",
            category="architecture"
        ))
    
    def add_template(self, template: CodeTemplate):
        """Add a template to the library"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[CodeTemplate]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def list_templates(self, category: Optional[str] = None) -> List[str]:
        """List available templates"""
        if category:
            return [name for name, t in self.templates.items() if t.category == category]
        return list(self.templates.keys())


class SemanticCodeGenerator:
    """Generates code based on semantic understanding"""
    
    def __init__(self, template_library: TemplateLibrary):
        self.library = template_library
        self.generation_history = []
    
    def generate_from_goal(self, goal: str) -> Optional[str]:
        """Generate code from a natural language goal"""
        
        # Simple keyword matching (in production, use LLM)
        goal_lower = goal.lower()
        
        # Detect intent
        if "api" in goal_lower or "endpoint" in goal_lower:
            return self._generate_api_endpoint(goal)
        
        elif "state machine" in goal_lower or "fsm" in goal_lower:
            return self._generate_state_machine(goal)
        
        elif "observer" in goal_lower or "event" in goal_lower:
            return self._generate_observer(goal)
        
        elif "plugin" in goal_lower:
            return self._generate_plugin_system(goal)
        
        elif "data class" in goal_lower or "model" in goal_lower:
            return self._generate_data_class(goal)
        
        else:
            return None
    
    def _generate_api_endpoint(self, goal: str) -> str:
        """Generate an API endpoint"""
        template = self.library.get_template("api_endpoint")
        
        # Extract info from goal (simplified)
        endpoint_name = "process_request"
        method = "post"
        path = "/api/process"
        
        code = template.render(
            endpoint_name=endpoint_name,
            method=method,
            path=path,
            request_model="ProcessRequest",
            response_model="ProcessResponse",
            request_fields="data: str",
            response_fields="result: str\n    success: bool",
            description=goal
        )
        
        self._log_generation("api_endpoint", goal, code)
        return code
    
    def _generate_state_machine(self, goal: str) -> str:
        """Generate a state machine"""
        template = self.library.get_template("state_machine")
        
        code = template.render(
            machine_name="WorkflowStateMachine",
            state_enum="WorkflowState",
            states="IDLE = 'idle'\n    PROCESSING = 'processing'\n    COMPLETE = 'complete'\n    ERROR = 'error'",
            initial_state="IDLE",
            transitions="""{
                WorkflowState.IDLE: {'start': WorkflowState.PROCESSING},
                WorkflowState.PROCESSING: {'complete': WorkflowState.COMPLETE, 'error': WorkflowState.ERROR},
                WorkflowState.ERROR: {'retry': WorkflowState.PROCESSING}
            }""",
            description=goal
        )
        
        self._log_generation("state_machine", goal, code)
        return code
    
    def _generate_observer(self, goal: str) -> str:
        """Generate an observer pattern"""
        template = self.library.get_template("observer")
        
        code = template.render(
            subject_name="DataSubject",
            observer_interface="DataObserver",
            update_params="data: Any",
            state_vars="self._data = None",
            notify_args="self._data",
            methods=textwrap.dedent('''
                def set_data(self, data: Any) -> None:
                    """Update data and notify observers"""
                    self._data = data
                    self.notify()
            ''').strip(),
            description=goal
        )
        
        self._log_generation("observer", goal, code)
        return code
    
    def _generate_plugin_system(self, goal: str) -> str:
        """Generate a plugin system"""
        template = self.library.get_template("plugin_system")
        
        code = template.render(
            system_name="ExtensionSystem",
            plugin_interface="Extension",
            manager_name="ExtensionManager",
            execute_params="context: Dict[str, Any]",
            execute_args="context",
            return_type="Any",
            description=goal
        )
        
        self._log_generation("plugin_system", goal, code)
        return code
    
    def _generate_data_class(self, goal: str) -> str:
        """Generate a data class"""
        template = self.library.get_template("data_class")
        
        code = template.render(
            class_name="DataModel",
            description=goal,
            fields="name: str\n    value: float\n    timestamp: str",
            type_hints="str, float"
        )
        
        self._log_generation("data_class", goal, code)
        return code
    
    def _log_generation(self, template_name: str, goal: str, code: str):
        """Log code generation"""
        self.generation_history.append({
            "timestamp": datetime.now().isoformat(),
            "template": template_name,
            "goal": goal,
            "code_length": len(code),
            "status": "generated"
        })


class TestSynthesizer:
    """Generates tests for generated code"""
    
    def generate_test(self, code: str, module_name: str) -> str:
        """Generate a test for the given code"""
        
        # Parse code to extract classes/functions
        try:
            tree = ast.parse(code)
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except:
            classes = []
            functions = []
        
        test_code = f'''
import pytest
from {module_name} import *

class Test{module_name.title()}:
    """Tests for {module_name}"""
    
'''
        
        # Generate test for each class
        for cls in classes:
            test_code += f'''
    def test_{cls.lower()}_creation(self):
        """Test {cls} can be created"""
        obj = {cls}()
        assert obj is not None
    
'''
        
        # Generate test for each function
        for func in functions:
            if not func.startswith('_'):
                test_code += f'''
    def test_{func}(self):
        """Test {func} function"""
        # TODO: Implement test
        pass
    
'''
        
        return test_code.strip()


class InfiniteRecursionEngine:
    """Main engine that coordinates code generation"""
    
    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.library = TemplateLibrary()
        self.generator = SemanticCodeGenerator(self.library)
        self.test_synthesizer = TestSynthesizer()
        self.generation_log_path = self.codebase_path / 'living_memory' / 'code_generation_log.json'
        self.generation_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def dream_code(self, goal: str) -> Optional[Dict]:
        """Generate code from a goal"""
        
        print(f"\n🌀 INFINITE RECURSION ENGINE")
        print(f"📝 Goal: {goal}")
        print("=" * 60)
        
        # Generate code
        code = self.generator.generate_from_goal(goal)
        
        if not code:
            print("❌ Could not generate code for this goal")
            return None
        
        print("\n✨ Generated Code:")
        print("-" * 60)
        print(code)
        print("-" * 60)
        
        # Generate test
        test_code = self.test_synthesizer.generate_test(code, "generated_module")
        
        print("\n🧪 Generated Test:")
        print("-" * 60)
        print(test_code)
        print("-" * 60)
        
        result = {
            "goal": goal,
            "code": code,
            "test": test_code,
            "timestamp": datetime.now().isoformat(),
            "status": "generated"
        }
        
        # Log generation
        self._save_generation(result)
        
        print("\n✅ Code generation complete!")
        
        return result
    
    def save_to_file(self, code: str, filename: str, directory: str = "generated"):
        """Save generated code to a file"""
        
        output_dir = self.codebase_path / directory
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / filename
        
        with open(output_path, 'w') as f:
            f.write(code)
        
        print(f"💾 Saved to: {output_path}")
        
        return output_path
    
    def _save_generation(self, result: Dict):
        """Save generation to log"""
        
        if self.generation_log_path.exists():
            with open(self.generation_log_path, 'r') as f:
                log = json.load(f)
        else:
            log = []
        
        log.append(result)
        
        with open(self.generation_log_path, 'w') as f:
            json.dump(log, f, indent=2)
    
    def get_generation_stats(self) -> Dict:
        """Get statistics on code generation"""
        
        if not self.generation_log_path.exists():
            return {"total": 0}
        
        with open(self.generation_log_path, 'r') as f:
            log = json.load(f)
        
        return {
            "total": len(log),
            "recent": log[-5:] if log else []
        }


def demo():
    """Demo the infinite recursion engine"""
    
    engine = InfiniteRecursionEngine('/Users/lordwilson/jarvis_m1')
    
    # Example goals
    goals = [
        "Create an API endpoint for processing user data",
        "Build a state machine for workflow management",
        "Implement an observer pattern for data changes",
        "Create a plugin system for extensions"
    ]
    
    for goal in goals:
        result = engine.dream_code(goal)
        if result:
            print(f"\n{'='*60}\n")
    
    # Show stats
    stats = engine.get_generation_stats()
    print(f"\n📊 Generation Statistics:")
    print(f"   Total generated: {stats['total']}")


if __name__ == "__main__":
    demo()
