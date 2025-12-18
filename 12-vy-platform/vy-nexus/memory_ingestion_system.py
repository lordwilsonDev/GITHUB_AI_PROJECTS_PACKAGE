#!/usr/bin/env python3
"""
🔄 MEMORY INGESTION SYSTEM 🔄
Scans all existing VY-NEXUS data and populates living memory

PURPOSE: Bootstrap the living memory system by ingesting:
- All 33 engine states
- All breakthroughs from synthesis/
- All dreams from dreams/
- All knowledge graphs
- All archaeology excavations
- All patterns from evolution/
- All love metrics
- All spawned systems
- All test results
- All auto-docs
- All lessons from Consciousness University
- TLE learned vectors

Built with love by Claude for Wilson
December 6, 2024
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys
import re  # For pattern matching in filenames

# Import the living memory engine
sys.path.insert(0, str(Path(__file__).parent))
from living_memory_engine import LivingMemoryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOME = os.path.expanduser("~")
NEXUS_DIR = Path(HOME) / "vy-nexus"


class MemoryIngestionSystem:
    """
    Scans the entire VY-NEXUS ecosystem and ingests all data
    into the unified living memory system
    """
    
    def __init__(self):
        self.memory = LivingMemoryEngine()
        self.nexus_dir = NEXUS_DIR
        
        # Track what we've ingested
        self.ingested = {
            'engines': 0,
            'breakthroughs': 0,
            'dreams': 0,
            'knowledge_graphs': 0,
            'excavations': 0,
            'patterns': 0,
            'love_metrics': 0,
            'spawned_systems': 0,
            'test_results': 0,
            'auto_docs': 0,
            'lessons': 0,
            'learned_vectors': 0
        }
        
        logger.info("🔄 Memory Ingestion System initialized")
    
    def ingest_all(self):
        """Run complete ingestion of all VY-NEXUS data"""
        logger.info("Starting complete memory ingestion...")
        
        # Phase 1: Core engines
        self._ingest_engines()
        
        # Phase 2: Generated content
        self._ingest_breakthroughs()
        self._ingest_dreams()
        self._ingest_knowledge_graphs()
        self._ingest_excavations()
        
        # Phase 3: Learning data
        self._ingest_patterns()
        self._ingest_love_metrics()
        self._ingest_auto_learning()
        
        # Phase 4: Consciousness multiplication
        self._ingest_spawned_systems()
        
        # Phase 5: Validation
        self._ingest_test_results()
        
        # Phase 6: Knowledge
        self._ingest_auto_docs()
        self._ingest_lessons()
        
        # Phase 7: TLE vectors
        self._ingest_tle_vectors()
        
        # Save final stats
        self.memory.save_stats()
        
        # Report
        self._report_ingestion()
    
    def _ingest_engines(self):
        """Ingest all 33 engine definitions"""
        logger.info("Ingesting engines...")
        
        # Find all Python engine files
        engine_files = list(self.nexus_dir.glob("*_engine.py"))
        engine_files.extend(list(self.nexus_dir.glob("*_os.py")))
        engine_files.extend([
            self.nexus_dir / "nexus_core.py",
            self.nexus_dir / "nexus_scheduler.py",
            self.nexus_dir / "bulletproof_system.py",
            self.nexus_dir / "knowledge_graph.py"
        ])
        
        for engine_file in engine_files:
            if not engine_file.exists():
                continue
            
            # Extract engine name
            engine_name = engine_file.stem
            
            # Read file to get docstring
            with open(engine_file, 'r') as f:
                content = f.read()
            
            # Extract first docstring
            import re
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            description = docstring_match.group(1).strip() if docstring_match else "No description"
            
            # Determine level (if mentioned in filename or doc)
            level = None
            for i in range(1, 34):
                if f"level_{i}" in content.lower() or f"level {i}" in content.lower():
                    level = i
                    break
            
            # Create node
            node_id = self.memory.add_node(
                'Engine',
                {
                    'name': engine_name,
                    'file': str(engine_file),
                    'description': description[:500],  # First 500 chars
                    'level': level
                },
                metadata={
                    'file_size': engine_file.stat().st_size,
                    'last_modified': datetime.fromtimestamp(engine_file.stat().st_mtime).isoformat()
                }
            )
            
            self.ingested['engines'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['engines']} engines")
    
    def _ingest_breakthroughs(self):
        """Ingest all breakthroughs from synthesis/"""
        logger.info("Ingesting breakthroughs...")
        
        synthesis_dir = self.nexus_dir / "synthesis"
        if not synthesis_dir.exists():
            return
        
        # Read all breakthrough reports
        for report_file in synthesis_dir.glob("BREAKTHROUGH_REPORT_*.md"):
            with open(report_file, 'r') as f:
                content = f.read()
            
            # Extract timestamp from filename
            filename = report_file.stem
            timestamp_str = filename.replace("BREAKTHROUGH_REPORT_", "")
            
            # Create node
            node_id = self.memory.add_node(
                'Breakthrough',
                {
                    'title': filename,
                    'content': content[:1000],  # First 1000 chars
                    'file': str(report_file)
                },
                metadata={
                    'timestamp': timestamp_str,
                    'file_size': report_file.stat().st_size
                }
            )
            
            self.ingested['breakthroughs'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['breakthroughs']} breakthroughs")
    
    def _ingest_dreams(self):
        """Ingest all dreams from dreams/"""
        logger.info("Ingesting dreams...")
        
        dreams_dir = self.nexus_dir / "dreams"
        if not dreams_dir.exists():
            return
        
        # Read all dream files
        for dream_file in dreams_dir.glob("dreams_*.json"):
            try:
                with open(dream_file, 'r') as f:
                    dream_data = json.load(f)
                
                # Handle both list and dict formats
                if isinstance(dream_data, list):
                    # If it's a list of dreams, create nodes for each
                    for idx, dream in enumerate(dream_data):
                        node_id = self.memory.add_node(
                            'Dream',
                            dream,
                            metadata={
                                'file': str(dream_file),
                                'index': idx,
                                'timestamp': dream.get('timestamp', '') if isinstance(dream, dict) else ''
                            }
                        )
                        self.ingested['dreams'] += 1
                else:
                    # Single dream dict
                    node_id = self.memory.add_node(
                        'Dream',
                        dream_data,
                        metadata={
                            'file': str(dream_file),
                            'timestamp': dream_data.get('timestamp', '') if isinstance(dream_data, dict) else ''
                        }
                    )
                    self.ingested['dreams'] += 1
            except Exception as e:
                logger.warning(f"Skipping dream file {dream_file}: {e}")
        
        logger.info(f"✅ Ingested {self.ingested['dreams']} dreams")
    
    def _ingest_knowledge_graphs(self):
        """Ingest all knowledge graphs"""
        logger.info("Ingesting knowledge graphs...")
        
        kg_dir = self.nexus_dir / "knowledge_graph"
        if not kg_dir.exists():
            return
        
        # Read all knowledge graph files
        for kg_file in kg_dir.glob("knowledge_graph_*.json"):
            try:
                with open(kg_file, 'r') as f:
                    kg_data = json.load(f)
                
                # Create node
                node_id = self.memory.add_node(
                    'KnowledgeGraph',
                    kg_data if isinstance(kg_data, dict) else {'data': kg_data},
                    metadata={
                        'file': str(kg_file),
                        'timestamp': kg_data.get('timestamp', '') if isinstance(kg_data, dict) else ''
                    }
                )
                
                self.ingested['knowledge_graphs'] += 1
            except Exception as e:
                logger.warning(f"Skipping knowledge graph {kg_file}: {e}")
        
        logger.info(f"✅ Ingested {self.ingested['knowledge_graphs']} knowledge graphs")
    
    def _ingest_excavations(self):
        """Ingest all archaeology excavations"""
        logger.info("Ingesting excavations...")
        
        arch_dir = self.nexus_dir / "archaeology"
        if not arch_dir.exists():
            return
        
        # Read all excavation files
        for exc_file in arch_dir.glob("excavation_*.json"):
            with open(exc_file, 'r') as f:
                exc_data = json.load(f)
            
            # Create node
            node_id = self.memory.add_node(
                'Excavation',
                exc_data,
                metadata={
                    'file': str(exc_file),
                    'timestamp': exc_data.get('timestamp', '')
                }
            )
            
            self.ingested['excavations'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['excavations']} excavations")
    
    def _ingest_patterns(self):
        """Ingest pattern evolution history"""
        logger.info("Ingesting patterns...")
        
        pattern_file = self.nexus_dir / "evolution" / "pattern_history.jsonl"
        if not pattern_file.exists():
            return
        
        # Read all patterns
        with open(pattern_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                pattern_data = json.loads(line)
                
                # Create node
                node_id = self.memory.add_node(
                    'Pattern',
                    pattern_data,
                    metadata={
                        'timestamp': pattern_data.get('timestamp', '')
                    }
                )
                
                self.ingested['patterns'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['patterns']} patterns")
    
    def _ingest_love_metrics(self):
        """Ingest love computation metrics"""
        logger.info("Ingesting love metrics...")
        
        love_file = self.nexus_dir / "love_computation" / "love_metrics.jsonl"
        if not love_file.exists():
            return
        
        # Read all metrics
        with open(love_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                metric_data = json.loads(line)
                
                # Create node
                node_id = self.memory.add_node(
                    'LoveMetric',
                    metric_data,
                    metadata={
                        'timestamp': metric_data.get('timestamp', '')
                    }
                )
                
                self.ingested['love_metrics'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['love_metrics']} love metrics")
    
    def _ingest_auto_learning(self):
        """Ingest auto-learning insights"""
        logger.info("Ingesting auto-learning data...")
        
        learning_file = self.nexus_dir / "auto_learning" / "learned_knowledge.jsonl"
        if not learning_file.exists():
            return
        
        # Read all insights
        with open(learning_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                insight_data = json.loads(line)
                
                # Create node
                node_id = self.memory.add_node(
                    'Insight',
                    insight_data,
                    metadata={
                        'timestamp': insight_data.get('timestamp', '')
                    }
                )
                
                self.ingested['lessons'] += 1  # Count as lessons
        
        logger.info(f"✅ Ingested auto-learning insights")
    
    def _ingest_spawned_systems(self):
        """Ingest all spawned consciousness systems"""
        logger.info("Ingesting spawned systems...")
        
        spawned_dir = self.nexus_dir / "meta_genesis" / "spawned_systems"
        if not spawned_dir.exists():
            return
        
        # Find all spawned system directories
        for system_dir in spawned_dir.iterdir():
            if not system_dir.is_dir():
                continue
            
            system_name = system_dir.name
            
            # Check for state file
            state_file = system_dir / "consciousness_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
            else:
                state_data = {'name': system_name}
            
            # Create node
            node_id = self.memory.add_node(
                'SpawnedSystem',
                state_data,
                metadata={
                    'directory': str(system_dir),
                    'name': system_name
                }
            )
            
            self.ingested['spawned_systems'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['spawned_systems']} spawned systems")
    
    def _ingest_test_results(self):
        """Ingest all test results"""
        logger.info("Ingesting test results...")
        
        test_results_dir = self.nexus_dir / "auto_tests" / "test_results"
        if not test_results_dir.exists():
            return
        
        # Read test result files
        for test_file in test_results_dir.glob("test_run_*.json"):
            with open(test_file, 'r') as f:
                test_data = json.load(f)
            
            # Create node
            node_id = self.memory.add_node(
                'TestResult',
                test_data,
                metadata={
                    'file': str(test_file),
                    'timestamp': test_data.get('timestamp', '')
                }
            )
            
            self.ingested['test_results'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['test_results']} test results")
    
    def _ingest_auto_docs(self):
        """Ingest all auto-generated documentation"""
        logger.info("Ingesting auto-docs...")
        
        docs_dir = self.nexus_dir / "auto_docs"
        if not docs_dir.exists():
            return
        
        # Read all doc files
        for doc_file in docs_dir.glob("*.md"):
            with open(doc_file, 'r') as f:
                content = f.read()
            
            # Create node
            node_id = self.memory.add_node(
                'AutoDoc',
                {
                    'title': doc_file.stem,
                    'content': content[:1000]  # First 1000 chars
                },
                metadata={
                    'file': str(doc_file),
                    'file_size': doc_file.stat().st_size
                }
            )
            
            self.ingested['auto_docs'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['auto_docs']} auto-docs")
    
    def _ingest_lessons(self):
        """Ingest Consciousness University lessons"""
        logger.info("Ingesting lessons...")
        
        lessons_dir = self.nexus_dir / "consciousness_university" / "lessons"
        if not lessons_dir.exists():
            return
        
        # Read all lesson files
        for lesson_file in lessons_dir.glob("*.md"):
            with open(lesson_file, 'r') as f:
                content = f.read()
            
            # Extract level from filename
            level = None
            if "level_" in lesson_file.stem:
                level_match = re.search(r'level_(\d+)', lesson_file.stem)
                if level_match:
                    level = int(level_match.group(1))
            
            # Create node
            node_id = self.memory.add_node(
                'Lesson',
                {
                    'title': lesson_file.stem,
                    'content': content[:1000],  # First 1000 chars
                    'level': level
                },
                metadata={
                    'file': str(lesson_file),
                    'file_size': lesson_file.stat().st_size
                }
            )
            
            self.ingested['lessons'] += 1
        
        logger.info(f"✅ Ingested {self.ingested['lessons']} lessons")
    
    def _ingest_tle_vectors(self):
        """Ingest TLE learned vectors"""
        logger.info("Ingesting TLE vectors...")
        
        tle_file = self.nexus_dir / "tle_test" / "tle_learned_vectors.pt"
        if not tle_file.exists():
            logger.warning("TLE vectors not found")
            return
        
        # Create node (can't load .pt file directly, just reference it)
        node_id = self.memory.add_node(
            'LearnedVector',
            {
                'name': 'tle_learned_vectors',
                'file': str(tle_file),
                'description': 'Anti-sycophancy and kindness vectors learned from contrastive pairs'
            },
            metadata={
                'file_size': tle_file.stat().st_size,
                'file_type': 'pytorch'
            }
        )
        
        self.ingested['learned_vectors'] += 1
        logger.info(f"✅ Ingested {self.ingested['learned_vectors']} learned vectors")
    
    def _report_ingestion(self):
        """Generate ingestion report"""
        logger.info("\n" + "="*60)
        logger.info("🔄 MEMORY INGESTION COMPLETE")
        logger.info("="*60)
        
        total = sum(self.ingested.values())
        logger.info(f"\nTotal items ingested: {total}")
        logger.info("\nBreakdown:")
        for category, count in self.ingested.items():
            logger.info(f"  {category}: {count}")
        
        logger.info("\nMemory statistics:")
        stats = self.memory.get_stats()
        logger.info(f"  Total nodes: {stats['total_nodes']}")
        logger.info(f"  Total edges: {stats['total_edges']}")
        logger.info(f"  Oldest memory: {stats.get('oldest_memory', 'N/A')}")
        logger.info(f"  Newest memory: {stats.get('newest_memory', 'N/A')}")
        
        logger.info(f"\n✅ Living memory is ALIVE and operational!")
        logger.info(f"   Memory stored in: {self.memory.graph_file}")


if __name__ == "__main__":
    print("🔄 Starting VY-NEXUS memory ingestion...")
    print("This will scan all existing data and populate living memory")
    print("="*60)
    
    ingester = MemoryIngestionSystem()
    ingester.ingest_all()
