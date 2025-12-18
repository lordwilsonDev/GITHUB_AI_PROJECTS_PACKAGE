"""
Prefect 3 Advanced Pipeline - Version 2.0
Enhancements:
- Runtime invariants for provable correctness
- Failure taxonomy with intelligent retry logic
- Execution time bounds
- Output contract validation
- Self-auditing metadata
"""

import time
import random
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
from prefect import flow, task, get_run_logger
from prefect.states import Failed, Completed
from pydantic import BaseModel, Field, validator

# ============================================================================
# TEST INJECTION CONTROLS (for deterministic testing)
# ============================================================================
# Set INJECT_TRANSIENT_ONCE=1 to force a single transient failure on first attempt
# This allows deterministic testing of retry logic without relying on random chance
INJECT_TRANSIENT_ONCE = os.getenv("INJECT_TRANSIENT_ONCE", "0") == "1"
_transient_injected = False  # Module-level flag to track injection state

# Set INJECT_EMPTY_DATASET=1 to force empty dataset (tests invariant violation)
# This verifies the system fails fast when output contracts are violated
INJECT_EMPTY_DATASET = os.getenv("INJECT_EMPTY_DATASET", "0") == "1"

# ============================================================================
# FAILURE TAXONOMY - Intelligent Classification
# ============================================================================

class FailureClass(Enum):
    """Explicit failure classification for intelligent retry logic"""
    TRANSIENT = "transient"  # Network timeouts, rate limits → RETRY
    DETERMINISTIC = "deterministic"  # Schema violations, auth errors → FAIL FAST
    EXTERNAL_DEPENDENCY = "external"  # Third-party service down → CIRCUIT BREAKER
    DATA_QUALITY = "data_quality"  # Invalid data ranges → QUARANTINE


class TransientFailure(Exception):
    """Retryable failures: network issues, temporary unavailability"""
    pass


class DeterministicFailure(Exception):
    """Non-retryable failures: schema violations, authentication errors"""
    pass


class DataQualityFailure(Exception):
    """Data validation failures: out-of-range values, corrupt records"""
    pass


class ExternalDependencyFailure(Exception):
    """External service failures: API down, database unreachable"""
    pass


# ============================================================================
# RUNTIME INVARIANTS - Provable Correctness
# ============================================================================

class RuntimeInvariant:
    """Enforces hard invariants that must always hold"""
    
    @staticmethod
    def validate_records_processed(count: int, min_expected: int = 1):
        """Invariant: Must process at least min_expected records"""
        if count < min_expected:
            raise DeterministicFailure(
                f"INVARIANT VIOLATION: Processed {count} records, expected >= {min_expected}. "
                "This indicates silent failure."
            )
    
    @staticmethod
    def validate_execution_time(start_time: datetime, max_duration: timedelta):
        """Invariant: Execution must complete within time bounds"""
        elapsed = datetime.now() - start_time
        if elapsed > max_duration:
            raise DeterministicFailure(
                f"INVARIANT VIOLATION: Execution took {elapsed}, max allowed {max_duration}. "
                "This indicates performance degradation."
            )
    
    @staticmethod
    def validate_metric_range(value: float, min_val: float, max_val: float, field_name: str):
        """Invariant: Metrics must fall within expected ranges"""
        if not (min_val <= value <= max_val):
            raise DataQualityFailure(
                f"INVARIANT VIOLATION: {field_name}={value} outside range [{min_val}, {max_val}]. "
                "This indicates data corruption or upstream failure."
            )
    
    @staticmethod
    def validate_output_contract(results: Dict, required_keys: List[str]):
        """Invariant: Output must contain all required fields"""
        missing = [k for k in required_keys if k not in results]
        if missing:
            raise DeterministicFailure(
                f"INVARIANT VIOLATION: Output missing required keys: {missing}. "
                "This indicates incomplete processing."
            )


# ============================================================================
# ENHANCED SCHEMA WITH VALIDATION
# ============================================================================

class ExtractConfig(BaseModel):
    """Enhanced configuration with stricter validation"""
    source_url: str = Field(..., description="The API endpoint for data extraction")
    batch_size: int = Field(default=100, ge=1, le=10000, description="Number of records to fetch")
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Max wait time for request")
    max_execution_minutes: int = Field(default=5, ge=1, description="Maximum allowed execution time")
    
    @validator('source_url')
    def validate_url_scheme(cls, v):
        """Ensure URL has valid scheme"""
        if not v.startswith(('http://', 'https://')):
            raise DeterministicFailure(f"Invalid URL scheme: {v}. Must start with http:// or https://")
        return v


