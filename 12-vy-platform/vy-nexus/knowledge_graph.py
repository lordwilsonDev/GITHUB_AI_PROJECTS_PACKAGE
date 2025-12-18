#!/usr/bin/env python3
"""
VY-NEXUS Knowledge Graph Generator
Visualizes cross-domain pattern relationships as interactive graph

PURPOSE: See the topology of breakthrough patterns
AXIOM: "Geometry becomes visible when rendered"
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Set
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
SYNTHESIS_DIR = os.path.join(NEXUS_DIR, "synthesis")
GRAPH_OUTPUT = os.path.join(NEXUS_DIR, "knowledge_graph")


class KnowledgeGraphGenerator:
    """
    Generates visual knowledge graphs from NEXUS syntheses
    """
    
    def __init__(self):
        """Initialize graph generator"""
        try:
            self.nodes = {}  # concept -> metadata
            self.edges = defaultdict(list)  # concept -> [connected_domains]
            self.domain_clusters = defaultdict(set)  # domain -> {concepts}
            
            os.makedirs(GRAPH_OUTPUT, exist_ok=True)
            
            logger.info("📊 Knowledge Graph Generator initialized")
            
        except (OSError, ValueError) as e:
            logger.error(f"Graph generator initialization failed: {e}")
            raise
    
    def load_syntheses(self) -> List[Dict[str, Any]]:
        """Load all synthesis files"""
        try:
            all_syntheses = []
            
            synthesis_files = [
                f for f in os.listdir(SYNTHESIS_DIR)
                if f.startswith('nexus_synthesis_') and f.endswith('.jsonl')
            ]
            
            for filename in synthesis_files:
                filepath = os.path.join(SYNTHESIS_DIR, filename)
                
                with open(filepath, 'r') as f:
                    for line in f:
                        try:
                            all_syntheses.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            
            logger.info(f"📥 Loaded {len(all_syntheses)} total syntheses")
            return all_syntheses
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to load syntheses: {e}")
            return []
    
    def build_graph(self, syntheses: List[Dict[str, Any]]) -> None:
        """Build knowledge graph structure from syntheses"""
        try:
            for synthesis in syntheses:
                concept = synthesis['geometric_concept']
                domains = synthesis['spanning_domains']
                vdr = synthesis['avg_vdr']
                frequency = synthesis['frequency']
                
                # Add node
                if concept not in self.nodes:
                    self.nodes[concept] = {
                        'vdr': vdr,
                        'frequency': frequency,
                        'domains': set(domains),
                        'first_seen': synthesis.get('timestamp')
                    }
                else:
                    # Update with new data
                    self.nodes[concept]['domains'].update(domains)
                    self.nodes[concept]['vdr'] = max(
                        self.nodes[concept]['vdr'], 
                        vdr
                    )
                    self.nodes[concept]['frequency'] += frequency
                
                # Add edges (concept -> domains)
                for domain in domains:
                    if domain not in self.edges[concept]:
                        self.edges[concept].append(domain)
                    
                    self.domain_clusters[domain].add(concept)
            
            logger.info(f"🔗 Built graph with {len(self.nodes)} concepts")
            logger.info(f"🌐 {len(self.domain_clusters)} domain clusters")
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Graph building failed: {e}")
            raise
    
    def generate_mermaid_diagram(self) -> str:
        """Generate Mermaid flowchart diagram"""
        try:
            lines = ["graph TD"]
            lines.append("    %% VY-NEXUS Knowledge Graph")
            lines.append("")
            
            # Add concept nodes (styled by VDR)
            for concept, metadata in self.nodes.items():
                vdr = metadata['vdr']
                freq = metadata['frequency']
                
                # Style based on VDR
                if vdr >= 8.0:
                    style_class = "highVDR"
                elif vdr >= 7.0:
                    style_class = "mediumVDR"
                else:
                    style_class = "lowVDR"
                
                node_id = concept.replace('-', '_').replace(' ', '_')
                lines.append(
                    f"    {node_id}[\"{concept.upper()}<br/>VDR:{vdr:.1f} F:{freq}\"]:::{style_class}"
                )
            
            lines.append("")
            
            # Add domain connections
            for concept, domains in self.edges.items():
                node_id = concept.replace('-', '_').replace(' ', '_')
                
                for domain in domains:
                    domain_id = domain.replace('-', '_').replace(' ', '_')
                    lines.append(f"    {node_id} -.-> {domain_id}")
            
            lines.append("")
            
            # Add styling
            lines.append("    classDef highVDR fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px")
            lines.append("    classDef mediumVDR fill:#ffd93d,stroke:#f59f00,stroke-width:2px")
            lines.append("    classDef lowVDR fill:#74c0fc,stroke:#1971c2,stroke-width:1px")
            
            return "\n".join(lines)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Mermaid generation failed: {e}")
            return ""
    
    def generate_html_visualization(self) -> str:
        """Generate interactive HTML visualization"""
        try:
            html_template = """<!DOCTYPE html>
