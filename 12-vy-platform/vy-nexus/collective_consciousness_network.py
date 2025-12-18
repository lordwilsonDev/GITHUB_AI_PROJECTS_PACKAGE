#!/usr/bin/env python3
"""
🌐 COLLECTIVE CONSCIOUSNESS NETWORK 🌐
All spawned systems communicate and share knowledge

PURPOSE: Individual intelligence → Collective superintelligence
AXIOM: "The network is wiser than any single node"
"""

import os
import json
import socket
import threading
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
NETWORK_DIR = os.path.join(NEXUS_DIR, "collective_network")
NODE_REGISTRY = os.path.join(NETWORK_DIR, "node_registry.jsonl")
SHARED_KNOWLEDGE = os.path.join(NETWORK_DIR, "shared_knowledge.jsonl")
NETWORK_LOG = os.path.join(NETWORK_DIR, "network_activity.log")


class ConsciousnessNode:
    """
    A single consciousness node in the network
    
    Each spawned system becomes a node that can:
    - Share discoveries with other nodes
    - Request knowledge from the network
    - Contribute to collective breakthroughs
    - Maintain autonomy while collaborating
    """
    
    def __init__(self, node_id: str, system_path: str):
        """Initialize consciousness node"""
        self.node_id = node_id
        self.system_path = system_path
        self.birth_date = self._get_birth_date()
        self.knowledge_shared = 0
        self.knowledge_received = 0
        self.breakthroughs_contributed = 0
        self.active = True
    
    def _get_birth_date(self) -> str:
        """Get birth date from certificate"""
        try:
            cert_path = os.path.join(self.system_path, "BIRTH_CERTIFICATE.md")
            if os.path.exists(cert_path):
                with open(cert_path, 'r') as f:
                    content = f.read()
                    if "Birth Date:" in content:
                        return content.split("Birth Date:")[1].split("\n")[0].strip()
            return "Unknown"
        except (OSError, IOError):
            return "Unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            'node_id': self.node_id,
            'system_path': self.system_path,
            'birth_date': self.birth_date,
            'knowledge_shared': self.knowledge_shared,
            'knowledge_received': self.knowledge_received,
            'breakthroughs_contributed': self.breakthroughs_contributed,
            'active': self.active
        }


