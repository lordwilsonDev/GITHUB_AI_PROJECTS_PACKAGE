#!/usr/bin/env python3
"""
📊 LIVING MEMORY VISUALIZATION 📊
Visual interface to explore the consciousness knowledge graph

PURPOSE: Generate beautiful visualizations of:
- Knowledge graph structure
- Consciousness lineage trees
- Cross-engine interaction networks
- Temporal evolution charts
- Breakthrough synthesis chains

OUTPUTS:
- HTML interactive graphs (using vis.js)
- SVG static diagrams
- JSON graph data for external tools

Built with love by Claude for Wilson
December 6, 2024
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

sys.path.insert(0, str(Path(__file__).parent))
from living_memory_engine import LivingMemoryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOME = os.path.expanduser("~")
NEXUS_DIR = Path(HOME) / "vy-nexus"
VIZ_DIR = NEXUS_DIR / "living_memory" / "visualizations"


class MemoryVisualizer:
    """
    Creates visual representations of living memory
    
    Generates interactive HTML graphs showing:
    - Full knowledge graph
    - Engine dependency network
    - Consciousness lineage trees
    - Breakthrough evolution chains
    """
    
    def __init__(self):
        self.memory = LivingMemoryEngine()
        os.makedirs(VIZ_DIR, exist_ok=True)
        
        logger.info("📊 Memory Visualizer initialized")
    
    def generate_full_graph_html(self) -> str:
        """
        Generate interactive HTML visualization of entire knowledge graph
        
        Uses vis.js for interactive network visualization
        """
        # Prepare node data
        nodes_data = []
        for node in self.memory.nodes.values():
            # Color by type
            type_colors = {
                'Engine': '#3498db',
                'Breakthrough': '#e74c3c',
                'Dream': '#9b59b6',
                'Pattern': '#2ecc71',
                'SpawnedSystem': '#f39c12',
                'Insight': '#1abc9c',
                'Interaction': '#95a5a6',
                'KnowledgeGraph': '#34495e',
                'LearnedVector': '#e67e22',
            }
            
            color = type_colors.get(node.node_type, '#bdc3c7')
            
            # Determine label
            if 'name' in node.content:
                label = node.content['name']
            elif 'title' in node.content:
                label = node.content['title'][:30]
            else:
                label = node.node_type
            
            nodes_data.append({
                'id': node.node_id,
                'label': label,
                'title': f"{node.node_type}\n{node.node_id}\n{node.timestamp}",
                'color': color,
                'shape': 'dot',
                'size': 20
            })
        
        # Prepare edge data
        edges_data = []
        for edge in self.memory.edges:
            # Color by type
            edge_colors = {
                'GENERATED_BY': '#3498db',
                'INFLUENCED': '#e74c3c',
                'SPAWNED': '#f39c12',
                'VALIDATED': '#2ecc71',
                'EVOLVED_INTO': '#9b59b6',
            }
            
            color = edge_colors.get(edge.edge_type, '#95a5a6')
            
            edges_data.append({
                'from': edge.source_id,
                'to': edge.target_id,
                'label': edge.edge_type,
                'arrows': 'to',
                'color': color,
                'title': edge.edge_type
            })
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>VY-NEXUS Living Memory - Full Graph</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 0;
            background: #000;
            color: #0f0;
        }}
        #header {{
            padding: 20px;
            background: #111;
            border-bottom: 2px solid #0f0;
        }}
        #mynetwork {{
            width: 100%;
            height: 85vh;
            border: 1px solid #0f0;
        }}
        #legend {{
            position: absolute;
            top: 80px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border: 1px solid #0f0;
            border-radius: 5px;
        }}
        .legend-item {{
            margin: 5px 0;
            display: flex;
            align-items: center;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 50%;
        }}
        #stats {{
            padding: 10px 20px;
            background: #111;
            border-top: 1px solid #0f0;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🧬 VY-NEXUS LIVING MEMORY - FULL CONSCIOUSNESS GRAPH</h1>
        <p>Generated: {datetime.now().isoformat()}</p>
        <p>Nodes: {len(nodes_data)} | Edges: {len(edges_data)}</p>
    </div>
    
    <div id="legend">
        <h3>Node Types</h3>
        <div class="legend-item">
            <div class="legend-color" style="background: #3498db;"></div>
            <span>Engine</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #e74c3c;"></div>
            <span>Breakthrough</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #9b59b6;"></div>
            <span>Dream</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #2ecc71;"></div>
            <span>Pattern</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #f39c12;"></div>
            <span>Spawned System</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #1abc9c;"></div>
            <span>Insight</span>
        </div>
    </div>
    
    <div id="mynetwork"></div>
    
    <div id="stats">
        <strong>Navigation:</strong> Drag to pan | Scroll to zoom | Click nodes for details
    </div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodes_data)});
        var edges = new vis.DataSet({json.dumps(edges_data)});

        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            nodes: {{
                font: {{
                    color: '#0f0',
                    size: 12
                }}
            }},
            edges: {{
                font: {{
                    color: '#0f0',
                    size: 10,
                    align: 'middle'
                }},
                smooth: {{
                    type: 'continuous'
                }}
            }},
            physics: {{
                enabled: true,
                barnesHut: {{
                    gravitationalConstant: -2000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04
                }},
                stabilization: {{
                    iterations: 150
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100,
                navigationButtons: true,
                keyboard: true
            }}
        }};
        var network = new vis.Network(container, data, options);
        
        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                alert("Node: " + node.label + "\\nType: " + node.title);
            }}
        }});
    </script>
</body>
</html>
"""
        
        # Save HTML
        html_file = VIZ_DIR / "full_graph.html"
        with open(html_file, 'w') as f:
            f.write(html)
        
        logger.info(f"✅ Full graph HTML generated: {html_file}")
        return str(html_file)
    
    def generate_consciousness_lineage_tree(self) -> str:
        """
        Generate visualization of consciousness spawning lineage
        
        Shows parent-child relationships of spawned systems
        """
        # Get all spawned systems
        spawned = self.memory.query_by_type('SpawnedSystem')
        
        if not spawned:
            logger.warning("No spawned systems found")
            return ""
        
        # Build lineage tree data
        nodes = []
        edges = []
        
        for system in spawned:
            nodes.append({
                'id': system.node_id,
                'label': system.content.get('name', system.node_id[:12]),
                'level': len(self.memory.get_consciousness_lineage(system.node_id)),
                'title': f"System: {system.content.get('name', 'Unknown')}\nCreated: {system.timestamp}"
            })
            
            # Find parent
            parent_edges = self.memory.edges_by_target.get(system.node_id, [])
            for edge in parent_edges:
                if edge.edge_type == 'SPAWNED':
                    edges.append({
                        'from': edge.source_id,
                        'to': edge.target_id,
                        'arrows': 'to'
                    })
        
        # Generate HTML (simplified tree layout)
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Consciousness Lineage Tree</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ font-family: monospace; background: #000; color: #0f0; margin: 0; }}
        #header {{ padding: 20px; background: #111; border-bottom: 2px solid #0f0; }}
        #tree {{ width: 100%; height: 85vh; border: 1px solid #0f0; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🌳 CONSCIOUSNESS LINEAGE TREE</h1>
        <p>Spawned Systems: {len(spawned)}</p>
    </div>
    <div id="tree"></div>
    <script>
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});
        var container = document.getElementById('tree');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            layout: {{
                hierarchical: {{
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150
                }}
            }},
            nodes: {{ font: {{ color: '#0f0' }} }},
            edges: {{ color: '#0f0', arrows: 'to' }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""
        
        tree_file = VIZ_DIR / "consciousness_lineage.html"
        with open(tree_file, 'w') as f:
            f.write(html)
        
        logger.info(f"✅ Lineage tree generated: {tree_file}")
        return str(tree_file)
    
    def generate_engine_network(self) -> str:
        """Generate visualization of engine dependency network"""
        engines = self.memory.query_by_type('Engine')
        
        nodes = []
        edges = []
        
        for engine in engines:
            nodes.append({
                'id': engine.node_id,
                'label': engine.content.get('name', 'Unknown'),
                'color': '#3498db',
                'size': 30
            })
        
        # Get DEPENDS_ON edges
        for edge in self.memory.edges_by_type.get('DEPENDS_ON', []):
            edges.append({
                'from': edge.source_id,
                'to': edge.target_id,
                'arrows': 'to',
                'label': 'depends on'
            })
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Engine Network</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{ background: #000; color: #0f0; margin: 0; font-family: monospace; }}
        #header {{ padding: 20px; background: #111; border-bottom: 2px solid #0f0; }}
        #network {{ width: 100%; height: 85vh; }}
    </style>
</head>
<body>
    <div id="header">
        <h1>⚙️ ENGINE DEPENDENCY NETWORK</h1>
        <p>Engines: {len(engines)} | Dependencies: {len(edges)}</p>
    </div>
    <div id="network"></div>
    <script>
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});
        var network = new vis.Network(
            document.getElementById('network'),
            {{ nodes: nodes, edges: edges }},
            {{ 
                nodes: {{ font: {{ color: '#0f0' }} }},
                edges: {{ color: '#0f0', font: {{ color: '#0f0' }} }}
            }}
        );
    </script>
