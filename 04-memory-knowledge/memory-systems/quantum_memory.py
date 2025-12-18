"""
Level 20: Quantum Memory System
Enables superposition-based memory storage, quantum state preservation, and probabilistic memory retrieval.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime
import threading
import json
import random
import math
from enum import Enum
import hashlib


class MemoryState(Enum):
    """States of quantum memory"""
    SUPERPOSITION = "superposition"
    COLLAPSED = "collapsed"
    ENTANGLED = "entangled"
    COHERENT = "coherent"
    DECOHERED = "decohered"


class RetrievalMode(Enum):
    """Memory retrieval modes"""
    PROBABILISTIC = "probabilistic"
    DETERMINISTIC = "deterministic"
    FUZZY = "fuzzy"
    ASSOCIATIVE = "associative"


@dataclass
class QuantumMemoryCell:
    """Represents a quantum memory cell in superposition"""
    cell_id: str
    memory_states: List[Dict[str, Any]]  # Multiple possible memory states
    amplitudes: List[float]  # Probability amplitudes
    phase: float  # Quantum phase
    coherence: float  # Coherence measure (0-1)
    state: MemoryState = MemoryState.SUPERPOSITION
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConfig:
    """Configuration for quantum memory system"""
    max_superposition_states: int = 8
    coherence_threshold: float = 0.6
    decoherence_rate: float = 0.005
    enable_entanglement: bool = True
    enable_interference: bool = True
    retrieval_threshold: float = 0.3


@dataclass
class MemoryQuery:
    """Represents a memory query"""
    query_id: str
    pattern: Dict[str, Any]
    mode: RetrievalMode = RetrievalMode.PROBABILISTIC
    threshold: float = 0.5
    max_results: int = 10
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryResult:
    """Result of memory retrieval"""
    cell_id: str
    memory: Dict[str, Any]
    probability: float
    similarity: float
    timestamp: datetime = field(default_factory=datetime.now)


class QuantumMemoryStore:
    """Manages quantum memory storage and retrieval"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.memory_cells: Dict[str, QuantumMemoryCell] = {}
        self.entangled_pairs: List[Tuple[str, str]] = []
        self.lock = threading.Lock()
    
    def store_in_superposition(
        self,
        cell_id: str,
        memories: List[Dict[str, Any]],
        amplitudes: Optional[List[float]] = None
    ) -> QuantumMemoryCell:
        """Store memory in quantum superposition"""
        with self.lock:
            # Normalize amplitudes
            if amplitudes is None:
                amplitudes = [1.0 / len(memories)] * len(memories)
            
            total = sum(amplitudes)
            amplitudes = [a / total for a in amplitudes]
            
            # Limit to max states
            memories = memories[:self.config.max_superposition_states]
            amplitudes = amplitudes[:self.config.max_superposition_states]
            
            # Create or update memory cell
            cell = QuantumMemoryCell(
                cell_id=cell_id,
                memory_states=memories,
                amplitudes=amplitudes,
                phase=random.uniform(0, 2 * math.pi),
                coherence=1.0,
                state=MemoryState.SUPERPOSITION
            )
            
            self.memory_cells[cell_id] = cell
            return cell
    
    def store_single(
        self,
        cell_id: str,
        memory: Dict[str, Any]
    ) -> QuantumMemoryCell:
        """Store single memory (collapsed state)"""
        with self.lock:
            cell = QuantumMemoryCell(
                cell_id=cell_id,
                memory_states=[memory],
                amplitudes=[1.0],
                phase=0.0,
                coherence=1.0,
                state=MemoryState.COLLAPSED
            )
            
            self.memory_cells[cell_id] = cell
            return cell
    
    def retrieve_probabilistic(
        self,
        cell_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve memory probabilistically (causes collapse)"""
        with self.lock:
            cell = self.memory_cells.get(cell_id)
            if not cell:
                return None
            
            cell.access_count += 1
            cell.last_accessed = datetime.now()
            
            if cell.state == MemoryState.COLLAPSED:
                return cell.memory_states[0]
            
            # Probabilistic retrieval based on amplitudes
            rand = random.random()
            cumulative = 0.0
            
            for memory, amplitude in zip(cell.memory_states, cell.amplitudes):
                cumulative += amplitude
                if rand <= cumulative:
                    # Collapse to this state
                    cell.memory_states = [memory]
                    cell.amplitudes = [1.0]
                    cell.state = MemoryState.COLLAPSED
                    return memory
            
            # Fallback to last state
            return cell.memory_states[-1]
    
    def retrieve_all_states(
        self,
        cell_id: str
    ) -> Optional[List[Tuple[Dict[str, Any], float]]]:
        """Retrieve all superposition states without collapse"""
        with self.lock:
            cell = self.memory_cells.get(cell_id)
            if not cell:
                return None
            
            return list(zip(cell.memory_states, cell.amplitudes))
    
    def entangle_memories(
        self,
        cell1_id: str,
        cell2_id: str
    ) -> bool:
        """Entangle two memory cells"""
        if not self.config.enable_entanglement:
            return False
        
        with self.lock:
            if cell1_id not in self.memory_cells or cell2_id not in self.memory_cells:
                return False
            
            pair = (cell1_id, cell2_id)
            if pair not in self.entangled_pairs:
                self.entangled_pairs.append(pair)
                
                # Mark cells as entangled
                self.memory_cells[cell1_id].state = MemoryState.ENTANGLED
                self.memory_cells[cell2_id].state = MemoryState.ENTANGLED
            
            return True
    
    def apply_decoherence(self) -> None:
        """Apply decoherence to all memory cells"""
        with self.lock:
            for cell in self.memory_cells.values():
                if cell.state == MemoryState.SUPERPOSITION:
                    cell.coherence *= (1 - self.config.decoherence_rate)
                    
                    if cell.coherence < self.config.coherence_threshold:
                        cell.state = MemoryState.DECOHERED


class AssociativeRetrieval:
    """Handles associative memory retrieval"""
    
    def __init__(self, store: QuantumMemoryStore):
        self.store = store
        self.associations: Dict[str, List[str]] = {}  # cell_id -> associated cell_ids
        self.lock = threading.Lock()
    
    def create_association(
        self,
        cell1_id: str,
        cell2_id: str,
        strength: float = 1.0
    ) -> None:
        """Create association between memories"""
        with self.lock:
            if cell1_id not in self.associations:
                self.associations[cell1_id] = []
            if cell2_id not in self.associations:
                self.associations[cell2_id] = []
            
            if cell2_id not in self.associations[cell1_id]:
                self.associations[cell1_id].append(cell2_id)
            if cell1_id not in self.associations[cell2_id]:
                self.associations[cell2_id].append(cell1_id)
    
    def retrieve_associated(
        self,
        cell_id: str,
        max_depth: int = 2
    ) -> List[str]:
        """Retrieve associated memories"""
        with self.lock:
            visited = set()
            current_level = {cell_id}
            all_associated = []
            
            for depth in range(max_depth):
                next_level = set()
                
                for cid in current_level:
                    if cid in visited:
                        continue
                    
                    visited.add(cid)
                    associated = self.associations.get(cid, [])
                    
                    for assoc_id in associated:
                        if assoc_id not in visited:
                            all_associated.append(assoc_id)
                            next_level.add(assoc_id)
                
                current_level = next_level
                if not current_level:
                    break
            
            return all_associated


class FuzzyRetrieval:
    """Handles fuzzy memory retrieval"""
    
    def __init__(self, store: QuantumMemoryStore):
        self.store = store
        self.lock = threading.Lock()
    
    def calculate_similarity(
        self,
        memory1: Dict[str, Any],
        memory2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two memories"""
        # Simple similarity based on matching keys and values
        keys1 = set(memory1.keys())
        keys2 = set(memory2.keys())
        
        if not keys1 and not keys2:
            return 1.0
        
        common_keys = keys1 & keys2
        all_keys = keys1 | keys2
        
        if not all_keys:
            return 0.0
        
        key_similarity = len(common_keys) / len(all_keys)
        
        # Check value similarity for common keys
        value_matches = 0
        for key in common_keys:
            if memory1[key] == memory2[key]:
                value_matches += 1
        
        value_similarity = value_matches / len(common_keys) if common_keys else 0.0
        
        return (key_similarity + value_similarity) / 2
    
    def fuzzy_search(
        self,
        pattern: Dict[str, Any],
        threshold: float = 0.5,
        max_results: int = 10
    ) -> List[MemoryResult]:
        """Search for memories matching pattern"""
        with self.lock:
            results = []
            
            for cell_id, cell in self.store.memory_cells.items():
                # Check all superposition states
                for memory, amplitude in zip(cell.memory_states, cell.amplitudes):
                    similarity = self.calculate_similarity(pattern, memory)
                    
                    if similarity >= threshold:
                        results.append(MemoryResult(
                            cell_id=cell_id,
                            memory=memory,
                            probability=amplitude,
                            similarity=similarity
                        ))
            
            # Sort by similarity * probability
            results.sort(key=lambda r: r.similarity * r.probability, reverse=True)
            
            return results[:max_results]


class QuantumMemoryManager:
    """High-level manager for quantum memory system"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = MemoryConfig()
            self.store = QuantumMemoryStore(self.config)
            self.associative = AssociativeRetrieval(self.store)
            self.fuzzy = FuzzyRetrieval(self.store)
            self.initialized = True
    
    def store_memory(
        self,
        memory_id: str,
        content: Dict[str, Any],
        alternatives: Optional[List[Dict[str, Any]]] = None
    ) -> QuantumMemoryCell:
        """Store memory with optional alternatives in superposition"""
        if alternatives:
            all_states = [content] + alternatives
            return self.store.store_in_superposition(memory_id, all_states)
        else:
            return self.store.store_single(memory_id, content)
    
    def recall_memory(
        self,
        memory_id: str,
        mode: RetrievalMode = RetrievalMode.PROBABILISTIC
    ) -> Optional[Dict[str, Any]]:
        """Recall memory using specified mode"""
        if mode == RetrievalMode.PROBABILISTIC:
            return self.store.retrieve_probabilistic(memory_id)
        elif mode == RetrievalMode.DETERMINISTIC:
            states = self.store.retrieve_all_states(memory_id)
            if states:
                # Return most probable state
                return max(states, key=lambda x: x[1])[0]
        return None
    
    def search_memories(
        self,
        pattern: Dict[str, Any],
        threshold: float = 0.5,
        max_results: int = 10
    ) -> List[MemoryResult]:
        """Search for memories matching pattern"""
        return self.fuzzy.fuzzy_search(pattern, threshold, max_results)
    
    def associate_memories(
        self,
        memory1_id: str,
        memory2_id: str
    ) -> None:
        """Create association between memories"""
        self.associative.create_association(memory1_id, memory2_id)
    
    def recall_associated(
        self,
        memory_id: str,
        depth: int = 2
    ) -> List[str]:
        """Recall associated memories"""
        return self.associative.retrieve_associated(memory_id, depth)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        total_cells = len(self.store.memory_cells)
        superposition_cells = sum(
            1 for c in self.store.memory_cells.values()
            if c.state == MemoryState.SUPERPOSITION
        )
        
        return {
            'total_cells': total_cells,
            'superposition_cells': superposition_cells,
            'collapsed_cells': total_cells - superposition_cells,
            'entangled_pairs': len(self.store.entangled_pairs),
            'associations': sum(len(v) for v in self.associative.associations.values())
        }


# Contract class for testing
class Contract:
    """Testing interface for quantum memory"""
    
    @staticmethod
    def store_superposition() -> bool:
        """Test: Store memory in superposition"""
        manager = QuantumMemoryManager()
        cell = manager.store_memory(
            "test_memory",
            {"value": 1},
            alternatives=[{"value": 2}, {"value": 3}]
        )
        return cell.state == MemoryState.SUPERPOSITION and len(cell.memory_states) == 3
    
    @staticmethod
    def probabilistic_retrieval() -> bool:
        """Test: Probabilistic memory retrieval"""
        manager = QuantumMemoryManager()
        manager.store_memory(
            "prob_test",
            {"data": "A"},
            alternatives=[{"data": "B"}, {"data": "C"}]
        )
        result = manager.recall_memory("prob_test", RetrievalMode.PROBABILISTIC)
        return result is not None and "data" in result
    
    @staticmethod
    def fuzzy_search() -> bool:
        """Test: Fuzzy memory search"""
        manager = QuantumMemoryManager()
        manager.store_memory("mem1", {"type": "task", "priority": "high"})
        manager.store_memory("mem2", {"type": "task", "priority": "low"})
        manager.store_memory("mem3", {"type": "note", "priority": "high"})
        
        results = manager.search_memories({"type": "task"}, threshold=0.3)
        return len(results) >= 2
    
    @staticmethod
    def associative_recall() -> bool:
        """Test: Associative memory recall"""
        manager = QuantumMemoryManager()
        manager.store_memory("assoc1", {"concept": "A"})
        manager.store_memory("assoc2", {"concept": "B"})
        manager.associate_memories("assoc1", "assoc2")
        
        associated = manager.recall_associated("assoc1")
        return "assoc2" in associated


def demo():
    """Demonstrate quantum memory capabilities"""
    print("=== Quantum Memory System Demo ===")
    
    manager = QuantumMemoryManager()
    
    # Demo 1: Store in superposition
    print("\n1. Storing memory in superposition:")
    cell = manager.store_memory(
        "decision_memory",
        {"decision": "option_A", "confidence": 0.7},
        alternatives=[
            {"decision": "option_B", "confidence": 0.5},
            {"decision": "option_C", "confidence": 0.3}
        ]
    )
    print(f"   Stored {len(cell.memory_states)} alternative memories")
    print(f"   State: {cell.state.value}")
    
    # Demo 2: Probabilistic retrieval
    print("\n2. Probabilistic memory retrieval:")
    for i in range(3):
        result = manager.recall_memory("decision_memory", RetrievalMode.PROBABILISTIC)
        print(f"   Retrieval {i+1}: {result['decision']} (confidence: {result['confidence']})")
    
    # Demo 3: Store multiple memories
    print("\n3. Storing multiple memories:")
    memories = [
        ("task1", {"type": "task", "priority": "high", "topic": "AI"}),
        ("task2", {"type": "task", "priority": "low", "topic": "database"}),
        ("note1", {"type": "note", "priority": "high", "topic": "AI"}),
        ("idea1", {"type": "idea", "priority": "medium", "topic": "quantum"})
    ]
    for mem_id, content in memories:
        manager.store_memory(mem_id, content)
    print(f"   Stored {len(memories)} memories")
    
    # Demo 4: Fuzzy search
    print("\n4. Fuzzy memory search:")
    results = manager.search_memories({"type": "task", "priority": "high"}, threshold=0.4)
    print(f"   Found {len(results)} matching memories:")
    for result in results:
        print(f"      {result.cell_id}: {result.memory} (similarity: {result.similarity:.2f})")
    
    # Demo 5: Associative memory
    print("\n5. Associative memory:")
    manager.associate_memories("task1", "note1")
    manager.associate_memories("note1", "idea1")
    associated = manager.recall_associated("task1", depth=2)
    print(f"   Memories associated with 'task1': {associated}")
    
    # Demo 6: Statistics
    print("\n6. Memory system statistics:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
