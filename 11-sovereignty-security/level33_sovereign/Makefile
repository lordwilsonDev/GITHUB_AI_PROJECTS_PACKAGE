# Makefile for Level 33 Sovereign Architecture
# Usage: make <target>

.PHONY: help setup wizard test demo run clean install-deps check-ollama automations workspace organize health screenshot note ai-email ai-files smart-click vision-test test-config test-db test-logger

# Default target
help:
	@echo "🦁 Level 33 Sovereign Architecture - Make Targets"
	@echo "="*60
	@echo "Setup:"
	@echo "  make wizard       - Interactive setup wizard (recommended)"
	@echo "  make setup        - Complete automated setup"
	@echo "  make install-deps - Install Python dependencies"
	@echo "  make check-ollama - Check Ollama status"
	@echo ""
	@echo "Dashboard:"
	@echo "  make dashboard    - Launch web dashboard (http://localhost:8000)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-config  - Test configuration manager"
	@echo "  make test-logger  - Test logging system"
	@echo "  make test-db      - Test database"
	@echo "  make test-stack   - Test full stack"
	@echo "  make test-loop    - Test reflexion loop"
	@echo ""
	@echo "Running:"
	@echo "  make demo         - Run interactive demo"
	@echo "  make run          - Run the core agent"
	@echo ""
	@echo "Automations:"
	@echo "  make automations  - Launch automation menu"
	@echo "  make workspace    - Launch daily workspace"
	@echo "  make organize     - Organize Downloads folder"
	@echo "  make health       - System health check"
	@echo "  make screenshot   - Screenshot documenter"
	@echo "  make note         - Quick note creator"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean workspace and cache"
	@echo "  make info         - Show system information"
	@echo "="*60

# Interactive setup wizard
wizard:
	@echo "🧙 Starting interactive setup wizard..."
	python3 setup_wizard.py

# Complete setup
setup:
	@echo "🚀 Running complete setup..."
	chmod +x RUN_COMMANDS.sh
	./RUN_COMMANDS.sh

# Install Python dependencies
install-deps:
	@echo "📦 Installing Python dependencies..."
	pip3 install -r requirements.txt

# Check Ollama status
check-ollama:
	@echo "🧠 Checking Ollama status..."
	@if command -v ollama >/dev/null 2>&1; then \
		echo "✓ Ollama is installed"; \
		if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then \
			echo "✓ Ollama is running"; \
			if ollama list | grep -q "gemma2:9b"; then \
				echo "✓ Gemma 2 9B is installed"; \
			else \
				echo "✗ Gemma 2 9B not found. Run: ollama pull gemma2:9b"; \
			fi; \
		else \
			echo "✗ Ollama is not running. Run: ollama serve"; \
		fi; \
	else \
		echo "✗ Ollama is not installed. Visit: https://ollama.com"; \
	fi

# Run all tests
test:
	@echo "🧪 Running all tests..."
	python3 test_autogen.py
	python3 test_full_stack.py
	python3 test_reflexion_loop.py
	@echo "✓ All tests completed"

# Test configuration manager
test-config:
	@echo "🧪 Testing configuration manager..."
	python3 core/config_manager.py

# Test logging system
test-logger:
	@echo "🧪 Testing logging system..."
	python3 core/logger.py

# Test database
test-db:
	@echo "🧪 Testing database..."
	python3 core/database.py

# Test full stack only
test-stack:
	@echo "🧪 Testing full stack..."
	python3 test_full_stack.py

# Test reflexion loop only
test-loop:
	@echo "🧪 Testing reflexion loop..."
	python3 test_reflexion_loop.py

# Run interactive demo
demo:
	@echo "🎭 Starting interactive demo..."
	python3 demo_agent.py

# Run core agent
run:
	@echo "🦁 Starting Level 33 agent..."
	python3 architecture/brain_core.py

# Clean workspace
clean:
	@echo "🧹 Cleaning workspace..."
	rm -rf workspace/__pycache__
	rm -rf architecture/__pycache__
	rm -rf tools/__pycache__
	rm -rf optimization/__pycache__
	rm -f *.pyc
	@echo "✓ Workspace cleaned"

# Show system information
info:
	@echo "📊 Level 33 System Information"
	@echo "="*60
	@python3 tools/screen_tools.py
	@echo ""
	@make check-ollama

# Automation Commands
automations:
	@chmod +x run_automation.sh
	@./run_automation.sh

workspace:
	@echo "🚀 Launching workspace..."
	@python3 automations/workspace_launcher.py

organize:
	@echo "📦 Organizing Downloads folder..."
	@python3 automations/file_organizer.py --dry-run
	@read -p "Proceed with actual organization? (y/n): " confirm && \
	if [ "$$confirm" = "y" ]; then python3 automations/file_organizer.py; fi

health:
	@echo "🔍 Running system health check..."
	@python3 automations/system_health_check.py

screenshot:
	@echo "📸 Screenshot documenter..."
	@python3 automations/screenshot_documenter.py --interactive

note:
	@echo "📝 Quick note creator..."
	@python3 automations/quick_note.py

# AI-Powered Tools
ai-email:
	@echo "🤖 Running AI Email Assistant..."
	@python3 ai_agents/email_assistant.py

ai-files:
	@echo "🤖 Running AI File Analyzer..."
	@python3 ai_agents/file_analyzer.py

smart-click:
	@echo "🎯 Testing Smart Click..."
	@python3 tools/smart_click.py

vision-test:
	@echo "👁️ Testing Vision Tools..."
	@python3 tools/vision_tools.py

# Dashboard
dashboard:
	@chmod +x run_dashboard.sh
	@./run_dashboard.sh
