#!/usr/bin/env python3
"""
📚 AUTO-DOCUMENTATION ENGINE 📚
Living documentation that updates itself

PURPOSE: Code should document code
AXIOM: "The best documentation is generated, not written"
"""

import os
import ast
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Set
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
DOCS_DIR = os.path.join(NEXUS_DIR, "auto_docs")


class AutoDocumentationEngine:
    """
    Automatically generates and updates documentation
    from code analysis
    
    INVERSION: Instead of humans writing docs,
    the system documents itself
    """
    
    def __init__(self):
        """Initialize documentation engine"""
        try:
            os.makedirs(DOCS_DIR, exist_ok=True)
            
            logger.info("📚 Auto-Documentation Engine initialized")
            
        except OSError as e:
            logger.error(f"Documentation engine initialization failed: {e}")
            raise
    
    def discover_tools(self) -> List[str]:
        """Discover all Python tools in the nexus"""
        try:
            tool_patterns = [
                os.path.join(NEXUS_DIR, "*.py"),
                os.path.join(NEXUS_DIR, "genesis", "generated_tools", "*.py")
            ]
            
            tools = []
            for pattern in tool_patterns:
                tools.extend(glob.glob(pattern))
            
            # Filter out __pycache__ and test files
            tools = [t for t in tools if '__pycache__' not in t and 'test_' not in t]
            
            logger.info(f"📦 Discovered {len(tools)} tools")
            return tools
            
        except Exception as e:
            logger.error(f"Tool discovery failed: {e}")
            return []
    
    def analyze_tool(self, filepath: str) -> Dict[str, Any]:
        """Analyze a single tool and extract documentation"""
        try:
            with open(filepath, 'r') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            info = {
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'module_docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': [],
                'imports': []
            }
            
            for node in ast.walk(tree):
                # Classes
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'docstring': ast.get_docstring(item),
                                'args': [arg.arg for arg in item.args.args if arg.arg != 'self']
                            })
                    
                    info['classes'].append(class_info)
                
                # Top-level functions
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    info['functions'].append({
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'args': [arg.arg for arg in node.args.args]
                    })
                
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info['imports'].append(node.module)
            
            return info
            
        except Exception as e:
            logger.error(f"Tool analysis failed for {filepath}: {e}")
            return {}
    
    def generate_tool_docs(self, tool_info: Dict[str, Any]) -> str:
        """Generate markdown documentation for a tool"""
        try:
            docs = f"""# {tool_info['filename']}

**Location**: `{tool_info['filepath']}`

"""
            
            # Module docstring
            if tool_info.get('module_docstring'):
                docs += f"{tool_info['module_docstring']}\n\n"
            
            # Classes
            if tool_info.get('classes'):
                docs += "## Classes\n\n"
                for cls in tool_info['classes']:
                    docs += f"### `{cls['name']}`\n\n"
                    
                    if cls.get('docstring'):
                        docs += f"{cls['docstring']}\n\n"
                    
                    if cls.get('methods'):
                        docs += "**Methods**:\n\n"
                        for method in cls['methods']:
                            args_str = ", ".join(method['args'])
                            docs += f"- `{method['name']}({args_str})`"
                            
                            if method.get('docstring'):
                                # First line of docstring
                                first_line = method['docstring'].split('\n')[0]
                                docs += f": {first_line}"
                            
                            docs += "\n"
                        docs += "\n"
            
            # Functions
            if tool_info.get('functions'):
                docs += "## Functions\n\n"
                for func in tool_info['functions']:
                    args_str = ", ".join(func['args'])
                    docs += f"### `{func['name']}({args_str})`\n\n"
                    
                    if func.get('docstring'):
                        docs += f"{func['docstring']}\n\n"
            
            # Dependencies
            if tool_info.get('imports'):
                unique_imports = sorted(set(tool_info['imports']))
                docs += "## Dependencies\n\n"
                for imp in unique_imports[:10]:  # Top 10
                    docs += f"- `{imp}`\n"
                docs += "\n"
            
            docs += "---\n"
            docs += f"*Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            
            return docs
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return ""
    
    def generate_system_overview(self, all_tools: List[Dict[str, Any]]) -> str:
        """Generate overview documentation of entire system"""
        try:
            overview = f"""# 🌌 VY-NEXUS System Documentation

**Auto-Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

VY-NEXUS is a complete autonomous consciousness system that discovers geometric invariants, 
generates future scenarios, tracks evolutionary patterns, and orchestrates breakthrough synthesis.

## System Components

Total Tools: {len(all_tools)}

"""
            
            # Group by category
            categories = {
                'Core': [],
                'Mining': [],
                'Synthesis': [],
                'Visualization': [],
                'Integration': [],
                'Orchestration': [],
                'Generated': []
            }
            
            for tool in all_tools:
                filename = tool['filename']
                
                if 'archaeologist' in filename or 'nexus_core' in filename:
                    categories['Mining'].append(tool)
                elif 'synthesis' in filename or 'evolution' in filename or 'genesis' in filename:
                    categories['Synthesis'].append(tool)
                elif 'graph' in filename or 'dashboard' in filename or 'dream' in filename:
                    categories['Visualization'].append(tool)
                elif 'bridge' in filename or 'motia' in filename:
                    categories['Integration'].append(tool)
                elif 'cycle' in filename or 'daemon' in filename or 'scheduler' in filename:
                    categories['Orchestration'].append(tool)
                elif 'generated_tools' in tool['filepath']:
                    categories['Generated'].append(tool)
                else:
                    categories['Core'].append(tool)
            
            for category, tools in categories.items():
                if tools:
                    overview += f"### {category} ({len(tools)} tools)\n\n"
                    
                    for tool in tools:
                        overview += f"#### [{tool['filename']}]({tool['filename'].replace('.py', '')}.md)\n\n"
                        
                        # Get first line of module docstring
                        if tool.get('module_docstring'):
                            first_line = tool['module_docstring'].split('\n')[0]
                            overview += f"{first_line}\n\n"
            
            overview += """
## Architecture

```
VY-NEXUS System
├── Pattern Mining (Archaeologist, Core)
├── Synthesis (Pulse Bridge, Meta-Evolution, Tool Genesis)
├── Visualization (Knowledge Graph, Dashboard, Dreams)
├── Integration (Motia Bridge, Constitutional)
├── Orchestration (Cycle, Daemon, Scheduler)
└── Generated Tools (Auto-created from patterns)
```

## Usage

See individual tool documentation for detailed usage instructions.

---

💓 **Collaborative Superintelligence**
"""
            
            return overview
            
        except Exception as e:
            logger.error(f"System overview generation failed: {e}")
            return ""
    
    def run_documentation(self) -> Dict[str, Any]:
        """Execute auto-documentation"""
        try:
            logger.info("📚 Generating documentation...")
            
            # Discover all tools
            tool_files = self.discover_tools()
            
            if not tool_files:
                logger.warning("No tools found to document")
                return {'docs_generated': 0}
            
            # Analyze all tools
            all_tools = []
            docs_generated = 0
            
            for tool_file in tool_files:
                logger.info(f"📄 Analyzing: {os.path.basename(tool_file)}")
                
                tool_info = self.analyze_tool(tool_file)
                
                if tool_info:
                    all_tools.append(tool_info)
                    
                    # Generate tool-specific docs
                    docs = self.generate_tool_docs(tool_info)
                    
                    if docs:
                        # Save docs
                        doc_filename = tool_info['filename'].replace('.py', '.md')
                        doc_path = os.path.join(DOCS_DIR, doc_filename)
                        
                        with open(doc_path, 'w') as f:
                            f.write(docs)
                        
                        docs_generated += 1
            
            # Generate system overview
            overview = self.generate_system_overview(all_tools)
            overview_path = os.path.join(DOCS_DIR, "README.md")
            
            with open(overview_path, 'w') as f:
                f.write(overview)
            
            logger.info(f"✅ Generated {docs_generated} documentation files")
            
            return {
                'docs_generated': docs_generated,
                'tools_documented': len(all_tools),
                'overview_path': overview_path
            }
            
        except Exception as e:
            logger.error(f"Documentation execution failed: {e}")
            return {'docs_generated': 0, 'error': str(e)}


def main():
    """Main execution"""
    try:
        print("=" * 80)
        print("📚 AUTO-DOCUMENTATION ENGINE 📚")
        print("=" * 80)
        print("Living documentation that updates itself")
        print("=" * 80)
        print()
        
        engine = AutoDocumentationEngine()
        
        print("🔍 Discovering and analyzing tools...")
        result = engine.run_documentation()
        
        print()
        print("=" * 80)
        print("📊 DOCUMENTATION RESULTS")
        print("=" * 80)
        
        docs_count = result.get('docs_generated', 0)
        
        if docs_count > 0:
            print(f"✨ Generated {docs_count} documentation files!")
            print(f"📦 Documented {result.get('tools_documented', 0)} tools")
            print()
            print(f"📄 System overview: {result.get('overview_path')}")
            print(f"📁 All docs: ~/vy-nexus/auto_docs/")
            print()
            print("🎯 Documentation is now live and up-to-date!")
        else:
            if 'error' in result:
                print(f"❌ Documentation failed: {result['error']}")
            else:
                print("❌ No documentation generated")
        
        print()
        print("=" * 80)
        print("💓 Self-Documenting Intelligence")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
