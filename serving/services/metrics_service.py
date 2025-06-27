import os
import logging
import time
from prometheus_client import Gauge, Counter, Histogram, Summary
from typing import Dict, Optional

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus custom metrics following best practices
# Gauges for current values
MODEL_DURATION = Gauge('model_prediction_duration_seconds', 'Prediction duration in seconds', ['model_alias', 'event_uuid', 'model_version'])
MODEL_CPU = Gauge('model_prediction_cpu_percent', 'CPU usage during prediction', ['model_alias', 'event_uuid', 'model_version'])
MODEL_MEMORY = Gauge('model_prediction_memory_bytes', 'Memory usage during prediction', ['model_alias', 'event_uuid', 'model_version'])
MODEL_QUEUE_SIZE = Gauge('model_prediction_queue_size', 'Current queue size for model predictions', ['model_alias'])
MODEL_CONCURRENT_REQUESTS = Gauge('model_concurrent_requests', 'Number of concurrent requests being processed', ['model_alias'])

# Counters for cumulative values
MODEL_PREDICTIONS_TOTAL = Counter('model_predictions_total', 'Total number of predictions made', ['model_alias', 'model_version', 'status'])
MODEL_ERRORS_TOTAL = Counter('model_errors_total', 'Total number of prediction errors', ['model_alias', 'model_version', 'error_type'])
MODEL_REQUESTS_TOTAL = Counter('model_requests_total', 'Total number of requests received', ['model_alias', 'model_version', 'endpoint'])

# Histograms for distribution analysis
MODEL_PREDICTION_DURATION_HISTOGRAM = Histogram(
    'model_prediction_duration_histogram_seconds',
    'Prediction duration distribution',
    ['model_alias', 'model_version'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0]
)

MODEL_INPUT_SIZE_HISTOGRAM = Histogram(
    'model_input_size_bytes',
    'Input data size distribution',
    ['model_alias', 'model_version'],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
)

# Summaries for quantile analysis
MODEL_PREDICTION_DURATION_SUMMARY = Summary(
    'model_prediction_duration_summary_seconds',
    'Prediction duration summary with quantiles',
    ['model_alias', 'model_version']
)

def log_model_metrics(
    model_alias: str, 
    duration: float, 
    cpu_usage: float, 
    memory_usage: float, 
    event_uuid: str = None,
    model_version: str = "1.0",
    status: str = "success",
    input_size: int = 0,
    error_type: str = None
):
    """
    Log and expose comprehensive Prometheus metrics for a model prediction.
    
    Args:
        model_alias: Name/alias of the model
        duration: Prediction duration in seconds
        cpu_usage: CPU usage as decimal (0.0-1.0)
        memory_usage: Memory usage in bytes
        event_uuid: Unique identifier for the event
        model_version: Version of the model
        status: Status of the prediction (success, error, timeout)
        input_size: Size of input data in bytes
        error_type: Type of error if any occurred
    """
    # Log message
    msg = f"{model_alias.capitalize()} model metrics - CPU: {cpu_usage:.2%}, Memory: {memory_usage} bytes, Duration: {duration:.3f}s"
    if event_uuid:
        msg += f" | event_uuid: {event_uuid}"
    if model_version:
        msg += f" | version: {model_version}"
    logger.info(msg)
    
    # Set labels
    labels = {
        'model_alias': model_alias,
        'event_uuid': event_uuid or 'none',
        'model_version': model_version
    }
    
    # Update gauges
    MODEL_DURATION.labels(**labels).set(duration)
    MODEL_CPU.labels(**labels).set(cpu_usage)  
    MODEL_MEMORY.labels(**labels).set(memory_usage)
    
    # Update counters
    MODEL_PREDICTIONS_TOTAL.labels(
        model_alias=model_alias,
        model_version=model_version,
        status=status
    ).inc()
    
    if error_type:
        MODEL_ERRORS_TOTAL.labels(
            model_alias=model_alias,
            model_version=model_version,
            error_type=error_type
        ).inc()
    
    # Update histograms
    MODEL_PREDICTION_DURATION_HISTOGRAM.labels(
        model_alias=model_alias,
        model_version=model_version
    ).observe(duration)
    
    if input_size > 0:
        MODEL_INPUT_SIZE_HISTOGRAM.labels(
            model_alias=model_alias,
            model_version=model_version
        ).observe(input_size)
    
    # Update summary
    MODEL_PREDICTION_DURATION_SUMMARY.labels(
        model_alias=model_alias,
        model_version=model_version
    ).observe(duration)

def log_comparison_metrics(prod_metrics: Dict, shadow_metrics: Dict, event_uuid: str):
    """
    Log production and shadow model metrics side by side for a given event_uuid.
    
    Args:
        prod_metrics: Dictionary containing production model metrics
        shadow_metrics: Dictionary containing shadow model metrics
        event_uuid: Unique identifier for the event
    """
    prod_duration = prod_metrics.get('duration', 0)
    shadow_duration = shadow_metrics.get('duration', 0)
    duration_diff = abs(prod_duration - shadow_duration)
    duration_diff_percent = (duration_diff / prod_duration * 100) if prod_duration > 0 else 0
    
    msg = (
        f"Comparison metrics for event_uuid={event_uuid}:\n"
        f"  Production: duration={prod_duration:.3f}s, CPU={prod_metrics.get('cpu_usage', 0):.2%}, "
        f"Mem={prod_metrics.get('memory_usage', 0)} bytes\n"
        f"  Shadow:     duration={shadow_duration:.3f}s, CPU={shadow_metrics.get('cpu_usage', 0):.2%}, "
        f"Mem={shadow_metrics.get('memory_usage', 0)} bytes\n"
        f"  Difference: duration_diff={duration_diff:.3f}s ({duration_diff_percent:.1f}%)"
    )
    logger.info(msg)

def update_queue_metrics(model_alias: str, queue_size: int):
    """Update queue size metrics for a model."""
    MODEL_QUEUE_SIZE.labels(model_alias=model_alias).set(queue_size)

def update_concurrent_requests(model_alias: str, concurrent_count: int):
    """Update concurrent requests metrics for a model."""
    MODEL_CONCURRENT_REQUESTS.labels(model_alias=model_alias).set(concurrent_count)

def log_request_metrics(model_alias: str, model_version: str, endpoint: str):
    """Log request metrics for tracking API usage."""
    MODEL_REQUESTS_TOTAL.labels(
        model_alias=model_alias,
        model_version=model_version,
        endpoint=endpoint
    ).inc()