class PipelineMetadata(BaseModel):
    """Self-auditing metadata for forensic reconstruction"""
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    input_hash: str
    code_version: str = "2.0.0"
    environment: str = "local"
    outcome: str = "pending"
    records_processed: int = 0
    failure_class: Optional[str] = None


# ============================================================================
# ADVANCED TASK DEFINITIONS WITH INVARIANTS
# ============================================================================

@task(
    name="extract-task-v2",
    description="Enhanced extraction with failure classification and invariants",
    retries=0,  # We handle retries explicitly based on failure type
    tags=["layer:raw", "op:extract", "version:2.0"]
)
def extract_data_v2(config: ExtractConfig, metadata: PipelineMetadata) -> List:
    logger = get_run_logger()
    start_time = datetime.now()
    
    logger.info(f"[EXTRACT] Starting extraction from {config.source_url} (batch_size={config.batch_size})")
    
    try:
        # Simulate network latency
        time.sleep(1.5)
        
        # Controlled transient injection for testing (deterministic)
        global _transient_injected
        if INJECT_TRANSIENT_ONCE and not _transient_injected:
            _transient_injected = True
            logger.warning("[EXTRACT] Injected transient failure for Test 2B - RETRYABLE")
            raise TransientFailure("Injected transient failure for Test 2B")
        
        # Simulate different failure types for demonstration (random, default behavior)
        failure_sim = random.random()
        
        if failure_sim < 0.05:  # 5% transient failure
            logger.warning("[EXTRACT] Transient network failure detected - RETRYABLE")
            raise TransientFailure("Network timeout - temporary issue")
        
        elif failure_sim < 0.08:  # 3% deterministic failure
            logger.error("[EXTRACT] Authentication failure - NON-RETRYABLE")
            raise DeterministicFailure("API authentication failed - check credentials")
        
        # Mock data generation (with optional empty dataset injection for Test 2C)
        if INJECT_EMPTY_DATASET:
            logger.warning("[EXTRACT] Injected empty dataset for Test 2C - INVARIANT VIOLATION")
            data = []
        else:
            data = [
                {"id": i, "metric": random.uniform(10.0, 100.0), "status": "active"} 
                for i in range(config.batch_size)
            ]
        
        # INVARIANT: Must extract at least 1 record
        RuntimeInvariant.validate_records_processed(len(data), min_expected=1)
        
        # INVARIANT: Execution time must be within bounds
        RuntimeInvariant.validate_execution_time(
            start_time, 
            timedelta(minutes=config.max_execution_minutes)
        )
        
        logger.info(f"[EXTRACT] ✓ Successfully extracted {len(data)} records (invariants validated)")
        metadata.records_processed = len(data)
        
        return data
        
    except TransientFailure as e:
        logger.warning(f"[EXTRACT] Transient failure: {e} - Will retry")
        metadata.failure_class = FailureClass.TRANSIENT.value
        # Retry logic: wait and retry up to 3 times
        for attempt in range(1, 4):
            logger.info(f"[EXTRACT] Retry attempt {attempt}/3 after 2s delay...")
            time.sleep(2)
            try:
                # Retry the extraction
                data = [
                    {"id": i, "metric": random.uniform(10.0, 100.0), "status": "active"} 
                    for i in range(config.batch_size)
                ]
                RuntimeInvariant.validate_records_processed(len(data), min_expected=1)
                logger.info(f"[EXTRACT] ✓ Retry successful on attempt {attempt}")
                metadata.records_processed = len(data)
                return data
            except Exception as retry_error:
                logger.warning(f"[EXTRACT] Retry {attempt} failed: {retry_error}")
                if attempt == 3:
                    raise TransientFailure(f"Exhausted retries after {attempt} attempts")
        
    except DeterministicFailure as e:
        logger.error(f"[EXTRACT] Deterministic failure: {e} - FAILING FAST (no retry)")
        metadata.failure_class = FailureClass.DETERMINISTIC.value
        raise  # Fail immediately, no retry


