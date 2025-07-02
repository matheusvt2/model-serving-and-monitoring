import logging
import json
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from kafka.errors import NoBrokersAvailable
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import time
import os

# Configure logging with proper format and level
LOG_LEVEL = "INFO" #os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants for Kafka and Elasticsearch
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'predictions')
ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', 'elasticsearch:9200')
ES_INDEX = os.environ.get('ES_INDEX', 'predictions')


def create_kafka_topic_if_not_exists(broker, topic_name, num_partitions=1, replication_factor=1):
    """
    Create a Kafka topic if it doesn't already exist.
    
    Args:
        broker (str): Kafka broker address
        topic_name (str): Name of the topic to create
        num_partitions (int): Number of partitions for the topic
        replication_factor (int): Replication factor for the topic
    """
    admin_client = KafkaAdminClient(bootstrap_servers=broker)
    topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
    try:
        admin_client.create_topics([topic])
        logger.info(f"Topic '{topic_name}' created successfully")
    except TopicAlreadyExistsError:
        logger.info(f"Topic '{topic_name}' already exists")
    except Exception as e:
        logger.error(f"Error creating topic '{topic_name}': {e}")
    finally:
        admin_client.close()
        
# Ensure the Kafka topic exists before starting the consumer
create_kafka_topic_if_not_exists(KAFKA_BROKER, KAFKA_TOPIC)


# Initialize Kafka consumer with retry logic
for attempt in range(20):
    try:
        logger.info(f"Attempting to connect to Kafka broker at {KAFKA_BROKER} (attempt {attempt+1}/20)")
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        logger.info(f"Successfully connected to Kafka broker at {KAFKA_BROKER}")
        break
    except NoBrokersAvailable:
        logger.warning(f"Kafka broker not available, retrying in 5 seconds... (attempt {attempt+1}/20)")
        time.sleep(5)
else:
    logger.error("Kafka broker not available after multiple attempts, exiting.")
    exit(1)

# Initialize Elasticsearch client
try:
    es = Elasticsearch(
        [{'host': ELASTICSEARCH_HOST.split(':')[0], 'port': int(ELASTICSEARCH_HOST.split(':')[1]), 'scheme': 'http'}],
        headers={
            "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
            "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
        }
    )
    logger.info(f"Connected to Elasticsearch at {ELASTICSEARCH_HOST}")
except Exception as e:
    logger.error(f"Failed to connect to Elasticsearch: {e}")
    exit(1)

logger.info(f"Starting to consume messages from Kafka topic '{KAFKA_TOPIC}' and index into Elasticsearch index '{ES_INDEX}'")

# Main event loop: consume messages from Kafka and index them into Elasticsearch
for message in consumer:
    try:
        event = message.value
        logger.debug(f"Received event from Kafka: {event}")
        # Index event into Elasticsearch
        res = es.index(index=ES_INDEX, document=event)
        logger.info(f"Indexed event into Elasticsearch: {res['result']} (ID: {res['_id']})")
    except Exception as e:
        logger.error(f"Failed to index event: {e}")

