#!/bin/bash
import os
import logging
import time
import uuid
from fastapi import FastAPI, APIRouter, status, Response, HTTPException
from models import IrisInput, IrisPrediction, ErrorResponse, HealthResponse
import mlflow.pyfunc
import mlflow
from services.model_service import predict_with_model
from services.kafka_service import send_to_kafka
from services.metrics_service import log_model_metrics
from prometheus_fastapi_instrumentator import Instrumentator
import psutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment/config
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'predictions')
MODEL_PROD_NAME = os.environ.get('MODEL_NAME', 'RandomForestClassifier')
MODEL_SHADOW_NAME = os.environ.get('MODEL_NAME', 'RobustRandomForestClassifier')
MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://mlflow:5000')

# Load models
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
logger.info(f"MlFlow tracking URI: {MLFLOW_TRACKING_URI}")

# Initialize MLflow client
client = mlflow.tracking.MlflowClient()

model_uri_prod = f"models:/{MODEL_PROD_NAME}@production"
model_uri_shadow = f"models:/{MODEL_SHADOW_NAME}@shadow"

# Load production model and get version info
try:
    logger.info("Loading production model from MLflow...")
    model_prod = mlflow.pyfunc.load_model(model_uri_prod)
    model_info_prod = client.get_model_version_by_alias(MODEL_PROD_NAME, "production")
    prod_version = model_info_prod.version
    logger.info(f"Model (prod) successfully loaded from MlFlow - version: {prod_version}")
except Exception as e:
    logger.error(f"Failed to load model (prod) from MlFlow: {e}")
    model_prod = None
    prod_version = "unknown"

# Load shadow model and get version info
try:
    logger.info("Loading shadow model from MLflow...")
    model_shadow = mlflow.pyfunc.load_model(model_uri_shadow)
    model_info_shadow = client.get_model_version_by_alias(MODEL_SHADOW_NAME, "shadow")
    shadow_version = model_info_shadow.version
    logger.info(f"Model (shadow) successfully loaded from MlFlow - version: {shadow_version}")
except Exception as e:
    logger.error(f"Failed to load model (shadow) from MlFlow: {e}")
    model_shadow = None
    shadow_version = "unknown"

app = FastAPI()
router = APIRouter()

# ThreadPoolExecutor for model inference
executor = ThreadPoolExecutor(max_workers=4)

async def predict_async(model, iris_input):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, predict_with_model, model, iris_input)

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse
)
async def health_check():
    """Health check endpoint to verify service is running and model is loaded."""
    logger.info("Health check requested")
    response = HealthResponse(
        status="healthy",
        model_prod_loaded=model_prod is not None,
        model_shadow_loaded=model_shadow is not None,
        model_prod_name=MODEL_PROD_NAME,
        model_prod_version=prod_version,
        model_shadow_name=MODEL_SHADOW_NAME,
        model_shadow_version=shadow_version
    )
    logger.info(f"Health check response: {response}")
    return response

@router.post(
    "/predict",
    status_code=status.HTTP_201_CREATED,
    response_model=IrisPrediction
)
async def predict(
    iris_input: IrisInput,
    response: Response
):
    """Predict the iris species from input features using both production and shadow models, log metrics, and stream events to Kafka."""
    logger.info(f"Received prediction request with input: {iris_input}")
    event_uuid = str(uuid.uuid4())
    # --- Production Model ---
    prod_result = await predict_async(model_prod, iris_input)
    if prod_result["error"]:
        logger.error(f"Production model prediction failed: {prod_result['error']}")
        raise HTTPException(status_code=500, detail="Production prediction failed")
    # --- Shadow Model ---
    shadow_available = model_shadow is not None
    if shadow_available:
        shadow_result = await predict_async(model_shadow, iris_input)
    else:
        shadow_result = None
    # --- Send Events to Kafka ---
    event_common = {
        "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input": iris_input.model_dump(),
        "request_id": f"req_{int(time.time() * 1000)}",
        "event_uuid": event_uuid
    }
    # Production event
    event_prod = {
        **event_common,
        "model_alias": "production",
        "prediction": prod_result["result"],
        "prediction_value": prod_result["prediction_value"],
        "class_probabilities": prod_result["class_probabilities"],
        "class_probabilities_map": prod_result["class_probabilities_map"],
        "duration": prod_result["duration"]
    }
    logger.debug(f"Production event created: {event_prod}")
    await send_to_kafka(KAFKA_TOPIC, event_prod, KAFKA_BROKER)
    # Shadow event
    if shadow_available and shadow_result and not shadow_result["error"]:
        logger.debug(f"Creating shadow event with result: {shadow_result}")
        event_shadow = {
            **event_common,
            "model_alias": "shadow",
            "prediction": shadow_result["result"],
            "prediction_value": shadow_result["prediction_value"],
            "class_probabilities": shadow_result["class_probabilities"],
            "class_probabilities_map": shadow_result["class_probabilities_map"],
            "duration": shadow_result["duration"]
        }
        logger.debug(f"Shadow event created: {event_shadow}")
        await send_to_kafka(KAFKA_TOPIC, event_shadow, KAFKA_BROKER)
    # --- Prometheus Metrics ---
    try:
        process = psutil.Process(os.getpid())
        cpu_usage = process.cpu_percent(interval=None)  # Use last computed value, non-blocking
        memory_usage = process.memory_info().rss
        log_model_metrics("production", prod_result["duration"], cpu_usage, memory_usage, 
                         event_uuid=event_uuid, model_version=prod_version)
        if shadow_available and shadow_result and not shadow_result["error"]:
            log_model_metrics("shadow", shadow_result["duration"], cpu_usage, memory_usage, 
                             event_uuid=event_uuid, model_version=shadow_version)
    except Exception as e:
        logger.error(f"Failed to record metrics: {e}")
    logger.info("Prediction endpoint completed successfully.")
    return prod_result["result"]

app.include_router(router)

Instrumentator().instrument(app).expose(app)