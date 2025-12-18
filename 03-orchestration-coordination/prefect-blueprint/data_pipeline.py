import time
import random
from typing import List, Dict
from prefect import flow, task, get_run_logger
from pydantic import BaseModel, Field

# --- Schema Definition ---
# Prefect 3 leverages Pydantic V2 for robust parameter validation.
# This ensures that any data passed to the flow meets strict type requirements.
class ExtractConfig(BaseModel):
    source_url: str = Field(..., description="The API endpoint for data extraction")
    batch_size: int = Field(default=100, ge=1, description="Number of records to fetch")
    timeout_seconds: int = Field(default=30, description="Max wait time for request")

# --- Task Definitions ---
# Tasks are the atomic units of work. They are decorated with @task.
# Key features enabled here:
# - retries: If the task fails, it will auto-retry 3 times.
# - retry_delay_seconds: Waits 2 seconds between retries to allow transient issues to clear.
# - tags: Metadata for filtering in the UI.

@task(
    name="extract-task",
    description="Simulates network extraction with potential transient failure",
    retries=3,
    retry_delay_seconds=2,
    tags=["layer:raw", "op:extract"]
)
def extract_data(config: ExtractConfig) -> List:
    logger = get_run_logger()
    logger.info(f"Initiating extraction from {config.source_url} with batch size {config.batch_size}")
    
    # Simulation of network latency
    time.sleep(1.5)
    
    # Simulation of a transient network error (10% chance of failure)
    # This demonstrates the retry mechanism in the logs.
    if random.random() < 0.1:
        logger.error("Network connection unstable!")
        raise ConnectionError("Simulated transient network failure.")
    
    # Mock data generation
    data = [
        {"id": i, "metric": random.uniform(10.0, 100.0), "status": "active"} 
        for i in range(config.batch_size)
    ]
    
    logger.info(f"Successfully extracted {len(data)} records.")
    return data

@task(
    name="transform-task",
    description="Normalizes metrics and filters invalid records",
    tags=["layer:silver", "op:transform"]
)
def transform_data(raw_data: List) -> Dict[str, float]:
    logger = get_run_logger()
    logger.info("Starting transformation logic...")
    
    valid_records = [d for d in raw_data if d['status'] == 'active']
    total_metric = sum(d['metric'] for d in valid_records)
    average = total_metric / len(valid_records) if valid_records else 0.0
    
    time.sleep(1) # Simulate CPU intensive processing
    
    results = {
        "processed_count": len(valid_records),
        "average_metric": round(average, 4),
        "total_volume": round(total_metric, 2)
    }
    logger.info(f"Transformation complete. Insights: {results}")
    return results

@task(
    name="load-task",
    tags=["layer:gold", "op:load"]
)
def load_data(results: Dict[str, float], target_table: str):
    logger = get_run_logger()
    logger.info(f"Loading aggregations into {target_table}...")
    
    # Simulate database transaction
    time.sleep(0.5)
    
    logger.info("Transaction committed successfully.")

# --- Flow Definition ---
# The @flow decorator converts this function into a workflow.
# It manages the execution state of the tasks called within it.

@flow(
    name="Enterprise Data Pipeline",
    description="A hybrid-model ready pipeline for sales metrics",
    version="1.0.0",
    log_prints=True # Captures standard print statements as logs
)
def data_pipeline(
    source_url: str = "https://api.internal.prod/v1/metrics",
    target_table: str = "warehouse.public.daily_metrics",
    batch_size: int = 100
):
    logger = get_run_logger()
    logger.info("Pipeline execution started.")
    
    # Pydantic model instantiation for validation
    config = ExtractConfig(
        source_url=source_url, 
        batch_size=batch_size
    )
    
    # Task Execution
    # Note: We pass the Pydantic model directly to the task.
    # Prefect handles the serialization/deserialization of this complex object.
    raw_records = extract_data(config)
    aggregated_metrics = transform_data(raw_records)
    load_data(aggregated_metrics, target_table)
    
    logger.info("Pipeline execution finished.")

# --- Local Development Entrypoint ---
if __name__ == "__main__":
    # This allows developers to test the flow locally by simply running:
    # python data_pipeline.py
    data_pipeline()