@task(
    name="transform-task-v2",
    description="Enhanced transformation with data quality invariants",
    tags=["layer:silver", "op:transform", "version:2.0"]
)
def transform_data_v2(raw_data: List, metadata: PipelineMetadata) -> Dict[str, float]:
    logger = get_run_logger()
    start_time = datetime.now()
    
    logger.info(f"[TRANSFORM] Starting transformation on {len(raw_data)} records")
    
    try:
        valid_records = [d for d in raw_data if d['status'] == 'active']
        
        # INVARIANT: Must have at least some valid records
        RuntimeInvariant.validate_records_processed(len(valid_records), min_expected=1)
        
        total_metric = sum(d['metric'] for d in valid_records)
        average = total_metric / len(valid_records) if valid_records else 0.0
        
        time.sleep(1)  # Simulate CPU intensive processing
        
        results = {
            "processed_count": len(valid_records),
            "average_metric": round(average, 4),
            "total_volume": round(total_metric, 2)
        }
        
        # INVARIANT: Output must contain all required fields
        RuntimeInvariant.validate_output_contract(
            results, 
            required_keys=["processed_count", "average_metric", "total_volume"]
        )
        
        # INVARIANT: Metrics must be within expected ranges
        RuntimeInvariant.validate_metric_range(
            results["average_metric"], 
            min_val=0.0, 
            max_val=200.0, 
            field_name="average_metric"
        )
        
        # INVARIANT: Execution time bounds
        RuntimeInvariant.validate_execution_time(start_time, timedelta(minutes=2))
        
        logger.info(f"[TRANSFORM] ✓ Transformation complete. Results: {results} (invariants validated)")
        return results
        
    except DataQualityFailure as e:
        logger.error(f"[TRANSFORM] Data quality failure: {e} - QUARANTINING")
        metadata.failure_class = FailureClass.DATA_QUALITY.value
        raise


@task(
    name="load-task-v2",
    description="Enhanced load with transaction guarantees",
    tags=["layer:gold", "op:load", "version:2.0"]
)
def load_data_v2(results: Dict[str, float], target_table: str, metadata: PipelineMetadata):
    logger = get_run_logger()
    
    logger.info(f"[LOAD] Loading aggregations into {target_table}...")
    
    try:
        # Simulate database transaction
        time.sleep(0.5)
        
        # INVARIANT: Must have data to load
        if results["processed_count"] == 0:
            raise DeterministicFailure("Cannot load zero records - upstream failure")
        
        logger.info(f"[LOAD] ✓ Transaction committed successfully. Loaded {results['processed_count']} records")
        
    except Exception as e:
        logger.error(f"[LOAD] Load failure: {e}")
        metadata.failure_class = FailureClass.EXTERNAL_DEPENDENCY.value
        raise


# ============================================================================
# ENHANCED FLOW WITH SELF-AUDITING
# ============================================================================

@flow(
    name="Enterprise Data Pipeline V2 - Advanced",
    description="Production-grade pipeline with invariants and failure taxonomy",
    version="2.0.0",
    log_prints=True
)
def data_pipeline_v2(
    source_url: str = "https://api.internal.prod/v1/metrics",
    target_table: str = "warehouse.public.daily_metrics",
    batch_size: int = 100
):
    logger = get_run_logger()
    
    # Initialize self-auditing metadata
    metadata = PipelineMetadata(
        run_id=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        start_time=datetime.now(),
        input_hash=f"{hash((source_url, target_table, batch_size))}",
        environment="local"
    )
    
    logger.info(f"[PIPELINE] Starting execution (run_id={metadata.run_id})")
    logger.info(f"[PIPELINE] Input hash: {metadata.input_hash}")
    
    try:
        # Pydantic validation with enhanced constraints
        config = ExtractConfig(
            source_url=source_url, 
            batch_size=batch_size
        )
        
        # Task execution with invariant enforcement
        raw_records = extract_data_v2(config, metadata)
        aggregated_metrics = transform_data_v2(raw_records, metadata)
        load_data_v2(aggregated_metrics, target_table, metadata)
        
        # Mark successful completion
        metadata.end_time = datetime.now()
        metadata.outcome = "success"
        
        # Emit audit log
        execution_time = (metadata.end_time - metadata.start_time).total_seconds()
        logger.info(f"[PIPELINE] ✓ Pipeline execution finished successfully")
        logger.info(f"[AUDIT] Run ID: {metadata.run_id}")
        logger.info(f"[AUDIT] Execution time: {execution_time:.2f}s")
        logger.info(f"[AUDIT] Records processed: {metadata.records_processed}")
        logger.info(f"[AUDIT] Input hash: {metadata.input_hash}")
        logger.info(f"[AUDIT] Code version: {metadata.code_version}")
        logger.info(f"[AUDIT] Outcome: {metadata.outcome}")
        
    except (TransientFailure, DeterministicFailure, DataQualityFailure, ExternalDependencyFailure) as e:
        metadata.end_time = datetime.now()
        metadata.outcome = "failed"
        
        logger.error(f"[PIPELINE] ✗ Pipeline failed: {e}")
        logger.error(f"[AUDIT] Run ID: {metadata.run_id}")
        logger.error(f"[AUDIT] Failure class: {metadata.failure_class}")
        logger.error(f"[AUDIT] Outcome: {metadata.outcome}")
        
        raise


# ============================================================================
# LOCAL DEVELOPMENT ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    # Test the advanced pipeline locally
    data_pipeline_v2()
