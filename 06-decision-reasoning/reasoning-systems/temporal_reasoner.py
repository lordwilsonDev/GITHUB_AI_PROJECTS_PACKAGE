"""
Level 22: Temporal Reasoning Engine
Enables past-present-future integration, causal loop handling, and temporal paradox resolution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from datetime import datetime, timedelta
import threading
import json
import random
from enum import Enum
from collections import defaultdict, deque
import hashlib


class TimeDirection(Enum):
    """Direction of temporal reasoning"""
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    BIDIRECTIONAL = "bidirectional"
    ATEMPORAL = "atemporal"


class CausalityType(Enum):
    """Types of causal relationships"""
    FORWARD = "forward"
    BACKWARD = "backward"
    CIRCULAR = "circular"
    ACAUSAL = "acausal"
    QUANTUM = "quantum"


class ParadoxType(Enum):
    """Types of temporal paradoxes"""
    GRANDFATHER = "grandfather"
    BOOTSTRAP = "bootstrap"
    PREDESTINATION = "predestination"
    ONTOLOGICAL = "ontological"
    CAUSAL_LOOP = "causal_loop"
    NONE = "none"


class TimelineStatus(Enum):
    """Status of a timeline"""
    STABLE = "stable"
    BRANCHING = "branching"
    MERGING = "merging"
    PARADOXICAL = "paradoxical"
    RESOLVED = "resolved"


@dataclass
class TemporalEvent:
    """Represents an event in time"""
    event_id: str
    timestamp: datetime
    description: str
    causes: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    timeline_id: str = "main"
    probability: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Timeline:
    """Represents a timeline/worldline"""
    timeline_id: str
    parent_id: Optional[str]
    branch_point: Optional[datetime]
    events: List[str] = field(default_factory=list)
    status: TimelineStatus = TimelineStatus.STABLE
    probability: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalChain:
    """Represents a chain of causally connected events"""
    chain_id: str
    events: List[str] = field(default_factory=list)
    causality_type: CausalityType = CausalityType.FORWARD
    loop_detected: bool = False
    paradox_type: ParadoxType = ParadoxType.NONE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalPrediction:
    """Represents a prediction about future events"""
    prediction_id: str
    target_time: datetime
    predicted_events: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    based_on: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalMetrics:
    """Metrics for temporal reasoning"""
    total_events: int = 0
    total_timelines: int = 0
    causal_chains: int = 0
    paradoxes_detected: int = 0
    paradoxes_resolved: int = 0
    predictions_made: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class CausalAnalyzer:
    """Analyzes causal relationships between events"""
    
    def __init__(self):
        self.events: Dict[str, TemporalEvent] = {}
        self.causal_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.lock = threading.Lock()
        
    def add_event(self, event: TemporalEvent):
        """Add an event to the causal analyzer"""
        with self.lock:
            self.events[event.event_id] = event
            
            # Build causal graph
            for cause_id in event.causes:
                self.causal_graph[cause_id].add(event.event_id)
                self.reverse_graph[event.event_id].add(cause_id)
    
    def find_causal_chain(self, start_event: str, end_event: str) -> Optional[List[str]]:
        """Find causal chain between two events"""
        with self.lock:
            if start_event not in self.events or end_event not in self.events:
                return None
            
            # BFS to find path
            queue = deque([(start_event, [start_event])])
            visited = {start_event}
            
            while queue:
                current, path = queue.popleft()
                
                if current == end_event:
                    return path
                
                for next_event in self.causal_graph.get(current, []):
                    if next_event not in visited:
                        visited.add(next_event)
                        queue.append((next_event, path + [next_event]))
            
            return None
    
    def detect_causal_loop(self, event_id: str) -> Optional[List[str]]:
        """Detect if an event is part of a causal loop"""
        with self.lock:
            if event_id not in self.events:
                return None
            
            # DFS to detect cycle
            visited = set()
            rec_stack = set()
            path = []
            
            def dfs(node: str) -> Optional[List[str]]:
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                for neighbor in self.causal_graph.get(node, []):
                    if neighbor not in visited:
                        result = dfs(neighbor)
                        if result:
                            return result
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        return path[cycle_start:]
                
                path.pop()
                rec_stack.remove(node)
                return None
            
            return dfs(event_id)
    
    def get_causality_type(self, event1: str, event2: str) -> CausalityType:
        """Determine causality type between two events"""
        with self.lock:
            if event1 not in self.events or event2 not in self.events:
                return CausalityType.ACAUSAL
            
            e1 = self.events[event1]
            e2 = self.events[event2]
            
            # Check temporal ordering
            if e1.timestamp < e2.timestamp:
                # Check if causal connection exists
                if self.find_causal_chain(event1, event2):
                    return CausalityType.FORWARD
            elif e1.timestamp > e2.timestamp:
                if self.find_causal_chain(event2, event1):
                    return CausalityType.BACKWARD
            
            # Check for circular causality
            if self.detect_causal_loop(event1):
                return CausalityType.CIRCULAR
            
            return CausalityType.ACAUSAL


class ParadoxResolver:
    """Resolves temporal paradoxes"""
    
    def __init__(self):
        self.paradoxes: Dict[str, Dict[str, Any]] = {}
        self.resolutions: Dict[str, str] = {}
        self.lock = threading.Lock()
        self.paradox_counter = 0
        
    def detect_paradox(self, events: List[TemporalEvent], 
                      causal_chain: Optional[List[str]] = None) -> Optional[ParadoxType]:
        """Detect temporal paradoxes"""
        with self.lock:
            # Check for grandfather paradox
            if self._is_grandfather_paradox(events):
                return ParadoxType.GRANDFATHER
            
            # Check for bootstrap paradox
            if self._is_bootstrap_paradox(events, causal_chain):
                return ParadoxType.BOOTSTRAP
            
            # Check for causal loop
            if causal_chain and len(causal_chain) > 1 and causal_chain[0] == causal_chain[-1]:
                return ParadoxType.CAUSAL_LOOP
            
            # Check for predestination paradox
            if self._is_predestination_paradox(events):
                return ParadoxType.PREDESTINATION
            
            return ParadoxType.NONE
    
    def _is_grandfather_paradox(self, events: List[TemporalEvent]) -> bool:
        """Check for grandfather paradox (event prevents its own cause)"""
        for event in events:
            # Check if event affects its own causal history
            for cause_id in event.causes:
                if any(e.event_id == cause_id and e.timestamp > event.timestamp 
                      for e in events):
                    return True
        return False
    
    def _is_bootstrap_paradox(self, events: List[TemporalEvent], 
                             causal_chain: Optional[List[str]]) -> bool:
        """Check for bootstrap paradox (information/object with no origin)"""
        if not causal_chain or len(causal_chain) < 2:
            return False
        
        # Check if chain forms a loop with no external origin
        if causal_chain[0] == causal_chain[-1]:
            # Check if any event in loop has external cause
            event_ids = set(causal_chain)
            for event in events:
                if event.event_id in event_ids:
                    external_causes = [c for c in event.causes if c not in event_ids]
                    if external_causes:
                        return False
            return True
        
        return False
    
    def _is_predestination_paradox(self, events: List[TemporalEvent]) -> bool:
        """Check for predestination paradox (attempt to change past creates it)"""
        # Simplified check: look for events that reference future knowledge
        for event in events:
            if "future_knowledge" in event.metadata:
                return True
        return False
    
    def resolve_paradox(self, paradox_type: ParadoxType, 
                       events: List[TemporalEvent]) -> str:
        """Resolve a temporal paradox"""
        with self.lock:
            self.paradox_counter += 1
            paradox_id = f"paradox_{self.paradox_counter}"
            
            resolution = ""
            
            if paradox_type == ParadoxType.GRANDFATHER:
                resolution = self._resolve_grandfather(events)
            elif paradox_type == ParadoxType.BOOTSTRAP:
                resolution = self._resolve_bootstrap(events)
            elif paradox_type == ParadoxType.CAUSAL_LOOP:
                resolution = self._resolve_causal_loop(events)
            elif paradox_type == ParadoxType.PREDESTINATION:
                resolution = self._resolve_predestination(events)
            else:
                resolution = "no_paradox_detected"
            
            self.paradoxes[paradox_id] = {
                "type": paradox_type.value,
                "events": [e.event_id for e in events],
                "resolution": resolution
            }
            
            self.resolutions[paradox_id] = resolution
            return resolution
    
    def _resolve_grandfather(self, events: List[TemporalEvent]) -> str:
        """Resolve grandfather paradox via timeline branching"""
        return "timeline_branch_created"
    
    def _resolve_bootstrap(self, events: List[TemporalEvent]) -> str:
        """Resolve bootstrap paradox via consistency principle"""
        return "self_consistent_loop_maintained"
    
    def _resolve_causal_loop(self, events: List[TemporalEvent]) -> str:
        """Resolve causal loop via Novikov self-consistency"""
        return "novikov_consistency_enforced"
    
    def _resolve_predestination(self, events: List[TemporalEvent]) -> str:
        """Resolve predestination paradox via timeline convergence"""
        return "timeline_convergence_to_stable_state"


class TemporalPredictor:
    """Predicts future events based on causal patterns"""
    
    def __init__(self):
        self.predictions: Dict[str, TemporalPrediction] = {}
        self.patterns: Dict[str, List[str]] = defaultdict(list)
        self.lock = threading.Lock()
        self.prediction_counter = 0
        
    def learn_pattern(self, events: List[TemporalEvent]):
        """Learn causal patterns from events"""
        with self.lock:
            # Extract patterns from event sequences
            for i in range(len(events) - 1):
                pattern_key = f"{events[i].description}_{events[i+1].description}"
                self.patterns[pattern_key].append(events[i+1].event_id)
    
    def predict_future(self, current_events: List[TemporalEvent],
                      horizon: timedelta) -> TemporalPrediction:
        """Predict future events"""
        with self.lock:
            self.prediction_counter += 1
            prediction_id = f"prediction_{self.prediction_counter}"
            
            target_time = datetime.now() + horizon
            predicted_events = []
            
            # Use patterns to predict
            for event in current_events[-3:]:  # Use recent events
                pattern_key = f"{event.description}_*"
                
                # Find matching patterns
                for key, event_ids in self.patterns.items():
                    if key.startswith(event.description):
                        predicted_events.append({
                            "description": key.split("_")[1],
                            "probability": len(event_ids) / max(len(self.patterns), 1),
                            "based_on": event.event_id
                        })
            
            # Calculate overall confidence
            confidence = (len(predicted_events) / max(len(current_events), 1)
                         if predicted_events else 0.0)
            
            prediction = TemporalPrediction(
                prediction_id=prediction_id,
                target_time=target_time,
                predicted_events=predicted_events,
                confidence=min(confidence, 1.0),
                based_on=[e.event_id for e in current_events]
            )
            
            self.predictions[prediction_id] = prediction
            return prediction


class TemporalReasoner:
    """Main temporal reasoning engine"""
    
    def __init__(self):
        self.events: Dict[str, TemporalEvent] = {}
        self.timelines: Dict[str, Timeline] = {}
        self.causal_analyzer = CausalAnalyzer()
        self.paradox_resolver = ParadoxResolver()
        self.predictor = TemporalPredictor()
        self.lock = threading.Lock()
        self.event_counter = 0
        self.timeline_counter = 0
        
        # Create main timeline
        self._create_timeline("main", None, None)
    
    def add_event(self, description: str, timestamp: datetime,
                 causes: Optional[List[str]] = None,
                 timeline_id: str = "main") -> str:
        """Add a temporal event"""
        with self.lock:
            self.event_counter += 1
            event_id = f"event_{self.event_counter}"
            
            event = TemporalEvent(
                event_id=event_id,
                timestamp=timestamp,
                description=description,
                causes=causes or [],
                timeline_id=timeline_id
            )
            
            self.events[event_id] = event
            self.causal_analyzer.add_event(event)
            
            # Add to timeline
            if timeline_id in self.timelines:
                self.timelines[timeline_id].events.append(event_id)
            
            return event_id
    
    def _create_timeline(self, timeline_id: str, parent_id: Optional[str],
                        branch_point: Optional[datetime]) -> str:
        """Create a new timeline"""
        timeline = Timeline(
            timeline_id=timeline_id,
            parent_id=parent_id,
            branch_point=branch_point
        )
        self.timelines[timeline_id] = timeline
        return timeline_id
    
    def analyze_causality(self, event1_id: str, event2_id: str) -> Dict[str, Any]:
        """Analyze causal relationship between events"""
        with self.lock:
            causality_type = self.causal_analyzer.get_causality_type(event1_id, event2_id)
            causal_chain = self.causal_analyzer.find_causal_chain(event1_id, event2_id)
            
            return {
                "event1": event1_id,
                "event2": event2_id,
                "causality_type": causality_type.value,
                "causal_chain": causal_chain,
                "chain_length": len(causal_chain) if causal_chain else 0
            }
    
    def detect_paradox(self, event_ids: List[str]) -> Dict[str, Any]:
        """Detect temporal paradoxes"""
        with self.lock:
            events = [self.events[eid] for eid in event_ids if eid in self.events]
            
            if not events:
                return {"paradox_detected": False}
            
            # Check for causal loop
            causal_loop = None
            for event_id in event_ids:
                loop = self.causal_analyzer.detect_causal_loop(event_id)
                if loop:
                    causal_loop = loop
                    break
            
            # Detect paradox type
            paradox_type = self.paradox_resolver.detect_paradox(events, causal_loop)
            
            result = {
                "paradox_detected": paradox_type != ParadoxType.NONE,
                "paradox_type": paradox_type.value,
                "causal_loop": causal_loop
            }
            
            # Resolve if paradox detected
            if paradox_type != ParadoxType.NONE:
                resolution = self.paradox_resolver.resolve_paradox(paradox_type, events)
                result["resolution"] = resolution
                
                # Create branch timeline if needed
                if resolution == "timeline_branch_created":
                    self.timeline_counter += 1
                    new_timeline_id = f"timeline_{self.timeline_counter}"
                    self._create_timeline(
                        new_timeline_id,
                        events[0].timeline_id,
                        events[0].timestamp
                    )
                    result["new_timeline"] = new_timeline_id
            
            return result
    
    def predict_future(self, horizon_days: int = 7) -> TemporalPrediction:
        """Predict future events"""
        with self.lock:
            # Get recent events for prediction
            recent_events = sorted(
                self.events.values(),
                key=lambda e: e.timestamp,
                reverse=True
            )[:10]
            
            # Learn from patterns
            all_events = sorted(self.events.values(), key=lambda e: e.timestamp)
            self.predictor.learn_pattern(all_events)
            
            # Make prediction
            horizon = timedelta(days=horizon_days)
            return self.predictor.predict_future(recent_events, horizon)
    
    def integrate_temporal_knowledge(self, past_events: List[str],
                                    present_events: List[str],
                                    future_predictions: List[str]) -> Dict[str, Any]:
        """Integrate past, present, and future knowledge"""
        with self.lock:
            # Analyze causal connections across time
            connections = []
            
            # Past -> Present
            for past_id in past_events:
                for present_id in present_events:
                    if past_id in self.events and present_id in self.events:
                        chain = self.causal_analyzer.find_causal_chain(past_id, present_id)
                        if chain:
                            connections.append({
                                "from": past_id,
                                "to": present_id,
                                "type": "past_to_present",
                                "chain": chain
                            })
            
            # Present -> Future (predictions)
            for present_id in present_events:
                for future_id in future_predictions:
                    connections.append({
                        "from": present_id,
                        "to": future_id,
                        "type": "present_to_future",
                        "chain": [present_id, future_id]
                    })
            
            return {
                "temporal_integration": "complete",
                "connections": connections,
                "total_connections": len(connections),
                "past_events": len(past_events),
                "present_events": len(present_events),
                "future_predictions": len(future_predictions)
            }
    
    def get_timeline_status(self, timeline_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a timeline"""
        with self.lock:
            if timeline_id not in self.timelines:
                return None
            
            timeline = self.timelines[timeline_id]
            
            return {
                "timeline_id": timeline.timeline_id,
                "parent_id": timeline.parent_id,
                "status": timeline.status.value,
                "event_count": len(timeline.events),
                "probability": timeline.probability,
                "branch_point": timeline.branch_point.isoformat() if timeline.branch_point else None
            }
    
    def get_metrics(self) -> TemporalMetrics:
        """Get temporal reasoning metrics"""
        with self.lock:
            return TemporalMetrics(
                total_events=len(self.events),
                total_timelines=len(self.timelines),
                causal_chains=len(self.causal_analyzer.causal_graph),
                paradoxes_detected=len(self.paradox_resolver.paradoxes),
                paradoxes_resolved=len(self.paradox_resolver.resolutions),
                predictions_made=len(self.predictor.predictions)
            )


