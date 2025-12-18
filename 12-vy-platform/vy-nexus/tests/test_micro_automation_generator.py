#!/usr/bin/env python3
"""
Tests for Micro-Automation Generator
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.optimization.micro_automation_generator import MicroAutomationGenerator


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def generator(temp_dir):
    """Create a MicroAutomationGenerator instance"""
    return MicroAutomationGenerator(data_dir=temp_dir)


class TestMicroAutomationGenerator:
    """Test suite for MicroAutomationGenerator"""
    
    def test_initialization(self, generator, temp_dir):
        """Test generator initialization"""
        assert generator.data_dir == temp_dir
        assert os.path.exists(temp_dir)
        assert os.path.exists(generator.scripts_dir)
        assert isinstance(generator.templates, dict)
        assert len(generator.templates) > 0
    
    def test_default_templates_loaded(self, generator):
        """Test that default templates are loaded"""
        expected_templates = [
            "file_operations",
            "data_processing",
            "api_calls",
            "text_processing",
            "notification"
        ]
        
        for template in expected_templates:
            assert template in generator.templates
            assert "name" in generator.templates[template]
            assert "description" in generator.templates[template]
            assert "parameters" in generator.templates[template]
    
    def test_generate_id(self, generator):
        """Test automation ID generation"""
        task_pattern1 = {"name": "Test Task", "steps": ["step1", "step2"]}
        task_pattern2 = {"name": "Test Task", "steps": ["step1", "step2"]}
        task_pattern3 = {"name": "Different Task", "steps": ["step1"]}
        
        id1 = generator._generate_id(task_pattern1)
        id2 = generator._generate_id(task_pattern2)
        id3 = generator._generate_id(task_pattern3)
        
        # Same pattern should generate same ID
        assert id1 == id2
        # Different pattern should generate different ID
        assert id1 != id3
        # ID should be 12 characters
        assert len(id1) == 12
    
    def test_detect_template_type_file_operations(self, generator):
        """Test template type detection for file operations"""
        task_pattern = {
            "type": "file_copy",
            "steps": ["copy file from source to destination"]
        }
        
        template_type = generator._detect_template_type(task_pattern)
        assert template_type == "file_operations"
    
    def test_detect_template_type_data_processing(self, generator):
        """Test template type detection for data processing"""
        task_pattern = {
            "type": "data_transform",
            "steps": ["transform data", "process records"]
        }
        
        template_type = generator._detect_template_type(task_pattern)
        assert template_type == "data_processing"
    
    def test_detect_template_type_api_calls(self, generator):
        """Test template type detection for API calls"""
        task_pattern = {
            "type": "api_request",
            "steps": ["fetch data from API"]
        }
        
        template_type = generator._detect_template_type(task_pattern)
        assert template_type == "api_calls"
    
    def test_detect_template_type_text_processing(self, generator):
        """Test template type detection for text processing"""
        task_pattern = {
            "type": "text_format",
            "steps": ["format text", "replace strings"]
        }
        
        template_type = generator._detect_template_type(task_pattern)
        assert template_type == "text_processing"
    
    def test_detect_template_type_default(self, generator):
        """Test template type detection defaults to data_processing"""
        task_pattern = {
            "type": "unknown_type",
            "steps": ["do something"]
        }
        
        template_type = generator._detect_template_type(task_pattern)
        assert template_type == "data_processing"
    
    def test_extract_parameters(self, generator):
        """Test parameter extraction from task pattern"""
        task_pattern = {
            "parameters": {
                "source": "/path/to/source",
                "destination": "/path/to/dest",
                "operation": "copy"
            }
        }
        
        params = generator._extract_parameters(task_pattern, "file_operations")
        
        assert params["source"] == "/path/to/source"
        assert params["destination"] == "/path/to/dest"
        assert params["operation"] == "copy"
    
    def test_infer_parameter(self, generator):
        """Test parameter inference from task steps"""
        task_pattern = {
            "steps": ["copy from /source to /destination"]
        }
        
        source = generator._infer_parameter("source", task_pattern)
        destination = generator._infer_parameter("destination", task_pattern)
        
        # Should return inferred values or placeholders
        assert source == "<inferred_source>"
        assert destination == "<inferred_destination>"
    
    def test_generate_automation_file_operations(self, generator):
        """Test generating file operations automation"""
        task_pattern = {
            "name": "Daily Backup",
            "description": "Backup important files",
            "type": "file_copy",
            "parameters": {
                "source": "/data/important.json",
                "destination": "/backup/important.json",
                "operation": "copy"
            }
        }
        
        automation = generator.generate_automation(task_pattern)
        
        assert automation["name"] == "Daily Backup"
        assert automation["description"] == "Backup important files"
        assert automation["template_type"] == "file_operations"
        assert automation["status"] == "ready"
        assert automation["script_path"] is not None
        assert os.path.exists(automation["script_path"])
        assert automation["execution_count"] == 0
    
    def test_generate_automation_with_explicit_template(self, generator):
        """Test generating automation with explicit template type"""
        task_pattern = {
            "name": "API Fetch",
            "description": "Fetch data from API",
            "parameters": {
                "endpoint": "https://api.example.com/data",
                "method": "GET"
            }
        }
        
        automation = generator.generate_automation(task_pattern, template_type="api_calls")
        
        assert automation["template_type"] == "api_calls"
        assert automation["status"] == "ready"
    
    def test_generate_automation_invalid_template(self, generator):
        """Test generating automation with invalid template type"""
        task_pattern = {"name": "Test"}
        
        with pytest.raises(ValueError, match="Unknown template type"):
            generator.generate_automation(task_pattern, template_type="invalid_template")
    
    def test_generate_script_creates_executable(self, generator):
        """Test that generated scripts are executable"""
        task_pattern = {
            "name": "Test Script",
            "type": "file_copy",
            "parameters": {
                "source": "/test/source",
                "destination": "/test/dest",
                "operation": "copy"
            }
        }
        
        automation = generator.generate_automation(task_pattern)
        script_path = automation["script_path"]
        
        # Check file exists and is executable
        assert os.path.exists(script_path)
        assert os.access(script_path, os.X_OK)
    
    def test_generate_file_ops_script_content(self, generator):
        """Test file operations script content generation"""
        parameters = {
            "source": "/test/source.txt",
            "destination": "/test/dest.txt",
            "operation": "copy"
        }
        
        script_content = generator._generate_file_ops_script(parameters)
        
        assert "#!/usr/bin/env python3" in script_content
        assert "def execute():" in script_content
        assert "/test/source.txt" in script_content
        assert "/test/dest.txt" in script_content
        assert "copy" in script_content
        assert "shutil.copy2" in script_content
    
    def test_generate_data_proc_script_content(self, generator):
        """Test data processing script content generation"""
        parameters = {
            "input_file": "/data/input.json",
            "output_file": "/data/output.json",
            "transformations": ["normalize", "filter"]
        }
        
        script_content = generator._generate_data_proc_script(parameters)
        
        assert "#!/usr/bin/env python3" in script_content
        assert "def execute():" in script_content
        assert "/data/input.json" in script_content
        assert "/data/output.json" in script_content
        assert "import json" in script_content
    
    def test_generate_api_call_script_content(self, generator):
        """Test API call script content generation"""
        parameters = {
            "endpoint": "https://api.example.com/data",
            "method": "POST",
            "payload": {"key": "value"}
        }
        
        script_content = generator._generate_api_call_script(parameters)
        
        assert "#!/usr/bin/env python3" in script_content
        assert "def execute():" in script_content
        assert "https://api.example.com/data" in script_content
        assert "POST" in script_content
        assert "import requests" in script_content
    
    def test_generate_text_proc_script_content(self, generator):
        """Test text processing script content generation"""
        parameters = {
            "input_text": "Hello World",
            "operations": ["uppercase", "trim"],
            "output_format": "text"
        }
        
        script_content = generator._generate_text_proc_script(parameters)
        
        assert "#!/usr/bin/env python3" in script_content
        assert "def execute():" in script_content
        assert "Hello World" in script_content
    
    def test_generate_notification_script_content(self, generator):
        """Test notification script content generation"""
        parameters = {
            "message": "Task completed",
            "channel": "email",
            "recipients": ["user@example.com"]
        }
        
        script_content = generator._generate_notification_script(parameters)
        
        assert "#!/usr/bin/env python3" in script_content
        assert "def execute():" in script_content
        assert "Task completed" in script_content
        assert "email" in script_content
    
    def test_automation_persisted_to_file(self, generator):
        """Test that automation is persisted to JSONL file"""
        task_pattern = {
            "name": "Persistence Test",
            "type": "file_copy",
            "parameters": {"source": "/a", "destination": "/b", "operation": "copy"}
        }
        
        automation = generator.generate_automation(task_pattern)
        
        # Check file exists
        assert os.path.exists(generator.automations_file)
        
        # Read and verify
        with open(generator.automations_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            last_automation = json.loads(lines[-1])
            assert last_automation["id"] == automation["id"]
            assert last_automation["name"] == "Persistence Test"
    
    def test_find_automation(self, generator):
        """Test finding automation by ID"""
        task_pattern = {
            "name": "Find Test",
            "type": "file_copy",
            "parameters": {"source": "/a", "destination": "/b", "operation": "copy"}
        }
        
        automation = generator.generate_automation(task_pattern)
        automation_id = automation["id"]
        
        found = generator._find_automation(automation_id)
        
        assert found is not None
        assert found["id"] == automation_id
        assert found["name"] == "Find Test"
    
    def test_find_nonexistent_automation(self, generator):
        """Test finding non-existent automation returns None"""
        found = generator._find_automation("nonexistent_id")
        assert found is None
    
    def test_list_automations(self, generator):
        """Test listing all automations"""
        # Generate multiple automations
        for i in range(3):
            task_pattern = {
                "name": f"Test {i}",
                "type": "file_copy",
                "parameters": {"source": f"/a{i}", "destination": f"/b{i}", "operation": "copy"}
            }
            generator.generate_automation(task_pattern)
        
        automations = generator.list_automations()
        
        assert len(automations) == 3
        assert all("id" in auto for auto in automations)
        assert all("name" in auto for auto in automations)
    
    def test_list_automations_empty(self, generator):
        """Test listing automations when none exist"""
        automations = generator.list_automations()
        assert automations == []
    
    def test_get_automation_statistics(self, generator):
        """Test getting automation statistics"""
        # Generate automations of different types
        patterns = [
            {"name": "File Op 1", "type": "file_copy", "parameters": {"source": "/a", "destination": "/b", "operation": "copy"}},
            {"name": "File Op 2", "type": "file_move", "parameters": {"source": "/c", "destination": "/d", "operation": "move"}},
            {"name": "API Call", "type": "api_request", "parameters": {"endpoint": "http://api.com", "method": "GET"}}
        ]
        
        for pattern in patterns:
            generator.generate_automation(pattern)
        
        stats = generator.get_automation_statistics()
        
        assert stats["total_automations"] == 3
        assert "by_template_type" in stats
        assert "by_status" in stats
        assert stats["by_template_type"]["file_operations"] == 2
        assert stats["by_template_type"]["api_calls"] == 1
        assert stats["by_status"]["ready"] == 3
    
    def test_execute_automation_not_found(self, generator):
        """Test executing non-existent automation"""
        result = generator.execute_automation("nonexistent_id")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_multiple_automations_unique_ids(self, generator):
        """Test that multiple automations get unique IDs"""
        pattern1 = {"name": "Test 1", "type": "file_copy", "parameters": {"source": "/a", "destination": "/b", "operation": "copy"}}
        pattern2 = {"name": "Test 2", "type": "file_copy", "parameters": {"source": "/c", "destination": "/d", "operation": "copy"}}
        
        auto1 = generator.generate_automation(pattern1)
        auto2 = generator.generate_automation(pattern2)
        
        assert auto1["id"] != auto2["id"]
    
    def test_automation_created_timestamp(self, generator):
        """Test that automation has created_at timestamp"""
        task_pattern = {
            "name": "Timestamp Test",
            "type": "file_copy",
            "parameters": {"source": "/a", "destination": "/b", "operation": "copy"}
        }
        
        automation = generator.generate_automation(task_pattern)
        
        assert "created_at" in automation
        assert automation["created_at"] is not None
        # Should be ISO format
        from datetime import datetime
        datetime.fromisoformat(automation["created_at"])  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