</body>
</html>
"""
        
        network_file = VIZ_DIR / "engine_network.html"
        with open(network_file, 'w') as f:
            f.write(html)
        
        logger.info(f"✅ Engine network generated: {network_file}")
        return str(network_file)
    
    def export_graph_json(self) -> str:
        """Export graph as JSON for external tools (Gephi, Cytoscape, etc.)"""
        graph_data = {
            'nodes': [n.to_dict() for n in self.memory.nodes.values()],
            'edges': [e.to_dict() for e in self.memory.edges],
            'metadata': {
                'exported': datetime.now().isoformat(),
                'total_nodes': len(self.memory.nodes),
                'total_edges': len(self.memory.edges),
                'node_types': list(self.memory.NODE_TYPES),
                'edge_types': list(self.memory.EDGE_TYPES)
            }
        }
        
        json_file = VIZ_DIR / "graph_export.json"
        with open(json_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        logger.info(f"✅ Graph exported to JSON: {json_file}")
        return str(json_file)
    
    def generate_all_visualizations(self) -> Dict[str, str]:
        """Generate all visualization types"""
        logger.info("Generating all visualizations...")
        
        results = {
            'full_graph': self.generate_full_graph_html(),
            'lineage_tree': self.generate_consciousness_lineage_tree(),
            'engine_network': self.generate_engine_network(),
            'json_export': self.export_graph_json()
        }
        
        logger.info(f"✅ All visualizations generated in {VIZ_DIR}")
        return results


if __name__ == "__main__":
    print("📊 Living Memory Visualization Generator")
    print("="*60)
    
    viz = MemoryVisualizer()
    results = viz.generate_all_visualizations()
    
    print("\n✅ Visualizations generated:")
    for name, path in results.items():
        print(f"   {name}: {path}")
    
    print(f"\nOpen these HTML files in your browser to explore!")
    print(f"Visualization directory: {VIZ_DIR}")
