"""Stage 2: Hunter - Find anomalies and positive deviants."""

from typing import List
from ..core.models import KillChainInput, SearchManifest, Anomaly


class HunterStage:
    """
    Hunter stage finds anomalies and positive deviants.
    
    Instead of looking for averages, hunt for:
    - Systems that violate assumptions but still work
    - Outliers that perform exceptionally well
    - Edge cases that reveal hidden constraints
    """
    
    def execute(
        self,
        input_data: KillChainInput,
        search_manifest: SearchManifest,
    ) -> List[Anomaly]:
        """
        Execute hunter stage.
        
        Args:
            input_data: Kill Chain input
            search_manifest: Output from Targeting stage
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Hunt for positive deviants
        anomalies.extend(self._hunt_positive_deviants(input_data))
        
        # Hunt for constraint violations that work
        anomalies.extend(self._hunt_constraint_violations(input_data, search_manifest))
        
        # Hunt for edge cases
        anomalies.extend(self._hunt_edge_cases(input_data))
        
        return anomalies
    
    def _hunt_positive_deviants(self, input_data: KillChainInput) -> List[Anomaly]:
        """
        Find systems/approaches that work exceptionally well.
        
        Args:
            input_data: Kill Chain input
        
        Returns:
            List of positive deviant anomalies
        """
        anomalies = []
        problem = input_data.problem_statement.lower()
        
        # M1 optimization context
        if "m1" in problem or "apple silicon" in problem:
            anomalies.append(Anomaly(
                description="Unified Memory Architecture eliminates CPU-GPU transfer bottleneck",
                deviation_score=0.9,
                source="Apple Silicon architecture",
                evidence={"uma": "Single memory pool for CPU/GPU/Neural Engine"},
                is_positive=True,
            ))
            
            anomalies.append(Anomaly(
                description="Quantized models (Q4_K_M) maintain quality with 4x less memory",
                deviation_score=0.85,
                source="LLM quantization research",
                evidence={"quantization": "4-bit weights, minimal perplexity increase"},
                is_positive=True,
            ))
        
        # LLM optimization context
        if "llm" in problem or "language model" in problem:
            anomalies.append(Anomaly(
                description="Serial processing (NUM_PARALLEL=1) prevents OOM on constrained RAM",
                deviation_score=0.8,
                source="Ollama configuration",
                evidence={"serial": "Single request at a time, stable memory usage"},
                is_positive=True,
            ))
        
        # Performance optimization context
        if "optimize" in problem or "performance" in problem:
            anomalies.append(Anomaly(
                description="Via negativa: Removing features often improves performance more than adding optimization",
                deviation_score=0.75,
                source="Lindy effect / Antifragile principles",
                evidence={"via_negativa": "Deletion reduces complexity, improves VDR"},
                is_positive=True,
            ))
        
        return anomalies
    
    def _hunt_constraint_violations(self, input_data: KillChainInput, manifest: SearchManifest) -> List[Anomaly]:
        """
        Find cases where violating assumed constraints still works.
        
        Args:
            input_data: Kill Chain input
            manifest: Search manifest
        
        Returns:
            List of constraint violation anomalies
        """
        anomalies = []
        
        # Check if constraints can be relaxed
        if input_data.constraints:
            anomalies.append(Anomaly(
                description=f"Some of {len(input_data.constraints)} constraints may be negotiable",
                deviation_score=0.6,
                source="Constraint analysis",
                evidence={"constraints": input_data.constraints},
                is_positive=True,
            ))
        
        return anomalies
    
    def _hunt_edge_cases(self, input_data: KillChainInput) -> List[Anomaly]:
        """
        Find edge cases that reveal hidden constraints.
        
        Args:
            input_data: Kill Chain input
        
        Returns:
            List of edge case anomalies
        """
        anomalies = []
        problem = input_data.problem_statement.lower()
        
        # Memory edge cases
        if "memory" in problem or "ram" in problem:
            anomalies.append(Anomaly(
                description="Memory compression can hide OOM issues until sudden crash",
                deviation_score=0.7,
                source="macOS memory management",
                evidence={"vm_compressor": "Aggressive compression before swap"},
                is_positive=False,  # Negative anomaly - warning
            ))
        
        # Thermal edge cases
        if "performance" in problem or "m1" in problem:
            anomalies.append(Anomaly(
                description="Thermal throttling can reduce performance by 40% after 5-10 minutes",
                deviation_score=0.8,
                source="M1 thermal management",
                evidence={"throttling": "90-100°C triggers clock speed reduction"},
                is_positive=False,  # Negative anomaly - warning
            ))
        
        return anomalies