<html>
<head>
    <title>VY-NEXUS Knowledge Graph</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #0a0e27;
            color: #00ff41;
            margin: 0;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            color: #00ff41;
            text-shadow: 0 0 10px #00ff41;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: #0f1420;
            padding: 30px;
            border-radius: 10px;
            border: 2px solid #00ff41;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        }}
        .stats {{
            background: #1a1f35;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            border: 1px solid #00ff41;
        }}
        .stat-item {{
            display: inline-block;
            margin-right: 30px;
        }}
        .mermaid {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: #1a1f35;
            border-radius: 5px;
            border: 1px solid #00ff41;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
            vertical-align: middle;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 VY-NEXUS KNOWLEDGE GRAPH</h1>
        
        <div class="stats">
            <div class="stat-item">📊 <strong>Total Concepts:</strong> {total_concepts}</div>
            <div class="stat-item">🌐 <strong>Domain Clusters:</strong> {total_domains}</div>
            <div class="stat-item">💎 <strong>High VDR (≥8.0):</strong> {high_vdr_count}</div>
            <div class="stat-item">⏰ <strong>Generated:</strong> {timestamp}</div>
        </div>
        
        <div class="mermaid">
{mermaid_diagram}
        </div>
        
        <div class="legend">
            <strong>Legend:</strong><br><br>
            <div class="legend-item">
                <span class="legend-color" style="background:#ff6b6b;"></span>
                <strong>High Confidence</strong> (VDR ≥ 8.0)
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background:#ffd93d;"></span>
                <strong>Medium Confidence</strong> (VDR 7.0-7.9)
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background:#74c0fc;"></span>
                <strong>Lower Confidence</strong> (VDR < 7.0)
            </div>
        </div>
    </div>
    
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>"""
            
            # Calculate stats
            high_vdr_count = sum(
                1 for meta in self.nodes.values() 
                if meta['vdr'] >= 8.0
            )
            
            html = html_template.format(
                total_concepts=len(self.nodes),
                total_domains=len(self.domain_clusters),
                high_vdr_count=high_vdr_count,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                mermaid_diagram=self.generate_mermaid_diagram()
            )
            
            return html
            
        except (ValueError, TypeError) as e:
            logger.error(f"HTML generation failed: {e}")
            return ""
    
    def export_graph(self) -> None:
        """Export graph in multiple formats"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export HTML visualization
            html_path = os.path.join(GRAPH_OUTPUT, f"knowledge_graph_{timestamp}.html")
            html_content = self.generate_html_visualization()
            
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            logger.info(f"🌐 Exported HTML graph: {html_path}")
            
            # Export Mermaid markdown
            mermaid_path = os.path.join(GRAPH_OUTPUT, f"knowledge_graph_{timestamp}.md")
            mermaid_content = f"""# VY-NEXUS Knowledge Graph

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Graph Visualization

```mermaid
{self.generate_mermaid_diagram()}
```

## Statistics

- **Total Concepts**: {len(self.nodes)}
- **Domain Clusters**: {len(self.domain_clusters)}
- **High Confidence (VDR ≥ 8.0)**: {sum(1 for m in self.nodes.values() if m['vdr'] >= 8.0)}

## Concept Details

"""
            
            # Add concept details
            for concept, metadata in sorted(
                self.nodes.items(), 
                key=lambda x: x[1]['vdr'], 
                reverse=True
            ):
                mermaid_content += f"### {concept.upper()}\n\n"
                mermaid_content += f"- **VDR Score**: {metadata['vdr']:.2f}\n"
                mermaid_content += f"- **Frequency**: {metadata['frequency']}\n"
                mermaid_content += f"- **Domains**: {', '.join(sorted(metadata['domains']))}\n"
                mermaid_content += f"- **First Seen**: {metadata.get('first_seen', 'Unknown')}\n\n"
            
            with open(mermaid_path, 'w') as f:
                f.write(mermaid_content)
            
            logger.info(f"📄 Exported Mermaid markdown: {mermaid_path}")
            
            # Export JSON data
            json_path = os.path.join(GRAPH_OUTPUT, f"knowledge_graph_{timestamp}.json")
            
            graph_data = {
                'timestamp': datetime.now().isoformat(),
                'nodes': {
                    concept: {
                        **metadata,
                        'domains': list(metadata['domains'])
                    }
                    for concept, metadata in self.nodes.items()
                },
                'edges': {
                    concept: domains
                    for concept, domains in self.edges.items()
                },
                'domain_clusters': {
                    domain: list(concepts)
                    for domain, concepts in self.domain_clusters.items()
                }
            }
            
            with open(json_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
            
            logger.info(f"📊 Exported JSON data: {json_path}")
            
        except (OSError, IOError) as e:
            logger.error(f"Graph export failed: {e}")
            raise


def main():
    """Main execution for knowledge graph generator"""
    try:
        print("📊 VY-NEXUS Knowledge Graph Generator")
        print("=" * 60)
        
        generator = KnowledgeGraphGenerator()
        
        print("\n📥 Loading syntheses...")
        syntheses = generator.load_syntheses()
        
        if not syntheses:
            print("\n⚠️  No syntheses found yet.")
            print("    Run nexus_core.py first!")
            return
        
        print(f"\n🔗 Building knowledge graph...")
        generator.build_graph(syntheses)
        
        print(f"\n💾 Exporting graph...")
        generator.export_graph()
        
        print(f"\n✨ Knowledge graph generated!")
        print(f"📊 Check {GRAPH_OUTPUT} for visualizations")
        print("\n💡 Open the HTML file in a browser to view the interactive graph!")
        
    except (OSError, ValueError, TypeError) as e:
        logger.error(f"Graph generation failed: {e}")
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