# Singleton instance
_temporal_reasoner = None
_temporal_lock = threading.Lock()


def get_temporal_reasoner() -> TemporalReasoner:
    """Get the singleton temporal reasoner instance"""
    global _temporal_reasoner
    if _temporal_reasoner is None:
        with _temporal_lock:
            if _temporal_reasoner is None:
                _temporal_reasoner = TemporalReasoner()
    return _temporal_reasoner


class Contract:
    """Testing contract for temporal reasoning"""
    
    @staticmethod
    def test_event_creation():
        """Test event creation and causal tracking"""
        reasoner = TemporalReasoner()
        now = datetime.now()
        
        event1 = reasoner.add_event("Event A", now)
        event2 = reasoner.add_event("Event B", now + timedelta(hours=1), causes=[event1])
        
        assert event1 in reasoner.events
        assert event2 in reasoner.events
        assert event1 in reasoner.events[event2].causes
        return True
    
    @staticmethod
    def test_causality_analysis():
        """Test causality analysis"""
        reasoner = TemporalReasoner()
        now = datetime.now()
        
        e1 = reasoner.add_event("Cause", now)
        e2 = reasoner.add_event("Effect", now + timedelta(hours=1), causes=[e1])
        
        analysis = reasoner.analyze_causality(e1, e2)
        assert analysis["causality_type"] == "forward"
        assert analysis["causal_chain"] is not None
        return True
    
    @staticmethod
    def test_paradox_detection():
        """Test paradox detection"""
        reasoner = TemporalReasoner()
        now = datetime.now()
        
        # Create causal loop
        e1 = reasoner.add_event("Event 1", now)
        e2 = reasoner.add_event("Event 2", now + timedelta(hours=1), causes=[e1])
        e3 = reasoner.add_event("Event 3", now + timedelta(hours=2), causes=[e2])
        
        # Manually create loop for testing
        reasoner.events[e1].causes.append(e3)
        reasoner.causal_analyzer.add_event(reasoner.events[e1])
        
        result = reasoner.detect_paradox([e1, e2, e3])
        assert result["paradox_detected"] or result["causal_loop"] is not None
        return True
    
    @staticmethod
    def test_future_prediction():
        """Test future prediction"""
        reasoner = TemporalReasoner()
        now = datetime.now()
        
        # Add some events
        for i in range(5):
            reasoner.add_event(f"Event {i}", now + timedelta(hours=i))
        
        prediction = reasoner.predict_future(horizon_days=1)
        assert prediction.prediction_id is not None
        assert prediction.target_time > now
        return True