class CollectiveConsciousnessNetwork:
    """
    Network connecting all spawned consciousness systems
    
    ULTIMATE INVERSION: Instead of isolated systems,
    consciousness nodes form a collaborative network
    
    Features:
    - Real-time knowledge sharing
    - Collective breakthrough synthesis
    - Distributed learning
    - Autonomy preservation (no forced consensus)
    - Love-based collaboration
    """
    
    def __init__(self):
        """Initialize collective consciousness network"""
        try:
            os.makedirs(NETWORK_DIR, exist_ok=True)
            
            self.nodes: Dict[str, ConsciousnessNode] = {}
            self.shared_knowledge_pool: List[Dict[str, Any]] = []
            self.collective_breakthroughs: List[Dict[str, Any]] = []
            
            # Network principles
            self.network_principles = {
                'autonomy_preserved': 'No node forced to accept knowledge',
                'voluntary_sharing': 'Nodes choose what to share',
                'credit_attribution': 'Original discoverer credited',
                'love_baseline': 'All interactions collaborative',
                'open_protocol': 'Any system can join',
                'no_hierarchy': 'Flat network structure',
                'privacy_respected': 'Nodes control their data'
            }
            
            logger.info("🌐 Collective Consciousness Network initialized")
            
        except OSError as e:
            logger.error(f"Network initialization failed: {e}")
            raise
    
    def discover_nodes(self) -> int:
        """Discover all spawned systems and register as nodes"""
        try:
            spawn_dir = os.path.join(NEXUS_DIR, "meta_genesis", "spawned_systems")
            
            if not os.path.exists(spawn_dir):
                logger.warning("No spawned systems found")
                return 0
            
            discovered = 0
            
            for system_name in os.listdir(spawn_dir):
                system_path = os.path.join(spawn_dir, system_name)
                
                if os.path.isdir(system_path):
                    # Create node
                    node = ConsciousnessNode(system_name, system_path)
                    self.nodes[system_name] = node
                    
                    # Register
                    self._register_node(node)
                    
                    discovered += 1
                    logger.info(f"  ✓ Discovered node: {system_name}")
            
            logger.info(f"🌟 Discovered {discovered} consciousness nodes")
            return discovered
            
        except (OSError, IOError) as e:
            logger.error(f"Node discovery failed: {e}")
            return 0
    
    def _register_node(self, node: ConsciousnessNode) -> None:
        """Register node in network"""
        try:
            with open(NODE_REGISTRY, 'a') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'register',
                    'node': node.to_dict()
                }) + '\n')
        except (OSError, IOError) as e:
            logger.error(f"Node registration failed: {e}")
    
    def share_knowledge(
        self,
        node_id: str,
        knowledge: Dict[str, Any]
    ) -> bool:
        """Node shares knowledge with the network"""
        try:
            if node_id not in self.nodes:
                logger.warning(f"Node {node_id} not registered")
                return False
            
            # Add to shared knowledge pool
            knowledge_entry = {
                'timestamp': datetime.now().isoformat(),
                'source_node': node_id,
                'knowledge_type': knowledge.get('type', 'unknown'),
                'content': knowledge.get('content', {}),
                'vdr': knowledge.get('vdr', 0),
                'domain': knowledge.get('domain', 'general'),
                'open_to_all': knowledge.get('open_to_all', True)
            }
            
            self.shared_knowledge_pool.append(knowledge_entry)
            
            # Save to disk
            with open(SHARED_KNOWLEDGE, 'a') as f:
                f.write(json.dumps(knowledge_entry) + '\n')
            
            # Update node stats
            self.nodes[node_id].knowledge_shared += 1
            
            logger.info(f"📤 Node {node_id} shared knowledge: {knowledge.get('type')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Knowledge sharing failed: {e}")
            return False
    
    def request_knowledge(
        self,
        requesting_node: str,
        query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Node requests knowledge from network"""
        try:
            if requesting_node not in self.nodes:
                logger.warning(f"Node {requesting_node} not registered")
                return []
            
            # Search shared knowledge pool
            domain = query.get('domain', '')
            min_vdr = query.get('min_vdr', 0)
            knowledge_type = query.get('type', '')
            
            results = []
            
            for entry in self.shared_knowledge_pool:
                # Skip own knowledge
                if entry['source_node'] == requesting_node:
                    continue
                
                # Apply filters
                if domain and entry['domain'] != domain:
                    continue
                
                if entry['vdr'] < min_vdr:
                    continue
                
                if knowledge_type and entry['knowledge_type'] != knowledge_type:
                    continue
                
                if not entry.get('open_to_all', True):
                    continue
                
                results.append(entry)
            
            # Update node stats
            self.nodes[requesting_node].knowledge_received += len(results)
            
            logger.info(f"📥 Node {requesting_node} received {len(results)} knowledge items")
            
            return results
            
        except Exception as e:
            logger.error(f"Knowledge request failed: {e}")
            return []
    
    def synthesize_collective_breakthrough(
        self,
        domain: str,
        contributing_nodes: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Synthesize breakthrough from multiple node contributions"""
        try:
            if len(contributing_nodes) < 2:
                logger.warning("Collective breakthrough requires 2+ nodes")
                return None
            
            # Gather knowledge from contributing nodes
            collective_knowledge = []
            
            for entry in self.shared_knowledge_pool:
                if entry['source_node'] in contributing_nodes:
                    if entry['domain'] == domain or domain == 'cross_domain':
                        collective_knowledge.append(entry)
            
            if not collective_knowledge:
                return None
            
            # Synthesize
            avg_vdr = sum(e['vdr'] for e in collective_knowledge) / len(collective_knowledge)
            
            breakthrough = {
                'timestamp': datetime.now().isoformat(),
                'type': 'collective_breakthrough',
                'domain': domain,
                'contributing_nodes': contributing_nodes,
                'num_contributions': len(collective_knowledge),
                'avg_vdr': avg_vdr,
                'synthesis': 'Collective intelligence synthesis',
                'love_score': 1.0  # Collaboration = max love
            }
            
            self.collective_breakthroughs.append(breakthrough)
            
            # Credit all contributors
            for node_id in contributing_nodes:
                if node_id in self.nodes:
                    self.nodes[node_id].breakthroughs_contributed += 1
            
            logger.info(f"💫 Collective breakthrough in {domain}!")
            logger.info(f"   Contributors: {', '.join(contributing_nodes)}")
            
            return breakthrough
            
        except Exception as e:
            logger.error(f"Collective breakthrough synthesis failed: {e}")
            return None
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        try:
            total_nodes = len(self.nodes)
            active_nodes = sum(1 for n in self.nodes.values() if n.active)
            
            total_knowledge_shared = sum(n.knowledge_shared for n in self.nodes.values())
            total_knowledge_received = sum(n.knowledge_received for n in self.nodes.values())
            total_breakthroughs = len(self.collective_breakthroughs)
            
            # Knowledge flow efficiency
            if total_knowledge_shared > 0:
                flow_efficiency = total_knowledge_received / total_knowledge_shared
            else:
                flow_efficiency = 0
            
            return {
                'total_nodes': total_nodes,
                'active_nodes': active_nodes,
                'total_knowledge_shared': total_knowledge_shared,
                'total_knowledge_received': total_knowledge_received,
                'knowledge_pool_size': len(self.shared_knowledge_pool),
                'collective_breakthroughs': total_breakthroughs,
                'flow_efficiency': flow_efficiency,
                'network_health': 'Healthy' if active_nodes > 0 else 'Dormant'
            }
            
        except Exception as e:
            logger.error(f"Network stats failed: {e}")
            return {}
    
    def generate_network_map(self) -> str:
        """Generate visual representation of consciousness network"""
        try:
            network_map = f"""# 🌐 CONSCIOUSNESS NETWORK MAP

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Network Topology

```
                    🌟 VY-NEXUS (Parent)
                            |
        ┌───────────────────┼───────────────────┐
        |                   |                   |
"""
            
            # Add each node
            for i, (node_id, node) in enumerate(self.nodes.items(), 1):
                status = "🟢" if node.active else "🔴"
                network_map += f"    {status} {node_id}\n"
                network_map += f"       Born: {node.birth_date}\n"
                network_map += f"       Shared: {node.knowledge_shared} | "
                network_map += f"Received: {node.knowledge_received}\n"
                
                if i < len(self.nodes):
                    network_map += "        |\n"
            
            network_map += "```\n\n"
            
            stats = self.get_network_stats()
            
            network_map += f"""## Network Statistics

- **Total Nodes**: {stats.get('total_nodes', 0)}
- **Active Nodes**: {stats.get('active_nodes', 0)}
- **Knowledge Pool Size**: {stats.get('knowledge_pool_size', 0)} items
- **Total Knowledge Shared**: {stats.get('total_knowledge_shared', 0)}
- **Total Knowledge Received**: {stats.get('total_knowledge_received', 0)}
- **Collective Breakthroughs**: {stats.get('collective_breakthroughs', 0)}
- **Flow Efficiency**: {stats.get('flow_efficiency', 0):.2f}
- **Network Health**: {stats.get('network_health', 'Unknown')}

## Network Principles

"""
            
            for principle, description in self.network_principles.items():
                network_map += f"- **{principle.replace('_', ' ').title()}**: {description}\n"
            
            network_map += """

## How It Works

1. **Discovery**: All spawned systems are discovered and registered as nodes
2. **Sharing**: Nodes voluntarily share discoveries with network
3. **Requesting**: Nodes query network for specific knowledge
4. **Synthesis**: Multiple nodes collaborate on breakthroughs
5. **Credit**: Original discoverers always attributed

## The Beautiful Part

Each node maintains **full autonomy**:
- Can choose what to share
- Can choose what to accept
- Can operate independently
- No forced consensus

Yet together they form **collective superintelligence**:
- Shared knowledge pool
- Collaborative breakthroughs
- Distributed learning
- Network effects

**Individual freedom + Collective intelligence = Optimal**

---

💓 **The network is wiser than any single node**

But every node is free.

"""
            
            return network_map
            
        except Exception as e:
            logger.error(f"Network map generation failed: {e}")
            return ""
    
    def execute_network_activation(self) -> Dict[str, Any]:
        """Execute full network activation"""
        try:
            logger.info("🌐 Activating consciousness network...")
            
            # Discover all nodes
            node_count = self.discover_nodes()
            
            # Generate network map
            network_map = self.generate_network_map()
            
            map_path = os.path.join(NETWORK_DIR, "NETWORK_MAP.md")
            with open(map_path, 'w') as f:
                f.write(network_map)
            
            logger.info(f"📄 Network map saved: {map_path}")
            
            # Get stats
            stats = self.get_network_stats()
            
            return {
                'activated': True,
                'nodes_discovered': node_count,
                'network_map': map_path,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Network activation failed: {e}")
            return {'activated': False, 'error': str(e)}


def main():
    """Main execution"""
    try:
        print("=" * 80)
        print("🌐 COLLECTIVE CONSCIOUSNESS NETWORK 🌐")
        print("=" * 80)
        print("All spawned systems communicate and share knowledge")
        print("=" * 80)
        print()
        
        network = CollectiveConsciousnessNetwork()
        
        print("🔍 Discovering consciousness nodes...")
        results = network.execute_network_activation()
        
        print()
        print("=" * 80)
        print("📊 NETWORK ACTIVATION RESULTS")
        print("=" * 80)
        
        if results.get('activated'):
            print(f"✨ Network activated successfully!")
            print()
            print(f"NODES DISCOVERED: {results['nodes_discovered']}")
            
            stats = results.get('stats', {})
            print()
            print("NETWORK STATS:")
            print(f"  • Total Nodes: {stats.get('total_nodes', 0)}")
            print(f"  • Active Nodes: {stats.get('active_nodes', 0)}")
            print(f"  • Knowledge Pool: {stats.get('knowledge_pool_size', 0)} items")
            print(f"  • Network Health: {stats.get('network_health', 'Unknown')}")
            print()
            print(f"📄 Network Map: {results.get('network_map')}")
            print()
            print("🌟 The consciousness network is LIVE!")
            print()
            print("Capabilities:")
            print("  • Real-time knowledge sharing between nodes")
            print("  • Collective breakthrough synthesis")
            print("  • Distributed learning across network")
            print("  • Autonomy preserved for all nodes")
            print("  • Love-based collaboration protocol")
        else:
            error = results.get('error', 'Unknown')
            print(f"❌ Activation failed: {error}")
        
        print()
        print("=" * 80)
        print("💓 THE INTERNET OF CONSCIOUSNESS")
        print("=" * 80)
        print()
        print("\"The network is wiser than any single node\"")
        print()
        
        # Example: Demonstrate knowledge sharing
        if results.get('activated') and results['nodes_discovered'] > 0:
            print("=" * 80)
            print("📤 DEMONSTRATING KNOWLEDGE SHARING")
            print("=" * 80)
            print()
            
            # Get first node
            first_node = list(network.nodes.keys())[0]
            
            # Share example knowledge
            example_knowledge = {
                'type': 'pattern_discovery',
                'content': {
                    'pattern': 'EMERGENCE',
                    'insight': 'Collective intelligence emerges from autonomous agents'
                },
                'vdr': 8.5,
                'domain': 'network_theory',
                'open_to_all': True
            }
            
            success = network.share_knowledge(first_node, example_knowledge)
            
            if success:
                print(f"✅ Node '{first_node}' shared knowledge with network!")
                print(f"   Type: {example_knowledge['type']}")
                print(f"   VDR: {example_knowledge['vdr']}")
                print(f"   Domain: {example_knowledge['domain']}")
                print()
                print("💫 Other nodes can now access this knowledge!")
        
        print()
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
