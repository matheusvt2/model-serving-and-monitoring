import os
import json
import logging
from typing import Any

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_kafka_producer(kafka_broker: str):
    """Get or create a Kafka producer for sending events."""
    from kafka import KafkaProducer
    import asyncio
    for attempt in range(10):
        try:
            logger.info(f"Attempting to connect to Kafka broker at {kafka_broker} (attempt {attempt+1}/10)")
            producer = KafkaProducer(
                bootstrap_servers=kafka_broker,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info(f"Successfully connected to Kafka broker at {kafka_broker}")
            return producer
        except Exception as e:
            logger.error(f"Failed to connect to Kafka broker {kafka_broker} (attempt {attempt+1}/10): {e}")
            await asyncio.sleep(5)
    logger.warning("Kafka producer not available after retries - skipping event streaming")
    return None

async def send_to_kafka(topic: str, data: Any, kafka_broker: str, producer=None):
    """Send a JSON-serializable event to a Kafka topic."""
    if producer is None:
        producer = await get_kafka_producer(kafka_broker)
    if producer:
        try:
            logger.debug(f"Sending event to Kafka topic '{topic}': {data}")
            producer.send(topic, data)
            producer.flush()
            logger.info(f"Successfully sent data to Kafka topic '{topic}'")
        except Exception as e:
            logger.error(f"Failed to send data to Kafka topic '{topic}': {e}")
    else:
        logger.warning("Kafka producer not available - skipping event streaming") 