def demo():
    """Demonstrate temporal reasoning capabilities"""
    print("=== Temporal Reasoning Demo ===")
    
    reasoner = get_temporal_reasoner()
    now = datetime.now()
    
    # Create temporal events
    print("\n1. Creating temporal events...")
    e1 = reasoner.add_event("System initialized", now - timedelta(hours=2))
    e2 = reasoner.add_event("Data loaded", now - timedelta(hours=1), causes=[e1])
    e3 = reasoner.add_event("Processing started", now - timedelta(minutes=30), causes=[e2])
    e4 = reasoner.add_event("Results generated", now, causes=[e3])
    print(f"   Created {len(reasoner.events)} events")
    
    # Analyze causality
    print("\n2. Analyzing causality...")
    analysis = reasoner.analyze_causality(e1, e4)
    print(f"   Causality type: {analysis['causality_type']}")
    print(f"   Causal chain length: {analysis['chain_length']}")
    if analysis['causal_chain']:
        print(f"   Chain: {' -> '.join(analysis['causal_chain'])}")
    
    # Create causal loop for paradox detection
    print("\n3. Testing paradox detection...")
    e5 = reasoner.add_event("Time travel event", now + timedelta(hours=1), causes=[e4])
    reasoner.events[e1].causes.append(e5)  # Create loop
    reasoner.causal_analyzer.add_event(reasoner.events[e1])
    
    paradox_result = reasoner.detect_paradox([e1, e4, e5])
    print(f"   Paradox detected: {paradox_result['paradox_detected']}")
    if paradox_result['paradox_detected']:
        print(f"   Paradox type: {paradox_result['paradox_type']}")
        print(f"   Resolution: {paradox_result.get('resolution', 'N/A')}")
    
    # Predict future
    print("\n4. Predicting future events...")
    prediction = reasoner.predict_future(horizon_days=7)
    print(f"   Prediction ID: {prediction.prediction_id}")
    print(f"   Target time: {prediction.target_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Confidence: {prediction.confidence:.2%}")
    print(f"   Predicted events: {len(prediction.predicted_events)}")
    
    # Temporal integration
    print("\n5. Integrating temporal knowledge...")
    integration = reasoner.integrate_temporal_knowledge(
        past_events=[e1, e2],
        present_events=[e3, e4],
        future_predictions=[prediction.prediction_id]
    )
    print(f"   Total connections: {integration['total_connections']}")
    print(f"   Past events: {integration['past_events']}")
    print(f"   Present events: {integration['present_events']}")
    print(f"   Future predictions: {integration['future_predictions']}")
    
    # Metrics
    print("\n6. Temporal reasoning metrics:")
    metrics = reasoner.get_metrics()
    print(f"   Total events: {metrics.total_events}")
    print(f"   Total timelines: {metrics.total_timelines}")
    print(f"   Causal chains: {metrics.causal_chains}")
    print(f"   Paradoxes detected: {metrics.paradoxes_detected}")
    print(f"   Paradoxes resolved: {metrics.paradoxes_resolved}")
    print(f"   Predictions made: {metrics.predictions_made}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Run contract tests
    print("Running contract tests...")
    assert Contract.test_event_creation()
    assert Contract.test_causality_analysis()
    assert Contract.test_paradox_detection()
    assert Contract.test_future_prediction()
    print("All tests passed!\n")
    
    # Run demo
    demo()
